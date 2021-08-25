import asyncio
from aiosearchads import AioSearchAds


async def create_token():
    client_id = '***'
    team_id = '***'
    key_id = '***'
    private_key = '''
-----BEGIN EC PRIVATE KEY-----
***
-----END EC PRIVATE KEY-----
    '''
    core = AioSearchAds(client_id=client_id, team_id=team_id,
                        key_id=key_id, private_key=private_key)
    data = await core.create_token()
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(create_token())
