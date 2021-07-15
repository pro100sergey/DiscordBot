import datetime
import os
import discord
import asyncio
import time
import datetime

import requests
import json
import PIL
from PIL import Image , ImageFont, ImageDraw


from random import randint
from time import sleep
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from itertools import cycle
from datetime import timedelta


TOKEN = ""
Bot = commands.Bot(command_prefix= '!')
Bot.remove_command('help')
extra_count = 0
log_id = 0
class Messages:

    def __init__(self, Bot):
        self.Bot = Bot

    async def number_messages(self, member):
        n_messages = 0
        for guild in self.Bot.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit = None):
                        if message.author == member:
                            n_messages += 1
                except (discord.Forbidden, discord.HTTPException):
                    continue
        return n_messages

# Быстрая сортировка по цене предмета
# Quick sort by price
def quicksort(array):
    if len(array) < 2:
        return array
    else:
        pivot = array[0]
        less = [i for i in array[1:] if int(i[0].replace(',','')) <= int(array[0][0].replace(',', ''))]

        greater = [i for i in array[1:] if int(i[0].replace(',','')) > int(array[0][0].replace(',', ''))]

        return quicksort(greater) + [pivot] + quicksort(less) 

# Основаная функция, возвращает готовое изображение
# returns ready image  
  
def get_shop():
    url = 'https://fnbr.co/api/shop'

    r = requests.get(
        url,
        headers=  {
        
        }
    )
    r = json.loads(r.text)
    #print(r)
    items_amount = len(r['data']['featured']) + len(r['data']['daily'])
    ls = []
    for i in range(items_amount):
        ls.append([])
    #print(ls)
    i = 0
    for item in r['data']['featured']:
        if item['images']['featured'] == False:
            #print( item['images']['icon'] )
            ls[i].append(item['price'])
            ls[i].append(item['images']['icon'])
            ls[i].append(item['rarity'])
            ls[i].append(item['type'])
            i += 1
        else:
            #print(item['images']['featured'])
            ls[i].append(item['price'])
            ls[i].append(item['images']['featured'])
            ls[i].append(item['rarity'])
            ls[i].append(item['type'])
            i += 1
    #print('-------------------------------------------------------')
    for item in r['data']['daily']:
        if item['images']['featured'] == False:
            #print( item['images']['icon'])
            ls[i].append(item['price'])
            ls[i].append(item['images']['icon'])
            ls[i].append(item['rarity'])
            ls[i].append(item['type'])
            i += 1
        else:
            #print( item['images']['featured'])
            ls[i].append(item['price'])
            ls[i].append(item['images']['featured'])
            ls[i].append(item['rarity'])
            ls[i].append(item['type'])
            i += 1
    ls = quicksort(ls)
    #print(ls)

    # Ассоциации редкости предметов с фонами и рамками
    associate = {
        'epic' : ['images for transform/epic.png', 'images for transform/borders/epic.png'],
        'uncommon' : ['images for transform/uncommon.png', 'images for transform/borders/uncommon.png'],
        'rare' : ['images for transform/rare.png', 'images for transform/borders/rare.png'],
        'legendary' : ['images for transform/legendary.png', 'images for transform/borders/legendary.png'],
        'dark_series' : ['images for transform/dark_series.png', 'images for transform/borders/dark_series.png'],
        'common' : ['images for transform/black.png', 'images for transform/borders/block.png'],
        'dc' : ['images for transform/dc.png', 'images for transform/borders/dc.png'],
        'frozen_series' : ['images for transform/frozen_series.png', 'images for transform/borders/frozen_series.png'],
        'icon_series' : ['images for transform/icon_series.png', 'images for transform/borders/icon_series.png'],
        'lava_series' : ['images for transform/lava_series.png', 'images for transform/borders/lava_series.png'],
        'marvel' : ['images for transform/marvel.png', 'images for transform/borders/marvel.png'],
        'shadow_series' : ['images for transform/black.png', 'images for transform/borders/black.png'],
        'star_wars_series' : ['images for transform/white.png', 'images for transform/borders/white.png'],
        'defaults' : ['images for transform/defaults.png', 'images for transform/borders/black.png']
    }


    if len(ls) % 4 == 0:
        black_height = (len(ls) // 4) * 250 +  ((len(ls) // 4) - 1 ) * 8
    else:
        black_height = ( (len(ls) // 4 ) + 1 ) * 250 + ( ( len(ls) // 4 ) * 8 )

    black_fon = width , height = 1024 , black_height
    price_block = Image.open('images for transform/price_block.png')


    im_black = Image.new( "RGB", black_fon, "black")

    row = 0
    column = 0

    for item in ls:
        if item[2] not in associate:
            item[2] = 'defaults'
            print('Была получена новая редкость, нужно добавить её в словарь associate')

        image = Image.open(requests.get(item[1], stream=True).raw)
        (width, height) = image.size
        if (int(width) > 512 or int(height) > 512) and ( item[3] !='emote' ):
            area = (int(width*0.15625) , 0 , int(width*0.84375), int(height*0.6875) )
            image = image.crop(area)

        print(item[1])
        size_2 = width , height = 250 , 250
        image = image.resize(size_2).convert('RGBA')
        background = Image.open( associate[item[2]][0] )
        background.paste(image, (0,0), image)
        border = Image.open( associate[ item[2] ][1] )
        background.paste( border, (0,0), border  )
        background.paste( price_block, (0,0), price_block)
        font = ImageFont.truetype(font="fonts\Lato-Bold.ttf", size=30)
        draw = ImageDraw.Draw(background)
        (width, height) = background.size
        draw.text(xy=(108,203), text = f'{item[0]}', fill=(255,255,255), font= font)
        area = ( (column * 250 +  column*8), ( row * 250  + row * 8 ), ( 250 + column * 250 +  column*8 ), (row * 250 +  row * 8 + 250)  )
        im_black.paste(background, area)
        if column == 3:
            column = 0
            row += 1
        else:
            column += 1
    now = datetime.datetime.utcnow()
    im_black.save( 'shop images' +f"\{now.year}" + f".{now.month}" + f".{now.day}"    +'.png')
    del ls, now , area , draw, background , border , font , size_2, image
    return im_black


@Bot.event
async def on_ready():
    global extra_count
    global log_id
    guild = Bot.guilds[0]
    async for entry in guild.audit_logs(action= discord.AuditLogAction.message_delete,limit=1):
        log_id = entry.id
        extra_count = entry.extra.count
    online.start()
    unban.start()
    shop.start()
    print('Online: {0.user}'.format(Bot))
    await Bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name='Принимаю жалобы'))

# Привет !
@Bot.command()
async def hello(ctx):
	await ctx.send('Hello')

# Пресечение обхода мута через перезаход на сервер   
@Bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=f"{member.id}")
    if not channel:
        return
    else:
        role = discord.utils.get(member.guild.roles, name="mute")
        await  member.add_roles(role)

