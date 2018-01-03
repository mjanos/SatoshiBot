import os
import re
import discord
import asyncio
import urllib.request
import aiohttp
import json
import datetime
import time
import random
import aiofiles

def safe_float(x):
    if type(x) is list and len(x) > 0:
        return float(x[0])
    else:
        return 0

class SatoshiBot(discord.Client):
    def __init__(self,*args,**kwargs):

        self.exchange_rates = []

        self.negative_file_mtime = None
        self.positive_file_mtime = None
        self.negative_gifs_mtime = None
        self.positive_gifs_mtime = None
        self.neutral_file_mtime = None

        self.hot10 = []

        self.previous_btc = None

        super().__init__(*args,**kwargs)

    async def load_messages(self):
        if os.path.exists("positive_gifs") and self.positive_gifs_mtime is None or os.path.getmtime("positive_gifs") != self.positive_gifs_mtime:
            self.positive_files = []
            for f in os.listdir("positive_gifs"):
                self.positive_files.append(f)

        if self.positive_file_mtime is None or os.path.getmtime("positive_messages.txt") != self.positive_file_mtime:
            self.positive_messages = []
            async with aiofiles.open("positive_messages.txt","r") as positive_file:
                async for line in positive_file:
                    self.positive_messages.append(line)
            self.positive_file_mtime = os.path.getmtime("positive_messages.txt")


        if os.path.exists("negative_gifs") and self.negative_gifs_mtime is None or os.path.getmtime("negative_gifs") != self.negative_gifs_mtime:
            self.negative_files = []
            for f in os.listdir("negative_gifs"):
                self.negative_files.append(f)

        if self.negative_file_mtime is None or os.path.getmtime("negative_messages.txt") != self.negative_file_mtime:
            self.negative_messages = []
            async with aiofiles.open("negative_messages.txt","r") as negative_file:
                async for line in negative_file:
                    self.negative_messages.append(line)
            self.negative_file_mtime = os.path.getmtime("negative_messages.txt")

        if self.neutral_file_mtime is None or os.path.getmtime("neutral_messages.txt") != self.neutral_file_mtime:
            self.neutral_messages = []
            async with aiofiles.open("neutral_messages.txt","r") as neutral_file:
                async for line in neutral_file:
                    self.neutral_messages.append(line)
            self.neutral_file_mtime = os.path.getmtime("neutral_messages.txt")

    async def get_crypto_data(self):
        try:
            async with aiohttp.get("https://api.coinmarketcap.com/v1/ticker/?limit=1000") as linkobj:
                if linkobj.status == 200:
                    self.exchange_rates = await linkobj.json()
        except: pass

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self,message):
        if self.user in message.mentions or message.content.lower().startswith("$"):
            valid_currency = False
            price_fail = False
            crypto_symbol = ""
            try:
                crypto_symbol = re.match("\$?([A-Za-z1-9]+)",message.content).group(1)
                if re.match("\$([A-Za-z]+)",message.content):
                    valid_currency = True
            except:
                try:
                    crypto_symbol = message.content.split(" ")[0]
                except:
                    price_fail = True

            if valid_currency:
                msg = await self.send_message(message.channel, 'Getting %s Price...' % crypto_symbol)
                if price_fail:
                    msg = await self.send_message(message.channel, 'Unable to get price for %s' % crypto_symbol)

            await self.get_crypto_data()

            if valid_currency:
                price_float = safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == crypto_symbol.upper()])
                sat_float = safe_float([x.get('price_btc',None) for x in self.exchange_rates if x.get('symbol',None) == crypto_symbol.upper()]) * 100000000
                if price_float > 0 and price_float < 0.01:
                    price_string = "1 %s = $%0.7f USD" % (crypto_symbol.upper(),price_float)
                    satoshi_string = "\n1 %s = %0.0f SAT" % (crypto_symbol.upper(),sat_float)
                    if price_string or satoshi_string:
                        await self.edit_message(msg,"```" + price_string + satoshi_string + "```")

                    self.hot10 = [crypto_symbol] + [x for x in self.hot10 if crypto_symbol.lower().strip() != x.lower().strip()]
                    if len(self.hot10) > 10:
                        del self.hot10[-1]

                elif price_float > 0 and price_float >= 0.01:
                    price_string = "1 %s = $%0.2f USD" % (crypto_symbol.upper(),price_float)
                    satoshi_string = "\n1 %s = %0.0f SAT" % (crypto_symbol.upper(),sat_float)
                    if price_string or satoshi_string:
                        await self.edit_message(msg,"```" + price_string + satoshi_string + "```")

                    self.hot10 = [crypto_symbol] + [x for x in self.hot10 if crypto_symbol.lower().strip() != x.lower().strip()]
                    if len(self.hot10) > 10:
                        del self.hot10[-1]

                elif price_float == 0:
                    price_string = "#wrong"
                    await self.delete_message(msg)
                    await self.send_message(message.channel,"#wrong")

            elif message.content.lower().startswith('$help'):
                await self.send_message(message.channel,'```Convert any symbol to USD by starting with "$"\n@Satoshi for more info```')

            if self.user in message.mentions:
                await self.load_messages()
                current_btc = safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == 'BTC'])
                if self.previous_btc is None:
                    msg1 = await self.send_message(message.channel,"I'M BACK BITCH!")
                else:
                    if self.previous_btc < current_btc:
                        if bool(random.getrandbits(1)):
                            rand_msg = random.choice(self.positive_messages)
                            if rand_msg.strip():
                                await self.send_message(message.channel,rand_msg)
                        else:
                            await self.send_file(message.channel,os.path.join(os.path.dirname(os.path.realpath(__file__)),"positive_gifs",random.choice(self.positive_files)))

                    elif self.previous_btc > current_btc:
                        if bool(random.getrandbits(1)):
                            rand_msg = random.choice(self.negative_messages)
                            if rand_msg.strip():
                                await self.send_message(message.channel,rand_msg)
                        else:
                            random_file = random.choice(self.negative_files)
                            if random_file:
                                await self.send_file(message.channel,os.path.join(os.path.dirname(os.path.realpath(__file__)),"negative_gifs",random_file))
                    else:
                        rand_msg = random.choice(self.neutral_messages)
                        if rand_msg.strip():
                            await self.send_message(message.channel,rand_msg)

                price_string = time.strftime('```%b %d, %Y -- %I:%M%p```')
                #GET BTC

                if not self.previous_btc is None and self.previous_btc < current_btc:
                    price_trajectory = ":chart_with_upwards_trend:"
                elif not self.previous_btc is None and self.previous_btc > current_btc:
                    price_trajectory = ":chart_with_downwards_trend:"
                else:
                    price_trajectory = ""

                price_string = "%s\n%s\n```1 BTC = $%0.2f USD\n1 ETH = %0.5f BTC\n1 LTC = %0.5f BTC\n" % (price_string,price_trajectory,
                                                                                                    safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == 'BTC']),
                                                                                                    safe_float([x.get('price_btc',None) for x in self.exchange_rates if x.get('symbol',None) == 'ETH']),
                                                                                                    safe_float([x.get('price_btc',None) for x in self.exchange_rates if x.get('symbol',None) == 'LTC']),
                                                                                                    )
                #GET ETH
                price_string = "%s\n1 ETH = $%0.2f USD" % (price_string,safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == 'ETH']))

                #GET LTC
                price_string = "%s\n1 LTC = $%0.2f USD" % (price_string,safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == 'LTC']))

                #GET HOT 10
                if self.hot10:
                    price_string = "%s```\n:fire:HOT 10:fire:```" % (price_string)

                    for c in self.hot10:
                        price_string = "%s%s: $%s\n" % (price_string,c.upper(),safe_float([x.get('price_usd',None) for x in self.exchange_rates if x.get('symbol',None) == c.upper().strip()]))
                if price_string:
                    await self.send_message(message.channel,price_string + "```")

                self.previous_btc = current_btc
        #await self.process_commands(message)

if __name__=="__main__":
    client = SatoshiBot()
    client.run(os.environ['SATOSHI_KEY'])
