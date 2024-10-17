import asyncio

import guajillo.app as app
from rich.traceback import install

install(show_locals=True)

if __name__ == "__main__":
    theapp = app.App()
    asyncio.run(theapp.run())
