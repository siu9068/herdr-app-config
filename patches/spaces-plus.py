"""Patches a spaces-plus clone: an "Open folder" button beside the + in the Spaces header, and a
group mode that puts this computer's spaces under folding groups you name and fill by dragging.

Usage: python3 spaces-plus.py <path to mods/spaces-plus/main.js>
The clone comes from `herdr-app do mod.clone '{"name":"spaces","as":"spaces-plus"}'`, so this patches
whatever the installed Herdr ships; it fails loudly if the code it anchors on has changed.
"""
import sys

path = sys.argv[1]
src = open(path).read()

HEADER_BUTTONS = '''        .child(h_flex().gap(2).items_center()
          // Group mode: this computer's spaces under folding groups of your own.
          .child(div().id("space-groups").size(26).flex_none().flex().items_center().justify_center().rounded(6)
            .when(this.groups.on, el => el.bg(t.selected).text_color(t.foreground))
            .hover(s => s.bg(t.hover).text_color(t.foreground))
            .tooltip(this.groups.on ? "Show spaces as one list" : "Group spaces")
            .on_click((_e, cx) => { this.groups.on = !this.groups.on; this.editing = undefined; this.saveGroups(); cx.notify(); })
            .child(svg("mods/workspace-chrome/layers.svg").size(14)))
          // Open folder: the macOS folder picker, then a new space there (this computer).
          .child(div().id("space-open-folder").size(26).flex_none().flex().items_center().justify_center().rounded(6).hover(s => s.bg(t.hover).text_color(t.foreground))
            .tooltip("Open folder as a space")
            .on_click((_e, cx) => cx.spawn(async () => {
              const folder = await pickFolder({ prompt: "Open" });
              if (folder) run("space.new", { folder, machine: "" });
            }))
            .child(svg("mods/workspace-chrome/folder.svg").size(14)))
'''

INIT = '''
    // Group mode: group names in order, which space is in which (by id), folded groups.
    this.groups = { on: false, list: [], of: {}, folded: [], ...JSON.parse(localStorage.getItem("groups") ?? "{}") };
    this.overGroup = undefined; // the group header a dragged space is over; null: Ungrouped
    this.editing = undefined; // the group whose name is being typed; null: a new one
    this.groupInput = InputState.new({ placeholder: "Group name" });
    this.groupInput.on("submit", (_e, cx) => this.nameGroup(cx));
    this.groupInput.on("blur", (_e, cx) => { this.editing = undefined; cx.notify(); });'''

METHODS = '''  // Keeps the groups, dropping closed spaces and removed groups.
  saveGroups() {
    const g = this.groups, ids = new Set(spaces().map((s) => s.id));
    g.of = Object.fromEntries(Object.entries(g.of).filter(([id, n]) => ids.has(id) && g.list.includes(n)));
    g.folded = g.folded.filter((n) => g.list.includes(n));
    localStorage.setItem("groups", JSON.stringify(g));
  }

  setGroup(id, name) {
    if (name) this.groups.of[id] = name;
    else delete this.groups.of[id];
    this.saveGroups();
  }

  editGroup(name, cx) {
    this.editing = name;
    this.groupInput.set_value(name ?? "");
    this.groupInput.focus();
    // The field only exists from the next frame on.
    cx.timer.after(50, () => this.groupInput.focus());
    cx.notify();
  }

  // Enter in the name field: a new group, a new name, or "" to remove the group (its spaces go to Ungrouped).
  nameGroup(cx) {
    const g = this.groups, old = this.editing, name = this.groupInput.value().trim();
    this.editing = undefined;
    if (old === null) {
      if (name && !g.list.includes(name)) g.list.push(name);
    } else if (!name) {
      g.list = g.list.filter((n) => n !== old);
    } else if (old !== undefined && name !== old && !g.list.includes(name)) {
      g.list = g.list.map((n) => (n === old ? name : n));
      for (const id in g.of) if (g.of[id] === old) g.of[id] = name;
      g.folded = g.folded.map((n) => (n === old ? name : n));
    }
    this.saveGroups();
    cx.notify();
  }

  // A space being dragged from this computer (only those go in groups).
  draggingLocal() {
    const s = this.pressed === null ? null : spaces().find((s) => s.id === this.pressed);
    return Boolean(s) && !s.machine;
  }

  // This computer's rows in group mode: each group under a folding header, then Ungrouped.
  // A worktree row stays under its checkout's row, in that one's group.
  byGroup(rows, t, collapsed, draw) {
    const g = this.groups;
    this.groupOf = null;
    if (!g.on || collapsed) return rows.map(draw);
    const blocks = [];
    for (const r of rows) r.tree && blocks.length ? blocks[blocks.length - 1].push(r) : blocks.push([r]);
    const of = (b) => (g.list.includes(g.of[b[0].w.id]) ? g.of[b[0].w.id] : null);
    this.groupOf = {};
    for (const b of blocks) for (const r of b) this.groupOf[r.w.id] = of(b);
    const out = [];
    for (const name of [...g.list, null]) {
      const mine = blocks.filter((b) => of(b) === name).flat();
      // Ungrouped gets a header once groups exist, and shows while dragging so a space can be taken out.
      if (name === null && g.list.length && (mine.length || this.draggingLocal())) out.push(this.groupHead(null, mine.length, t));
      if (name !== null) out.push(this.groupHead(name, mine.length, t));
      if (name === null || !g.folded.includes(name)) out.push(...mine.map(draw));
    }
    out.push(this.editing === null ? this.nameRow(t)
      : h_flex().id("group-new").h(26).flex_none().px(8).gap(7).items_center().rounded(7)
        .text_size(12).text_color(t.dim).hover((s) => s.bg(t.hover).text_color(t.foreground))
        .on_click((_e, cx) => this.editGroup(null, cx))
        .child(svg("mods/workspace-chrome/plus.svg").size(12)).child("New group"));
    return out;
  }

  nameRow(t) {
    return h_flex().id("group-name").h(28).flex_none().px(4).items_center()
      .on_key_down((e, cx) => {
        if (e.key !== "escape") return;
        this.editing = undefined;
        cx.stop_propagation();
        cx.notify();
      })
      .child(Input.new(this.groupInput).flex_1().h(24).px(6).rounded(6).border_1().border_color(t.accent)
        .bg(t.background).text_size(12).text_color(t.foreground));
  }

  // A group's header (null: Ungrouped): click folds, right-click renames, a dragged space dropped here joins it.
  groupHead(name, count, t) {
    if (name !== null && this.editing === name) return this.nameRow(t);
    const folded = name !== null && this.groups.folded.includes(name);
    const target = this.draggingLocal() && this.overGroup === name;
    return h_flex().id(`group-${name ?? "none"}`).h(24).mt(4).flex_none().px(8).gap(6).items_center().rounded(6)
      .text_size(11).text_color(t.dim)
      .when(target, (el) => el.bg(t.selected).text_color(t.foreground))
      .when(!target, (el) => el.hover((s) => s.bg(t.hover)))
      .on_mouse_move((_e, cx) => {
        if (!this.draggingLocal() || this.overGroup === name) return;
        this.overGroup = name;
        this.over = null;
        cx.notify();
      })
      .on_mouse_up("left", (_e, cx) => {
        if (this.draggingLocal() && this.overGroup === name) this.setGroup(this.pressed, name);
        this.pressed = null;
        this.over = null;
        this.overGroup = undefined;
        cx.notify();
      })
      .when(name !== null, (el) => el
        .tooltip("Right-click to rename. An empty name removes the group.")
        .on_click((_e, cx) => {
          const g = this.groups;
          g.folded = folded ? g.folded.filter((n) => n !== name) : [...g.folded, name];
          this.saveGroups();
          cx.notify();
        })
        .on_mouse_down("right", (_e, cx) => this.editGroup(name, cx))
        .child(svg(`mods/workspace-chrome/chevron-${folded ? "right" : "down"}.svg`).size(11).flex_none()))
      .child(div().flex_1().truncate().child(name ?? "Ungrouped"))
      .child(div().flex_none().child(String(count)));
  }

'''