# Команда помощи
@Bot.command()
async def help(ctx):
    desc = "Help"
    help_menu= discord.Embed( description= desc, colour= 0xFF8000)
    help_menu.add_field(name= "`!ban @user`", value="банит ползователя", inline=False)
    help_menu.add_field(name= "`!unban @user`", value="разбан бользователя", inline=False)
    help_menu.add_field(name= "`!kick @user`", value="кик участника", inline=False)
    help_menu.add_field(name= "`!p (!play) ссылка или название`", value="проигрывать музыку", inline=False)
    help_menu.add_field(name= "`!seek секунд`", value="перемотка на n секунд", inline=False)
    help_menu.add_field(name= "`!skip`", value="следующий трек", inline=False)
    help_menu.add_field(name= "`!stop`", value="прекращение воспроизведения музыки(не пауза)", inline=False)
    help_menu.add_field(name= "`!now (!np) (!n)`", value="что сейчас играет", inline=False)
    help_menu.add_field(name= "`!queue (!q) номер страницы`", value="отображает очередь воспроизведения", inline=False)
    help_menu.add_field(name= "`!pause (!resume)`", value="поставить на паузу / возобновить ", inline=False)
    help_menu.add_field(name= "`!volume 0-1000`", value="Настройка громкости", inline=False)
    help_menu.add_field(name= "`!shuffle`", value="перемешать плейлист", inline=False)
    help_menu.add_field(name= "`!repeat`", value="повтор текущего трека", inline=False)
    help_menu.add_field(name= "`!remove номер`", value="убирает из очереди под опредлённым номером", inline=False)
    help_menu.add_field(name= "`!find`", value="отображает первые 10 видео по запросу", inline=False)
    help_menu.add_field(name= "`!disconnet (!ds)`", value="бот покидает голосовой канал", inline=False)
    help_menu.add_field(name= "`!random число1 число2`", value="рандомное число в указанном диапазоне", inline=False)
    help_menu.add_field(name= "`!avatar @user`", value="аватар пользователя", inline=False)
    help_menu.add_field(name= "`!msg @user`", value="количество сообщений пользователя на сервере", inline=False)
    help_menu.add_field(name= "`!secret название(без пробелов) @user`", value="создаёт секретный канал", inline=False)
    help_menu.add_field(name= "`!clear кол-во сообщений`", value="удаляет сообщения", inline=False)
    help_menu.add_field(name= "`!say #канал сообщение`", value="отправить сообщение от имени бота", inline=False)
    
    await ctx.message.delete()

    await ctx.author.send(embed = help_menu)

