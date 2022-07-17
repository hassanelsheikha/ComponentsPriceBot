import time

import apscheduler.schedulers.blocking
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands, tasks

from store import BestBuy

from dotenv import load_dotenv
import os

import schedule, time

load_dotenv()

client = commands.Bot(command_prefix='.')

AWAY = False

MAILING_LIST = {}

@client.event
async def on_ready():
    print('Bot is running.')
    scheduler.start()
    print('all done')


async def away_message(ctx):
    await ctx.send('I am currently undergoing maintenance. Please try again later. ')

@client.command()
async def price(ctx, *, name):
    global AWAY
    if AWAY:
        await away_message(ctx)
        return
    price = BestBuy.item_price(name)
    discount = BestBuy.item_discount(name)
    url = BestBuy.item_link(name)
    if price is not None:
        if discount != 0.0:
            await ctx.send(f'The price of {BestBuy.actual_name(name)} at BestBuy is $~~{price + discount}~~ $**{price}**. See {url}')
        else:
            await ctx.send(f'The price of {BestBuy.actual_name(name)} at BestBuy is $**{price}**. See {url}')
    else:
        await ctx.send(f'{name} is not sold at BestBuy')


@client.command()
async def instock(ctx, *, name):
    global AWAY
    if AWAY:
        await away_message(ctx)
        return
    stock = BestBuy.item_stock(name)
    url = BestBuy.item_link(name)
    if stock is not None:
        if stock:
            await ctx.send(f'{BestBuy.actual_name(name)} is in stock at BestBuy. See {url}')
        else:
            await ctx.send(f'{BestBuy.actual_name(name)} is not in stock at BestBuy. See {url}')
    else:
        await ctx.send(f'{name} is not sold at BestBuy.')


@client.command()
async def notify(ctx, *, name=None):
    global AWAY
    if AWAY:
        await away_message(ctx)
        return
    if BestBuy.item_price(name) is None:
        await ctx.send(f'{name} is not sold at BestBuy. ')
    else:

        MAILING_LIST.setdefault(BestBuy.actual_name(name), [])
        if ctx.message.author not in MAILING_LIST[BestBuy.actual_name(name)]:
            await ctx.send(f'Okay! I will notify you every day at 8:00am (EDT) about the details of {BestBuy.actual_name(name)} at BestBuy.')
            MAILING_LIST[BestBuy.actual_name(name)].append(ctx.message.author)
        else:
            await ctx.send(f'Oops! Looks like you are already on the notification list for the details of {BestBuy.actual_name(name)} at BestBuy.')


@client.command()
async def p(ctx):
    await ctx.send('Hi! I am a bot that fetches prices of PC components from BestBuy. I can notify you everyday about '
                   'the details of one or more items\n If you would like me to notify you, simply type  `.notify '
                   'PRODUCTNAME`. If you would like the price of a product now, type `.price PRODUCTNAME`.')


async def text_mailing_list():
    for name in MAILING_LIST:
        if MAILING_LIST[name] == []:
            continue
        price = BestBuy.item_price(name)
        discount = BestBuy.item_discount(name)
        stock = BestBuy.item_stock(name)
        url = BestBuy.item_link(name)

        if discount != 0.0:
            message = f'The price of {name} at BestBuy is $~~{price + discount}~~ $**{price}**. '
        else:
            message = f'The price of {name} at BestBuy is $**{price}. **'

        if stock:
            message += f'{name} is in stock at BestBuy ✅.'
        else:
            message += f'{name} is not in stock at BestBuy ❌.'

        message += f'\nSee {url}'

        for user in MAILING_LIST[name]:
            await user.send(message)


def update_database():
    global AWAY
    AWAY = True
    print('UPDATING INVENTORY')
    BestBuy.update_inventory()
    print('INVENTORY DONE')
    AWAY = False


def update_mailing_list_items():
    print('UPDATING MAILING LIST NOW')
    global MAILING_LIST
    temp = {}
    for name in BestBuy.all_names():
        if name in MAILING_LIST:
            temp[name] = MAILING_LIST[name]
        else:
            temp[name] = []
    MAILING_LIST = temp
    print('DONE UPDATING')


scheduler = AsyncIOScheduler()
scheduler.add_job(update_database, 'cron', day_of_week='0-6', hour=1)
scheduler.add_job(update_mailing_list_items, 'cron', day_of_week='0-6', hour=2, minute=30)
scheduler.add_job(text_mailing_list, 'cron', day_of_week='0-6', hour=8)
client.run(os.environ.get('bot_token'))

