// Invisible layout block. After a Herdr update, runs this repo's install.sh again (once per version),
// so main-limits and spaces-plus are rebuilt from the new shipped layout and Spaces mod.
// install.sh records the repo path and the Herdr version it was applied to in ~/.local/state/herdr-app-config.

import { View, div } from "gpui-kit";
import { exec, hc, home, readTextFile, writeTextFile, notify } from "herdr";

const JOB = "herdr-config-sync";
const state = () => `${home()}/.local/state/herdr-app-config`;
const read = async (name) => (await readTextFile(`${state()}/${name}`))?.trim() || null;

async function running() {
  const r = await hc(["get", JOB, "--json"]);
  if (r.code !== 0) return false;
  try { return JSON.parse(r.stdout).state === "live"; } catch { return false; }
}

export default class ConfigSync extends View {
  init(_props, cx) {
    this.watching = false; // a run this copy started or found, to report when it ends
    this.busy = false;
    cx.spawn(async () => this.check());
    cx.timer.every(3000, () => { if (this.watching && !this.busy) cx.spawn(async () => this.check()); });
  }

  async check() {
    this.busy = true;
    try {
      const repo = await read("repo");
      if (!repo) return; // install.sh never ran here
      const version = (await exec("herdr-app", ["--version"])).stdout.trim().split(/\s+/).pop();
      if (await running()) { this.watching = true; return; }
      const applied = await read("applied");
      const attempted = await read("attempted");
      if (applied === version) {
        // Announce an automatic run once, even if this copy was reloaded while it ran.
        const announced = await read("announced");
        if (attempted === version && announced !== version) {
          await writeTextFile(`${state()}/announced`, `${version}\n`, announced === null ? null : `${announced}\n`).catch(() => {});
          const warning = (await readTextFile(`${state()}/sync.log`))?.split("\n").find((l) => l.startsWith("warning:"));
          notify(warning
            ? { title: `Config re-applied with a warning (Herdr ${version})`, body: warning.slice(9).trim(), level: "warning" }
            : { title: `Config re-applied (Herdr ${version})`, level: "success" });
        }
        this.watching = false;
        return;
      }
      if (attempted === version) {
        // Tried for this version and it didn't finish: say so once per start, don't loop.
        if (this.watching || !this.reported) notify({ title: `Config re-apply failed (Herdr ${version})`, body: "Log: ~/.local/state/herdr-app-config/sync.log", level: "error" });
        this.reported = true;
        this.watching = false;
        return;
      }
      notify({ title: `Herdr ${version}: re-applying config`, body: "Rebuilding layout and Spaces", level: "info" });
      const r = await hc(["run", "--bg", "--no-parent", "--rm", "--no-notify", "--name", JOB, "--cwd", repo, "--",
        "sh", "-c", 'printf "%s\\n" "$1" >"$2/attempted" && sh ./install.sh >"$2/sync.log" 2>&1', "_", version, state()]);
      if (r.code !== 0) notify({ title: "herdr-app-config sync could not start", body: r.stderr.trim(), level: "error" });
      else this.watching = true;
    } catch (e) {
      notify({ title: "herdr-app-config sync failed", body: String(e?.message ?? e), level: "error" });
      this.watching = false;
    } finally {
      this.busy = false;
    }
  }

  render() {
    return div();
  }
}
