import asyncio

from rich.traceback import install

import guajillo.app as app

install(show_locals=True)

if __name__ == "__main__":
    theapp = app.App()
    asyncio.run(theapp.run())
