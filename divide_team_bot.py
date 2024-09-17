import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 存儲正在玩遊戲的玩家
players = set()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.event
async def on_guild_join(guild):
    """當機器人加入新的伺服器時，發送使用說明"""
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(get_help_message())
            break


def get_help_message():
    """返回幫助信息"""
    return """
    歡迎使用Team Divider Bot！以下是可用的命令：
    
    `!join` - 加入遊戲隊列
    `!leave` - 離開遊戲隊列
    `!divide` - 將玩家隨機分為兩隊
    `!list` - 列出當前在隊列中的所有玩家
    `!clear` - 清除所有在隊列中的玩家
    `!kick @用戶` - 將指定用戶踢出隊列
    `!bothelp` - 顯示此幫助信息
    
    開始使用吧！如果有任何問題，請隨時詢問管理員。
    """


@bot.command(name="join")
async def join(ctx):
    players.add(ctx.author)
    await ctx.send(f"{ctx.author.name} 已加入遊戲隊列!")


@bot.command(name="leave")
async def leave(ctx):
    if ctx.author in players:
        players.remove(ctx.author)
        await ctx.send(f"{ctx.author.name} 已離開遊戲隊列!")
    else:
        await ctx.send(f"{ctx.author.name} 不在遊戲隊列中!")


@bot.command(name="divide")
async def divide_teams(ctx):
    if len(players) < 2:
        await ctx.send("至少需要2名玩家才能分隊!")
        return

    player_list = list(players)
    random.shuffle(player_list)
    mid = len(player_list) // 2

    team1 = player_list[:mid]
    team2 = player_list[mid:]

    team1_names = ", ".join([player.name for player in team1])
    team2_names = ", ".join([player.name for player in team2])

    await ctx.send(f"隊伍1: {team1_names}\n隊伍2: {team2_names}")


@bot.command(name="list")
async def list_players(ctx):
    if not players:
        await ctx.send("目前沒有玩家在遊戲隊列中!")
    else:
        player_names = ", ".join([player.name for player in players])
        await ctx.send(f"當前在隊列中的玩家: {player_names}")


@bot.command(name="clear")
async def clear_queue(ctx):
    """清除所有在隊列中的玩家"""
    player_count = len(players)
    players.clear()
    await ctx.send(f"隊列已清空！共移除了 {player_count} 名玩家。")


@bot.command(name="kick")
async def kick_player(ctx, member: discord.Member):
    """將指定玩家踢出隊列"""
    if member in players:
        players.remove(member)
        await ctx.send(f"{member.name} 已被踢出遊戲隊列。")
    else:
        await ctx.send(f"{member.name} 不在遊戲隊列中。")


@kick_player.error
async def kick_player_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("你沒有權限使用此命令。只有管理員可以踢出玩家。")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("找不到指定的成員。請確保你提及了正確的用戶。")
    else:
        await ctx.send(f"發生錯誤：{str(error)}")


@bot.command(name="bothelp")
async def bothelp(ctx):
    """顯示幫助信息"""
    await ctx.send(get_help_message())


# 在這裡替換為您的機器人令牌
bot.run("YOUR_BOT_TOKEN")
