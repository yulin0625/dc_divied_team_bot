import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import random

# 載入 .env 檔案
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class TeamDividerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.players = set()

    async def setup_hook(self):
        await self.tree.sync()
        print(f"已同步斜線命令 for {self.user}")


bot = TeamDividerBot()


@bot.event
async def on_ready():
    print(f"{bot.user} 已連接到 Discord!")
    await bot.change_presence(activity=discord.Game(name="分隊遊戲"))


@bot.tree.command(name="start", description="開始分隊遊戲")
async def start_game(interaction: discord.Interaction):
    await send_response_with_buttons(interaction, "歡迎使用分隊機器人！請選擇以下操作：")


def get_player_list_and_count_message():
    player_count = len(bot.players)
    if not bot.players:
        return f"目前沒有玩家在遊戲隊列中。\n\n當前隊伍人數：0"
    else:
        player_names = ", ".join([player.name for player in bot.players])
        return f"當前在隊列中的玩家: {player_names}\n\n當前隊伍人數：{player_count}"


async def send_response_with_buttons(interaction: discord.Interaction, content=None):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="加入隊列", style=discord.ButtonStyle.green, custom_id="join"))
    view.add_item(discord.ui.Button(label="離開隊列", style=discord.ButtonStyle.red, custom_id="leave"))
    view.add_item(discord.ui.Button(label="分隊", style=discord.ButtonStyle.blurple, custom_id="divide"))
    view.add_item(discord.ui.Button(label="清空隊列", style=discord.ButtonStyle.danger, custom_id="clear"))
    view.add_item(discord.ui.Button(label="幫助", style=discord.ButtonStyle.secondary, custom_id="help"))

    player_info = get_player_list_and_count_message()
    full_content = f"{content}\n\n{player_info}" if content else player_info
    await interaction.response.send_message(content=full_content, view=view)


async def update_message_with_buttons(interaction: discord.Interaction, content=None):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="加入隊列", style=discord.ButtonStyle.green, custom_id="join"))
    view.add_item(discord.ui.Button(label="離開隊列", style=discord.ButtonStyle.red, custom_id="leave"))
    view.add_item(discord.ui.Button(label="分隊", style=discord.ButtonStyle.blurple, custom_id="divide"))
    view.add_item(discord.ui.Button(label="清空隊列", style=discord.ButtonStyle.danger, custom_id="clear"))
    view.add_item(discord.ui.Button(label="幫助", style=discord.ButtonStyle.secondary, custom_id="help"))

    player_info = get_player_list_and_count_message()
    full_content = f"{content}\n\n{player_info}" if content else player_info
    await interaction.response.edit_message(content=full_content, view=view)


async def handle_button_interaction(interaction: discord.Interaction):
    custom_id = interaction.data["custom_id"]
    if custom_id == "join":
        bot.players.add(interaction.user)
        await update_message_with_buttons(interaction, f"{interaction.user.name} 已加入遊戲隊列!")
    elif custom_id == "leave":
        if interaction.user in bot.players:
            bot.players.remove(interaction.user)
            await update_message_with_buttons(interaction, f"{interaction.user.name} 已離開遊戲隊列!")
        else:
            await update_message_with_buttons(interaction, f"{interaction.user.name} 不在遊戲隊列中!")
    elif custom_id == "divide":
        if len(bot.players) < 2:
            await update_message_with_buttons(interaction, "至少需要2名玩家才能分隊!")
            return

        player_list = list(bot.players)
        random.shuffle(player_list)
        mid = len(player_list) // 2

        team1 = player_list[:mid]
        team2 = player_list[mid:]

        team1_names = ", ".join([player.name for player in team1])
        team2_names = ", ".join([player.name for player in team2])

        result = f"隊伍1 ({len(team1)}人): {team1_names}\n隊伍2 ({len(team2)}人): {team2_names}"
        await update_message_with_buttons(interaction, result)
    elif custom_id == "clear":
        player_count = len(bot.players)
        bot.players.clear()
        await update_message_with_buttons(interaction, f"隊列已清空！共移除了 {player_count} 名玩家。")
    elif custom_id == "help":
        await send_help_message(interaction)


async def send_help_message(interaction: discord.Interaction):
    help_content = """
Team Divider Bot 使用說明:
• 加入隊列：將你加入到遊戲隊列中
• 離開隊列：將你從遊戲隊列中移除
• 分隊：將當前隊列中的玩家隨機分為兩隊
• 清空隊列：清除所有在隊列中的玩家
• 幫助：顯示此使用說明

如有任何問題，請聯繫伺服器管理員。
    """
    admin_id = os.getenv("ADMIN_ID")
    help_content += f"\n如需幫助，請聯繫管理員：<@{admin_id}>"

    await update_message_with_buttons(interaction, help_content)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        await handle_button_interaction(interaction)


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


# 從環境變量中獲取機器人令牌
bot_token = os.getenv("DISCORD_BOT_TOKEN")
bot.run(bot_token)
