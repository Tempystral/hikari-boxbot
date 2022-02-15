import lightbulb
from hikari import MessageFlag

debug_plugin = lightbulb.Plugin("Debug")

@debug_plugin.command
@lightbulb.command("debug", "Manage internal settings for the bot")
@lightbulb.implements(lightbulb.SlashCommandGroup, lightbulb.PrefixCommandGroup)
async def module_group(ctx: lightbulb.Context) -> None:
    pass

@module_group.child
@lightbulb.option("module_name", "The module to target.", type=str)
@lightbulb.command("reload", "Reloads a module.")
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)
async def reload_module(ctx: lightbulb.Context):
    """Reload a module in Tanjun"""

    module_name = getModuleName(ctx)

    try:
        ctx.bot.reload_extensions(module_name)
    except ValueError:
        ctx.bot.load_extensions(module_name)

    #await ctx.bot.declare_global_commands()
    await ctx.respond(f"Reloaded module {module_name}", flags=MessageFlag.EPHEMERAL)


@module_group.child
@lightbulb.option("module_name", "The module to target.")
@lightbulb.command("unload", "Removes a module.")
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)
async def unload_module(ctx: lightbulb.Context):
    """Unload a module in Tanjun"""

    module_name = getModuleName(ctx)

    try:
        ctx.bot.unload_extensions(module_name)
    except lightbulb.errors.ExtensionMissingUnload or lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"Couldn't unload module {module_name}", flags=MessageFlag.EPHEMERAL)
        return

    # Set global commands again?
    await ctx.respond("Unloaded!")

@module_group.child
@lightbulb.option("module_name", "The module to reload.")
@lightbulb.command("load", "Loads a module.")
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)

async def load_module(ctx: lightbulb.Context):
    """Load a module in Tanjun"""

    module_name = getModuleName(ctx)

    try:
        ctx.bot.load_extensions(module_name)
    except lightbulb.errors.ExtensionAlreadyLoaded or lightbulb.errors.ExtensionMissingLoad:
        await ctx.respond(f"Can't find module {module_name}", flags=MessageFlag.EPHEMERAL)
        return

    #await ctx.bot.declare_global_commands()
    await ctx.respond("Loaded!")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(debug_plugin)

def getModuleName(ctx: lightbulb.Context) -> str:
    return f"modules.{ctx.options.module_name}"