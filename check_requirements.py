import sys, os
print(f"Running as user {os.getenv("USER")}, should be running as {sys.argv[2]}")
user_site_packages = os.path.expanduser(f'/home/{sys.argv[2]}/.local/lib/python3.13/site-packages')
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
    sys.exit(1)
else:
    print("\nSome modules are missing. Install them before running minecraft_spy_bot! Make sure your user has the packages installed. Sometimes root doesn't have access to user-installed packages.\nInstall them using `pip install -r requirements.txt`.")
    sys.exit(0)
