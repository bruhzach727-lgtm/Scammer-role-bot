import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def scam(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="SCAMMER⚠️")

    if role is None:
        await ctx.send("I couldn't find a role named `SCAMMER⚠️`.")
        return

    if role >= ctx.guild.me.top_role:
        await ctx.send("I can't give this role because my bot role is not high enough.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"⚠️ {member.mention} has been given the **SCAMMER⚠️** role.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to give that role.")

@scam.error
async def scam_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need the **Manage Roles** permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!scam @member`")

bot.run(os.environ["DISCORD_TOKEN"])
