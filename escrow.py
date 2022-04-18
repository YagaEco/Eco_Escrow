import os
import discord
#import logging
#from dotenv import load_dotenv
from discord.ext import commands



class TutorialBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Greetings
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} ({self.bot.user.id})')

    @commands.Cog.listener()
    async def on_resumed(self):
        print('Bot has reconnected!')

    # Error Handlers
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Invalid Command!')
            await ctx.send(error)

        # Bot does not have permission
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('Bot Permission Missing!')


intents = discord.Intents.default()
intents.members = True
intents.presences = True


bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),
                   description='New  voting Bot',intents=intents) 

TOKEN = '' #KEY#
if __name__ == '__main__':
	for filename in os.listdir('./commands'):
		print(f'commands.{filename[: -3]}')
		if filename.endswith('.py'):
			print(filename[: -3])
			bot.load_extension(f'commands.{filename[: -3]}')

	bot.add_cog(TutorialBot(bot))
	bot.run(TOKEN,reconnect=True)