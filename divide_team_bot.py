import discord
from discord import app_commands
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class TeamDividerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.players = set()

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")


bot = TeamDividerBot()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="分隊遊戲"))


@bot.tree.command(name="join", description="加入遊戲隊列")
async def join(interaction: discord.Interaction):
    bot.players.add(interaction.user)
    await interaction.response.send_message(f"{interaction.user.name} 已加入遊戲隊列!", ephemeral=True)


@bot.tree.command(name="leave", description="離開遊戲隊列")
async def leave(interaction: discord.Interaction):
    if interaction.user in bot.players:
        bot.players.remove(interaction.user)
        await interaction.response.send_message(f"{interaction.user.name} 已離開遊戲隊列!", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.name} 不在遊戲隊列中!", ephemeral=True)


@bot.tree.command(name="divide", description="將玩家隨機分為兩隊")
async def divide_teams(interaction: discord.Interaction):
    if len(bot.players) < 2:
        await interaction.response.send_message("至少需要2名玩家才能分隊!", ephemeral=True)
        return

    player_list = list(bot.players)
    random.shuffle(player_list)
    mid = len(player_list) // 2

    team1 = player_list[:mid]
    team2 = player_list[mid:]

    team1_names = ", ".join([player.name for player in team1])
    team2_names = ", ".join([player.name for player in team2])

    await interaction.response.send_message(f"隊伍1: {team1_names}\n隊伍2: {team2_names}")


@bot.tree.command(name="list", description="列出當前在隊列中的所有玩家")
async def list_players(interaction: discord.Interaction):
    if not bot.players:
        await interaction.response.send_message("目前沒有玩家在遊戲隊列中!", ephemeral=True)
    else:
        player_names = ", ".join([player.name for player in bot.players])
        await interaction.response.send_message(f"當前在隊列中的玩家: {player_names}", ephemeral=True)


@bot.tree.command(name="clear", description="清除所有在隊列中的玩家")
async def clear_queue(interaction: discord.Interaction):
    player_count = len(bot.players)
    bot.players.clear()
    await interaction.response.send_message(f"隊列已清空！共移除了 {player_count} 名玩家。")


@bot.tree.command(name="kick", description="將指定玩家踢出隊列")
async def kick_player(interaction: discord.Interaction, member: discord.Member):
    if member in bot.players:
        bot.players.remove(member)
        await interaction.response.send_message(f"{member.name} 已被踢出遊戲隊列。")
    else:
        await interaction.response.send_message(f"{member.name} 不在遊戲隊列中。", ephemeral=True)


@bot.tree.command(name="help", description="顯示機器人的使用說明")
async def help_command(interaction: discord.Interaction):
    help_embed = discord.Embed(title="小馬哥分隊機器人 使用說明", color=discord.Color.blue())
    help_embed.add_field(name="/join", value="加入遊戲隊列", inline=False)
    help_embed.add_field(name="/leave", value="離開遊戲隊列", inline=False)
    help_embed.add_field(name="/divide", value="將玩家隨機分為兩隊", inline=False)
    help_embed.add_field(name="/list", value="列出當前在隊列中的所有玩家", inline=False)
    help_embed.add_field(name="/clear", value="清除所有在隊列中的玩家", inline=False)
    help_embed.add_field(name="/kick @用戶", value="將指定玩家踢出隊列", inline=False)
    help_embed.add_field(name="/help", value="顯示此使用說明", inline=False)

    # 替換 YOUR_DISCORD_USER_ID 為您的實際 Discord 用戶 ID
    admin_id = "620961564824043530"
    help_embed.set_footer(
        text=f"如有任何問題，請聯繫伺服器管理員。點擊這裡聯繫管理員",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty,
    )
    help_embed.description = f"如需幫助，請聯繫管理員：<@{admin_id}>"

    await interaction.response.send_message(embed=help_embed, ephemeral=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"請稍後再試。冷卻時間還剩 {error.retry_after:.2f} 秒。", ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("你沒有權限使用此命令。", ephemeral=True)
    else:
        await interaction.response.send_message(f"發生錯誤：{str(error)}", ephemeral=True)


# 在這裡替換為您的機器人令牌
bot.run("YOUR_BOT_TOKEN")
