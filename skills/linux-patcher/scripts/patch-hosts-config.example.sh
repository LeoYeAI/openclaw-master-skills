#!/bin/bash
# Example configuration file for patch-multiple.sh
# Copy this file and customize for your infrastructure
#
# Usage:
#   1. Copy: cp patch-hosts-config.example.sh my-servers.conf
#   2. Edit: nano my-servers.conf
#   3. Run: ./patch-multiple.sh my-servers.conf

# ============================================
# HOST DEFINITIONS
# ============================================
# Format: "hostname,ssh_user,docker_path"
#
# hostname     - FQDN or IP address
# ssh_user     - SSH username (leave empty to use current user)
# docker_path  - Path to docker-compose.yml (leave empty for auto-detect)
#
# Examples:
#   "webserver.example.com,ubuntu,/opt/docker"
#   "db.example.com,root,/home/admin/compose"
#   "monitor.local,docker,"  # auto-detect Docker path
#   "backup.local,,"         # current user + auto-detect

HOSTS=(
    "server1.example.com,admin,/home/admin/docker"
    "server2.example.com,ubuntu,/opt/docker"
    "server3.example.com,docker,"
)

# ============================================
# UPDATE MODE
# ============================================
# Options:
#   "host-only" - Update packages only (no Docker)
#   "full"      - Update packages + Docker containers

UPDATE_MODE="full"

# ============================================
# DRY RUN MODE
# ============================================
# Set to "true" to preview changes without applying them
# Set to "false" to actually apply updates

DRY_RUN="true"

# ============================================
# PARALLEL EXECUTION (Future)
# ============================================
# Number of hosts to update simultaneously
# Currently not implemented - hosts are processed sequentially

# PARALLEL_JOBS=2