# Логи: удалённые сообщения
@Bot.event
async def on_raw_message_delete(payload):
    global log_id
    global extra_count
    guild = Bot.get_guild(payload.guild_id)
    async for entry in guild.audit_logs(action= discord.AuditLogAction.message_delete,limit=1):
        print('action: {0.action} user: {0.user}\n id: {0.id}\n target: {0.target}\n reason: {0.reason}\n extra {0.extra}\n category {0.category}\n changes: {0.changes}'.format(entry))
    async for entry in guild.audit_logs(action= discord.AuditLogAction.message_delete):
        print('action: {0.user} deleted message of {0.target}'.format(entry))
        
        if (log_id == entry.id) and (extra_count == entry.extra.count):
            if not payload.cached_message:
                return
            else:
                for item in guild.channels:
                    if item.name.startswith('logs'):
                        channel_log = item
                        break
                message = payload.cached_message
                emb = discord.Embed(title= "`Сообщения было удалено`", colour=0xe74c3c)
                emb.add_field(name= "Удалённое сообщение: ", value= f"{message.content}" or "`[Контекст отсутствует]`", inline= False)
                emb.add_field(name= "Автор сообщения: ", value= f"{message.author.mention}", inline= False)
                emb.add_field(name= "Сообщение удалил: ", value= f"{message.author.mention}", inline=False)
                emb.add_field(name= "В канале: ", value= f"{message.channel.mention}")
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text= f"ID сообщения: {message.id} "[:65])
                await channel_log.send(embed=emb)
                return
        else:
            v
            print(time)  
        user_deliting = entry.user
        if user_deliting == Bot.user:
            return
        
        user_name = str(entry.target)
        break

     
    if not payload.cached_message:
        content = "Нет в кэше" 
    else:
        message = payload.cached_message
        content = message.content
    author = guild.get_member_named(user_name)     
    channel = Bot.get_channel(payload.channel_id)
    for item in guild.channels:
        if item.name.startswith('logs'):
            channel_log = item
            break
    emb = discord.Embed(title= "`Сообщения было удалено`", colour=0xe74c3c)
    emb.add_field(name= "Удалённое сообщение: ", value= f"{content}" or "`[Контекст отсутствует]`", inline= False)
    emb.add_field(name= "Автор сообщения: ", value= f"{author.mention}", inline= False)
    emb.add_field(name= "Сообщение удалил: ", value= f"{user_deliting.mention}", inline=False)
    emb.add_field(name= "В канале: ", value= f"{channel.mention}")
    emb.timestamp = datetime.datetime.utcnow()
    emb.set_footer(text= f"ID сообщения: {payload.message_id} "[:65])
    await channel_log.send(embed=emb)



# Создание канлов Logs и Онлайн при подключении к серверу             
@Bot.event
async def on_guild_join(guild):
    overwrites_1 = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False ),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    overwrites_2 = {
        guild.default_role: discord.PermissionOverwrite(connect=False, speak =False),
    	guild.me: discord.PermissionOverwrite(connect=True, speak = True)
    }
    await guild.create_text_channel('Logs', overwrites=overwrites_1, position= 1)
    await guild.create_voice_channel('Онлайн', overwrites=overwrites_2, position = 0)

# При создании канала делает так, чтобы роль mute не могла читать и присоединяться к этому каналу
@Bot.event
async def on_guild_channel_create(channel):
    role = discord.utils.get(channel.guild.roles, name='mute')
    if not role:
        guild = channel.guild
        await guild.create_role(name='mute')
        role = discord.utils.get(channel.guild.roles, name='mute')
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.connect=False
    overwrite.speak = False
    await channel.set_permissions(role, overwrite=overwrite)
    



