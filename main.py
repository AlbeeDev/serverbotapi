import discord
from discord.ext import tasks
import socket
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
SERVER_ADDRESS = 'albeedev.ddns.net' 
PORT = 25565

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def save_state(state):
    with open('server_state.txt', 'w') as file:
        file.write(state)


def read_state():
    try:
        with open('server_state.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def check_port(server, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)  # Timeout in seconds
        try:
            sock.connect((server, port))
            return True
        except socket.error:
            return False


async def send_status_update(message):
    channel = client.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(message)


last_state = None


@tasks.loop(minutes=5)  # Adjust the interval as needed
async def check_server_status():
    global last_state
    current_state = "online" if check_port(SERVER_ADDRESS, PORT) else "offline"
    last_state = read_state()
    if current_state != last_state:
        # The state has changed
        message = f'Server is {current_state}!'
        await send_status_update(message)
        save_state(current_state)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    check_server_status.start()  # Start the background task


client.run(TOKEN)
