#!/usr/bin/env python3
import os
import sys
import subprocess

"""
Creates a systemd service for minecraft_spy_bot
"""

if os.geteuid() != 0:
    print("Error: This script must be run as root (use sudo)")
    sys.exit(1)


SERVICE_NAME = input("Enter service name: ")
if input(f"Confirm service name: ") != SERVICE_NAME:
    print("Name doesn't match: Aborting...")
    exit()
SERVICE_FILE = f"/etc/systemd/system/{SERVICE_NAME}.service"
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "minecraft_spy_bot.py")
USER = os.getenv("USER")

SERVICE_CONTENT = f"""[Unit]
Description=Minecraft Spy Bot Service
After=network.target
Wants=network.target

[Service]
Type=simple
User={USER}
WorkingDirectory={os.path.dirname(SCRIPT_PATH)}
ExecStart={sys.executable} {SCRIPT_PATH}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

def create_service():
    """Create and enable the systemd service"""
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo)")
        sys.exit(1)
    
    try:
        with open(SERVICE_FILE, "w") as f:
            f.write(SERVICE_CONTENT)
        print(f"✓ Service file created at {SERVICE_FILE}")
        
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)
        print(f"✓ Service '{SERVICE_NAME}' enabled")
        print(f"\nStart service: sudo systemctl start {SERVICE_NAME}")
        print(f"Check status: sudo systemctl status {SERVICE_NAME}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_service()