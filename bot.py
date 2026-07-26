import os
import discord
from discord import app_commands
from discord.ext import commands

# =========================
# SETTINGS
# =========================

SCAM_ROLE_NAME = "SCAMMER⚠️"
SCAM_VOUCH_CHANNEL_NAME = "scam-vouches"
VOUCHES_NEEDED = 3

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# target_user_id -> set of unique users who vouched
scam_vouches = {}


# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Slash command sync error: {e}")

    print(f"Logged in as {bot.user}")


# =========================
# /SCAM
# =========================

@bot.tree.command(name="scam", description="Give a member the SCAMMER role")
@app_commands.checks.has_permissions(manage_roles=True)
async def scam(interaction: discord.Interaction, member: discord.Member):

    role = discord.utils.get(
        interaction.guild.roles,
        name=SCAM_ROLE_NAME
    )

    if role is None:
        await interaction.response.send_message(
            f"I couldn't find the role `{SCAM_ROLE_NAME}`.",
            ephemeral=True
        )
        return

    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            "My bot role must be above the SCAMMER role.",
            ephemeral=True
        )
        return

    await member.add_roles(role)

    await interaction.response.send_message(
        f"⚠️ {member.mention} has been given the **{SCAM_ROLE_NAME}** role."
    )


# =========================
# /KICK
# =========================

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided"
):

    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 {member.mention} was kicked.\nReason: {reason}"
    )


# =========================
# /BAN
# =========================

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided"
):

    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 {member.mention} was banned.\nReason: {reason}"
    )


# =========================
# /TIMEOUT
# =========================

@bot.tree.command(name="timeout", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "No reason provided"
):

    if minutes < 1 or minutes > 40320:
        await interaction.response.send_message(
            "Timeout duration must be between 1 minute and 28 days.",
            ephemeral=True
        )
        return

    duration = discord.utils.utcnow() + discord.timedelta(
        minutes=minutes
    )

    await member.timeout(
        duration,
        reason=reason
    )

    await interaction.response.send_message(
        f"⏳ {member.mention} was timed out for {minutes} minutes.\nReason: {reason}"
    )


# =========================
# SCAM VOUCH SYSTEM
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.name != SCAM_VOUCH_CHANNEL_NAME:
        await bot.process_commands(message)
        return

    for target in message.mentions:

        # Don't allow someone to vouch for themselves
        if target.id == message.author.id:
            continue

        # Create a set for this target if needed
        if target.id not in scam_vouches:
            scam_vouches[target.id] = set()

        # Add the person who vouched
        scam_vouches[target.id].add(message.author.id)

        count = len(scam_vouches[target.id])

        await message.channel.send(
            f"⚠️ {target.mention} has **{count}/{VOUCHES_NEEDED} unique scam vouches**."
        )

        if count >= VOUCHES_NEEDED:

            role = discord.utils.get(
                message.guild.roles,
                name=SCAM_ROLE_NAME
            )

            if role is not None:
                await target.add_roles(role)

            timeout_until = discord.utils.utcnow() + discord.timedelta(
                days=7
            )

            await target.timeout(
                timeout_until,
                reason="Reached the scam vouch threshold"
            )

            await message.channel.send(
                f"🚨 {target.mention} reached **{VOUCHES_NEEDED} unique scam vouches** "
                f"and has been given **{SCAM_ROLE_NAME}** and timed out for **7 days**."
            )

    await bot.process_commands(message)


# =========================
# ERROR HANDLING
# =========================

@scam.error
async def scam_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )


# =========================
# START BOT
# =========================

bot.run(os.environ["DISCORD_TOKEN"])
