import os
from solis.bot import bot
if os.name != "nt":
    import uvloop

    uvloop.install()
if __name__ == "__main__":
    bot.run()