# Бан
@Bot.command(pass_context= True)
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, reason= None):
    await ctx.guild.ban(user)
    emb = discord.Embed(title= "**Участник {}, был забанен.**".format(user), colour= 0xb0fe0a)
    await ctx.message.channel.send(embed= emb)


# Разбан
@Bot.command(pass_context= True)
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, reason= None):
    await ctx.guild.unban(user)
    emb = discord.Embed(title= "**Участник {}, был раззабанен.**".format(user), colour= 0xb0fe0a)
    await ctx.message.channel.send(embed= emb)

# Кик    
@Bot.command(pass_context= True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.User, reason= None):
    await ctx.guild.kick(user)
    emb = discord.Embed(title= "**Участник __{}__, был кикнут.**".format(user), colour= 0x3600ff)
    await ctx.message.channel.send(embed= emb)

# Удаление сообщений
@Bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amount: str):
    await ctx.channel.purge(limit=int(amount))

# Мут
@Bot.command()
async def msg(ctx, member: discord.Member = None):
    if (member == None):
        number = await Messages(Bot).number_messages(ctx.author)
        us = ctx.author
    else:
        number = await Messages(Bot).number_messages(member)
        us = member 
    embed = discord.Embed(description = f"Количество сообщений на сервере от **{us.mention}** — **{number}**!")
    await ctx.send(embed = embed)

# Разбут
@Bot.command()
async def unmute(ctx, member : discord.Member = None):
    if not member:
        await ctx.send("Укажите пользователя!")
        return
    else:
        unmute_cnt = f"Пользователь {member.mention} был размучен {ctx.author.mention}"
        unmute = discord.Embed(title= "UnMute", description= unmute_cnt, colour= 0x000000)
        role = discord.utils.get(ctx.message.guild.roles, name="mute")
        mute_channel = discord.utils.get(member.guild.channels, name=f"вам-выдан-мут{member.id}")
        await mute_channel.delete()
        await member.remove_roles(role)
        print(f'Пользователь был размучен {member.name}')
        await ctx.send(embed= unmute)

# Мут
@Bot.command()
@commands.has_permissions(administrator = True)
async def mute(ctx, member:discord.Member, time=0, reason='none'):
    role = discord.utils.get(ctx.message.guild.roles, name="mute")
    if not role:
        ctx.guild.create_role('mute')
        role = discord.utils.get(ctx.message.guild.roles, name="mute")
    guild = ctx.guild
    if not time:
        await ctx.send("Укажите время мута")
        return
    if not reason:
        await ctx.send("Укажите причину мута")
        return
    if not member:
        await ctx.send("Укажите пользователя!")
        return
    else:
        mute_cnt = f"Пользователь {member.mention} был замучен {ctx.author.mention} на {time} часов(-а) "
        mute = discord.Embed(title= "Mute", description= mute_cnt, colour= 0x000000)
        await ctx.send(embed= mute)
        print(role.id)
        await member.add_roles(role)
        print(f'Пользователь был замучен {member.name}')
        category = discord.utils.get(guild.categories, name='muted-users')
        if not category:
            await guild.create_category('muted-users')
            category = discord.utils.get(guild.categories, name='muted-users')
        overwrites_m = {
            member.guild.default_role: discord.PermissionOverwrite(read_messages=False ),
            member.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        
        await category.create_text_channel(f'вам-выдан-мут{member.id}', overwrites=overwrites_m)

        role = discord.utils.get(member.guild.roles, name='mute')
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        
        channel_for_mute = discord.utils.get(guild.text_channels, name=f'вам-выдан-мут{member.id}')
        await channel_for_mute.set_permissions(member, overwrite=overwrite)
        
        emb = discord.Embed(title=f'Вам запрещено отправлять сообщения в чаты:', description= '', color=member.color)
        emb.set_author(name = f'{member.name}', icon_url=f'{member.avatar_url}')
        emb.add_field(name= "Причина ", value = f"{reason}", inline= True)
        emb.add_field(name= "срок ",value = f'{time} час(-а)', inline= True)
        emb.add_field(name= "мут выдал ",value = f'{ctx.message.author.mention}', inline= False)

        emb.set_footer(text= f'Ограничение будет снято')
        emb.timestamp = datetime.datetime.utcnow() + timedelta(seconds=time)
        await channel_for_mute.send(embed=emb)       
    # Добавление запрета на отправку сообщений во все каналы
    for c in guild.channels:
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.connect=False
        overwrite.speak = False
        await c.set_permissions(role, overwrite=overwrite)
    await asyncio.sleep(time*3600)
    await member.remove_roles(role)
    await channel_for_mute.delete()

# Возвращает аватар пользователя
@Bot.command()
async def avatar(ctx, member : discord.Member = None):   
    if member == None:
        member = ctx.message.author
    await ctx.message.delete()
    embed = discord.Embed(title=f'Аватар пользователя {member.name}', description= f'[Ссылка на изображение]({member.avatar_url})', color=member.color)
    embed.set_footer(text= f'Вызвано: {ctx.message.author}', icon_url= str(ctx.message.author.avatar_url))
    embed.set_image(url=member.avatar_url)
    embed.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=embed)

