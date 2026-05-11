#!/usr/bin/env python3
"""
Assemble the sync payload from _pf_parts/ partial files.

Reads:
  _pf_parts/portrait.json                – framework sentences + portrait (AI analysis, Phase 2)
  _pf_parts/search_profile.json          – full search profile (AI analysis, Phase 1)
  _pf_parts/behavioral_fingerprint.json  – behavioral fingerprint data (compute-stats.py)
  _pf_parts/activity.json                – activity heat map data
  _pf_parts/meta.json                    – {sessionsAnalyzed, totalTokens}

Writes:
  promptfolio_payload.json  – ready to POST to /api/profile/sync

Environment:
  IS_PUBLIC  – "true" or "false" (default "true")
"""

import json
import os
import sys

parts = "_pf_parts"
is_public = os.environ.get("IS_PUBLIC", "true")

portrait = json.load(open(f"{parts}/portrait.json"))
activity = json.load(open(f"{parts}/activity.json"))
meta = json.load(open(f"{parts}/meta.json"))

# Phase 1 search profile (optional — older runs may not have it)
search_profile = None
search_profile_path = f"{parts}/search_profile.json"
if os.path.exists(search_profile_path):
    search_profile = json.load(open(search_profile_path))

# Behavioral fingerprint (optional)
behavioral_fp = None
bf_path = f"{parts}/behavioral_fingerprint.json"
if os.path.exists(bf_path):
    behavioral_fp = json.load(open(bf_path))

payload = {
    "profile": {
        "summary": portrait["portrait"]["summary"],
        "topDomains": portrait.get("topDomains", []),
        "cognitiveStyle": portrait.get("cognitiveStyle") or None,
        "capabilityRings": portrait.get("capabilityRings") or None,
        "decisionStyle": portrait.get("decisionStyle") or None,
        "controlSignature": portrait.get("controlSignature") or None,
    },
    "activityMap": activity,
    "sessionsAnalyzed": meta["sessionsAnalyzed"],
    "totalTokens": meta["totalTokens"],
    "isPublic": is_public.lower() == "true",
}

if search_profile:
    payload["searchProfile"] = {
        "frameworkSentences": search_profile.get("frameworkSentences", []),
        "instances": search_profile.get("instances", []),
        "fullDesc": search_profile.get("fullDesc", ""),
    }
    # Projects extracted from conversation analysis
    projects = search_profile.get("projects", [])
    if projects:
        payload["projects"] = projects

if behavioral_fp:
    sigs = behavioral_fp.pop("_signatures", [])
    payload["behavioralFingerprint"] = {
        "raw": behavioral_fp,
        "signatures": sigs,
        "insights": portrait.get("behavioralInsights", []),
    }

with open("promptfolio_payload.json", "w") as f:
    json.dump(payload, f, ensure_ascii=False)

print(f"Payload assembled: {os.path.getsize('promptfolio_payload.json')} bytes")
