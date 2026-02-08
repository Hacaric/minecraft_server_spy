#
#    Simple python utility to track player activity on a minecraft server
#    This code was created with help of Google Gemini and OpenAI Gpt4  :D
#
#

DISCORD_BOT_TOKEN_FILE = ".discord_token.key"
CONFIG_TEMPLATE_FILE = "config_template.json"
CONFIG_FILE = "config.json"

DISCORD_BOT_TOKEN = None
USER_REPORT_ID = None



from mcstatus import JavaServer
import discord
from discord.ext import commands
import discord
import time
import aiohttp
import json
import asyncio
import os
from datetime import datetime


try:
    with open(CONFIG_FILE, "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print(f"Error loading {CONFIG_FILE}, file doesn't exist.")
    print(f"\nWelcome to Minecraft server spy, a simple utility for monitoring player connection times on a Minecraft server.\nTo start, create config.json using template in config_template.json and enter your discord bot token to .discord_token.key.")
    if input(f"Create config files? (y/n)> ")[0] == "y":
        with open(CONFIG_TEMPLATE_FILE, "r") as f:
            with open(CONFIG_FILE, "w") as f2:
                f2.write(f.read())
        print(f"Copyed {CONFIG_TEMPLATE_FILE} into {CONFIG_FILE}. Please edit config.json before running this script again.")
    if input(f"Add discord bot token? (y/n)")[0] == "y":
        token = input("Enter discord bot token: ")
        with open(DISCORD_BOT_TOKEN_FILE, "w") as f:
            f.write(token)
        print(f"Created discord token file: {DISCORD_BOT_TOKEN_FILE}")
    print(f"\nGo edit {CONFIG_FILE} before running this again!\nExiting...")
    exit()
except Exception as e:
    print(f"Error loading config file {CONFIG_FILE}: {e}. \nMake sure your json is correctly formted!")
    print(f"\nGo edit {CONFIG_FILE} before running this again!\nExiting...")
    exit()

try:
    with open(DISCORD_BOT_TOKEN_FILE, "r") as f:
        DISCORD_BOT_TOKEN = f.readlines()[0]
except FileNotFoundError:
    DISCORD_BOT_TOKEN = input(f"Discord bot token missing (file .discord_token.key doesn't exist):\nEnter discord bot token: ")
    with open(DISCORD_BOT_TOKEN_FILE, "w") as f:
        f.write(DISCORD_BOT_TOKEN)
    


async def send_message(client, session: aiohttp.ClientSession, targets:list, message=None):
    try:
        for target in targets:
            if target["target_type"] == "USER":
                try:
                    user = client.get_user(target["target_id"])
                    if user:
                        await user.send(message)
                except Exception as e:
                    print(f"Error sending message to user {target['target_id']}: {e}")
            elif target["target_type"] == "CHANNEL":
                try:
                    channel = client.get_channel(target["target_id"])
                    if channel:
                        await channel.send(message)
                except Exception as e:
                    print(f"Error sending message to channel {target['target_id']}: {e}")
            elif target["target_type"] == "WEBHOOK":
                try:
                    data = {"content": message, "username": target['bot_name']}
                    async with session.post(target["target_id"], json=data) as response:
                        response.raise_for_status()
                except (aiohttp.ClientError, asyncio.TimeoutError) as http_error:
                    print(f"Error sending message to webhook {target['target_id']}: {http_error}")
                except Exception as e:
                    print(f"Error sending message to webhook {target['target_id']}: {e}")
            else:
                print(f"Unknown target type: {target['target_type']}")

    except Exception as e:
        log(f"Error sending message: {e}")


def run_discord_bot():
    try:
    
        intents1 = discord.Intents.all()
        client = commands.Bot(command_prefix="/", intents=intents1)

        @client.event
        async def on_ready():
            log(f'{client.user} is now running')
            client.loop.create_task(server_status_check(client, CONFIG))

        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(e)
    return "error"


async def server_status_check(client, CONFIG):
    server = await JavaServer.async_lookup(f"{CONFIG["minecraft_server_url"]}:{CONFIG["minecraft_server_port"]}")
    targets = CONFIG["report_targets"]
    log(CONFIG)
    log(targets[0])
    LAST_PLAYER_STATUS = 99999
    LAST_ONLINE_PLAYER_TIME = 0
    i = 0
    async with aiohttp.ClientSession() as session:
        await send_message(client, session, targets, f"Bot started...")
        RETRIES = 0

        while True:
            player_list = []
            try:
                status = await server.async_status()
                if isinstance(status.players.sample, list):
                    player_list = sorted([player.name for player in status.players.sample])
                if LAST_PLAYER_STATUS != player_list:
                    await send_message(client, session, targets, f"Minecraft server player count: {status.players.online}  {player_list}")
                    log(f"{status.players.online} {player_list}", statisctics=True)
                    LAST_PLAYER_STATUS = player_list
                    RETRIES = 0
                    if status.players.online > 0:
                        LAST_ONLINE_PLAYER_TIME = time.time()
            except Exception as e:
                if LAST_PLAYER_STATUS != -1 and RETRIES == 3:
                    try:
                        async with session.get(CONFIG["online_check_reference"]) as response:
                            response.raise_for_status()
                        await send_message(client, session, targets, f"Minecraft server is offline: {e}")
                        log("-1 []", statisctics=True)
                        LAST_PLAYER_STATUS = -1
                        RETRIES = 0
                    except (aiohttp.ClientError, asyncio.TimeoutError) as http_error:
                        log(f"Our internet is down... (can't reach server nor {CONFIG['online_check_reference']}): {http_error}")
                        log("-2 []", statisctics=True)
                    except Exception as inner_e:
                        log(f"Unexpected error during internet check: {inner_e}")
                        log("-2 []", statisctics=True)
                else:
                    RETRIES += 1
            if time.time() - LAST_ONLINE_PLAYER_TIME < CONFIG["INACTIVITY_THRESHOLD_SECONDS"]:
                await asyncio.sleep(CONFIG["ACTIVE_CHECK_DELAY"])
            else:
                await asyncio.sleep(CONFIG["IDLE_CHECK_DELAY"])

            i += 1

def setup_logger():
    global log_file, stats_file
    now = datetime.now()
    formatted_date_time = now.strftime("%d-%m-%Y_%H-%M")
    # log_file_name = f"log_{formatted_date_time}.txt"
    # log_file = open(os.path.join(os.path.dirname(__file__), "log", log_file_name), "wt")
    # stats_file_name = f"statisctic_{formatted_date_time}.txt"
    # stats_file = open(os.path.join(os.path.dirname(__file__), "stats", stats_file_name), "wt")
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "log")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "log"))
    log_file_name = os.path.join(os.path.dirname(__file__), "log", f"log_{formatted_date_time}.txt")
    log_file = open(log_file_name, "wt")
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "stats")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "stats"))
    stats_file_name = os.path.join(os.path.dirname(__file__), "stats", f"statisctic_{formatted_date_time}.txt")
    stats_file = open(stats_file_name, "wt")

