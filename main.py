import os
import threading
from dotenv import load_dotenv
from flask import Flask
import discord
from discord import app_commands
from api.routes import routes_bp
from api.pages import pages_bp
from bot.commands import setup_commands

load_dotenv()

class DarkBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self): 
        await self.tree.sync()

    async def on_ready(self):
        print(f"{self.user} was turned on.")

bot = DarkBot()

setup_commands(bot)

def run_flask():
    app = Flask(__name__, template_folder='templates', static_folder='templates')
    
    app.bot = bot
    
    app.register_blueprint(routes_bp, url_prefix='/api')
    app.register_blueprint(pages_bp, url_prefix='/')
    
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False
    )

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

bot.run(os.getenv("BOT_TOKEN"))
