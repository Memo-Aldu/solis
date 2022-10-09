from __future__ import annotations

import asyncio
import hikari
import lightbulb
import logging
import miru
import config
import solis.helper.riddle
from solis.views.view import ButtonView
from __init__ import __version__
from aiohttp import ClientSession
from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler

is_playing_riddle = False


def setup() -> None:
    logging.info("Running bot setup...")


bot = lightbulb.BotApp(
    token=config.token,
    default_enabled_guilds=config.DEFAULT_GUILD_ID,
    owner_ids=config.OWNERS_ID,
    help_slash_command=True,
    case_insensitive_prefix_commands=True,
    prefix="!",
    intents=hikari.Intents.ALL

)
bot.d.scheduler = AsyncIOScheduler()
bot.d.scheduler.configure(timezome=utc)
bot.load_extensions_from("../solis/extensions")
miru.load(bot)


@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.scheduler.start()
    bot.d.session = ClientSession(trust_env=True)
    logging.info("AIOHTTP session started")


@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    await bot.rest.create_message(
        config.TEST_CHANNEL_ID,
        f"Solis is now online! (Version {__version__})"
    )


@bot.listen(hikari.StoppingEvent)
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.session.close()
    logging.info("AIOHTTP session closed")
    bot.d.scheduler.shutdown()
    await bot.rest.create_message(
        config.TEST_CHANNEL_ID,
        f"Solis is shutting down. (Version {__version__})"
    )


@bot.listen(hikari.DMMessageCreateEvent)
async def on_pm_message_create(event: hikari.DMMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return

    await event.message.respond(
        f"You need to DM <@{config.BOT_OWNER}> to send a message to moderators."
    )


@bot.command
@lightbulb.command('ping', 'say pong!')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond(
        f"Pong! DWSP latency: {ctx.bot.heartbeat_latency * 1_000:,.0f} ms.")


@bot.command
@lightbulb.command('button', 'button test')
@lightbulb.implements(lightbulb.SlashCommand)
async def button(ctx: lightbulb.SlashContext):
    view = ButtonView(timeout=60)
    message = await ctx.respond("Button test", components=view.build())
    message = await message
    view.start(message)
    await view.wait()
    print("All done.")


def run() -> None:
    setup()
    bot.run(
        activity=hikari.Activity(
            name=f"/help | Version {__version__}",
            type=hikari.ActivityType.WATCHING
        )
    )


# Bot is listening to the specified guilds
@bot.listen(hikari.GuildMessageCreateEvent)
async def on_guild_message_event(event: hikari.GuildMessageCreateEvent) -> None:
    event_author = event.message.author
    message = event.message

    global is_playing_riddle
    if event_author.is_bot or not message.content:
        return

    if any(e in message.content.lower().split(" ") or i in message.content.lower()
           for e in {"gm", "gm!", "goodmorning"}
           for i in {"good morning", "morning everyone"}):
        await message.respond("Good morning! " + event_author.mention,
                              user_mentions=True,
                              mentions_reply=True)

    if any(e in message.content.lower().split(" ") or i in message.content.lower()
           for e in {"gn", "gn!", "goodnight"}
           for i in {"good night", "night everyone"}):
        await message.respond("Good night! " + event_author.mention,
                              user_mentions=True,
                              mentions_reply=True)

    if any(e in message.content.lower().split(" ") for e in
           {"riddle", "teaser", "riddles", "teasers"}) and is_playing_riddle is False \
            and message.content != "!fun riddle" and message.content != "/fun riddle":
        resp = await message.respond("Did someone mention a riddle? :eyes: " + event_author.mention,
                                     user_mentions=True,
                                     mentions_reply=True)
        await resp.add_reaction("❌")
        await resp.add_reaction("✅")
        is_playing_riddle = True
        try:
            reaction = await bot.wait_for(
                hikari.ReactionAddEvent,
                timeout=10,
                predicate=lambda new_event:
                isinstance(new_event, hikari.ReactionEvent)
                and new_event.user_id == event_author.id
                and str(new_event.emoji_name) in {"❌", "✅"}
            )
            if reaction.emoji_name == "✅":
                await resp.remove_reaction(emoji="❌")
                await solis.helper.riddle.on_riddle(message)
                is_playing_riddle = False
            else:
                await resp.remove_reaction(emoji="✅")
                await resp.edit("Okay maybe next time!")
                is_playing_riddle = False

        except asyncio.TimeoutError:
            is_playing_riddle = False
            await message.respond("The riddle timed out :c")


@bot.listen(lightbulb.CommandErrorEvent)
async def on_command_error(event: lightbulb.CommandErrorEvent) -> None:
    exc = getattr(event.exception, "__cause__", event.exception)

    if isinstance(exc, lightbulb.NotOwner):
        await event.context.respond("You need to be an owner to do that.")
        return
    raise event.exception


