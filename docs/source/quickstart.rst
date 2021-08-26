.. _quickstart:

Quickstart
==========

.. currentmodule:: aiosearchads

It's time to write your first example. This guide assumes you have a working
understanding of `aiohttp <https://github.com/aio-libs/aiohttp>`_, and that you have already
installed both aiohttp and Aiosearchads.  If not, then follow the steps in the
:ref:`installation` section.

A Minimal Example
-----------------

A minimal Aiosearchads example looks like this: ::

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


Acls
-----

Fetches roles and organizations that the API has access to Looks like this: ::

    import asyncio
    from aiosearchads import AioSearchAds


    async def acls():
        core = AioSearchAds(token='')
        data = await core.acls()
        print(data)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(acls()())


Find Campaigns
-----

Fetches campaigns with selector operators and return results looks like this: ::

    import asyncio
    from aiosearchads import AioSearchAds


    async def find_campaigns():
        core = AioSearchAds(org_id='', token='')
        # can by it
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


Other
-----

Call an action and return results looks like this: ::

    import asyncio
    from aiosearchads import AioSearchAds


    async def do():
        core = AioSearchAds(org_id='', token='')
        resource = 'campaigns/%s/adgroups/%s/targetingkeywords' % (
            campaign_id, adgroup_id)
        params = {'offset': 0, 'limit': 10}
        return await self.call('get', resource, params=params)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(do())