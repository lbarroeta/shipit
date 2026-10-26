#!/usr/bin/env bash
# shipit companion check / install.
#
# Default: report only. Nothing is installed, nothing is mutated.
#   ./scripts/companions.sh
#
# With --yes: install what can be installed safely and locally.
#   ./scripts/companions.sh --yes
#
# Never does, at any flag:
#   - build a graph (`init` builds the code-only graph; a semantic `graphify .` costs tokens)
#   - pipe curl into a shell
#   - use sudo
#   - install a package manager
#
# Anything outside those limits is printed as a command for you to run.

set -uo pipefail

YES=0
[ "${1:-}" = "--yes" ] && YES=1

ok()   { printf '  \033[32mok\033[0m      %-18s %s\n' "$1" "${2:-}"; }
miss() { printf '  \033[33mmissing\033[0m %-18s %s\n' "$1" "${2:-}"; }
note() { printf '          %s\n' "$1"; }
run()  { printf '  \033[36m$\033[0m %s\n' "$*"; [ "$YES" = 1 ] && "$@"; }

has() { command -v "$1" >/dev/null 2>&1; }

# A plugin counts as present when `claude plugin list` names it. Grep is scoped
# to the line start so a marketplace description mentioning it does not match.
plugin_present() {
  has claude || return 1
  claude plugin list 2>/dev/null | grep -qE "(^|[[:space:]])$1([[:space:]]|@|$)"
}

echo
echo "tier 0 — required"
if has git; then ok git "$(git --version | awk '{print $3}')"
else
  miss git "shipit cannot run without it"
  note "install git, then re-run this script"
  exit 1
fi

echo
echo "tier 1 — recommended (handoff needs these to reach GitHub; review needs ponytail)"
if has gh; then
  if gh auth status >/dev/null 2>&1; then
    ok gh "authenticated as $(gh api user --jq .login 2>/dev/null || echo '?')"
  else
    miss gh "installed but not authenticated"
    note "run: gh auth login"
  fi
else
  miss gh "handoff cannot open or update pull requests"
  note "macOS: brew install gh   ·   see https://cli.github.com for other platforms"
fi

if plugin_present ponytail; then
  ok ponytail "code-review engine"
else
  miss ponytail "code-review and run's review stage cannot run"
  note "claude plugin marketplace add DietrichGebert/ponytail"
  note "claude plugin install ponytail@ponytail"
  note "shipit's own rules override its test and report-length rules inside shipit skills"
fi

echo
echo "tier 2 — accelerators (shipit works without them, just costs more tokens)"
if has graphify; then
  ok "graphify cli" "$(command -v graphify)"
elif has uv; then
  miss "graphify cli" "discovery falls back to rg / git grep"
  run uv tool install graphifyy
elif has pipx; then
  miss "graphify cli" "discovery falls back to rg / git grep"
  run pipx install graphifyy
else
  miss "graphify cli" "discovery falls back to rg / git grep"
  note "needs uv or pipx first — this script will not install a package manager"
  note "macOS: brew install uv    then: uv tool install graphifyy"
fi

if [ -f graphify-out/graph.json ]; then
  ok "graphify graph" "graphify-out/graph.json"
else
  miss "graphify graph" "having the CLI does not give you a graph"
  note "build it in the main checkout: graphify update ."
  note "code only: no LLM, no tokens. /shipit:init runs it."
fi

if plugin_present caveman; then
  ok caveman "prose compression active"
else
  miss caveman "reports and chat prose stay uncompressed"
  note "claude plugin marketplace add JuliusBrussee/caveman"
  note "claude plugin install caveman@caveman"
  note "shipit exempts non-developer QA steps and PR bodies from compression"
fi

# The Context7 MCP is a session fact this script cannot see; doctor adds it.
# `ctx7 whoami` exits 0 either way; only its text tells the states apart. Anything but `Logged in` counts as not ready.
if has ctx7; then
  if ctx7 whoami 2>/dev/null | grep -q "Logged in"; then
    ok "context7 cli" "$(command -v ctx7), logged in"
  else
    miss "context7 login" "ctx7 installed but not logged in or failing: lookups may fail"
    note "run: ctx7 login    (or export CONTEXT7_API_KEY=<key>)"
  fi
else
  miss "context7 cli" "fine if the Context7 MCP is connected; otherwise API facts are unverified"
  note "MCP (preferred): claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp --header \"Authorization: Bearer <key>\""
  note "or CLI: npm install -g ctx7 && ctx7 login"
fi

echo
if [ "$YES" = 1 ]; then
  echo "done. commands above with \$ were executed; the rest are yours to run."
else
  echo "report only — nothing was installed. re-run with --yes to install tier 1-2."
fi
echo
