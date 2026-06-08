/**
 * Patch for ui/src/ui/app-gateway.ts
 *
 * 1. Add these imports:
 *
 *    import { uiPluginRegistry } from "./plugins/registry.ts";
 *    import { renderTeamProjects } from "./views/team-projects.ts";
 *
 * 2. In `onHello`, after `applySnapshot(host, hello)`, add:
 *
 *    registerTeamProjectsPlugin(host as unknown as OpenClawApp);
 *
 * 3. Add this function at the end of the file:
 */

/** Register the team-projects plugin view and renderer (client-side). */
function registerTeamProjectsPlugin(host: OpenClawApp): void {
  // Register the team-projects view if not already present
  if (!uiPluginRegistry.hasView("team-projects")) {
    uiPluginRegistry.registerView({
      id: "team-projects",
      label: "Projects",
      subtitle: "Multi-agent team projects",
      icon: "fileText",
      group: "control",
      position: 3,
      pluginId: "team-projects",
    });
  }
  // Always (re-)register the renderer so it captures the latest host reference
  uiPluginRegistry.registerViewRenderer("team-projects", () =>
    renderTeamProjects({ client: host.client, connected: host.connected }),
  );
}
