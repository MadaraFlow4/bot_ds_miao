import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput, Select
from discord import SelectOption

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = "MTQ3MTE2NjYwNDA2NTg5ODcyMA.GvGStL.UquXHFYmSDLTeJp86F0QQlUhgj9uXrphgPIJd8"
GUILD_ID = 1471135586965258437
CATEGORY_ID = 1471135588739715147
STAFF_ROLE_IDS = [1471135586965258443, 1471135586965258444]
LOG_CHANNEL_ID = 1471201833665167440
ROLE_MAIN_ID = 1471135586965258442 
ROLE_TEST_ID = 1471145283126820958   

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# ПРОВЕРКА РОЛИ
# =========================

def has_staff_role(member: discord.Member):
    return any(role.id in STAFF_ROLE_IDS for role in member.roles)

# =========================
# КНОПКИ УПРАВЛЕНИЯ
# =========================

class ApplicationControlView(View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=None)
        self.author = author

    async def no_access(self, interaction):
        await interaction.response.send_message("❌ Нет доступа.", ephemeral=True)

    async def log_action(self, guild, text):
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(description=text, color=discord.Color.green())
            await channel.send(embed=embed)

    @discord.ui.button(label="❌ Отклонить", style=discord.ButtonStyle.danger)
    async def reject(self, interaction, button):
        if interaction.user == self.author or not has_staff_role(interaction.user):
            return await self.no_access(interaction)

        await interaction.response.defer()

        await self.log_action(
            interaction.guild,
            f"❌ Заявка {self.author.mention} отклонена модератором {interaction.user.mention}"
        )

        try:
            await self.author.send("❌ Ваша заявка была отклонена.")
        except:
            pass

        await interaction.channel.delete()

    @discord.ui.button(label="⭐ Принять MAIN", style=discord.ButtonStyle.success)
    async def accept_main(self, interaction, button):
        if interaction.user == self.author or not has_staff_role(interaction.user):
            return await self.no_access(interaction)

        await interaction.response.defer()

        role = interaction.guild.get_role(ROLE_MAIN_ID)
        if role:
            await self.author.add_roles(role)

        await self.log_action(
            interaction.guild,
            f"⭐ {self.author.mention} принят в MAIN | Модератор: {interaction.user.mention}"
        )

        try:
            await self.author.send("⭐ Вы приняты в семью **Miao** на роль **MAIN**.")
        except:
            pass

        await interaction.channel.delete()

    @discord.ui.button(label="🌍 Принять TEST", style=discord.ButtonStyle.success)
    async def accept_test(self, interaction, button):
        if interaction.user == self.author or not has_staff_role(interaction.user):
            return await self.no_access(interaction)

        await interaction.response.defer()

        role = interaction.guild.get_role(ROLE_TEST_ID)
        if role:
            await self.author.add_roles(role)

        await self.log_action(
            interaction.guild,
            f"🌍 {self.author.mention} принят в TEST | Модератор: {interaction.user.mention}"
        )

        try:
            await self.author.send("🌍 Вы приняты в семью **Miao** на роль **TEST**.")
        except:
            pass

        await interaction.channel.delete()



# =========================
# МОДАЛКА
# =========================

class MiaoModal(Modal, title="Заявка в семью Miao"):

    nick = TextInput(
        label="Ник | Статик | Имя | Возраст",
        placeholder="Abdurahmed | 1488 | Аскар | 67"
    )

    screenshot = TextInput(
        label="Скриншот персонажей",
        placeholder="Ссылка на uapix / imgur"
    )

    goal = TextInput(
        label="Цель вступления",
        placeholder="Играть капты, мл, рп движуху"
    )

    history = TextInput(
        label="История семьи",
        style=discord.TextStyle.paragraph,
        placeholder="gussi allegri kolbasenko vex trur"
    )

    recoil = TextInput(
        label="Откат с гр (MAIN)",
        placeholder="Если TEST — поставьте '-'"
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        log_channel = guild.get_channel(LOG_CHANNEL_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        for role_id in STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True)

        channel = await guild.create_text_channel(
            name=f"заявка-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="📨 Новая заявка в семью Miao",
            color=discord.Color.red()
        )

        embed.add_field(name="👤 Игрок", value=interaction.user.mention, inline=False)
        embed.add_field(name="Ник | Статик | Имя | Возраст", value=self.nick.value, inline=False)
        embed.add_field(name="Скриншот персонажей", value=self.screenshot.value, inline=False)
        embed.add_field(name="Цель вступления", value=self.goal.value, inline=False)
        embed.add_field(name="История семьи", value=self.history.value, inline=False)
        embed.add_field(name="Откат с гр (MAIN)", value=self.recoil.value, inline=False)

        await channel.send(embed=embed, view=ApplicationControlView(interaction.user))

        # ЛОГ
        if log_channel:
            log_embed = discord.Embed(
                title="📝 Подана новая заявка",
                color=discord.Color.orange()
            )
            log_embed.add_field(name="Игрок", value=interaction.user.mention)
            log_embed.add_field(name="Канал", value=channel.mention)
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message(
            f"✅ Ваша заявка создана: {channel.mention}",
            ephemeral=True
        )

# =========================
# VIEW СОЗДАНИЯ ЗАЯВКИ
# =========================

class CreateApplicationView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(CreateApplicationSelect())


class CreateApplicationSelect(Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Создать заявку",
                description="Создать заявку на вступление в семью",
                emoji="📨",
                value="create_application"
            )
        ]

        super().__init__(
            placeholder="Выберите действие...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "create_application":
            await interaction.response.send_modal(MiaoModal())

# =========================
# SLASH-КОМАНДА /заявка
# =========================

@bot.tree.command(name="заявка", description="Создать заявку в семью Miao")
async def zayavka(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🐉 Заявки в семью Miao",
        description=(
            "**На роль TEST** — откат не требуется, поле с откатом стрельбы пропускаете.\n"
            "**На роль MAIN** — требуется **2 полных отката** с арены **15 / 16 / 17 серверов** "
            "(тяжка + сайга), а также откаты с МП: **КАПТ, MCL**."
        ),
        color=discord.Color.from_rgb(180, 0, 60)
    )

    embed.add_field(
        name="🔥 Ты нам подходишь, если:",
        value=(
            "✔ Активный игрок, стремящийся к прогрессу и развитию\n"
            "✔ Готов влиться в движения фамы и вкладываться в общее развитие\n"
            "✔ Имеешь базовые знания игры\n"
            "✔ Готов отстаивать честь семьи"
        ),
        inline=False
    )

    embed.add_field(
        name="📨 Как вступить в семью Miao",
        value=(
            "Для вступления необходимо **подать заявку**, нажав кнопку ниже.\n\n"
            "⚠ При оформлении заявки **ответственно отнеситесь к опроснику** —\n"
            "подробно отвечайте на **все заданные вопросы**."
        ),
        inline=False
    )

    embed.add_field(
        name="📌 Требования",
        value=(
            "🔹 **Возраст:** 15+\n"
            "🔹 **Активность и адекватность**\n"
            "🔹 **Скриншот персонажей при входе** (обязательно)\n"
            "🔹 **Среднее понимание игры и выше**\n"
            "🔹 **Готовность пройти обзвон**"
        ),
        inline=False
    )

    embed.set_footer(text="Семья Miao • Отбор строго по требованиям")

    await interaction.response.send_message(
        embed=embed,
        view=CreateApplicationView()
    )

# =========================
# SYNC КОМАНД
# =========================

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print("Slash-команды синхронизированы")
    except Exception as e:
        print(e)

    print(f"Бот запущен как {bot.user}")

bot.run(TOKEN)