# Рандомное число в указанном диапазоне
@Bot.command()
async def random(ctx, numb_1 :int, numb_2 :int):
    await ctx.send(str(randint(numb_1,numb_2)))

# Отправка сообщения от имени бота
@Bot.command()
@commands.has_permissions(administrator= True)
async def say(ctx, channel : discord.TextChannel, *args):
    await ctx.message.delete()
    if not channel:
        await ctx.send('Введите канал, в который вы хотите отправить сообщение')
        return
    if not args:
        await ctx.send('Необходимо ввести текст сообщения')
    text = ''
    for item in args:
        text = text + item + ' '
    await channel.send(text)

# Создание секретного канала нужно указать имя человека и только для вас 2 будет создан канал
# Create secret channel
@Bot.command()
@commands.has_permissions(administrator= True)
async def secret(ctx, name : str, member : discord.Member):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False ),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        member: discord.PermissionOverwrite(read_messages = True)
    }

    await guild.create_text_channel(f'{name}',overwrites=overwrites, position= 1)

# Сколько пользователей онлайн

@tasks.loop(seconds=3)
async def online():
    for item_1 in Bot.guilds:
        online_users = 0
        channel = item_1.voice_channels[0]
        for item in item_1.voice_channels:
            if item.name.startswith('Онлайн'):
                channel = item
                break

        for item in item_1.members:
            if str(item.status) != "offline":
                online_users += 1
        online_users = f"Онлайн: {online_users}"
        await channel.edit(name = online_users)




months = ['января','февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'февраля']
# Отправка магазина в канал shop
@tasks.loop(seconds=60)
async def shop():
    now = datetime.datetime.now()
    if (now.hour == 21) and (now.minute == 38):
        print('Отправка магазина...')
        for item in Bot.guilds:
            channel = discord.utils.get(item.text_channels, name= "shop")
            if not channel:
                await item.create_text_channel('shop')
                channel = discord.utils.get(item.text_channels, name= "shop")
            get_shop()
            shop_path = 'shop images' +f"\{now.year}" + f".{now.month}" + f".{now.day}"    +'.png'
            file = discord.File(shop_path, filename="shop.png")
            embed = discord.Embed( title=f'Магазин на {now.day} {months[now.month]}', color=0x06d9ff)
            embed.set_image( url="attachment://shop.png")
            await channel.purge(limit=2)
            await channel.send(file=file, embed=embed)

@tasks.loop(seconds=1800)
async def unban():
    now = datetime.datetime.utcnow()
    for item in Bot.guilds:
        guild = item
        category = discord.utils.get(item.categories, name= "muted-users")
        for some in category.channels:
            channel = some
            if 'вам-выдан-мут' not in some.name:
                continue
            member_id = some.name.replace('вам-выдан-мут', '')
            banned_member = guild.get_member(int(member_id))
            if not banned_member:
                continue
            role = discord.utils.get(guild.roles, name= 'mute')
            async for message in some.history(limit=1, oldest_first= True):
                date = message.created_at
                for i in message.embeds:
                    ban_time = int(i.fields[1].value.replace(' час(-а)', ''))
                    ban_time = date + timedelta(hours=ban_time)

                    if ban_time < now:
                        await banned_member.remove_roles(role)
                        print(f'Был разбанен {banned_member}')
                        await channel.delete()




# Подключение когов (музыки)
'''
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        Bot.load_extension(f'cogs.{filename[:-3]}')
'''

Bot.run(TOKEN)