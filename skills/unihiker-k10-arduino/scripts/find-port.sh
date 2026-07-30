#!/bin/bash
#
# Unihiker K10 Skill - Port Detection
# Auto-detects K10 serial port based on VID/PID or common patterns
#

# Known K10 USB IDs (ESP32-S3 based)
# These may need updating based on actual K10 hardware
K10_VID="303a"  # Espressif VID
K10_PID="1001"  # ESP32-S3 PID (placeholder, update with actual)

# Alternative: Match by product string
K10_PRODUCT_KEYWORDS=("unihiker" "k10" "esp32" "cp210" "ch340" "ft232")

# Detect OS
get_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(get_os)

# Find port on Linux
find_port_linux() {
    local port=""
    
    # Method 1: Look for ESP32-S3 or common USB-UART chips
    for tty in /dev/ttyUSB* /dev/ttyACM*; do
        if [[ -e "$tty" ]]; then
            # Check if it's a USB device with known VID/PID
            local sys_path
            sys_path=$(readlink -f "/sys/class/tty/$(basename "$tty")" 2>/dev/null || true)
            
            if [[ -n "$sys_path" ]]; then
                # Check for ESP32 or common USB-UART
                if [[ "$sys_path" == *"usb"* ]]; then
                    # Read VID/PID if available
                    local vid_pid_path
                    vid_pid_path=$(echo "$sys_path" | sed 's|/tty.*||')/modalias 2>/dev/null || true
                    
                    if [[ -f "$vid_pid_path" ]]; then
                        local modalias
                        modalias=$(cat "$vid_pid_path" 2>/dev/null || true)
                        # Check for Espressif VID
                        if [[ "$modalias" == *"${K10_VID}"* ]] || [[ "$modalias" == *"10c4"* ]] || [[ "$modalias" == *"1a86"* ]]; then
                            port="$tty"
                            break
                        fi
                    else
                        # Fallback: check udev info
                        if udevadm info -q property -n "$tty" 2>/dev/null | grep -qiE "(unihiker|k10|esp32|cp210|ch340)"; then
                            port="$tty"
                            break
                        fi
                    fi
                fi
            fi
        fi
    done
    
    # Method 2: If only one USB serial port, assume it's K10
    if [[ -z "$port" ]]; then
        local ports
        ports=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | wc -l)
        if [[ "$ports" -eq 1 ]]; then
            port=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
        fi
    fi
    
    echo "$port"
}

# Find port on macOS
find_port_macos() {
    local port=""
    
    # List all serial ports
    for tty in /dev/cu.usb* /dev/tty.usb* /dev/cu.SLAB* /dev/cu.wchusb*; do
        if [[ -e "$tty" ]]; then
            # Check ioreg for device info
            local device_info
            device_info=$(ioreg -p IOUSB -w0 -l 2>/dev/null | grep -iE "(unihiker|k10|esp32|cp210|ch340|ft232)" || true)
            
            if [[ -n "$device_info" ]]; then
                port="$tty"
                break
            fi
            
            # Fallback: check port name patterns
            if [[ "$(basename "$tty")" =~ (usbserial|usbmodem|SLAB|wchusb) ]]; then
                port="$tty"
                break
            fi
        fi
    done
    
    echo "$port"
}

# Find port on Windows (using PowerShell)
find_port_windows() {
    # Use PowerShell to find COM ports
    powershell -Command "
        \$ports = Get-PnpDevice -Class Ports | Where-Object { \$_.FriendlyName -match 'USB' }
        foreach (\$port in \$ports) {
            if (\$port.FriendlyName -match 'COM(\d+)') {
                Write-Output \"COM\$([regex]::Match(\$port.FriendlyName, 'COM(\d+)').Groups[1].Value)\"
                break
            }
        }
    " 2>/dev/null || echo ""
}

# Main
main() {
    local port=""
    
    case $OS in
        linux)
            port=$(find_port_linux)
            ;;
        macos)
            port=$(find_port_macos)
            ;;
        windows)
            port=$(find_port_windows)
            ;;
        *)
            echo "Unsupported OS" >&2
            exit 1
            ;;
    esac
    
    if [[ -n "$port" ]]; then
        echo "$port"
        exit 0
    else
        exit 1
    fi
}

main
