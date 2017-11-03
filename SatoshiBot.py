import os
import discord
import asyncio
import urllib.request
import json
import datetime
import time

client = discord.Client()

@client.event
async def hourly_message():
    msg = None
    while True:
        price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
        #GET BTC
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data = json.load(btcdata)
        #price_string = "1 LTC = %0.5f BTC" % float(data.get('data').get('rates').get('BTC').replace(',',''))

        price_string = "%s\n```1 BTC = $%0.2f USD\n1 BTC = %0.5f ETH\n1 BTC = %0.5f LTC\n" % (price_string,
                                                                                            float(data.get('data').get('rates').get('USD').replace(',','')),
                                                                                            float(data.get('data').get('rates').get('ETH').replace(',','')),
                                                                                            float(data.get('data').get('rates').get('LTC').replace(',','')),
                                                                                            )

        #GET ETH
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/ETH-USD/spot")
        data = json.load(btcdata)
        price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))

        #GET LTC
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/LTC-USD/spot")
        data = json.load(btcdata)
        price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))

        for channel in client.get_all_channels():
            if channel.name == "bitcoinchat":
                for pin in await client.pins_from(channel):
                    if pin.author == client.user:
                        msg = pin
                if msg:
                    await client.edit_message(msg,price_string + "```")
                else:
                    msg = await client.send_message(channel,price_string + "```")
                await client.pin_message(msg)
        current_minute = datetime.datetime.today().minute
        current_second = datetime.datetime.today().second
        seconds_left = (59-current_minute)*60 + (60-current_second)
        await asyncio.sleep(seconds_left)

@client.event
async def milestone_message():
    msg = None
    # for channel in client.get_all_channels():
    #     if channel.name == "bitcoinchat":
    #         for message in await client.logs_from(channel,limit=5000):
    #             if message.author == client.user:
    #                 #re.match("")
    #                 pass
    # while True:
    #     await asyncio.sleep(600)
    print("inloop")
    # for channel in client.get_all_channels():
    #     if channel.name == "botchat-adminonly":
    #         await client.send_message(channel,"@Spikeybadooks test")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await hourly_message()
    await milestone_message()


@client.event
async def on_message(message):
    if message.content.lower().startswith('$btc'):
        msg = await client.send_message(message.channel, 'Getting BTC Price...')
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/BTC-USD/spot")
        data = json.load(btcdata)
        price_string = "1 BTC = $%0.2f USD" % float(data.get('data').get('amount').replace(',',''))
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$eth'):
        msg = await client.send_message(message.channel, 'Getting ETH Price...')
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        data = json.load(btcdata)
        price_string = "1 ETH = %0.5f BTC" % float(data.get('data').get('rates').get('BTC').replace(',',''))
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$ltc'):
        msg = await client.send_message(message.channel, 'Getting LTC Price...')
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/exchange-rates?currency=LTC")
        data = json.load(btcdata)
        price_string = "1 LTC = %0.5f BTC" % float(data.get('data').get('rates').get('BTC').replace(',',''))
        await client.edit_message(msg,price_string)
    elif message.content.lower().startswith('$help'):
        await client.send_message(message.channel,'BTC -> USD = !btc\nETH -> BTC = !eth\nLTC -> BTC = !ltc')

    if client.user in message.mentions:
        msg1 = await client.send_message(message.channel,'YES. UMM HI???? HELLO?????')
        price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
        #GET BTC
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/exchange-rates?currency=BTC")
        data = json.load(btcdata)
        #price_string = "1 LTC = %0.5f BTC" % float(data.get('data').get('rates').get('BTC').replace(',',''))

        price_string = "%s\n```1 BTC = $%0.2f USD\n1 BTC = %0.5f ETH\n1 BTC = %0.5f LTC\n" % (price_string,
                                                                                            float(data.get('data').get('rates').get('USD').replace(',','')),
                                                                                            float(data.get('data').get('rates').get('ETH').replace(',','')),
                                                                                            float(data.get('data').get('rates').get('LTC').replace(',','')),
                                                                                            )

        #GET ETH
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/ETH-USD/spot")
        data = json.load(btcdata)
        price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))

        #GET LTC
        btcdata = urllib.request.urlopen("https://api.coinbase.com/v2/prices/LTC-USD/spot")
        data = json.load(btcdata)
        price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,float(data.get('data').get('amount').replace(',','')))
        msg2 = await client.send_message(message.channel,price_string + "```")

client.run(os.environ['SATOSHI_KEY'])
