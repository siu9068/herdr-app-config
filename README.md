# herdr-app-config

My herdr-app (Herdr desktop app) additions.

| Path | What |
| --- | --- |
| `mods/agent-limits/` | Claude and Codex 5h/7d usage under the Agents list. Copy of [mchlkim/herdr-agent-limits](https://github.com/mchlkim/herdr-agent-limits) at `1ca10c7`, MIT. Reads the Claude Code Keychain token and calls `api.anthropic.com/api/oauth/usage`; runs `codex app-server`. |
| `mods/agent-worktree/`, `mods/agent-split-right/`, `mods/agent-split-down/` | Ask Claude (`claude --dangerously-skip-permissions`), Codex (`codex --yolo`) or Shell, then open the shipped New worktree dialog with that agent, or split the focused pane right or down with it. Each remembers its last choice. `picker.js` is the same file in all three (mods can't import across folders or through symlinks); edit one, copy it to the others. |
| `keys.json` | `cmd-shift-n` worktree, `cmd-d` split right, `cmd-shift-d` split down, each through the agent picker. Merged into the existing `keys.json`. |
| `install.sh` | Copies the mods, merges the keys, clones `main` as `main-limits` with the Limits block, switches to it. |

## Restore on a new machine

```sh
gh repo clone siu9068/herdr-app-config ~/Projects/herdr-app-config
# open herdr-app first
sh ~/Projects/herdr-app-config/install.sh
```

`ctrl-shift-l` switches layouts; `main` is still there.

## Update this repo from the live setup

```sh
for m in agent-worktree agent-split-right agent-split-down; do cp ~/.config/herdr-app/mods/$m/{main.js,mod.json,picker.js} ~/Projects/herdr-app-config/mods/$m/; done
```
