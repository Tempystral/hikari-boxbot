from logging import getLogger
from decouple import config
import hikari
import hikari.permissions
import lightbulb as lb
from hikari.permissions import Permissions
import miru
from bot.utils.checks import elevated_user
from bot.utils.config import ServerConfig, BoxbotException

log = getLogger("rocket.extensions.admin")

plugin = lb.Plugin("Admin")
ladleOptions = [ miru.SelectOption(label= x) for x in config("EXTRACTORS", cast=str).split(",") ]

@plugin.command
@lb.add_checks(elevated_user)
@lb.command("boxbot", "Manage server-specific settings for the bot")
@lb.implements(lb.SlashCommandGroup, lb.PrefixCommandGroup)
async def admin_group(ctx: lb.Context) -> None:
  pass

@admin_group.child
@lb.command("admin", "Set variables", inherit_checks=True)
@lb.implements(lb.SlashSubGroup, lb.PrefixSubGroup)
async def set_command(ctx: lb.Context):
  pass

@set_command.child
@lb.command("roles", "Choose elevated roles", inherit_checks=True)
@lb.implements(lb.SlashSubCommand)
async def choose_mod_roles(ctx: lb.Context):
  response, view = await __create_view(ctx, RoleSelectView(), "Select elevated roles:")
  await view.wait_for_input()
  await response.delete()
  save_settings()

@set_command.child
@lb.command("channels", "Exclude channels from processing", inherit_checks=True)
@lb.implements(lb.SlashSubCommand)
async def choose_channels(ctx: lb.Context):
  response, view = await __create_view(ctx, ChannelSelectView(), "Select channels to exclude from processing:")
  await view.wait_for_input()
  await response.delete()
  save_settings()

@set_command.child
@lb.command("ladles", "Choose which ladles are active", inherit_checks=True)
@lb.implements(lb.SlashSubCommand)
async def choose_ladles(ctx: lb.Context):
  response, view = await __create_view(ctx, LadleSelectView(), "Select ladles to activate:")
  await view.wait_for_input()
  await response.delete()
  save_settings()

@admin_group.child
@lb.add_checks(lb.checks.owner_only)
@lb.command("setup", "Set up the guild to use Boxbot", inherit_checks=True)
@lb.implements(lb.SlashSubCommand, lb.PrefixSubCommand)
async def setup(ctx: lb.Context):
  settings: ServerConfig = ctx.bot.d.settings
  assert ctx.guild_id

  settings.add_guild(ctx.guild_id, ctx.get_guild().name)
  settings.save()
  response = hikari.Embed(description=f"Registered **{ctx.get_guild().name}**")
  await ctx.respond(embed=response)

async def __create_view(ctx: lb.Context, view: miru.View, msg: str):
  response = await ctx.respond(msg, components=view)
  ctx.bot.d.client.start_view(view)
  return response, view

@plugin.set_error_handler
async def on_error(event: lb.events.CommandErrorEvent) -> bool | None:
  log.warning(f"Caught exception: {type(event.exception)}")
  # if isinstance(event.exception, lb.errors.CommandInvocationError):
  if isinstance(event.exception, BoxbotException):
    await event.context.respond(event.exception.message, flags=hikari.MessageFlag.EPHEMERAL)
    return True # To tell the bot not to propogate this error event up the chain


class ChannelSelectView(miru.View):
  @miru.channel_select(
      placeholder="Exclude channels from processing",
      channel_types=[hikari.ChannelType.GUILD_TEXT],
      min_values=0,
      max_values=25
  )
  async def get_channels(self, ctx: miru.ViewContext, select: miru.ChannelSelect) -> None:
    settings: ServerConfig = plugin.bot.d.settings
    assert ctx.guild_id
    settings.set_excluded_channels(ctx.guild_id, select.values)
    await ctx.respond(f"Confirmed: {", ".join([ch.mention for ch in select.values])} will be excluded from processing.")

class RoleSelectView(miru.View):
  @miru.role_select(placeholder="Select elevated roles", min_values=1, max_values=25)
  async def get_roles(self, ctx: miru.ViewContext, select: miru.RoleSelect) -> None:
    if len(select.values) > 0:
      settings: ServerConfig = plugin.bot.d.settings
      assert ctx.guild_id
      settings.set_elevated_roles(ctx.guild_id, select.values)
      await ctx.respond(f"Confirmed: {[role.mention for role in select.values]}")

class LadleSelectView(miru.View):
  @miru.text_select(placeholder="Select active ladles",
                    min_values=1,
                    max_values=len(ladleOptions),
                    options=ladleOptions
                    )
  async def get_ladles(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
    if len(select.values) > 0:
      settings: ServerConfig = plugin.bot.d.settings
      assert ctx.guild_id
      settings.set_extractors(ctx.guild_id, select.values)
      await ctx.respond(f"Confirmed: {select.values} will be used")

def save_settings():
  settings: ServerConfig = plugin.bot.d.settings
  settings.save()

def load(bot: lb.BotApp) -> None:
  bot.add_plugin(plugin)
  bot.d.client = miru.Client(plugin.bot)

def unload(bot: lb.BotApp) -> None:
  bot.remove_plugin(plugin)