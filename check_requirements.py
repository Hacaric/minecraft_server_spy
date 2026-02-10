import sys
import os

# Warn if running as root and not running from setup_service.py (which gives username as argument)
if os.getenv("USER") == "root" and len(sys.argv) <= 1:
    print("Warning! This script is running as root.")
    print("Root may not have access to user-installed packages.")
    print("If this is during setup_service, ensure your service has `[User]=yourname` to run as a regular user.\n")
    if input("Do you want to continue? (y/n)")[0] != "y":
        sys.exit(1)

username = sys.argv[1] if len(sys.argv) > 1 else os.getenv("USER")
print(f"Testing packages for user {username}. Make sure your script is being run by this user!")
user_site_packages = os.path.expanduser(f'/home/{username}/.local/lib/python3.13/site-packages')
if user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

print(f"Checking required modules...\n")
run = True
try:
    import mcstatus
    print("[Ok] mcstatus module found!")
except:
    print("[Fail] mcstatus module missing!")
    run = False
try:
    import discord
    print("[Ok] discord module found!")
except:
    print("[Fail] discord module missing!")
    run = False
try:
    import aiohttp
    print("[Ok] aiohttp module found!")
except:
    print("[Fail] aiohttp module missing!")
    run = False

if run:
    print("\nAll modules are installed.")
else:
    print("\nSome modules are missing. Install them before running minecraft_spy_bot! Make sure your user has the packages installed. Sometimes root doesn't have access to user-installed packages.\nInstall them using `pip install -r requirements.txt`.")
