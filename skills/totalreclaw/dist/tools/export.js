"use strict";
/**
 * TotalReclaw Skill - Export Tool
 *
 * Tool for exporting memories from TotalReclaw.
 * This is the totalreclaw_export tool implementation.
 *
 * Supports two formats:
 * - JSON: Structured data format for programmatic use
 * - Markdown: Human-readable format for documentation
 *
 * @example
 * ```typescript
 * // Export as JSON
 * const jsonResult = await exportTool(client, { format: 'json' });
 *
 * // Export as Markdown
 * const mdResult = await exportTool(client, { format: 'markdown' });
 * ```
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.exportTool = exportTool;
exports.createExportTool = createExportTool;
exports.restoreBuffers = restoreBuffers;
const client_1 = require("@totalreclaw/client");
/**
 * Default export format
 */
const DEFAULT_FORMAT = 'json';
/**
 * Export all memories from TotalReclaw
 *
 * @param client - The TotalReclaw client instance
 * @param params - Tool parameters (format?)
 * @returns Result containing success status and exported data
 *
 * @throws {TotalReclawError} If the client is not initialized or operation fails
 *
 * @example
 * ```typescript
 * // Export as JSON (default)
 * const result = await exportTool(client, {});
 *
 * // Export as Markdown
 * const result = await exportTool(client, { format: 'markdown' });
 *
 * if (result.success) {
 *   console.log(`Exported ${result.count} memories`);
 *   fs.writeFileSync('export.md', result.data);
 * }
 * ```
 */
async function exportTool(client, params = {}) {
    // Validate and normalize format
    const format = params.format ?? DEFAULT_FORMAT;
    const validFormats = ['json', 'markdown'];
    if (!validFormats.includes(format)) {
        return {
            success: false,
            error: `Invalid format: must be one of ${validFormats.join(', ')}`,
        };
    }
    try {
        // Export data from client
        const exportedData = await client.export();
        // Format based on requested format
        let formattedData;
        let count;
        if (format === 'markdown') {
            formattedData = formatAsMarkdown(exportedData);
            count = exportedData.facts.length;
        }
        else {
            formattedData = JSON.stringify(exportedData, jsonReplacer, 2);
            count = exportedData.facts.length;
        }
        return {
            success: true,
            data: formattedData,
            format,
            count,
        };
    }
    catch (error) {
        // Handle known error types
        if (error instanceof client_1.TotalReclawError) {
            // Map specific error codes to user-friendly messages
            switch (error.code) {
                case client_1.TotalReclawErrorCode.NOT_REGISTERED:
                    return {
                        success: false,
                        error: 'Client not authenticated. Please initialize the client first.',
                    };
                case client_1.TotalReclawErrorCode.NETWORK_ERROR:
                    return {
                        success: false,
                        error: 'Network error. Please check your connection and try again.',
                    };
                default:
                    return {
                        success: false,
                        error: `TotalReclaw error (${error.code}): ${error.message}`,
                    };
            }
        }
        // Handle unknown errors
        const message = error instanceof Error ? error.message : 'Unknown error occurred';
        return {
            success: false,
            error: `Failed to export memories: ${message}`,
        };
    }
}
/**
 * JSON replacer function for handling Buffer and Date serialization
 */
function jsonReplacer(_key, value) {
    // Handle Buffer serialization
    if (Buffer.isBuffer(value)) {
        return {
            __type: 'Buffer',
            data: value.toString('base64'),
        };
    }
    // Handle Date serialization (ensure ISO format)
    if (value instanceof Date) {
        return {
            __type: 'Date',
            iso: value.toISOString(),
        };
    }
    return value;
}
/**
 * Shorten a fact ID for human-readable display
 *
 * @param id - The full fact ID
 * @returns Shortened ID (first 8 characters)
 */
function shortenId(id) {
    // Take first 8 characters for a readable short ID
    return id.length > 8 ? id.substring(0, 8) + '...' : id;
}
/**
 * Format exported data as Markdown
 *
 * This format is designed for human readability. Technical configuration
 * details (LSH params, key params) are only included in JSON export for
 * programmatic re-import.
 *
 * @param data - The exported data
 * @returns Formatted markdown string
 */
function formatAsMarkdown(data) {
    const lines = [
        '# TotalReclaw Export',
        '',
        `**Exported at:** ${data.exportedAt.toISOString()}`,
        `**Total memories:** ${data.facts.length}`,
        '',
        '---',
        '',
    ];
    if (data.facts.length === 0) {
        lines.push('_No memories stored yet._');
        lines.push('');
        lines.push('> **Note:** Use `format: "json"` for full export including configuration for re-import.');
    }
    else {
        lines.push('## Memories');
        lines.push('');
        for (let i = 0; i < data.facts.length; i++) {
            const fact = data.facts[i];
            const importance = Math.round((fact.decayScore ?? 0.5) * 10);
            const createdDate = new Date(fact.timestamp).toISOString().split('T')[0];
            const encryptedPreview = fact.encryptedDoc.toString('base64').substring(0, 60);
            lines.push(`### ${i + 1}. \`${shortenId(fact.id)}\``);
            lines.push('');
            lines.push(`| Field | Value |`);
            lines.push(`|-------|-------|`);
            lines.push(`| Created | ${createdDate} |`);
            lines.push(`| Importance | ${importance}/10 |`);
            lines.push(`| Encrypted | \`${encryptedPreview}...\` |`);
            lines.push('');
        }
    }
    lines.push('---');
    lines.push('');
    lines.push('_Generated by TotalReclaw Skill_');
    lines.push('');
    lines.push('> **Tip:** For programmatic re-import, use `format: "json"` which includes LSH configuration and key parameters.');
    return lines.join('\n');
}
/**
 * Create a bound export tool function
 *
 * Useful for creating a tool that's pre-bound to a client instance.
 *
 * @param client - The TotalReclaw client instance
 * @returns A function that accepts ExportToolParams and returns ExportToolResult
 */
function createExportTool(client) {
    return (params) => exportTool(client, params);
}
/**
 * Restore a Buffer from JSON-serialized format
 *
 * Useful for parsing exported JSON data.
 *
 * @param obj - Object that may contain serialized Buffers
 * @returns Object with restored Buffers
 */
function restoreBuffers(obj) {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    if (Array.isArray(obj)) {
        return obj.map(restoreBuffers);
    }
    const record = obj;
    // Restore Buffer
    if (record.__type === 'Buffer' && typeof record.data === 'string') {
        return Buffer.from(record.data, 'base64');
    }
    // Restore Date
    if (record.__type === 'Date' && typeof record.iso === 'string') {
        return new Date(record.iso);
    }
    // Recursively process nested objects
    const result = {};
    for (const [key, value] of Object.entries(record)) {
        result[key] = restoreBuffers(value);
    }
    return result;
}
exports.default = exportTool;
//# sourceMappingURL=export.js.map