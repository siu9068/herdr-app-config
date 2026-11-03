"""Adds an "Open folder" button beside the + in the Spaces header of a spaces-plus clone.

Usage: python3 spaces-plus.py <path to mods/spaces-plus/main.js>
The clone comes from `herdr-app do mod.clone '{"name":"spaces","as":"spaces-plus"}'`, so this patches
whatever the installed Herdr ships; it fails loudly if the code it anchors on has changed.
"""
import sys

path = sys.argv[1]
src = open(path).read()

IMPORT = 'import { spaces, machines, panes, run, openOverlay, exec, hc, theme, shared, setShared, watchFolder, window, layout } from "herdr";'
PLUS = '        .child(div().id("space-new").size(26)'
BUTTON = '''        .child(h_flex().gap(2).items_center()
          // Open folder: the macOS folder picker, then a new space there (this computer).
          .child(div().id("space-open-folder").size(26).flex_none().flex().items_center().justify_center().rounded(6).hover(s => s.bg(t.hover).text_color(t.foreground))
            .tooltip("Open folder as a space")
            .on_click((_e, cx) => cx.spawn(async () => {
              const folder = await pickFolder({ prompt: "Open" });
              if (folder) run("space.new", { folder, machine: "" });
            }))
            .child(svg("mods/workspace-chrome/folder.svg").size(14)))
'''
CLOSE_OLD = '          .on_click(() => run("space.new")).child(svg("mods/workspace-chrome/plus.svg").size(14))))'
CLOSE_NEW = '          .on_click(() => run("space.new")).child(svg("mods/workspace-chrome/plus.svg").size(14)))))'

if "space-open-folder" in src:
    sys.exit(0)  # already patched
for anchor in (IMPORT, PLUS, CLOSE_OLD):
    if src.count(anchor) != 1:
        sys.exit(f"spaces-plus patch: anchor not found once, Herdr's spaces mod changed: {anchor[:60]}")

src = src.replace(IMPORT, IMPORT.replace("layout }", "layout, pickFolder }"))
src = src.replace(PLUS, BUTTON + "  " + PLUS.replace("        .child(div()", "        .child(div()", 1), 1)
src = src.replace(CLOSE_OLD, CLOSE_NEW, 1)
open(path, "w").write(src)