def log(*msg, statisctics = False):
    global log_file, stats_file
    now = datetime.now()
    final_message = f"[{now.strftime('%H:%M:%S')}]"
    for text in msg:
        if isinstance(text, str):
            final_message += " " + text
        else:
            try:
                text = str(text)
                final_message += " " + text
            except Exception as e:
                # text = f"Error: Can't convert log message to string: {e}"
                final_message += "{Error converting to str}"
    # raise Exception("Failed successfully")
    if final_message:
        log_file.write(final_message + "\n")
        log_file.flush()
        if statisctics:
            print(final_message)
            stats_file.write(final_message + "\n")
            stats_file.flush()
        else:
            print(final_message)

if __name__ == "__main__":
    setup_logger()

    async def initial_internet_check(config_ref):
        log(f"Waiting for internet access... (reference: {config_ref})")
        online = False
        while not online:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(config_ref) as response:
                        response.raise_for_status()
                online = True
                log("Came online!")
                return True
            except (aiohttp.ClientError, asyncio.TimeoutError) as http_error:
                log(f"Internet check failed: {http_error}")
            except Exception as e:
                log(f"Unexpected error during internet check: {e}")
            await asyncio.sleep(5) # Add a small delay between retries
        return False

    try:
        # Run the initial internet check asynchronously
        asyncio.run(initial_internet_check(CONFIG['online_check_reference']))
        run_discord_bot()
    except KeyboardInterrupt:
        print("KeyboardInterrupt - Closing log files...")
        log_file.close()
        stats_file.close()
    except Exception as e:
        print(f"Error: {e} - Closing log files...")
        log_file.close()
        stats_file.close()
