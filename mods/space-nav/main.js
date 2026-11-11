// Invisible layout block outside the sidebar, so its keys work with the sidebar hidden too.
// "space-nav.next" / "space-nav.prev": like space.next/prev (sidebar order, wrapping around), skipping
// spaces in folded groups and under folded machines. spaces-plus shares those ids as "spaces-plus.folded".

import { View, div } from "gpui-kit";
import { spaces, run, shared, nextCommand } from "herdr";

function step(by) {
  const folded = new Set(shared("spaces-plus.folded") ?? []);
  // The current space stays in the list even when folded away, so stepping starts from it.
  const list = spaces().filter((s) => s.active || !folded.has(s.id));
  if (!list.length) return;
  const at = list.findIndex((s) => s.active);
  const next = list[((at === -1 ? (by > 0 ? -1 : 0) : at) + by + list.length) % list.length];
  if (!next.active) run("space.select", { id: next.id });
}

export default class SpaceNav extends View {
  init(_props, cx) {
    cx.spawn(async () => {
      for (;;) {
        const c = await nextCommand();
        if (c === "next" || c === "prev") step(c === "next" ? 1 : -1);
      }
    });
  }

  render() {
    return div();
  }
}
