import hikari
import lightbulb
import logging

plugin = lightbulb.Plugin("Admin-plugin")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("shutdown", "Shut Solis down.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_shutdown(ctx: lightbulb.SlashContext) -> None:
    logging.info("Shutdown signal received")
    await ctx.respond("Now shutting down.")
    await ctx.bot.close()


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)