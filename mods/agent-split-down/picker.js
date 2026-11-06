// Shared by agent-worktree, agent-split-right and agent-split-down (mods can't import across folders,
// so each folder carries an identical copy). Asks which agent to start, then makes the worktree or split.

import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { focused, openOverlay, closeOverlay, props, theme, run } from "herdr";

const CHOICES = [
  { name: "Claude", argv: ["claude", "--dangerously-skip-permissions"] },
  { name: "Codex", argv: ["codex", "--no-daemon", "--yolo"] },
  { name: "Shell", argv: null },
];

// Herdr execs argv with its own PATH, which misses tools set up in the shell rc (nvm, mise...).
// Run the agent through the user's login + interactive shell so it is found wherever it is installed.
const viaShell = (argv) => ["/bin/sh", "-c", 'exec "${SHELL:-/bin/sh}" -lic "$0"', "exec " + argv.join(" ")];

const TITLE = { worktree: "New worktree with", right: "Split right with", down: "Split down with" };

function lastChoice() {
  try {
    const i = Number(localStorage.getItem("choice"));
    return i >= 0 && i < CHOICES.length ? i : 0;
  } catch { return 0; }
}

// action: "worktree" opens the shipped worktree dialog; "right" / "down" split the focused pane.
export default function picker(action) {
  return class AgentPicker extends View {
    init(_props, cx) {
      // Read before the dialog takes focus: the space and pane the key was pressed in.
      const f = focused();
      this.space = f?.space;
      this.pane = f?.pane;
      this.at = lastChoice();
      this.handle = cx.focus_handle();
      this.handle.focus();
      cx.timer.after(300, () => this.handle.focus());
    }

    pick(i) {
      try { localStorage.setItem("choice", String(i)); } catch {}
      closeOverlay(props().overlay);
      const argv = CHOICES[i].argv && viaShell(CHOICES[i].argv);
      if (action === "worktree") {
        if (this.space) openOverlay({ mod: "worktree", kind: "dialog", width: 440, height: 260, props: { space: this.space, action: "new", ...(argv ? { argv } : {}) } });
      } else {
        run("pane.split", { direction: action, ...(this.pane ? { pane: this.pane } : {}), ...(argv ? { argv } : {}) });
      }
    }

    key(e, cx) {
      const n = CHOICES.length;
      const digit = Number(e.key);
      if (digit >= 1 && digit <= n) return this.pick(digit - 1);
      if (e.key === "enter") return this.pick(this.at);
      if (e.key === "down" || e.key === "up") this.at = (this.at + (e.key === "down" ? 1 : n - 1)) % n;
      else return;
      cx.stop_propagation();
      cx.notify();
    }

    render() {
      const t = theme();
      const row = (c, i) => {
        const on = i === this.at;
        return h_flex().id(`ap-${i}`).h(34).px(10).gap(10).items_center().rounded(7).cursor_pointer()
          .when(on, (el) => el.bg(t.selected))
          .when(!on, (el) => el.hover((s) => s.bg(t.hover)))
          .on_click(() => this.pick(i))
          .child(div().w(12).text_size(11).text_color(t.dim).child(String(i + 1)))
          .child(div().w(52).text_color(t.foreground).child(c.name))
          .child(div().flex_1().min_w(0).truncate().text_size(11.5).text_color(t.dim).child(c.argv ? c.argv.join(" ") : "no agent"));
      };
      return v_flex().id("agent-picker").track_focus(this.handle).on_key_down((e, cx) => this.key(e, cx))
        .size_full().p(16).gap(8).bg(t.popover).text_size(13)
        .child(div().font_semibold().text_color(t.foreground).child(TITLE[action]))
        .child(v_flex().gap(2).children(CHOICES.map(row)))
        .child(h_flex().justify_end().text_size(11).text_color(t.dim).child("1-3 or ↑↓ ↵ choose · esc close"));
    }
  };
}
