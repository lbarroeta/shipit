#!/usr/bin/env bash
# shipit installer for OpenCode.
#
# Fresh machine:
#   git clone https://github.com/KodimTech/shipit ~/.config/opencode/plugins/shipit
#   ~/.config/opencode/plugins/shipit/scripts/install-opencode.sh
#
# Already cloned anywhere:
#   ./scripts/install-opencode.sh
#
# What it does: clone or update the repo, then symlink the available commands into
# your OpenCode commands directory. Re-running it is an update — safe any time.
#
# Never does: sudo, npm install, touch opencode.json, or write outside
# $SHIPIT_ROOT and the commands directory.
#
# Uninstall:
#   rm ~/.config/opencode/commands/shipit-*.md && rm -rf "$SHIPIT_ROOT"

set -uo pipefail

REPO="${SHIPIT_REPO:-https://github.com/KodimTech/shipit}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
ROOT="${SHIPIT_ROOT:-$CONFIG/plugins/shipit}"
COMMANDS="$CONFIG/commands"

ok()   { printf '  \033[32mok\033[0m    %s\n' "$1"; }
info() { printf '  \033[36m→\033[0m     %s\n' "$1"; }
die()  { printf '  \033[31mfail\033[0m  %s\n' "$1" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "git not found. Install git, then re-run."

# Running from inside a checkout already? Use it — do not clone a second copy.
here=$(CDPATH= cd -- "$(dirname -- "$0")/.." 2>/dev/null && pwd)
if [ -d "${here:-/nonexistent}/.opencode/command" ]; then
  ROOT=$here
  info "using this checkout: $ROOT"
fi
if [ -d "$ROOT/.git" ]; then
  if git -C "$ROOT" pull --ff-only --quiet; then ok "updated $ROOT"
  else info "not updated (local changes or another branch); linking current files"; fi
else
  mkdir -p "$(dirname "$ROOT")" || die "cannot create $(dirname "$ROOT")"
  git clone --quiet --depth 1 "$REPO" "$ROOT" ||
    die "clone failed from $REPO. Check the network, then re-run."
  ok "cloned into $ROOT"
fi

src="$ROOT/.opencode/command"
[ -d "$src" ] || die "no commands at $src — wrong SHIPIT_ROOT?"

mkdir -p "$COMMANDS" || die "cannot create $COMMANDS"
# Retire only installer-owned links for renamed commands.
# Preserve user-authored command files and unrelated symlinks.
for legacy_name in task plan implement handoff; do
  legacy_command="$COMMANDS/shipit-$legacy_name.md"
  if [ -L "$legacy_command" ] && [ "$(readlink "$legacy_command")" = "$src/shipit-$legacy_name.md" ]; then
    rm "$legacy_command" || die "cannot retire old shipit-$legacy_name command link"
  fi
done
n=0
for f in "$src"/*.md; do
  [ -e "$f" ] || break
  ln -sfn "$f" "$COMMANDS/$(basename "$f")" || die "cannot link $(basename "$f")"
  n=$((n + 1))
done
[ "$n" -gt 0 ] || die "no command files found in $src"
ok "linked $n commands into $COMMANDS"

# The check: OpenCode itself must resolve them, not just the filesystem.
if command -v opencode >/dev/null 2>&1; then
  resolved=$(opencode debug config 2>/dev/null) || die "opencode debug config failed"
  found=0
  for f in "$src"/*.md; do
    [ -e "$f" ] || break
    command_name=$(basename "$f" .md)
    case "$resolved" in
      *\""$command_name"\"*) found=$((found + 1)) ;;
    esac
  done
  [ "$found" = "$n" ] ||
    die "opencode resolved $found of $n shipped commands. Run: opencode debug config"
  ok "opencode resolves all $n"
else
  info "opencode not on PATH — install it, then verify with: opencode debug config"
fi

printf '\nDone. In any repo: \033[1m/shipit-init\033[0m, then \033[1m/shipit-code-plan\033[0m.\n'
[ "$ROOT" != "${SHIPIT_ROOT:-$CONFIG/plugins/shipit}" ] &&
  printf 'Non-default location — add to your shell profile: export SHIPIT_ROOT=%s\n' "$ROOT"
exit 0
