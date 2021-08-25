import asyncio
from aiosearchads import AioSearchAds


async def acls():
    core = AioSearchAds(token='')
    data = await core.acls()
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(acls()())
