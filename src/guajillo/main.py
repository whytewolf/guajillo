import asyncio

from rich.traceback import install

import guajillo.app as app

install(show_locals=False)

if __name__ == "__main__":
    theapp = app.App()
    theapp.setup()
    asyncio.run(theapp.run())
