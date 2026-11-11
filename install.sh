#!/bin/sh
# Restores this herdr-app setup into ~/.config/herdr-app (or $HERDR_APP_HOME).
# Run with herdr-app open: the layout and Spaces are cloned from the installed version's shipped ones.
# Safe to run again: mods are replaced with this repo's copies, keys are merged, the layout is rebuilt.
# The config-sync mod runs it again by itself after a Herdr update.
set -eu

REPO=$(cd "$(dirname "$0")" && pwd)
HOME_DIR=${HERDR_APP_HOME:-$HOME/.config/herdr-app}
LAYOUT=main-limits
STATE=$HOME/.local/state/herdr-app-config
# off: the Spaces sidebar no longer scrolls to the current space (patches/spaces-plus-scroll.py).
SPACES_SCROLL=on

command -v herdr-app >/dev/null || { echo "herdr-app not found; install Herdr first" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 not found (xcode-select --install)" >&2; exit 1; }
[ -d "$HOME_DIR/mods" ] || { echo "$HOME_DIR/mods missing; open herdr-app once first" >&2; exit 1; }

wait_for() { i=0; while [ ! -f "$1" ] && [ "$i" -lt 20 ]; do sleep 0.5; i=$((i + 1)); done; [ -f "$1" ]; }

# 1. Mods: check every repo copy before replacing anything, so a broken one leaves the installed mods alone.
for m in "$REPO"/mods/*/; do herdr-app check "$m"; done
for m in "$REPO"/mods/*/; do
  name=$(basename "$m")
  rm -rf "$HOME_DIR/mods/$name"
  cp -R "$m" "$HOME_DIR/mods/$name"
done

# 2. Keys: add this repo's bindings; existing keys with the same name are replaced.
keys="$HOME_DIR/keys.json"
[ -f "$keys" ] || echo '{}' >"$keys"
cp "$keys" "$keys.bak"
# Separate lines: set -e ignores a failure on the left of &&.
jq -s '.[0] * .[1]' "$keys.bak" "$REPO/keys.json" >"$keys.tmp"
mv "$keys.tmp" "$keys"

# 3. herdr-core templates (hc run <name> "<task>"); same names are replaced.
TEMPLATES=$HOME/.config/herdr-core/templates
mkdir -p "$TEMPLATES"
cp "$REPO"/templates/*.md "$TEMPLATES/"

# 4. spaces-plus: a fresh clone of the shipped Spaces mod with an "Open folder" button beside its + and a group mode.
# Built beside the old one and swapped in only when it patches and checks, so a Herdr change that
# breaks the patch keeps the working copy (or plain Spaces) instead of a broken sidebar.
SPACES_MOD=spaces-plus
rm -rf "$HOME_DIR/mods/spaces-plus-new"
herdr-app do mod.clone '{"name":"spaces","as":"spaces-plus-new"}' >/dev/null
if wait_for "$HOME_DIR/mods/spaces-plus-new/main.js" &&
  python3 "$REPO/patches/spaces-plus.py" "$HOME_DIR/mods/spaces-plus-new/main.js" &&
  { [ "$SPACES_SCROLL" = off ] || python3 "$REPO/patches/spaces-plus-scroll.py" "$HOME_DIR/mods/spaces-plus-new/main.js"; } &&
  herdr-app check "$HOME_DIR/mods/spaces-plus-new"; then
  # The clone rewrote its own asset prefix; point it at the final name.
  sed -i '' 's#mods/spaces-plus-new/#mods/spaces-plus/#g' "$HOME_DIR/mods/spaces-plus-new/main.js"
  rm -rf "$HOME_DIR/mods/spaces-plus"
  mv "$HOME_DIR/mods/spaces-plus-new" "$HOME_DIR/mods/spaces-plus"
else
  rm -rf "$HOME_DIR/mods/spaces-plus-new"
  if [ -f "$HOME_DIR/mods/spaces-plus/main.js" ]; then
    echo "warning: spaces-plus patch failed on this Herdr; keeping the previous spaces-plus" >&2
  else
    echo "warning: spaces-plus patch failed on this Herdr; using plain Spaces (no Open folder button, no groups)" >&2
    SPACES_MOD=spaces
  fi
fi

# 5. Layout: a fresh clone of shipped `main` with the Limits panel and the invisible config-sync block
# under Agents, spaces-plus for Spaces, and the invisible space-nav and space-guard blocks in the work
# column (outside the sidebar: a hidden mod gets no keys, so theirs work with the sidebar hidden too).
rm -f "$HOME_DIR/layouts/$LAYOUT.json"
herdr-app do layout.clone "{\"name\":\"main\",\"as\":\"$LAYOUT\"}" >/dev/null
f="$HOME_DIR/layouts/$LAYOUT.json"
wait_for "$f" || { echo "layout clone did not appear; is herdr-app open?" >&2; exit 1; }
jq --arg spaces "$SPACES_MOD" '
    {"id":"agent-limits","type":"block","content":{"mod":"agent-limits"},"size":{"px":130}} as $b
  | {"id":"space-guard","type":"block","content":{"mod":"space-guard"},"size":{"px":0}} as $g
  | {"id":"config-sync","type":"block","content":{"mod":"config-sync"},"size":{"px":0}} as $c
  | walk(if type == "object" and (.children | type) == "array"
         then .children |= [.[] | select(.id != "agent-limits" and .id != "space-guard" and .id != "config-sync")
                                | if .id == "agents" then ., $b, $c else . end]
         else . end)
  | walk(if type == "object" and .content?.mod? == "spaces" then .content.mod = $spaces else . end)
  | {"id":"space-nav","type":"block","content":{"mod":"space-nav"},"size":{"px":0}} as $n
  | walk(if type == "object" and .id? == "work" then .children |= ([.[] | select(.id != "space-nav" and .id != "space-guard")] + [$n, $g]) else . end)' "$f" >"$f.tmp"
mv "$f.tmp" "$f"
grep -q '"agent-limits"' "$f" || { echo "no \"agents\" block found in $LAYOUT; add the Limits block by hand" >&2; exit 1; }
grep -q '"space-guard"' "$f" && grep -q '"space-nav"' "$f" || { echo "no \"work\" column found in $LAYOUT; add the space-nav and space-guard blocks by hand" >&2; exit 1; }

# 6. Remember where this repo is and which "<Herdr version> <commit>" it applied (config-sync compares it),
# then switch last: switching reloads the mods, and config-sync must already see this version.
mkdir -p "$STATE"
printf '%s\n' "$REPO" >"$STATE/repo"
rev=$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo none)
printf '%s %s\n' "$(herdr-app --version | awk '{print $NF}')" "$rev" >"$STATE/applied"
herdr-app do layout.switch "{\"name\":\"$LAYOUT\"}" >/dev/null

echo "done: mods, keys (backup: $keys.bak), templates in $TEMPLATES, layout $LAYOUT, Herdr $(cat "$STATE/applied")"
