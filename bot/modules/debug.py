import lightbulb
from decouple import config
from hikari import MessageFlag

debug_plugin = lightbulb.Plugin("Debug")

@debug_plugin.command
@lightbulb.add_checks(lightbulb.has_roles(config("ELEVATED_ROLES", cast=int)))
@lightbulb.command("debug", "Manage internal settings for the bot", hidden=True)
@lightbulb.implements(lightbulb.SlashCommandGroup, lightbulb.PrefixCommandGroup)
async def module_group(ctx: lightbulb.Context) -> None:
  pass

@module_group.child
@lightbulb.option("module_name", "The module to target.", type=str)
@lightbulb.command("reload", "Reloads a module.", inherit_checks=True)
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


# @module_group.child
# @lightbulb.option("module_name", "The module to target.")
# @lightbulb.command("unload", "Removes a module.", inherit_checks=True)
# @lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)
# async def unload_module(ctx: lightbulb.Context):
#   """Unload a module in Tanjun"""

#   module_name = getModuleName(ctx)

#   try:
#     ctx.bot.unload_extensions(module_name)
#   except lightbulb.errors.ExtensionMissingUnload or lightbulb.errors.ExtensionNotFound:
#     await ctx.respond(f"Couldn't unload module {module_name}", flags=MessageFlag.EPHEMERAL)
#     return

#   # Set global commands again?
#   await ctx.respond("Unloaded!")

# @module_group.child
# @lightbulb.option("module_name", "The module to reload.")
# @lightbulb.command("load", "Loads a module.", inherit_checks=True)
# @lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)
# async def load_module(ctx: lightbulb.Context):
#   """Load a module in Tanjun"""

#   module_name = getModuleName(ctx)

#   try:
#     ctx.bot.load_extensions(module_name)
#   except lightbulb.errors.ExtensionAlreadyLoaded or lightbulb.errors.ExtensionMissingLoad:
#     await ctx.respond(f"Can't find module {module_name}", flags=MessageFlag.EPHEMERAL)
#     return

#   #await ctx.bot.declare_global_commands()
#   await ctx.respond("Loaded!")

@module_group.child
@lightbulb.command("test", "Puts the bot in testing mode.", inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand, lightbulb.PrefixSubCommand)
async def test_module(ctx: lightbulb.Context):
  """Put a module into test mode"""
  if not ctx.bot.d.testmode:
    ctx.bot.d.testmode = True
  else:
    ctx.bot.d.testmode = not ctx.bot.d.testmode

  prefix = "en" if ctx.bot.d.testmode else "dis"
  await ctx.respond(f"Test mode {prefix}abled!")


def load(bot: lightbulb.BotApp) -> None:
  bot.add_plugin(debug_plugin)

def getModuleName(ctx: lightbulb.Context) -> str:
  return f"modules.{ctx.options.module_name}"