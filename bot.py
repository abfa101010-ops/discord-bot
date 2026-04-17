import discord
from discord.ext import commands
from discord import app_commands
import datetime

TOKEN = "MTQ5NDQ4NTY4MDM5Nzc1MDM4Nw.G4Fq60.D7P19O_3U3hr6CV5JHUeSLF_zPLmBMcW8tpcYM"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def parse_custom_time(time_str: str) -> int:
    seconds = 0
    parts = time_str.lower().split()
    for part in parts:
        if part.endswith('d'):
            seconds += int(part[:-1]) * 86400
        elif part.endswith('h'):
            seconds += int(part[:-1]) * 3600
        elif part.endswith('m'):
            seconds += int(part[:-1]) * 60
    return seconds

async def send_dm_notification(member: discord.Member, action: str, reason: str, moderator: str):
    embed = discord.Embed(title=f"❗ {action}", color=discord.Color.dark_red())
    embed.add_field(name="السبب", value=reason, inline=False)
    embed.add_field(name="بواسطة المشرف", value=moderator, inline=False)
    embed.set_footer(text=f"سيرفر: {member.guild.name}")
    try:
        await member.send(embed=embed)
    except:
        pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} شغال 24 ساعة.")

@bot.tree.command(name="ادخل", description="يدخل الروم ويبقى 24 ساعة")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ لازم تكون في روم صوتي.", ephemeral=True)
        return
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
    await channel.connect()
    await interaction.response.send_message(f"✅ دخلت **{channel.name}** وبقعد للأبد.")

@bot.tree.command(name="اخرج", description="يطلع من الروم")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 خرجت.")
    else:
        await interaction.response.send_message("❌ مو موجود بروم.", ephemeral=True)

@bot.tree.command(name="تايم", description="اسكات مع ارسال السبب بالخاص")
@app_commands.describe(عضو="الشخص", المدة="مثال: 10m او 1d 2h", السبب="سبب الاسكات")
async def timeout(interaction: discord.Interaction, عضو: discord.Member, المدة: str, السبب: str):
    await interaction.response.defer(thinking=True)
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.followup.send("❌ صلاحية غير كافية.")
        return
    try:
        seconds = parse_custom_time(المدة)
        if seconds <= 0 or seconds > 2419200:
            await interaction.followup.send("❌ المدة خطأ. اقصى شي 28 يوم.")
            return
    except:
        await interaction.followup.send("❌ صيغة المدة غير مفهومة.")
        return
    duration = datetime.timedelta(seconds=seconds)
    await عضو.timeout(duration, reason=f"بواسطة {interaction.user}: {السبب}")
    await send_dm_notification(عضو, "تم اسكاتك (Timeout)", السبب, str(interaction.user))
    await interaction.followup.send(f"🔇 {عضو.mention} تم اسكاته لمدة `{المدة}`. السبب ارسل له بالخاص.")

@bot.tree.command(name="كيك", description="طرد مع ارسال السبب بالخاص")
@app_commands.describe(عضو="الشخص", السبب="سبب الطرد")
async def kick(interaction: discord.Interaction, عضو: discord.Member, السبب: str):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ صلاحية غير كافية.", ephemeral=True)
        return
    await send_dm_notification(عضو, "تم طردك من السيرفر", السبب, str(interaction.user))
    await عضو.kick(reason=f"بواسطة {interaction.user}: {السبب}")
    await interaction.response.send_message(f"👢 {عضو.name} انطرد. السبب: {السبب}")

@bot.tree.command(name="بان", description="حظر مع ارسال السبب بالخاص")
@app_commands.describe(عضو="الشخص", السبب="سبب الحظر")
async def ban(interaction: discord.Interaction, عضو: discord.Member, السبب: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ صلاحية غير كافية.", ephemeral=True)
        return
    await send_dm_notification(عضو, "تم حظرك من السيرفر", السبب, str(interaction.user))
    await عضو.ban(reason=f"بواسطة {interaction.user}: {السبب}")
    await interaction.response.send_message(f"🔨 {عضو.name} انحظر. السبب: {السبب}")

bot.run(TOKEN)
