import os
import discord
import asyncio
import urllib.request
import json
import datetime
import time
import random

class SatoshiBot(discord.Client):
    def __init__(self,*args,**kwargs):
        self.crypto_links = {'BTC':"https://api.coinbase.com/v2/exchange-rates?currency=BTC",
                            'ETH':"https://api.coinbase.com/v2/exchange-rates?currency=ETH",
                            'LTC':"https://api.coinbase.com/v2/exchange-rates?currency=LTC"}

        #self.positive_messages = ["McAfee might be on to something...",

                                    # "EAT THE RICH",
                                    # "https://www.youtube.com/watch?v=y2ak_oBeC-I",
                                    # "https://www.youtube.com/watch?v=HgzGwKwLmgM",
                                    # "Have you heard about our lord and saviour, Bitcoin?"
                                    # ]

        self.neutral_messages = ["YES. UMM HI???? HELLO?????"]

        #self.negative_messages = ["Yeah, yeah I know...","I SWEAR I DIDN'T DO THIS PLEASE I'M A GOOD BOT","Blame Trump","Maybe Dimon was right...","There's a reason nobody knows my identity","https://media.coindesk.com/uploads/2014/03/grumpy-nakamoto.png"]

        self.exchange_rates = {'BTC':{},'ETH':{},'LTC':{}}

        self.negative_file_mtime = None
        self.positive_file_mtime = None

        self.previous_btc = None

        self.latest_fetch = None

        super().__init__(*args,**kwargs)

    async def load_messages(self):
        if self.positive_file_mtime is None or os.path.getmtime("positive_messages.txt") != self.positive_file_mtime:
            self.positive_messages = []
            with open("positive_messages.txt","r") as positive_file:
                for line in positive_file:
                    self.positive_messages.append(line)
            self.positive_file_mtime = os.path.getmtime("positive_messages.txt")

        if self.negative_file_mtime is None or os.path.getmtime("negative_messages.txt") != self.negative_file_mtime:
            self.negative_messages = []
            with open("negative_messages.txt","r") as negative_file:
                for line in negative_file:
                    self.negative_messages.append(line)
            self.negative_file_mtime = os.path.getmtime("negative_messages.txt")

    async def get_crypto_data(self):
        if self.latest_fetch is None or datetime.datetime.now() - self.latest_fetch > datetime.timedelta(minutes=1):
            self.latest_fetch = datetime.datetime.now()
            for currency,link in self.crypto_links.items():
                data = urllib.request.urlopen(link)
                parsed_data = json.load(data)
                for k,v in parsed_data.get('data').get('rates').items():
                    self.exchange_rates[currency][k] = v.replace(',','')
        else:
            print("Skipping fetch")

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

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.load_messages()

    async def on_message(self,message):
        if self.user in message.mentions or message.content.lower().startswith('$btc') or message.content.lower().startswith('$eth') or message.content.lower().startswith('$ltc') or message.content.lower().startswith('$help'):
            if self.user in message.mentions:
                if self.previous_btc is None:
                    msg1 = await self.send_message(message.channel,'YES. UMM HI???? HELLO?????')
                else:
                    msg1 = await self.send_message(message.channel,"...")
                msg2 = await self.send_message(message.channel,"...")
                await self.load_messages()

            if message.content.lower().startswith('$btc'):
                msg = await self.send_message(message.channel, 'Getting BTC Price...')
            elif message.content.lower().startswith('$eth'):
                msg = await self.send_message(message.channel, 'Getting ETH Price...')
            elif message.content.lower().startswith('$ltc'):
                msg = await self.send_message(message.channel, 'Getting LTC Price...')

            await self.get_crypto_data()
            current_btc = float(self.exchange_rates['BTC']['USD'])

            if self.user in message.mentions:
                if not self.previous_btc is None:
                    if self.previous_btc <= current_btc:
                        await self.edit_message(msg1,random.choice(self.positive_messages))
                    elif self.previous_btc > current_btc:
                        await self.edit_message(msg1,random.choice(self.negative_messages))

            self.previous_btc = current_btc

            if message.content.lower().startswith('$btc'):
                price_string = "1 BTC = $%0.2f USD" % float(self.exchange_rates['BTC']['USD'])
                await self.edit_message(msg,price_string)
            elif message.content.lower().startswith('$eth'):
                price_string = "1 ETH = %0.5f BTC" % float(self.exchange_rates['ETH']['BTC'])
                await self.edit_message(msg,price_string)
            elif message.content.lower().startswith('$ltc'):
                price_string = "1 LTC = %0.5f BTC" % float(self.exchange_rates['LTC']['BTC'])
                await self.edit_message(msg,price_string)
            elif message.content.lower().startswith('$help'):
                await self.send_message(message.channel,'```BTC -> USD = $btc\nETH -> BTC = $eth\nLTC -> BTC = $ltc\n@Satoshi for more info```')

            if self.user in message.mentions:
                price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
                #GET BTC

                price_string = "%s\n```1 BTC = $%0.2f USD\n1 BTC = %0.5f ETH\n1 BTC = %0.5f LTC\n" % (price_string,
                                                                                                    float(self.exchange_rates['BTC']['USD']),
                                                                                                    float(self.exchange_rates['BTC']['ETH']),
                                                                                                    float(self.exchange_rates['BTC']['LTC']),
                                                                                                    )
                #GET ETH
                price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,float(self.exchange_rates['ETH']['USD']))

                #GET LTC
                price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,float(self.exchange_rates['LTC']['USD']))
                await self.edit_message(msg2,price_string + "```")

if __name__=="__main__":
    client = SatoshiBot()
    client.run(os.environ['SATOSHI_KEY'])
