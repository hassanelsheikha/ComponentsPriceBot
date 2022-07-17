import discord
from discord.ext import commands, tasks

from store import BestBuy

from dotenv import load_dotenv
import os

load_dotenv()

client = commands.Bot(command_prefix='.')

mailing_list = {}

@client.event
async def on_ready():
    print('Bot is running.')


@client.command()
async def priceof(ctx, *, name):
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
    print(type(ctx))
    print(ctx.message.author)
    if BestBuy.item_price(name) is None:
        await ctx.send(f'{name} is not sold at BestBuy. ')
    else:

        mailing_list.setdefault(BestBuy.actual_name(name), [])
        if ctx.message.author not in mailing_list[BestBuy.actual_name(name)]:
            await ctx.send(f'Okay! I will notify you every day at 8:00am (EDT) about the details of {BestBuy.actual_name(name)} at BestBuy.')
            mailing_list[BestBuy.actual_name(name)].append(ctx.message.author)
        else:
            await ctx.send(f'Oops! Looks like you are already on the notification list for the details of {BestBuy.actual_name(name)} at BestBuy.')

        await text_mailing_list()


@tasks.loop(hours=24)
async def text_mailing_list():
    for name in mailing_list:
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

        for user in mailing_list[name]:
            await user.send(message)


@tasks.loop(hours=24)
async def update_mailing_list_items():
    global mailing_list
    temp = {}
    for name in BestBuy.all_names():
        if name in mailing_list:
            temp[name] = mailing_list[name]
        else:
            temp[name] = []
    mailing_list = temp


client.run(os.environ.get('bot_token'))