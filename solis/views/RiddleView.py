import hikari
import miru
from hikari import GuildMessageCreateEvent


class RiddleView(miru.View):

    def __init__(self, event: GuildMessageCreateEvent, timeout: float):
        super().__init__(timeout=timeout)
        self.event = event

    @miru.button(label="", emoji="✅", style=hikari.ButtonStyle.PRIMARY)
    async def is_playing_riddle(self, button: miru.Button, ctx: miru.Context) -> None:
        print("done with riddle")
        self.stop()

    @miru.button(label="", emoji="✖️", style=hikari.ButtonStyle.DANGER)
    async def stop_riddle(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.respond("Okay maybe next time!", components=[])
        self.stop()
