#!/usr/bin/env python3
# Optional, on top of spaces-plus.py: the Spaces sidebar scrolls to keep the current space in view
# when it changes (cmd-alt-]/[, ctrl-1..9, a click elsewhere). Turned off with SPACES_SCROLL=off in install.sh.
# Needs ScrollHandle for normal scroll areas (Herdr 0.1.15); on an older Herdr this leaves main.js as it is.
import os
import re
import sys

path = sys.argv[1]
src = open(path).read()
# The app's own copy (in the herdr-app home, two folders up): the clone writes its copy after main.js.
here = os.path.dirname(os.path.abspath(path))
types = [p for p in (os.path.join(here, "..", "..", "gpui-kit.d.ts"), os.path.join(here, "gpui-kit.d.ts")) if os.path.exists(p)]
if not any(re.search(r"\bScrollHandle\b", open(p).read()) for p in types):
    print("spaces-plus scroll: this Herdr has no ScrollHandle (0.1.15+), skipped", file=sys.stderr)
    sys.exit(0)
if "followActive" in src:
    sys.exit(0)  # already patched

METHOD = '''
  // Scrolls the list to the current space once each time it changes, so a manual scroll stays put.
  // Not before its row is drawn (still loading, or in a folded group or machine).
  followActive(items) {
    const at = items.indexOf(this.activeRow);
    const id = spaces().find((s) => s.active)?.id;
    if (at >= 0 && id !== this.followed) {
      this.followed = id;
      this.scroll.scroll_to_item(at);
    }
    return items;
  }

'''

EDITS = [
    ('import { v_flex, h_flex, InputState, Input } from "gpui-base";',
     'import { v_flex, h_flex, InputState, Input, ScrollHandle } from "gpui-base";'),
    ('    this.folded = new Set(JSON.parse(localStorage.getItem("machines.folded") ?? "[]"));',
     '    this.folded = new Set(JSON.parse(localStorage.getItem("machines.folded") ?? "[]"));\n'
     '    this.scroll = ScrollHandle.new();'),
    ('    const draw = (r) => (collapsed ? this.compact(r, t) : this.row(r, t));',
     '    this.activeRow = null;\n'
     '    const draw = (r) => {\n'
     '      const el = collapsed ? this.compact(r, t) : this.row(r, t);\n'
     '      if (r.w.active) this.activeRow = el;\n'
     '      return el;\n'
     '    };'),
    ('.overflow_y_scrollbar().mode("always")',
     '.overflow_y_scrollbar().mode("always").track_scroll(this.scroll)'),
    ('        .children(this.grouped(t, collapsed)));',
     '        .children(this.followActive(this.grouped(t, collapsed))));'),
    ('  compact({ w, i }, t) {', METHOD.lstrip("\n") + '  compact({ w, i }, t) {'),
]

for anchor, _ in EDITS:
    if src.count(anchor) != 1:
        sys.exit(f"spaces-plus scroll patch: anchor not found once: {anchor[:60]}")
for anchor, new in EDITS:
    src = src.replace(anchor, new, 1)
open(path, "w").write(src)
