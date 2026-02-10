
# Minecraft server spy

Minecraft server spy is a simple utility for monitoring player connections on a Minecraft server and report to Discord.
Before you use it make sure you have permition from the server owner and/or its players.

## Usage

1. Create `config.json` (use template in `config_template.py` for reference) and add your report points (discord bot/webhook)
2. If you want to use discord bot, create `.dicord_token.key` and paste your discord bot token there.
3. Install required python packages using pip: `mcstatus`, `discord`, `aiohttp`
`pip install -r requirements.txt` or `pip3 install -r requirements.txt`
4. Run scipt: `python minecraft_spy_bot.py` or `python3 minecraft_spy_bot.py` or `py minecraft_spy_bot.py`
5. _(Optional, Linux only, for systemd)_ Setup systemd service that runs the script on startup using: `sudo setup_service.py`

## What will happen after running

- Log file will be created each time script runs (in `log/` directory)

```txt
Example log file:
[06:07:54] Waiting for internet access... (reference: https://google.com)
[06:07:54] Internet check failed: Cannot connect to host google.com:443 ssl:default [Could not contact DNS servers]
[06:07:59] Came online!
[06:08:02] example_bot#1234 is now running
[06:08:02] {'minecraft_server_url': 'example.com', 'minecraft_server_port': 25565, 'IDLE_CHECK_DELAY': 120, 'ACTIVE_CHECK_DELAY': 15, 'INACTIVITY_THRESHOLD_SECONDS': 300, 'online_check_reference': 'https://google.com', 'report_targets': [{'target_type': 'CHANNEL', 'target_id': 123456789123456789}]}
[06:08:02] 0 []
[06:08:50] 1 ['Notch']
[06:09:58] 2 ['Herobrine', 'Notch']
[06:11:50] 1 ['Herobrine']
[06:14:16] -1 []
```

- Statistic file will be created each time script runs (in `stats/` directory)

```txt
Example statistic file:
[06:08:02] 0 []
[06:08:50] 1 ['Notch']
[06:09:58] 2 ['Herobrine', 'Notch']
[06:11:50] 1 ['Herobrine']
[06:14:16] -1 []
[09:30:04] -2 []
```

```txt
Explanation:
// First number is number of players connected, then there is a list of all players
[06:08:02] 0 []                         // Server is empty
[06:08:50] 1 ['Notch']                  // There 1 player connected with nickname 'Notch'
[06:09:58] 2 ['Herobrine', 'Notch']
[06:11:50] 1 ['Herobrine']
[06:14:16] -1 []                        // Minecraft server is offline
[09:30:04] -2 []                        // We lost internet connection (aka we can't connect to our reference point set in `config.json` - in this case `https://google.com`)
```

### Notes

- Make sure that reference point in `config.json` has `https://` or `http://` prefix.
- You can only use one discord bot.
- You can send messages to multiple webhooks, channels or users.
