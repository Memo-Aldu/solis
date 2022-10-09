import hikari
import asyncio
from solis.bot import bot


async def on_riddle(event_riddle_message: hikari.Message) -> None:
    timer = 60  # seconds
    is_correct_answer = False
    async with bot.d.session.get(
            "https://ibk-riddles-api.herokuapp.com/"
    ) as response:
        api_res = await response.json()

        if response.ok:
            question = api_res["question"]
            answer = (api_res["answer"]).lower().strip(",.! ")
            print(answer)
            embed = hikari.Embed(colour=0xCCEE44)
            embed.set_author(name=question)
            embed.add_field("Time left ", str(timer) + "s", inline=True)
            embed.set_footer(
                text=f"Requested by {event_riddle_message.member.display_name}",
                icon=event_riddle_message.member.avatar_url or event_riddle_message.member.default_avatar_url,
            )
            resp = await event_riddle_message.respond(embed)
            while True:
                if timer == 0:
                    embed.edit_field(0, "Time is up!", ":c")
                    embed.add_field("The answer is", "||" + answer + "||", inline=True)
                    break
                embed.edit_field(0, "Time left: ", str(timer) + "s")
                await resp.edit(embed=embed)
                try:
                    await bot.wait_for(
                        hikari.MessageCreateEvent,
                        timeout=1,
                        predicate=lambda new_event:
                        isinstance(new_event, hikari.MessageCreateEvent)
                        and new_event.message.author == event_riddle_message.author
                        and new_event.message.channel_id == event_riddle_message.channel_id
                        and answer.lower() == new_event.message.content.lower()
                    )
                except asyncio.TimeoutError:
                    timer -= 1
                else:
                    is_correct_answer = True
                    embed.add_field("The answer is", "||" + answer + "||", inline=True)
                    break
            if is_correct_answer:
                await resp.edit(f"{event_riddle_message.author.mention} You guessed right!", embed=embed, components=[])
            else:
                await resp.edit(f"{event_riddle_message.author.mention} Your countdown Has ended!", embed=embed,
                                components=[])
