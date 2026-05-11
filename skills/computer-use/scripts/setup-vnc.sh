#!/bin/bash
# Setup stable VNC for computer-use skill
# Run once to install systemd services for flicker-free VNC desktop

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
USER=$(whoami)
HOME_DIR=$(eval echo "~$USER")

echo "=== Computer Use VNC Setup ==="
echo "User: $USER"
echo "Skill dir: $SKILL_DIR"
echo ""

# Install packages
echo "[1/6] Installing packages..."
sudo apt update -qq
sudo apt install -y xvfb xfce4 xfce4-terminal xdotool scrot imagemagick dbus-x11 x11vnc novnc websockify

# Copy minimal-desktop.sh to a stable location
echo "[2/6] Installing watchdog script..."
sudo mkdir -p /opt/computer-use
sudo cp "$SCRIPT_DIR/minimal-desktop.sh" /opt/computer-use/
sudo chmod +x /opt/computer-use/minimal-desktop.sh

# Install systemd services (generated inline)
echo "[3/6] Installing systemd services..."

cat <<EOF | sudo tee /etc/systemd/system/xvfb.service > /dev/null
[Unit]
Description=Xvfb Virtual Display :99
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -nolisten tcp -dpi 96
Restart=always
RestartSec=1
User=$USER
Environment="HOME=$HOME_DIR"

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/xfce-minimal.service > /dev/null
[Unit]
Description=XFCE Minimal Desktop for Computer Use
After=xvfb.service
Requires=xvfb.service

[Service]
Type=simple
ExecStart=/opt/computer-use/minimal-desktop.sh
Restart=always
RestartSec=3
User=$USER
Environment="HOME=$HOME_DIR"
Environment="DISPLAY=:99"

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/x11vnc.service > /dev/null
[Unit]
Description=x11vnc VNC Server
After=xfce-minimal.service
Requires=xfce-minimal.service

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -display :99 -forever -shared -rfbport 5900 -noxdamage -noxfixes -noclipboard
Restart=always
RestartSec=2
User=$USER
Environment="HOME=$HOME_DIR"
Environment="DISPLAY=:99"

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/novnc.service > /dev/null
[Unit]
Description=noVNC WebSocket Proxy
After=x11vnc.service
Requires=x11vnc.service

[Service]
Type=simple
ExecStart=/usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 --heartbeat 30
Restart=always
RestartSec=2
User=$USER
Environment="HOME=$HOME_DIR"

[Install]
WantedBy=multi-user.target
EOF

# Mask xfdesktop to prevent flickering
echo "[4/6] Masking xfdesktop (prevents flicker)..."
if [ -f /usr/bin/xfdesktop ] && [ ! -f /usr/bin/xfdesktop.real ]; then
    sudo mv /usr/bin/xfdesktop /usr/bin/xfdesktop.real
    echo '#!/bin/bash
# Masked - xfdesktop causes VNC flickering on Xvfb
exit 0' | sudo tee /usr/bin/xfdesktop > /dev/null
    sudo chmod +x /usr/bin/xfdesktop
    echo "  xfdesktop masked (original at /usr/bin/xfdesktop.real)"
else
    echo "  xfdesktop already masked or not found"
fi

# Enable and start services
echo "[5/6] Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable xvfb xfce-minimal x11vnc novnc

echo "[6/6] Starting services..."
sudo systemctl start xvfb
sleep 2
sudo systemctl start xfce-minimal
sleep 3
sudo systemctl start x11vnc
sleep 1
sudo systemctl start novnc

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services running:"
systemctl is-active xvfb xfce-minimal x11vnc novnc | paste - - - - | awk '{print "  xvfb: "$1"  xfce-minimal: "$2"  x11vnc: "$3"  novnc: "$4}'
echo ""
echo "Access VNC:"
echo "  1. SSH tunnel: ssh -L 6080:localhost:6080 $(hostname)"
echo "  2. Open: http://localhost:6080/vnc.html"
echo ""
echo "Or add to ~/.ssh/config:"
echo "  Host $(hostname)"
echo "    LocalForward 6080 127.0.0.1:6080"
