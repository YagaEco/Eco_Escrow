import json
import discord
import datetime
from discord.ext import commands, tasks
from brownie import *
#connect to need networt Polygon ot other...
network.connect('matic')


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #ADD Your ID BOT and Time_delta - time that is given for a meeting in seconds
        self.username_bot = 941283909637926936 ##################ID######################
        self.time_delta = 60 ############AMOUNT SECONDS FOR DEAL#################

    @commands.Cog.listener()
    #LOOP
    async def on_ready(self):
        self.poll_result.start()

    @commands.Cog.listener()

    async def on_message_delete(self, message):
        # Remove poll if already Done 
        with open('../db/escrow.json', 'r') as file:
            escrow_data = json.load(file)

        if str(message.id) in escrow_data:
            escrow_data.pop(str(message.id))

            with open('../db/escrow.json', 'w') as update_poll_data:
                json.dump(escrow_data, update_poll_data, indent=4)

    @commands.command()
    #Start Deal Escrow 
    #Example: !escrow 0xa6018d60139fbe7049c2f167d14c57c24eb4d7ac 0xd61749aC5805c84F0934eF8a6aFeF434475B5F42 @noobreckoner 290 10
    #
    async def escrow(self,ctx, from_:str, to_:str, user: discord.Member, nft:int,price:int): 
        d=0
        author = ctx.message.author.id
        print(author)

        print(from_,author,user) 
        #await ctx.send(f'{from_} {to_} {nft}')
        with open('./db/escrow.json', 'r') as poll_file:
            escrow_data = json.load(poll_file)
        # Next comes a check for balances, that is, the correctness of the address WEB3
        try:
            valid_to = web3.eth.getBalance(web3.toChecksumAddress(to_))
            valid_from= web3.eth.getBalance(web3.toChecksumAddress(from_))

            #If Deal exist
            for i in escrow_data.values():
                if str(from_) in i['from'] and str(to_) in i['to']:
                    if str(nft) not in str(i['nft']):
                        d=0
                    else:
                        print('Deal already exist')
                        await ctx.send('Deal already exist')
                        d= 1
                if str(nft) in str(i['nft']):
                    await ctx.send("NFT already in Deal") 
                    d= 1               
            # Checking against the parameters of our collection may change
            if from_!=to_ and nft>=0 and nft<=359 and d!=1:
                message = await ctx.send('Ok')

                cur_time = datetime.datetime.utcnow().strftime("%s")
                close_time = int(cur_time)+ self.time_delta

                escrow_data[message.id]={'message_id': message.id,'channel': message.channel.id,'escrow_start_time': cur_time,'close_time':close_time,'from':from_,'to':to_,'user_id_from':author,'user_from_name':ctx.message.author.mention,'user_id_to':user.id,'user_to_name':user.mention,'dest':user.discriminator,'nft':nft,'price':price,'payed':False,'transfer_nft':False}

                await ctx.send(f'{ctx.message.author.mention} please send <@&{self.username_bot}> {price} points \n `!send <@&{self.username_bot}> {price} {message.id}`')
                print(escrow_data)

                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)


        except Exception as e:
            print(e)
            await ctx.send('Please check from/to - not_valid')

    @commands.command()
    # transaction verification
    async def check(self,ctx, link): 
        # Our contract 0x0Ce9a6838F1574F78B84d145df716C6FD3160CA7, previously entered with brownie and abi
        NFT=Contract('0x0Ce9a6838F1574F78B84d145df716C6FD3160CA7')
        with open('./db/escrow.json', 'r') as poll_file:
            escrow_data = json.load(poll_file)
       # await ctx.send(link)
        link_= str(link)
        link = link_.split('/')
        link = link[-1]

        tx = web3.eth.getTransaction(link)
        if tx.to==NFT.address:# checking whether our contract is a transaction
            tx = NFT.decode_input(tx['input'])
            txx = [str(i).lower() for i in tx[1]]
            for i in escrow_data.values():
                # We verify the parameters of all transactions
                if [i['from'].lower(),i['to'].lower(),str(i['nft'])]==txx:
                    if i['payed']==True: # Additional check for points payment
                        print('TRUE')

                        user  = i['user_to_name']

                        print(user)
                        i['transfer_nft']=True
                        with open('./db/escrow.json', 'w') as new_escrow_data:
                            json.dump(escrow_data, new_escrow_data, indent=4)

                        await ctx.send(f'TX Complete , {user}')
                    else:
                        await ctx.send(f'Not payed')
 
                else:
                    await ctx.send(f'Please check valid link')
        else:
            await ctx.send(f'Please check valid link tx')

    @commands.command()
    # send command parsing
    async def send(self,ctx, user, amount:float, id_:int):
        if user==f'<@&{self.username_bot}>':  # Checking all submissions to our bot 
            with open('./db/escrow.json', 'r') as poll_file:
                escrow_data = json.load(poll_file)
            # If it has not been paid before, the amount is checked or more change if less than nothing (the user actually needs to just copy the previous response from the bot)
            if str(id_) in escrow_data and escrow_data[str(id_)]['price']==amount and escrow_data[str(id_)]['payed']==False:

                escrow_data[str(id_)]['payed']=True
                print(amount, ctx.author.id)
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)

                await ctx.send(f'Escrow bot get {amount} points from {ctx.author.mention}, deal ID:{id_}')
                await ctx.send(f'User {escrow_data[str(id_)]["user_to_name"]} please send NFT id : **{escrow_data[str(id_)]["nft"]}** \n from: `{escrow_data[str(id_)]["from"]}` \n to: `{escrow_data[str(id_)]["to"]}`')
            # In this case, if the user sent more, the bot returns the change
            if str(id_) in escrow_data and escrow_data[str(id_)]['price']>amount and escrow_data[str(id_)]['payed']==False:
                await ctx.send(f'Please check amount')
                await ctx.send(f'!send {escrow_data[str(id_)]["user_from_name"]} {amount} refund Deal ID: {escrow_data[str(id_)]["message_id"]}')
                await ctx.send(f'** Closed Deal ID: {escrow_data[str(id_)]["message_id"]} ** please retry')
                escrow_data.pop(str(id_))
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)
                pass


                
            
            # If less just refund and close the deal
            if str(id_) in escrow_data and escrow_data[str(id_)]['price']<amount and escrow_data[str(id_)]['payed']==False:
                dif_= amount-escrow_data[str(id_)]['price']
                print(dif_)
                await ctx.send(f'!send {escrow_data[str(id_)]["user_from_name"]} {dif_} refund Deal ID: {escrow_data[str(id_)]["message_id"]}')
                escrow_data[str(id_)]['payed']=True
                print(amount, ctx.author.id)
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)

                await ctx.send(f'Escrow bot get {amount} points (refund {dif_}) from {ctx.author.mention}, deal ID:{id_}')
                await ctx.send(f'User {escrow_data[str(id_)]["user_to_name"]} please send NFT id : **{escrow_data[str(id_)]["nft"]}** \n from: `{escrow_data[str(id_)]["from"]}` \n to: `{escrow_data[str(id_)]["to"]}`')


            if str(id_) not in escrow_data:
                await ctx.send(f'Deal {id_} not exist')



    @tasks.loop(seconds=10)
    async def poll_result(self):
        with open('./db/escrow.json', 'r') as poll_file:
            escrow_data = json.load(poll_file)

        for i in list(escrow_data.values()):
            channel = self.bot.get_channel(int(i['channel']))
            message = await channel.fetch_message(i['message_id'])
            cur_time = datetime.datetime.utcnow().strftime("%s")

            if int(cur_time)>=int(i['close_time']) and i['transfer_nft']==False and i['payed']==True:
                await channel.send(f'!send {i["user_from_name"]} {i["price"]} return Deal ID: {i["message_id"]}')
                escrow_data.pop(str(message.id))
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)
            if int(cur_time)>=int(i['close_time']) and i['transfer_nft']==True and i['payed']==True or i['transfer_nft']==True and i['payed']==True:
                await channel.send(f'!send {i["user_to_name"]} {i["price"]} success Deal ID: {i["message_id"]}')

                escrow_data.pop(str(message.id))
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)
            if int(cur_time)>=int(i['close_time']) and i['transfer_nft']==False and i['payed']==False:
                await channel.send(f'closed Deal ID: {i["message_id"]}')
                escrow_data.pop(str(message.id))
                with open('./db/escrow.json', 'w') as new_escrow_data:
                    json.dump(escrow_data, new_escrow_data, indent=4)



def setup(bot):
    bot.add_cog(Poll(bot))
