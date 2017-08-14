import sys

import discord
from discord.ext import commands

class Admin:
    '''
    A collection of administration commands
    '''
    def __init__(self, bot):
        self.bot = bot

    async def not_admin(self, message):
        await self.bot.add_reaction(message, '\N{FACE WITH NO GOOD GESTURE}')
        msg = 'User `{}` does not have administrator priviledge.'.format(message.author)
        await self.bot.send_message(message.channel, msg)

    def is_admin(context):
        user = context.message.author
        if context.bot.is_owner(user):
            return True

        if not hasattr(user, 'server'):
            return False

        admin_roles = []
        for role in context.message.server.roles:
            if role.name in context.bot.admin_roles:
                admin_roles.append(role)
        i = len(user.roles) - 1
        while i >= 0 and user.roles[i] not in admin_roles:
            i -= 1
        return i != -1

    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_admin)
    async def kill(self, context):
        await self.bot.ok(context)
        if self.bot.reactive:
            await self.bot.say('\N{WINKING FACE}\N{PISTOL}')
        sys.exit()

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    @commands.check(is_admin)
    async def ban(self, context, user: discord.Member = None, reason: str = None, delete: int = 0):
        if user is None:
            await self.bot.reply('please set a user to sentence.')
            return
        try:
            embed = discord.Embed(title="Ban notice", description='Reason: {}'.format(reason), colour=discord.Colour.dark_red())
            embed.set_author(name=context.message.server)
            await self.bot.send_message(user, embed=embed)
            await self.bot.ban(user, delete_message_days=delete)
            await self.bot.ok(context)
        except Exception as e:
            await self.bot.report(context, e)

    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_admin)
    async def edit(self, context, field: str = None, value: str = None):
        if field is None or value is None:
            await self.bot.reply('Please set a field/value.')
            return
        username = None
        #TODO avatar   = None
        if field == 'username':
            username = value
        try:
            await self.bot.edit_profile(username=username)
            await self.bot.ok(context)
        except Exception as e:
            await self.bot.report(context, e)

    @commands.command(pass_context=True, aliases=['cls', 'clear'], hidden=True)
    @commands.check(is_admin)
    async def clean(self, context, limit: int = 100):
        def predicate(message):
            return message.author == self.bot.user
        try:
            message = context.message
            deleted = await self.bot.purge_from(message.channel, limit=limit, check=predicate)
            await self.bot.say('Deleted {} messages.'.format(len(deleted)))
        except Exception as e:
            await self.bot.report(context, e)

    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_admin)
    async def purge(self, context, limit: int = 100, user: discord.Member = None):
        is_user  = None
        if user != None:
            def is_user(message):
                return message.author == user
        try:
            message = context.message
            deleted = await self.bot.purge_from(message.channel, limit=limit, check=is_user)
            await self.bot.say('Deleted {} messages.'.format(len(deleted)))
        except Exception as e:
            await self.bot.report(context, e)

    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_admin)
    async def set(self, context):
        content = self.bot.get_text(context)
        words   = content.split()
        if len(words) > 1:
            value = words[1].casefold()
