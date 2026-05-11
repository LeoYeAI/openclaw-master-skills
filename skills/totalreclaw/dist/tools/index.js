"use strict";
/**
 * TotalReclaw Skill - Tools Barrel Export
 *
 * This module exports all tool implementations for the TotalReclaw skill.
 * Each tool provides a specific capability for interacting with memories.
 *
 * ## Available Tools
 *
 * - **remember** - Store a new memory
 * - **recall** - Search and retrieve memories
 * - **forget** - Delete a specific memory
 * - **export** - Export all memories for portability
 *
 * ## Usage
 *
 * ```typescript
 * import {
 *   rememberTool,
 *   recallTool,
 *   forgetTool,
 *   exportTool,
 *   createRememberTool,
 *   createRecallTool,
 *   createForgetTool,
 *   createExportTool,
 * } from './tools';
 *
 * // Direct usage
 * const result = await rememberTool(client, { text: 'Important fact' });
 *
 * // Factory usage (pre-bound to client)
 * const remember = createRememberTool(client);
 * const result = await remember({ text: 'Important fact' });
 * ```
 *
 * ## Tool Results
 *
 * All tools return a result object with:
 * - `success: boolean` - Whether the operation succeeded
 * - `error?: string` - Error message if failed
 * - Tool-specific fields (e.g., `factId`, `results`, `data`)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createStatusTool = exports.statusTool = exports.restoreBuffers = exports.createExportTool = exports.exportTool = exports.createForgetTool = exports.forgetTool = exports.formatRecallResults = exports.createRecallTool = exports.recallTool = exports.createRememberTool = exports.rememberTool = void 0;
// ============================================================================
// Remember Tool
// ============================================================================
var remember_1 = require("./remember");
Object.defineProperty(exports, "rememberTool", { enumerable: true, get: function () { return remember_1.rememberTool; } });
Object.defineProperty(exports, "createRememberTool", { enumerable: true, get: function () { return remember_1.createRememberTool; } });
// ============================================================================
// Recall Tool
// ============================================================================
var recall_1 = require("./recall");
Object.defineProperty(exports, "recallTool", { enumerable: true, get: function () { return recall_1.recallTool; } });
Object.defineProperty(exports, "createRecallTool", { enumerable: true, get: function () { return recall_1.createRecallTool; } });
Object.defineProperty(exports, "formatRecallResults", { enumerable: true, get: function () { return recall_1.formatRecallResults; } });
// ============================================================================
// Forget Tool
// ============================================================================
var forget_1 = require("./forget");
Object.defineProperty(exports, "forgetTool", { enumerable: true, get: function () { return forget_1.forgetTool; } });
Object.defineProperty(exports, "createForgetTool", { enumerable: true, get: function () { return forget_1.createForgetTool; } });
// ============================================================================
// Export Tool
// ============================================================================
var export_1 = require("./export");
Object.defineProperty(exports, "exportTool", { enumerable: true, get: function () { return export_1.exportTool; } });
Object.defineProperty(exports, "createExportTool", { enumerable: true, get: function () { return export_1.createExportTool; } });
Object.defineProperty(exports, "restoreBuffers", { enumerable: true, get: function () { return export_1.restoreBuffers; } });
// ============================================================================
// Status Tool
// ============================================================================
var status_1 = require("./status");
Object.defineProperty(exports, "statusTool", { enumerable: true, get: function () { return status_1.statusTool; } });
Object.defineProperty(exports, "createStatusTool", { enumerable: true, get: function () { return status_1.createStatusTool; } });
//# sourceMappingURL=index.js.map