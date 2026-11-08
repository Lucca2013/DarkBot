from typing import Literal
import datetime
import discord
from discord import app_commands, ui
from discord.ext import commands
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta, timezone
import uuid
import asyncio

load_dotenv()

def setup_commands(bot):
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="ping",
        description="shows the bot ping"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def ping_command(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 pong! **{round(bot.latency * 1000)}ms**",
            ephemeral=True
        )
    
    @bot.tree.command(
        name="lock",
        description="locks the chat where the command was used"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def lock_command(interaction: discord.Interaction):        
        everyone_role = interaction.guild.default_role
        await interaction.channel.set_permissions(everyone_role, send_messages=False)
        
        await interaction.response.send_message(
            f"the chat was **locked**, \n you can use **/unlock** to unlock it.",
            ephemeral=True
        )
    
    @bot.tree.command(
        name="unlock",
        description="unlocks the chat where the command was used"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def unlock_command(interaction: discord.Interaction):        
        everyone_role = interaction.guild.default_role
        await interaction.channel.set_permissions(everyone_role, send_messages=True)
        
        await interaction.response.send_message(
            f"the chat was **unlocked**, \n you can use **/lock** to lock it.",
            ephemeral=True
        )
    
    @bot.tree.command(
        name="ban",
        description="ban a user"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def ban_command(interaction: discord.Interaction, user: discord.Member, reason: str): 
        if user == interaction.user:
            return await interaction.response.send_message("You cannot ban yourself!", ephemeral=True)
        
        await user.ban(reason=reason)
                       
        await interaction.response.send_message(
            f"The User {user.mention} was banned by reason **'{reason}'**, \n if you want to unban him, use the command **/unban**",
            ephemeral=True
        )
        
    @bot.tree.command(
        name="unban",
        description="unban a user"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def unban_command(interaction: discord.Interaction, user: discord.User, reason: str):
        await interaction.response.defer(ephemeral=True)

        try:
            await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            return await interaction.followup.send("That user is not banned.", ephemeral=True)
        
        await interaction.guild.unban(user, reason=reason)
        
        await interaction.followup.send(
            f"The User {user.mention} was unbanned by reason **'{reason}'**,\n"
            f"if you want to ban him back, use the command **/ban**",
            ephemeral=True
        )
    
    @bot.tree.command(
        name="ban_list",
        description="see the list of users banned"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def ban_list(interaction: discord.Interaction):
        guild = interaction.guild
        description = ""
        
        async for banned_user in guild.bans(limit=None):
            description += f"User: {banned_user.user.name} \nId: {banned_user.user.id} \nreason: {banned_user.reason}\n ----------------------------------------\n"
            
        embed = discord.Embed(
            title="Banned users:",
            description=description,
            color=discord.Color.dark_red()
        )
        
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
            
    @bot.tree.command(
        name="timeout",
        description="set a timeout for a user"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def timeout_commands(interaction: discord.Interaction, user: discord.Member, time: int,  time_measurement: Literal["minutes", "hours", "days"], reason: str):
        if time_measurement == "minutes" and time > 40320:
            return await interaction.response.send_message(
                f"the max timeout a user can suffer is 28 days, or 40320 minutes",
                ephemeral=True
            )
        elif time_measurement == "hours" and time > 672:
            return await interaction.response.send_message(
                f"the max timeout a user can suffer is 28 days, or 672 hours",
                ephemeral=True
            )
        elif time_measurement == "days" and time > 28:
            return await interaction.response.send_message(
                f"the max timeout a user can suffer is 28 days",
                ephemeral=True
            )
            
        time_minutes = 0
        
        if time_measurement == "minutes": time_minutes = time
        elif time_measurement == "hours": time_minutes = time * 60
        else: time_minutes = (time * 60) * 24
        
        await user.timeout(datetime.timedelta(minutes=time_minutes), reason=reason)
        
        await interaction.response.send_message(
            f"The User {user.mention} suffered a timeout of **{time} {time_measurement}** by reason **'{reason}'**,\n",
            ephemeral=True
        )
    
    @bot.tree.command(
        name="embed",
        description="generates a link where the user can customize and create a embed"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def embed_command(interaction: discord.Interaction): 
        payload = {
            "subject": {
                "id": interaction.guild_id,
                "text_channels": [
                    {"id": str(channel.id), "name": channel.name} 
                    for channel in interaction.guild.text_channels
                ]
            },
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, os.getenv("JWT_KEY"), algorithm="HS256")
              
        await interaction.response.send_message(            
            f"Acess [here]({os.getenv("SITE_URL")}/create_embed?{token}) to create your embed",
            ephemeral=True
        )
        
    @bot.tree.command(
        name="ticket",
        description="generates a link where the user can customize and create a ticket system"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_command(interaction: discord.Interaction): 
        payload = {
            "subject": {
                "id": interaction.guild_id,
                "text_channels": [
                    {"id": str(channel.id), "name": channel.name} 
                    for channel in interaction.guild.text_channels
                ],
                "roles": [
                    {"id": str(role.id), "name": role.name} 
                    for role in interaction.guild.roles
                ]
            },
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
            "iat": datetime.now(timezone.utc)
        }

        token = jwt.encode(payload, os.getenv("JWT_KEY"), algorithm="HS256")
              
        await interaction.response.send_message(            
            f"Acess [here]({os.getenv("SITE_URL")}/create_ticket?{token}) to create your ticket",
            ephemeral=True
        )

class DynamicSelect(discord.ui.Select):
    _bot = None
    _color = None
    _welcome_message = None
    _mention_role = None
    _feedback_channel = None
        
    def __init__(self, embed_options, bot, color, welcome_message, mention_role, feedback_channel):
        super().__init__(
            placeholder="Selecione uma das opções.",
            min_values=1,
            max_values=1,
            options=embed_options
        )
        
        self._bot = bot
        self._color = color
        self._welcome_message = welcome_message
        self._mention_role = mention_role
        self._feedback_channel = feedback_channel

    async def callback(self, interaction: discord.Interaction):
        clicked_option = self.values[0]
        
        clicked_option_label = next((opt.label for opt in self.options if opt.value == clicked_option), clicked_option)
        
        await interaction.message.edit(view=self.view)
        
        result, channel_id = await create_channel(
            self._bot,
            f"{interaction.user.name}-{clicked_option_label}",
            interaction.guild_id,
            adm_only=True,
            ticket_owner=interaction.user
        )
        
        if(result == False):
            await interaction.response.send_message(
                f"A error occured during the ticket creation",
                ephemeral=True
            )
            
            print(channel_id)   
            return
        
        channel = self._bot.get_channel(channel_id)
        overwrite = channel.overwrites_for(interaction.user)
        overwrite.read_messages = True
        overwrite.send_messages = True
        await channel.set_permissions(interaction.user, overwrite=overwrite)
        
        result = await send_embed(
            self._bot, 
            interaction.guild_id, 
            channel_id, 
            title=clicked_option_label, 
            color=self._color, 
            description=f"<@&{str(self._mention_role)}>\n{str(self._welcome_message[clicked_option])}",
            view_override=TicketControlView(self._feedback_channel, self._bot)
        )
        
        if result is not True:
            print(f"Error at creating ticket: {result}")
            return await interaction.response.send_message(
                "Error at creating the ticket",
                ephemeral=True
            )
        
        await interaction.response.send_message(
            f"Your ticket was opened at: **{self._bot.get_channel(channel_id).mention}**",
            ephemeral=True
        )
        
class TicketControlView(discord.ui.View):
    adm = None
    
    def __init__(self, feedback_channel, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.feedback_channel = feedback_channel
        
    def is_admin(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            return False
        
        return True
    
    @discord.ui.button(label="Take on ticket", style=discord.ButtonStyle.danger, custom_id="take_on_ticket", emoji="🤚", row=0)
    async def take_on_ticket_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(self.is_admin(interaction) == False):
            return await interaction.response.send_message("You do not have permission to do this", ephemeral=True)
        
        self.adm = interaction.user
        
        await interaction.response.send_message(f"**This ticket was taked on by {self.adm.mention}**", ephemeral=False)           

    @discord.ui.button(label="close ticket", style=discord.ButtonStyle.secondary, custom_id="close_ticket", emoji="🔒", row=0)
    async def concluir_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(self.is_admin(interaction) == False):
            return await interaction.response.send_message("You do not have permission to do this", ephemeral=True)
        
        channel = interaction.channel
        guild = interaction.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = False
        overwrite.send_messages_in_threads = False
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        for member in channel.members:
            if member.bot:
                continue

            member_overwrite = channel.overwrites_for(member)

            if member_overwrite.send_messages is True:
                member_overwrite.send_messages = False
                await channel.set_permissions(member, overwrite=member_overwrite)

        button.disabled = True

        await interaction.response.edit_message(view=self)

        await channel.send("🔒 **This ticket has been completed and locked.**")

    @discord.ui.button(label="Delete ticket", style=discord.ButtonStyle.danger, custom_id="delete_ticket", emoji="🗑️", row=0)
    async def deletar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(self.is_admin(interaction) == False):
            return await interaction.response.send_message("You do not have permission to do this", ephemeral=True)
        
        await interaction.response.send_message("**The ticket will be deleted in 5 seconds...**", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Close and delete ticket", style=discord.ButtonStyle.primary, custom_id="close_delete_ticket", emoji="⚡", row=0)
    async def concluir_deletar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(self.is_admin(interaction) == False):
            return await interaction.response.send_message("You do not have permission to do this", ephemeral=True)
        
        await interaction.response.send_message("**Locking and preparing to delete...**", ephemeral=False)
        
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        
        await interaction.followup.send("**The ticket has been closed and will be deleted in 5 seconds...**")
        await asyncio.sleep(5)
        await interaction.channel.delete()
        
    @discord.ui.button(label="Feedback", style=discord.ButtonStyle.primary, custom_id="feedback", emoji="📢", row=0)
    async def feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FeedbackModal(self.feedback_channel, self.bot, self.adm))

class FeedbackModal(ui.Modal, title="Send your feedback"):
    def __init__(self, feedback_channel, bot, adm):
        super().__init__()
        self.feedback_channel = feedback_channel
        self.bot = bot
        self.adm = adm
        
        self.score = ui.TextInput(
            label="Score (1/5)",
            placeholder="Ex: 5",
            min_length=1,
            max_length=1,
            style=discord.TextStyle.short
        )
        self.feedback_text = ui.TextInput(
            label="your Feedback",
            placeholder="Tell us your feedback...",
            style=discord.TextStyle.long,
            max_length=500
        )
        
        self.add_item(self.score)
        self.add_item(self.feedback_text)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not self.adm or not self.adm.mention:
            await interaction.followup.send("No one adm has open the ticket")
            return

        user_score = self.score.value
        user_feedback_text = self.feedback_text.value

        result = await send_embed(
            self.bot,
            interaction.guild_id,
            self.feedback_channel,
            title=f"Feedback from: {interaction.user.mention}",
            description=f"user: {interaction.user.mention} | adm: {self.adm.mention} \n feedback: {user_feedback_text} \n user score: {user_score}/5"
        )

        if not result:
            print(result)
            await interaction.followup.send("An error occurred while sending your feedback")
            return

        await interaction.followup.send("Thank you for your feedback")

class DynamicView(discord.ui.View):
    def __init__(self, embed_options, bot, color, welcome_message, mention_role, feedback_channel):
        super().__init__(timeout=None)
        self.add_item(DynamicSelect(embed_options, bot, color, welcome_message, mention_role, feedback_channel))


async def create_channel(
    bot,
    name: str,
    guild_id,
    adm_only: bool = False,
    ticket_owner: discord.Member | None = None
):
    if not bot:
        return False, "Bot not found"

    guild = bot.get_guild(int(guild_id))

    if not guild:
        return False, "Guild not found"

    try:
        overwrites = None

        if adm_only:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                )
            }

            if ticket_owner is not None:
                overwrites[ticket_owner] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )

            bot_member = guild.me

            if bot_member is not None:
                overwrites[bot_member] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True
                )

            for role in guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        manage_channels=True,
                        manage_messages=True
                    )

        new_channel = await guild.create_text_channel(
            name=name,
            overwrites=overwrites
        )

        return True, new_channel.id

    except Exception as e:
        return False, f"Failed to create channel: {str(e)}"

    
async def send_embed(
    bot,
    guild_id: str | int,
    channel_id: str | int,
    author: dict | None = None,
    title: str | None = None,
    url: str | None = None,
    color: str | int | None = None,
    description: str | None = None,
    image: dict | None = None,
    thumbnail: dict | None = None,
    footer: dict | None = None,
    options: list | None = None,
    mention_role: str | None = None,
    view_override: discord.ui.View | None = None,
    ticket_additionals: dict | None = None
):
    if not channel_id or not guild_id:
        return "Missing channel_id or guild_id"

    guild_id = int(guild_id)
    channel_id = int(channel_id)

    guild = bot.get_guild(guild_id)
    if not guild:
        try:
            guild = await bot.fetch_guild(guild_id)
        except Exception as e:
            return f"Bot is not in guild {guild_id} or guild not found"

    channel = guild.get_channel(channel_id)
    if not channel:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            return f"Channel {channel_id} not found"

    color_int = None
    if color:
        if isinstance(color, str):
            clean_hex = color.lstrip('#')
            if clean_hex:
                try:
                    color_int = int(clean_hex, 16)
                except ValueError:
                    color_int = 0x5865F2 
        elif isinstance(color, int):
            color_int = color

    embed = discord.Embed(
        title=title or None,
        url=url or None,
        color=color_int,
        description=description or None
    )

    if author and author.get("name"):
        embed.set_author(
            name=author.get("name"),
            url=author.get("url") or None,
            icon_url=author.get("icon_url") or None
        )

    if image and image.get("url"):
        embed.set_image(url=image.get("url"))

    if thumbnail and thumbnail.get("url"):
        embed.set_thumbnail(url=thumbnail.get("url"))

    if footer and footer.get("text"):
        embed.set_footer(
            text=footer.get("text"),
            icon_url=footer.get("icon_url") or None
        )
    
    view_component = None
    
    if view_override:
        view_component = view_override
    elif options:
        embed_options = []
        welcome_messages = {}
        
        for option in options:
            id = str(uuid.uuid4())
            welcome_messages[id] = option.get("welcome_message")
            
            embed_options.append(            
                discord.SelectOption(
                    label=option.get("title"),
                    description=option.get("description"), 
                    emoji=option.get("emoji"), 
                    value=id
                )
            )
        
        view_component = DynamicView(embed_options, bot, color, welcome_messages, mention_role, ticket_additionals.get("feedback_channel"))  

    try:
        await channel.send(embed=embed, view=view_component)
        return True
    except Exception as e:
        return f"Discord permission error or failure: {str(e)}"