# Changelog

## v1.2.0 (2026-02-23)

### Improved

- **Privacy & data scope**: Expanded privacy section to clearly describe what data is and is not sent to the Navifare MCP server. Only pre-booking itinerary details (flights, times, prices) are transmitted — no PII, no booking confirmations, no passenger names or payment info. Added links to [navifare.com](https://navifare.com) and [Terms of Service](https://navifare.com/terms).
- **Screenshot PII protection**: Skill instructions now explicitly direct agents to extract only itinerary data from screenshots and exclude any personal information before sending to the MCP server.

## v1.1.1 (2026-02-23)

### Fixed

- **Tool name consistency**: All documentation now correctly references `flight_pricecheck` and `format_flight_pricecheck_request`. Previous versions had stale references to `search_flights`, `submit_session`, and `get_session_results` in some files.
- **Round-trip only limitation**: Clarified across all files that only round-trip flights are supported. The README previously claimed one-way support, which was incorrect.
- **Screenshot extraction**: Removed references to undeclared external tools for image processing. Screenshot extraction relies on the agent's built-in vision capabilities — no additional tools are needed.
- **Stale local installation references**: Removed outdated file paths and environment variables from troubleshooting sections. The MCP server is a hosted service at `https://mcp.navifare.com/mcp`.

### Changed

- Documentation is now client-agnostic. Previously tied to Claude Code, it now works with any MCP-enabled client.

## v1.0.1 (2026-02-12)

### Fixed

- MCP response format updated to comply with the official MCP specification.
- Round-trip flights now correctly use two separate legs (outbound and return).
- Location parameter uses 2-letter ISO country codes.
- Travel class enum values match the API exactly.

## v1.0.0 (2025-02-11)

### Added

- Initial release.
- Price comparison across 10+ booking sites via Navifare MCP.
- Two-step workflow: format request, then search.
- IATA reference data for airports and airlines.
- Usage examples for common scenarios.
