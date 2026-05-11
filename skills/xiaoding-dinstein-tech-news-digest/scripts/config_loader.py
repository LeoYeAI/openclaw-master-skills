#!/usr/bin/env python3
"""
Configuration overlay loader for tech-news-digest.

Handles loading and merging of default configurations with optional user overlays.
Supports sources.json and topics.json with overlay logic for customization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def load_merged_sources(defaults_dir: Path, config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load and merge sources from defaults and optional user config overlay.
    
    Args:
        defaults_dir: Path to default configuration directory (skill defaults)
        config_dir: Optional path to user configuration directory (overlay)
    
    Returns:
        List of merged source configurations
        
    Merge Logic:
        1. Load defaults/sources.json as base
        2. If config_dir provided and has sources.json, load user overlay
        3. For each user source:
           - If id matches default source: user version completely replaces default
           - If id is new: append to list
           - If user source has "enabled": false: disable matching default source
    """
    defaults_path = defaults_dir / "sources.json"
    
    # Load default sources
    try:
        with open(defaults_path, 'r', encoding='utf-8') as f:
            defaults_data = json.load(f)
        default_sources = defaults_data.get("sources", [])
        logger.debug(f"Loaded {len(default_sources)} default sources from {defaults_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Default sources config not found: {defaults_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in default sources config: {e}")
    
    # Validate required fields
    validated = []
    required_fields = {"id", "type", "enabled"}
    for i, source in enumerate(default_sources):
        missing = required_fields - set(source.keys())
        if missing:
            logger.warning(f"Source #{i} missing required fields {missing}, skipping: {source}")
            continue
        validated.append(source)
    default_sources = validated

    # If no user config directory specified, return defaults only
    if config_dir is None:
        return default_sources
        
    config_path = config_dir / "tech-news-digest-sources.json"
    
    # Try to load user overlay
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        user_sources = config_data.get("sources", [])
        logger.debug(f"Loaded {len(user_sources)} user sources from {config_path}")
    except FileNotFoundError:
        logger.debug(f"No user sources config found at {config_path}, using defaults only")
        return default_sources
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in user sources config {config_path}: {e}, using defaults only")
        return default_sources
    
    # Merge logic: create lookup by id for efficient merging
    merged_sources = {}
    
    # Start with all default sources
    for source in default_sources:
        source_id = source.get("id")
        if source_id:
            merged_sources[source_id] = source.copy()
    
    # Apply user overlay
    for user_source in user_sources:
        source_id = user_source.get("id")
        if not source_id:
            continue
            
        if source_id in merged_sources:
            # User source overrides default completely
            if user_source.get("enabled") is False:
                # User explicitly disables this source
                merged_sources[source_id]["enabled"] = False
                logger.debug(f"User disabled source: {source_id}")
            else:
                # User replaces entire source config
                merged_sources[source_id] = user_source.copy()
                logger.debug(f"User overrode source: {source_id}")
        else:
            # New user source, append
            merged_sources[source_id] = user_source.copy()
            logger.debug(f"User added new source: {source_id}")
    
    # Convert back to list, maintaining order (defaults first, then user additions)
    result = []
    
    # Add default sources (potentially overridden)
    for source in default_sources:
        source_id = source.get("id")
        if source_id and source_id in merged_sources:
            result.append(merged_sources[source_id])
    
    # Add new user sources
    for user_source in user_sources:
        source_id = user_source.get("id")
        if source_id and source_id not in [s.get("id") for s in default_sources]:
            result.append(merged_sources[source_id])
    
    logger.info(f"Merged configuration: {len(default_sources)} defaults + {len(user_sources)} user = {len(result)} total sources")
    return result


def load_merged_topics(defaults_dir: Path, config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load and merge topics from defaults and optional user config overlay.
    
    Args:
        defaults_dir: Path to default configuration directory (skill defaults)
        config_dir: Optional path to user configuration directory (overlay)
    
    Returns:
        List of merged topic configurations
        
    Merge Logic:
        1. Load defaults/topics.json as base
        2. If config_dir provided and has topics.json, load user overlay
        3. For each user topic:
           - If id matches default topic: user version completely replaces default
           - If id is new: append to list
    """
    defaults_path = defaults_dir / "topics.json"
    
    # Load default topics
    try:
        with open(defaults_path, 'r', encoding='utf-8') as f:
            defaults_data = json.load(f)
        default_topics = defaults_data.get("topics", [])
        logger.debug(f"Loaded {len(default_topics)} default topics from {defaults_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Default topics config not found: {defaults_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in default topics config: {e}")
    
    # If no user config directory specified, return defaults only
    if config_dir is None:
        return default_topics
        
    config_path = config_dir / "tech-news-digest-topics.json"
    
    # Try to load user overlay
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        user_topics = config_data.get("topics", [])
        logger.debug(f"Loaded {len(user_topics)} user topics from {config_path}")
    except FileNotFoundError:
        logger.debug(f"No user topics config found at {config_path}, using defaults only")
        return default_topics
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in user topics config {config_path}: {e}, using defaults only")
        return default_topics
    
    # Merge logic: create lookup by id for efficient merging
    merged_topics = {}
    
    # Start with all default topics
    for topic in default_topics:
        topic_id = topic.get("id")
        if topic_id:
            merged_topics[topic_id] = topic.copy()
    
    # Apply user overlay
    for user_topic in user_topics:
        topic_id = user_topic.get("id")
        if not topic_id:
            continue
            
        if topic_id in merged_topics:
            # User topic overrides default completely
            merged_topics[topic_id] = user_topic.copy()
            logger.debug(f"User overrode topic: {topic_id}")
        else:
            # New user topic, append
            merged_topics[topic_id] = user_topic.copy()
            logger.debug(f"User added new topic: {topic_id}")
    
    # Convert back to list, maintaining order (defaults first, then user additions)
    result = []
    
    # Add default topics (potentially overridden)
    for topic in default_topics:
        topic_id = topic.get("id")
        if topic_id and topic_id in merged_topics:
            result.append(merged_topics[topic_id])
    
    # Add new user topics
    for user_topic in user_topics:
        topic_id = user_topic.get("id")
        if topic_id and topic_id not in [t.get("id") for t in default_topics]:
            result.append(merged_topics[topic_id])
    
    logger.info(f"Merged topics: {len(default_topics)} defaults + {len(user_topics)} user = {len(result)} total topics")
    return result


