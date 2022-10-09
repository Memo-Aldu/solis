import hikari
import miru


class ButtonView(miru.View):

    @miru.button(label="test", emoji="✅", style=hikari.ButtonStyle.PRIMARY)
    async def test_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.respond("Test Completed!")

    @miru.button(label="close", emoji="✖️", style=hikari.ButtonStyle.DANGER)
    async def close_test(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.respond("The menu was closed", components=[])
        self.stop()
