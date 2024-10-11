import asyncio

import guajillo.app as app

if __name__ == "__main__":
    theapp = app.App()
    asyncio.run(theapp.run())
