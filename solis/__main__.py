import os
import bot
if os.name != "nt":
    import uvloop

    uvloop.install()
if __name__ == "__main__":
    bot.run()