EDITS = [
    # imports
    ('import { v_flex, h_flex } from "gpui-base";',
     'import { v_flex, h_flex, InputState, Input } from "gpui-base";'),
    ('import { spaces, machines, panes, run, openOverlay, exec, hc, theme, shared, setShared, watchFolder, window, layout } from "herdr";',
     'import { spaces, machines, panes, run, openOverlay, exec, hc, theme, shared, setShared, watchFolder, window, layout, pickFolder } from "herdr";'),
    # group state
    ('    this.folded = new Set(JSON.parse(localStorage.getItem("machines.folded") ?? "[]"));',
     '    this.folded = new Set(JSON.parse(localStorage.getItem("machines.folded") ?? "[]"));' + INIT),
    # this computer's rows go through byGroup, alone or under its machine header
    ('return loading(null) && !rows.length ? [loadingRow(null)] : rows.map(draw);',
     'return loading(null) && !rows.length ? [loadingRow(null)] : this.byGroup(rows, t, collapsed, draw);'),
    ('mine.length ? mine.map(draw) :',
     'mine.length ? (m ? mine.map(draw) : this.byGroup(mine, t, collapsed, draw)) :'),
    # dragging over a row leaves any group header
    ('        if (this.pressed !== null && this.over !== over) {',
     '        if (this.pressed !== null && this.overGroup !== undefined) { this.overGroup = undefined; cx.notify(); }\n'
     '        if (this.pressed !== null && this.over !== over) {'),
    # dropped on a space in another group: it joins that group too (pressed/over hold space ids)
    ('        if (from !== null && over === w.id && from !== w.id) {',
     '        if (from !== null && over === w.id && from !== w.id && this.groupOf && w.id in this.groupOf) this.setGroup(from, this.groupOf[w.id]);\n'
     '        if (from !== null && over === w.id && from !== w.id) {'),
    ('.on_mouse_up("left", (_e, cx) => { this.pressed = null; cx.notify(); })',
     '.on_mouse_up("left", (_e, cx) => { this.pressed = null; this.overGroup = undefined; cx.notify(); })'),
    ('  compact({ w, i }, t) {', METHODS + '  compact({ w, i }, t) {'),
    # header buttons: groups and open folder, beside the +
    ('        .child(div().id("space-new").size(26)',
     HEADER_BUTTONS + '          .child(div().id("space-new").size(26)'),
    ('          .on_click(() => run("space.new")).child(svg("mods/workspace-chrome/plus.svg").size(14))))',
     '          .on_click(() => run("space.new")).child(svg("mods/workspace-chrome/plus.svg").size(14)))))'),
]

if "space-groups" in src:
    sys.exit(0)  # already patched
for anchor, _ in EDITS:
    if src.count(anchor) != 1:
        sys.exit(f"spaces-plus patch: anchor not found once, Herdr's spaces mod changed: {anchor[:60]}")
for anchor, new in EDITS:
    src = src.replace(anchor, new, 1)
open(path, "w").write(src)
