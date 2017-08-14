import json, os.path, asyncio, datetime

import discord
from discord.ext import commands

import config
import cogs
from Verifier import Verifier

def main():

    # define bot
    bot = Bot(
        description=config.description,
        verbose=config.verbose,
        bleeding=config.bleeding,
        reactive=config.reactive
    )
    bot.add_cog(cogs.Fun  (bot))
    bot.add_cog(cogs.Stats(bot))
    bot.add_cog(cogs.Info (bot))
    bot.add_cog(cogs.Admin(bot))

    # launch bot
    try:
        bot.run(config.token)
    except discord.errors.LoginFailure as e:
        print(e, end='\n\n')

class Bot(commands.Bot):

    def __init__(self, verbose=False, bleeding=False, reactive=True, *args, **kwargs):
        # Rewrite the command_prefix flag to force mention
        super().__init__(*args, command_prefix=commands.when_mentioned_or('!'), **kwargs)

        self.admins      = []
        self.admin_roles = ['Administrateur']
        self.config      = {
            'verbose'  : verbose,
            'bleeding' : bleeding,
            'reactive' : reactive,

            'rank_whitelist_file': 'rank_whitelist.txt'
        }
        self.rank_whitelist = []


        try:
            with open(self.config['rank_whitelist_file']) as f:
                for line in f:
                    self.rank_whitelist.append(line.rstrip('\n'))
        except FileNotFoundError as e:
            self.log('File {} does not exist.\n'
                .format(self.config['rank_whitelist_file'])
                + 'Create and maintain one if you wish to use the rank'
                + ' whitelist feature.')

    def log(self, txt):
        if self.config['verbose']:
            print(txt)

    def is_owner(self, user):
        return user.name + '#' + str(user.discriminator) == 'Tina#4153'

    def get_text(self, context):
        return context.message.content[(len(context.prefix + context.invoked_with)) + 1:]

    async def report(self, context, error):
        await self.doubt(context)
        msg   = 'Error !'
        embed = discord.Embed(description=str(error), colour=discord.Colour.orange())
        await self.send_message(context.message.channel, msg, embed=embed)

    async def ok(self, context):
        await self.react(context, '\N{OK HAND SIGN}')

    async def doubt(self, context):
        await self.react(context, '\N{THINKING FACE}')

    async def sees(self, context):
        await self.react(context, '\N{EYES}')

    async def replied(self, context):
        await self.react(context, '\N{RIGHTWARDS ARROW WITH HOOK}')

    async def react(self, context, emoji=None):
        if emoji is None:
            return
        if self.config['reactive']:
            try:
                await self.add_reaction(context.message, emoji)
            except discord.errors.NotFound:
                pass

    async def shrug(self, context):
        if self.config['reactive']:
            await self.send_message(context.message.channel, '¯\_(ツ)_/¯')

    async def on_ready(self):
        self.log('Logged as {}#{}'.format(self.user.name, self.user.id))
        self.log('My boty is ready')

    @asyncio.coroutine
    def on_message(self, message):
            def anti_lag(message2):
                # if bot = not a lag (bots do not lag, they are superior entities)
                if message.author.bot:
                    return False
                # same id = not a lag
                if message.id == message2.id:
                    return False
                # different author = not a lag
                if message.author != message2.author:
                    return False
                # more than 2 minutes delta = not a lag
                if message.timestamp - message2.timestamp > datetime.timedelta(0, 120):
                    return False
                # same content = a lag, not same content = not a lag
                return message.content == message2.content
            # call purge check anti_lag on every message
            yield from self.purge_from(message.channel, limit=10, check=anti_lag)
            # process commands
            yield from self.process_commands(message)

    async def on_member_join(self, member):
        if self.config['bleeding']:
            self.log('Initiating verification procedure for user "{}".'.format(member.name))
            msg  = 'Please send !register followed by your EPITECH mail adress\n'
            msg += 'i.e.: ```!register yournam_e@epitech.eu```\n'
            msg += 'It has to be an EPITECH address, any other address will not be accepted'
            await self.send_message(member, msg)
            Verifier.add(member)

if __name__ == '__main__':
    main()
