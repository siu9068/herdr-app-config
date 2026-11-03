# herdr-app-config

[Herdr](https://herdr.dev) 데스크톱 앱(`herdr-app`)에 추가한 mod와 단축키 모음입니다. herdr-app 0.1.12에서 만들고 확인했습니다.

## 기능

### Claude, Codex 사용량 패널

![Limits 패널](docs/limits.png)

사이드바 Agents 목록 바로 아래에 Limits 패널이 붙습니다. 에이전트마다 한 줄씩, 짧은 한도(5h)와 긴 한도(7d)를 막대와 퍼센트로 보여줍니다. 플랜에 5h 한도가 없으면 그 칸은 비어 있습니다.

- 70% 이상이면 주황, 90% 이상이면 빨강으로 바뀝니다.
- 줄에 마우스를 올리면 각 한도가 리셋되는 시각과 마지막 갱신 시각이 나옵니다.
- 로컬 기록은 30초마다, Anthropic과 OpenAI 서버는 5분마다 확인합니다. 오른쪽 위 새로고침 아이콘을 누르면 바로 다시 확인합니다.
- 지금 실행 중이 아닌 에이전트는 흐리게 보입니다.

### 새 worktree를 만들 때 에이전트 고르기

![New worktree 선택 창](docs/agent-worktree.png)

`cmd-shift-n`을 누르면 새 worktree에서 무엇을 띄울지 먼저 묻습니다. 고르고 나면 Herdr 기본 New worktree 다이얼로그가 열리고, 브랜치 이름을 입력하면 새 스페이스가 만들어지면서 고른 에이전트가 바로 실행됩니다. 스페이스 메뉴의 "New worktree"와 같은 다이얼로그이고, 지금 보고 있는 스페이스의 저장소를 기준으로 합니다.

### 화면을 나눌 때 에이전트 고르기

![Split 선택 창](docs/agent-split.png)

`cmd-d`(오른쪽), `cmd-shift-d`(아래)로 pane을 나눌 때도 같은 창이 뜹니다. 키를 누를 때 포커스가 있던 pane 옆에 새 pane이 열리고 고른 에이전트가 실행됩니다. 그냥 셸만 열려면 Shell을 고르면 됩니다.

| 키 | 동작 | 선택지 |
| --- | --- | --- |
| `cmd-shift-n` | 지금 스페이스의 저장소로 새 worktree 만들기 | Claude, Codex, Shell |
| `cmd-d` | 오른쪽으로 분할 | Claude, Codex, Shell |
| `cmd-shift-d` | 아래로 분할 | Claude, Codex, Shell |

선택지마다 실행하는 명령은 아래와 같습니다.

- Claude: `claude --dangerously-skip-permissions`
- Codex: `codex --no-daemon --yolo`. `--no-daemon`이 있어야 Codex 명령이 herdr 터미널 안에서 실행되고 `hc send` 같은 협업 명령이 동작합니다.
- Shell: 에이전트 없이 기본 셸

선택 창에서는 `1`~`3`을 누르거나 `↑↓`로 고른 뒤 `↵`를 누릅니다. 클릭해도 됩니다. `esc`를 누르면 닫힙니다. 마지막에 고른 항목은 키마다 따로 기억합니다.

## 설치

### 필요한 것

- macOS와 herdr-app. 설치 중에 herdr-app이 켜져 있어야 합니다.
- `git`, `jq`. 최근 macOS에는 `/usr/bin/jq`가 기본으로 들어 있습니다.
- 선택지로 쓸 `claude`, `codex` CLI. 사용량 패널에는 Claude Code나 Codex 로그인이 필요합니다.

### 설치 순서

1. herdr-app을 엽니다.
2. 터미널에서 저장소를 받고 설치 스크립트를 실행합니다.

   ```sh
   git clone https://github.com/siu9068/herdr-app-config.git ~/Projects/herdr-app-config
   sh ~/Projects/herdr-app-config/install.sh
   ```

3. 끝에 `done: mods, keys (...), layout main-limits`가 출력되면 설치된 것입니다. 사이드바 아래에 Limits 패널이 보이고 위 단축키가 바로 동작합니다.

### install.sh가 하는 일

1. `mods/` 아래 mod 네 개를 `~/.config/herdr-app/mods/`에 복사하고 각각 `herdr-app check`로 검사합니다. 같은 이름의 mod가 있으면 이 저장소 것으로 바꿉니다.
2. `keys.json`의 단축키 세 개를 `~/.config/herdr-app/keys.json`에 합칩니다. 원래 파일은 `keys.json.bak`으로 남습니다.
3. 설치된 버전의 기본 레이아웃 `main`을 `main-limits`로 복제하고, Agents 블록 바로 아래에 Limits 블록을 넣은 뒤 그 레이아웃으로 바꿉니다. 기본 레이아웃은 직접 고칠 수 없어서 복제본을 씁니다.

여러 번 실행해도 됩니다. 실행할 때마다 mod를 다시 복사하고 `main-limits`를 새로 만듭니다.

### 알아 둘 점

- `cmd-d`, `cmd-shift-d`의 기본 동작(바로 분할)을 선택 창으로 바꿉니다. 아무것도 띄우지 않고 분할하려면 선택 창에서 `3`(Shell)을 고르면 됩니다.
- `claude --dangerously-skip-permissions`와 `codex --no-daemon --yolo`는 권한 확인 없이 명령을 실행합니다.
- Limits 패널(`agent-limits`)은 macOS Keychain에서 Claude Code 로그인 토큰을 읽어 `https://api.anthropic.com/api/oauth/usage`에 보내고, `codex app-server`를 잠깐 실행해 Codex 사용량을 읽습니다. 캐시는 `~/.cache/agent-limits/`에 씁니다.
- 원래 레이아웃으로 돌아가려면 `cmd-shift-l`로 레이아웃을 바꾸면 됩니다. `main`은 그대로 남아 있습니다.

### 되돌리기

```sh
cd ~/.config/herdr-app
mv keys.json.bak keys.json
rm -rf mods/agent-limits mods/agent-worktree mods/agent-split-right mods/agent-split-down layouts/main-limits.json
```

`keys.json.bak`에는 마지막 설치 직전의 키 설정이 들어 있습니다.

## 파일

| 경로 | 내용 |
| --- | --- |
| `mods/agent-limits/` | Limits 패널. [mchlkim/herdr-agent-limits](https://github.com/mchlkim/herdr-agent-limits) `1ca10c7`의 사본이고 MIT 라이선스입니다. |
| `mods/agent-worktree/` | `cmd-shift-n`. 고른 에이전트를 실행할 명령으로 넘겨 기본 New worktree 다이얼로그를 엽니다. |
| `mods/agent-split-right/`, `mods/agent-split-down/` | `cmd-d`, `cmd-shift-d`. 포커스가 있는 pane을 나누고 고른 에이전트를 띄웁니다. |
| `keys.json` | 위 단축키 세 개. |
| `install.sh` | 설치 스크립트. |

## 선택지 바꾸기

선택지는 `picker.js` 맨 위 `CHOICES`에 있습니다. mod는 다른 폴더의 파일을 import할 수 없고 심볼릭 링크도 읽지 못해서, mod 세 개에 같은 `picker.js`가 하나씩 들어 있습니다. 한 곳을 고쳤으면 나머지 두 곳에 복사합니다.

```sh
cd ~/.config/herdr-app/mods
cp agent-worktree/picker.js agent-split-right/ && cp agent-worktree/picker.js agent-split-down/
```

## 지금 설정을 이 저장소에 반영하기

```sh
for m in agent-worktree agent-split-right agent-split-down; do
  cp ~/.config/herdr-app/mods/$m/{main.js,mod.json,picker.js} ~/Projects/herdr-app-config/mods/$m/
done
```

herdr-app이 mod 폴더마다 만드는 `gpui-kit.d.ts`, `jsconfig.json`은 `.gitignore`로 뺍니다.
