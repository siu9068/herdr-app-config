// Watches spaces from an invisible layout block. When one disappears (its last shell ran `exit`,
// or it was closed), posts a toast that reopens it with the same name and folder on click, and
// keeps it for "space-guard.reopen" (a key). Only the space comes back: its tabs, splits and agents do not.

import { View, div } from "gpui-kit";
import { spaces, panes, machines, notify, run, nextCommand } from "herdr";

const KEEP = 10;

// Machines whose spaces we can see right now (null: this computer).
const ready = () => new Set(machines().filter((m) => m.layout === "ready").map((m) => m.name));

// What it takes to open the space again: its name if someone named it, where its first terminal is now.
function snapshot() {
  const where = new Map();
  for (const p of panes()) if (p.terminal && p.cwd && !where.has(p.tab)) where.set(p.tab, p.cwd);
  const out = new Map();
  for (const s of spaces()) {
    const cwd = s.tabs.map((t) => where.get(t.id)).find(Boolean);
    out.set(s.id, { name: s.name, named: s.named, folder: cwd || s.folder || null, machine: s.machine ?? null });
  }
  return out;
}

function reopenArgs(s) {
  return { ...(s.named ? { name: s.name } : {}), ...(s.folder ? { folder: s.folder } : {}), machine: s.machine ?? "" };
}

export default class SpaceGuard extends View {
  init(_props, cx) {
    this.known = snapshot();
    this.closed = [];
    cx.timer.every(1000, () => this.check());
    cx.spawn(async () => {
      for (;;) {
        const c = await nextCommand();
        if (c === "reopen") this.reopen();
      }
    });
  }

  check() {
    const now = snapshot();
    const up = ready();
    for (const [id, s] of this.known) {
      // A machine going offline hides its spaces; that is not a close.
      if (now.has(id) || !up.has(s.machine)) continue;
      this.closed.unshift(s);
      this.closed.length = Math.min(this.closed.length, KEEP);
      notify({
        title: `Space "${s.name}" closed`,
        body: "Click to open it again (cmd-shift-t)",
        level: "info",
        action: { name: "space.new", args: reopenArgs(s) },
      });
    }
    // Keep the last known folder of spaces we can't see right now.
    for (const [id, s] of this.known) if (!now.has(id) && !up.has(s.machine)) now.set(id, s);
    this.known = now;
  }

  reopen() {
    const s = this.closed.shift();
    if (s) run("space.new", reopenArgs(s));
    else notify({ title: "No closed space to reopen", level: "info" });
  }

  render() {
    return div();
  }
}
