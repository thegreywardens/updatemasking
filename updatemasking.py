from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify
import discord


async def has_update_command_role(ctx: commands.Context) -> bool:
    """
    Checks if the user has the update command role.
    """
    if ctx.guild is None:
        return False
    uc_role = discord.utils.get(ctx.guild.roles, name="Update Command")
    jc_role = discord.utils.get(ctx.guild.roles, name="Junior Command")
    if uc_role is None:
        return False
    return (uc_role in ctx.author.roles) or (jc_role in ctx.author.roles) or (ctx.author.id == 300681028920541199)


async def has_liberator_role(ctx: commands.Context) -> bool:
    """
    Checks if the user has the update command role.
    """
    if ctx.guild is None:
        return False
    liberator_role = discord.utils.get(ctx.guild.roles, name="Liberator")
    return liberator_role in ctx.author.roles


async def has_updating_role(ctx: commands.Context) -> bool:
    """
    Checks if the user does not have the Updating role.
    """
    if ctx.guild is None:
        return False
    updating_role = discord.utils.get(ctx.guild.roles, name="Updating")
    return updating_role in ctx.author.roles


async def has_liberator_and_updating_role(ctx: commands.Context) -> bool:
    """
    Checks if the user has the Liberator role and does not have the Updating role.
    """
    if ctx.guild is None:
        return False
    return (await has_liberator_role(ctx)) and (await has_updating_role(ctx))


async def is_update_planning_channel(ctx: commands.Context) -> bool:
    """
    Checks if the command is being used in the Update Planning channel.
    """
    if ctx.guild is None:
        return False
    update_planning_channel = discord.utils.get(ctx.guild.channels, name="update-planning")
    return ctx.channel == update_planning_channel


async def has_update_command_role_and_is_update_planning_channel(ctx: commands.Context) -> bool:
    """
    Checks if the user has the update command role and is in the Update Planning channel.
    """
    return await has_update_command_role(ctx) and await is_update_planning_channel(ctx)


class UpdateMasking(commands.Cog):

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    def cog_unload(self):
        pass

    @commands.command()
    @commands.check(has_liberator_role)
    async def here(self, ctx: commands.Context):
        """Get the names of all users with the Updating role"""
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Updating")
        author = ctx.author
        try:
            await author.add_roles(role)
        except discord.errors.Forbidden as err:
            await ctx.send("I don't have permissions to mark you, {}: {}.".format(author.mention, err))
        except AttributeError:  # role_to_add is NoneType
            await ctx.send("That role isn't user settable, {}.".format(author.mention))
        else:
            await ctx.send("Marked {} as present for this update.".format(author.mention))

    @commands.command()
    @commands.check(has_liberator_and_updating_role)
    async def bye(self, ctx: commands.Context):
        """Remove the Updating role from the user"""
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Updating")
        author = ctx.author
        try:
            await author.remove_roles(role)
        except discord.errors.Forbidden as err:
            await ctx.send("I don't have permissions to unmark you, {}: {}.".format(author.mention, err))
        except AttributeError:  # role_to_remove is NoneType
            await ctx.send("That role isn't user settable, {}.".format(author.mention))
        else:
            await ctx.send(f"Unmarked {author.mention} as present for this update.")

    @commands.command()
    @commands.check(has_update_command_role)
    async def update_over(self, ctx: commands.Context):
        """Remove the Updating role from all users"""
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Updating")
        if role is None:
            await ctx.send("The Updating role does not exist.")
            return

        members = [member for member in guild.members if role in member.roles]
        if not members:
            await ctx.send("No users have the Updating role.")
            return

        for member in members:
            try:
                await member.remove_roles(role)
            except discord.errors.Forbidden as err:
                await ctx.send(f"Could not remove role from {member.mention}: {err}")
            else:
                await ctx.send(f"{member.mention}: Unmasked.")

    @commands.command()
    @commands.check(has_update_command_role_and_is_update_planning_channel)
    async def annoy_list(self, ctx: commands.Context):
        """List all users with the Updating role"""
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="Updating")
        liberator_role = discord.utils.get(guild.roles, name="Liberator")

        members = [member for member in guild.members if
                   (role not in member.roles) and (liberator_role in member.roles)]

        output = ""
        for member in members:
            output += f"<@{member.id}> "

        batch_num = 1
        # Use space as delimiter to avoid cutting mentions
        # Reduce page length to account for code block formatting
        for page in pagify(output, delims=[" "], page_length=1900):
            final_output = f"**Batch {batch_num}:**\n```\n\n{page}\n\n```"
            await ctx.send(final_output)
            batch_num += 1

