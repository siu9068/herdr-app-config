#!/bin/sh
# Restores this herdr-app setup into ~/.config/herdr-app (or $HERDR_APP_HOME).
# Run with herdr-app open: the layout is cloned from the installed version's shipped `main`.
# Safe to run again: mods are replaced with this repo's copies, keys are merged, the layout is rebuilt.
set -eu

REPO=$(cd "$(dirname "$0")" && pwd)
HOME_DIR=${HERDR_APP_HOME:-$HOME/.config/herdr-app}
LAYOUT=main-limits

command -v herdr-app >/dev/null || { echo "herdr-app not found; install Herdr first" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 1; }
[ -d "$HOME_DIR/mods" ] || { echo "$HOME_DIR/mods missing; open herdr-app once first" >&2; exit 1; }

# 1. Mods
for m in "$REPO"/mods/*/; do
  name=$(basename "$m")
  rm -rf "$HOME_DIR/mods/$name"
  cp -R "$m" "$HOME_DIR/mods/$name"
  herdr-app check "$HOME_DIR/mods/$name"
done

# 2. Keys: add this repo's bindings; existing keys with the same name are replaced.
keys="$HOME_DIR/keys.json"
[ -f "$keys" ] || echo '{}' >"$keys"
cp "$keys" "$keys.bak"
jq -s '.[0] * .[1]' "$keys.bak" "$REPO/keys.json" >"$keys.tmp" && mv "$keys.tmp" "$keys"

# 3. Layout: a fresh clone of shipped `main` with the Limits panel under Agents.
rm -f "$HOME_DIR/layouts/$LAYOUT.json"
herdr-app do layout.clone "{\"name\":\"main\",\"as\":\"$LAYOUT\"}" >/dev/null
i=0
while [ ! -f "$HOME_DIR/layouts/$LAYOUT.json" ] && [ "$i" -lt 20 ]; do sleep 0.5; i=$((i + 1)); done
f="$HOME_DIR/layouts/$LAYOUT.json"
[ -f "$f" ] || { echo "layout clone did not appear; is herdr-app open?" >&2; exit 1; }
jq '{"id":"agent-limits","type":"block","content":{"mod":"agent-limits"},"size":{"px":106}} as $b
  | walk(if type == "object" and (.children | type) == "array"
         then .children |= [.[] | select(.id != "agent-limits") | if .id == "agents" then ., $b else . end]
         else . end)' "$f" >"$f.tmp" && mv "$f.tmp" "$f"
grep -q '"agent-limits"' "$f" || { echo "no \"agents\" block found in $LAYOUT; add the Limits block by hand" >&2; exit 1; }
herdr-app do layout.switch "{\"name\":\"$LAYOUT\"}" >/dev/null

echo "done: mods, keys (backup: $keys.bak), layout $LAYOUT"
