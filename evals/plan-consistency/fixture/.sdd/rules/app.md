# App layer

Business behavior lives in app domain modules; API adapters shape public output.
External payload consumers must preserve their documented contracts. Enforce
permission checks before any storage read. Existing policy functions are the
local reuse candidates; verify their semantics before using one.
