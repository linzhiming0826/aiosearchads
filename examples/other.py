import asyncio
from aiosearchads import AioSearchAds


async def find_campaigns():
    # can by it
    core = AioSearchAds(org_id='', token='')
    data = await core.find_campaigns(0, 100)
    print(data)
    # can by it
    resource = 'campaigns/find'
    data = {'pagination': {'offset': 0, 'limit': 100},
            'orderBy': [], 'conditions': []}
    data = await core.call('post', resource, json=data)
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(find_campaigns())
