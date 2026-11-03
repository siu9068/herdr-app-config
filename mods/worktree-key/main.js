// Opened by a key (mod.open:worktree-key): hands off to the shipped worktree dialog for the focused space,
// the same dialog the space menu's "New worktree" opens.
import { View, div } from "gpui-kit";
import { focused, openOverlay, closeOverlay, props } from "herdr";

export default class WorktreeKey extends View {
  init(_props, cx) {
    const space = focused()?.space;
    if (props()?.overlay) closeOverlay(props().overlay);
    if (space) openOverlay({ mod: "worktree", kind: "dialog", width: 440, height: 260, props: { space, action: "new" } });
  }
  render() {
    return div();
  }
}
