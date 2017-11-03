import os
import discord
import asyncio
import urllib.request
import json
import datetime
import time

client = discord.Client()

async def get_crypto_data():
    crypto_links = {'BTC':"https://api.coinbase.com/v2/exchange-rates?currency=BTC",
                    'ETH':"https://api.coinbase.com/v2/exchange-rates?currency=ETH",
                    'LTC':"https://api.coinbase.com/v2/exchange-rates?currency=LTC"}
    exchange_rates = {'BTC':{},'ETH':{},'LTC':{}}

    for currency,link in crypto_links.items():
        data = urllib.request.urlopen(link)
        parsed_data = json.load(data)
        for k,v in parsed_data.get('data').get('rates').items():
            exchange_rates[currency][k] = v.replace(',','')

    return exchange_rates

# @client.event
# async def hourly_message():
#     msg = None
#     while True:
#         price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
#
#         price_string = "%s\n```1 BTC = $%0.2f USD\n1 BTC = %0.5f ETH\n1 BTC = %0.5f LTC\n" % (price_string,
#                                                                                             float(data.get('data').get('rates').get('USD').replace(',','')),
#                                                                                             float(data.get('data').get('rates').get('ETH').replace(',','')),
#                                                                                             float(data.get('data').get('rates').get('LTC').replace(',','')),
#                                                                                             )
#
#         #GET ETH
#         btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/ETH-USD/spot")
#         data = json.load(btcdata)
#         price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))
#
#         #GET LTC
#         btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/LTC-USD/spot")
#         data = json.load(btcdata)
#         price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))
#
#         for channel in client.get_all_channels():
#             if channel.name == "bitcoinchat":
#                 for pin in await client.pins_from(channel):
#                     if pin.author == client.user:
#                         msg = pin
#                 if msg:
#                     await client.edit_message(msg,price_string + "```")
#                 else:
#                     msg = await client.send_message(channel,price_string + "```")
#                 await client.pin_message(msg)
#         current_minute = datetime.datetime.today().minute
#         current_second = datetime.datetime.today().second
#         seconds_left = (59-current_minute)*60 + (60-current_second)
#         await asyncio.sleep(seconds_left)

# @client.event
# async def milestone_message():
#     msg = None
#     # for channel in client.get_all_channels():
#     #     if channel.name == "bitcoinchat":
#     #         for message in await client.logs_from(channel,limit=5000):
#     #             if message.author == client.user:
#     #                 #re.match("")
#     #                 pass
#     # while True:
#     #     await asyncio.sleep(600)
#     print("inloop")
#     # for channel in client.get_all_channels():
#     #     if channel.name == "botchat-adminonly":
#     #         await client.send_message(channel,"@Spikeybadooks test")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if client.user in message.mentions:
        msg1 = await client.send_message(message.channel,'YES. UMM HI???? HELLO?????')
        msg2 = await client.send_message(message.channel,"...")

    if message.content.lower().startswith('$btc'):
        msg = await client.send_message(message.channel, 'Getting BTC Price...')
    elif message.content.lower().startswith('$eth'):
        msg = await client.send_message(message.channel, 'Getting ETH Price...')
    elif message.content.lower().startswith('$ltc'):
        msg = await client.send_message(message.channel, 'Getting LTC Price...')



    exchange_rates = await get_crypto_data()
    if message.content.lower().startswith('$btc'):
        price_string = "1 BTC = $%0.2f USD" % float(exchange_rates['BTC']['USD'])
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$eth'):
        price_string = "1 ETH = %0.5f BTC" % float(exchange_rates['ETH']['BTC'])
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$ltc'):
        price_string = "1 LTC = %0.5f BTC" % float(exchange_rates['LTC']['BTC'])
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$help'):
        await client.send_message(message.channel,'BTC -> USD = $btc\nETH -> BTC = $eth\nLTC -> BTC = $ltc')

    if client.user in message.mentions:
        price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
        #GET BTC

        price_string = "%s\n```1 BTC = $%0.2f USD\n1 BTC = %0.5f ETH\n1 BTC = %0.5f LTC\n" % (price_string,
                                                                                            float(exchange_rates['BTC']['USD']),
                                                                                            float(exchange_rates['BTC']['ETH']),
                                                                                            float(exchange_rates['BTC']['LTC']),
                                                                                            )
        #GET ETH
        price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,float(exchange_rates['ETH']['USD']))

        #GET LTC
        price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,float(exchange_rates['LTC']['USD']))
        await client.edit_message(msg2,price_string + "```")

client.run(os.environ['SATOSHI_KEY'])
