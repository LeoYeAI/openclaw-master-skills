#!/bin/bash
# Minimal XFCE desktop without xfdesktop (prevents VNC flickering)
# Runs as a watchdog: starts xfwm4+panel, kills xfdesktop if it respawns

export DISPLAY=:99

# Wait for X server
while ! xdpyinfo -display :99 >/dev/null 2>&1; do
    sleep 0.5
done

# Kill any existing session/desktop that causes flickering
pkill -f xfce4-session 2>/dev/null
pkill -f xfdesktop 2>/dev/null
sleep 1

# Set static background (no redraw cycles = no flicker)
xsetroot -solid "#2d3436"

# Disable screen blanking
xset s off
xset s noblank
xset -dpms 2>/dev/null

# Start window manager (if not running)
pgrep -x xfwm4 || xfwm4 &

# Start panel (if not running)
pgrep -x xfce4-panel || xfce4-panel &

# Watchdog loop: kill flickering processes, respawn essentials
while true; do
    # Kill unwanted processes that cause flickering
    if pgrep -x xfdesktop >/dev/null; then
        pkill -f xfdesktop
        xsetroot -solid "#2d3436"
    fi
    if pgrep -x xfce4-session >/dev/null; then
        pkill -f xfce4-session
    fi
    
    # Respawn xfwm4 if it died
    if ! pgrep -x xfwm4 >/dev/null; then
        xfwm4 &
    fi
    
    # Respawn panel if it died
    if ! pgrep -x xfce4-panel >/dev/null; then
        xfce4-panel &
    fi
    
    sleep 1
done
