


## Aiosearchads

### Asynchronous apple searchads framework for asyncio and Python

## Document

[click me](https://aiosearchads.readthedocs.io)

## Installation
```linux
pip install aiosearchads
```

## Simple uses
```python
import asyncio
from aiosearchads import AioSearchAds


async def find_campaigns():
    core = AioSearchAds(org_id='', token='')
    data = await core.find_campaigns(0, 100)
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(find_campaigns())

```
