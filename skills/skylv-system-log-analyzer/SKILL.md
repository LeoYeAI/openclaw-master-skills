---
name: skylv-log-analyzer
slug: skylv-log-analyzer
version: 1.0.0
description: "Parses and summarizes log files. Extracts errors, warnings, patterns, and insights from server logs and debug output. Triggers: analyze logs, parse log file, error summary, log analysis, debug logs."
author: SKY-lv
license: MIT
tags: [logs, debugging, analysis, monitoring]
keywords: [logs, analysis, debugging, error-tracking, monitoring]
triggers: analyze logs, parse log file, error summary, log analysis
---

# Log Analyzer

## Overview
Parses and analyzes log files to extract errors, warnings, patterns, and actionable insights.

## When to Use
- User asks to "analyze these logs" or "check the error log"
- Debugging session needs pattern analysis

## How It Works

### Step 1: Read log file
Windows: type server.log or Get-Content error.log -Tail 100
macOS/Linux: tail -n 100 app.log

### Step 2: Detect log format
[2024-01-15 14:30:45] -> Timestamp bracketed
ERROR 2024-01-15 -> Level + timestamp
{ "level": "error" } -> JSON structured

### Step 3: Extract key information
Level: ERROR, WARN, INFO, DEBUG
Timestamp: when it happened
Source: which component/module
Message: what happened

### Step 4: Generate analysis report

## Output Format
Total lines: 1,247
Time range: 10:00 -> 18:00

Errors: 23
Warnings: 67
Info: 892

Top Errors by frequency:
1. Connection timeout (x12) - API calls to external service
2. Auth failure (x6) - Failed login from IP xxx

Anomaly: Unusual spike at 16:00-17:00 (18 errors in 1 hour)

Recommendations:
1. Check external service connectivity
2. Review failed logins for security
3. Add retry logic to DB writes