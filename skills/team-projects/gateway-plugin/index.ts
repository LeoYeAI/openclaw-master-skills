import type { OpenClawPluginApi } from "openclaw/plugin-sdk/team-projects";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/team-projects";

const plugin = {
  id: "team-projects",
  name: "Team Projects",
  description: "Multi-agent project management with task boards, @-mention routing, and orchestrated collaboration.",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    if (typeof api.registerView === "function") {
      api.registerView({
        id: "team-projects",
        label: "Projects",
        subtitle: "Multi-agent team projects",
        icon: "fileText",
        group: "control",
        position: 3,
      });
    }
  },
};

export default plugin;
