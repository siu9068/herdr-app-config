// Opened by a key (mod.open:worktree-key): asks which agent the new worktree starts with, then hands off
// to the shipped worktree dialog (the space menu's "New worktree"), passing that agent as its argv.

import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { focused, openOverlay, closeOverlay, props, theme } from "herdr";

const CHOICES = [
  { name: "Claude", argv: ["claude", "--dangerously-skip-permissions"] },
  { name: "Codex", argv: ["codex", "--yolo"] },
  { name: "Shell", argv: null },
];

function lastChoice() {
  try {
    const i = Number(localStorage.getItem("choice"));
    return i >= 0 && i < CHOICES.length ? i : 0;
  } catch { return 0; }
}

export default class WorktreeKey extends View {
  init(_props, cx) {
    this.space = focused()?.space;
    this.at = lastChoice();
    this.handle = cx.focus_handle();
    this.handle.focus();
    cx.timer.after(300, () => this.handle.focus());
  }

  pick(i) {
    try { localStorage.setItem("choice", String(i)); } catch {}
    const space = this.space;
    closeOverlay(props().overlay);
    const argv = CHOICES[i].argv;
    if (space) openOverlay({ mod: "worktree", kind: "dialog", width: 440, height: 260, props: { space, action: "new", ...(argv ? { argv } : {}) } });
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
      return h_flex().id(`wk-${i}`).h(34).px(10).gap(10).items_center().rounded(7).cursor_pointer()
        .when(on, (el) => el.bg(t.selected))
        .when(!on, (el) => el.hover((s) => s.bg(t.hover)))
        .on_click(() => this.pick(i))
        .child(div().w(12).text_size(11).text_color(t.dim).child(String(i + 1)))
        .child(div().w(52).text_color(t.foreground).child(c.name))
        .child(div().flex_1().min_w(0).truncate().text_size(11.5).text_color(t.dim).child(c.argv ? c.argv.join(" ") : "no agent"));
    };
    return v_flex().id("worktree-key").track_focus(this.handle).on_key_down((e, cx) => this.key(e, cx))
      .size_full().p(16).gap(8).bg(t.popover).text_size(13)
      .child(div().font_semibold().text_color(t.foreground).child("New worktree with"))
      .child(v_flex().gap(2).children(CHOICES.map(row)))
      .child(h_flex().justify_end().text_size(11).text_color(t.dim).child("1-3 or ↑↓ ↵ choose · esc close"));
  }
}
