# herdr-app-config

My herdr-app (Herdr desktop app) additions.

| Path | What |
| --- | --- |
| `mods/agent-limits/` | Claude and Codex 5h/7d usage under the Agents list. Copy of [mchlkim/herdr-agent-limits](https://github.com/mchlkim/herdr-agent-limits) at `1ca10c7`, MIT. Reads the Claude Code Keychain token and calls `api.anthropic.com/api/oauth/usage`; runs `codex app-server`. |
| `mods/worktree-key/` | Asks Claude (`claude --dangerously-skip-permissions`), Codex (`codex --yolo`) or Shell, then opens the shipped New worktree dialog for the focused space with that agent. Remembers the last choice. |
| `keys.json` | `cmd-shift-n`: New worktree. Merged into the existing `keys.json`. |
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
cp -R ~/.config/herdr-app/mods/worktree-key ~/Projects/herdr-app-config/mods/
```
