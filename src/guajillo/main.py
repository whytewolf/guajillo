import asyncio

from rich.traceback import install

import guajillo.app as app

install(show_locals=False)


def main():
    theapp = app.App()
    theapp.setup()
    asyncio.run(theapp.run())


if __name__ == "__main__":
    main()
