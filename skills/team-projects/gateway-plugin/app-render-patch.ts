/**
 * Patch for ui/src/ui/app-render.ts
 *
 * 1. Add these imports at the top:
 *
 *    import { uiPluginRegistry } from "./plugins/registry.ts";
 *    import { isPluginTab, getPluginViewInfo } from "./navigation.ts";
 *    import { renderTeamChatDrawer, renderTeamChatEdgeTab } from "./views/team-chat-drawer.ts";
 *
 * 2. Before </main>, add:
 *
 *    ${renderPluginTabContent(state)}
 *
 * 3. After </main> (outside the main content area), add:
 *
 *    ${renderTeamChatEdgeTab(state, state.client)}
 *    ${state.teamChatOpen ? renderTeamChatDrawer(state, state.client) : nothing}
 *
 * 4. Add the renderPluginTabContent() function:
 */

function renderPluginTabContent(state: AppViewState) {
  if (!isPluginTab(state.tab)) return nothing;
  const view = getPluginViewInfo(state.tab);
  if (!view) return nothing;

  // Check if a custom renderer is registered
  const renderer = uiPluginRegistry.getViewRenderer(state.tab);
  if (renderer) return renderer();

  // Default: show a placeholder with the plugin info
  return html`
    <div class="plugin-view" style="padding: 24px;">
      <div
        style="background: var(--bg-secondary, #1a1a2e); border: 1px solid var(--border, #333); border-radius: 12px; padding: 32px; text-align: center;"
      >
        <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
        <h2 style="margin: 0 0 8px 0; font-size: 20px;">${view.label}</h2>
        <p style="color: var(--text-muted, #888); margin: 0 0 24px 0;">${view.subtitle || ""}</p>
        <p style="color: var(--text-muted, #666); font-size: 13px;">
          Plugin view registered by <code>${view.pluginId || "unknown"}</code>
        </p>
      </div>
    </div>
  `;
}

/**
 * NOTE on team-chat-drawer styles:
 *
 * The OpenClaw app uses `createRenderRoot() { return this; }` (no Shadow DOM).
 * This means Lit `css` tagged templates are NOT applied — styles must be
 * embedded as inline `<style>` tags in the rendered HTML.
 *
 * The team-chat-drawer.ts file exports its styles via an inline `<style>` tag
 * included in the `renderTeamChatEdgeTab()` output (rendered even when the
 * drawer is closed, so styles are always present).
 */
