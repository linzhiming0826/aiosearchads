
__all__ = ('AioSearchads')


import jwt
import aiohttp
import datetime


class AioSearchAds:
    def __init__(self, org_id='', client_id='', team_id='',  key_id='', private_key='', version='v4', token=''):
        '''init
        '''
        self.org_id = org_id
        self.client_id = client_id
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = private_key
        self.version = version
        self.token = token

    async def get_token(self):
        '''get token
        '''
        return await self.create_token()

    async def request(self, method, url, **kwargs):
        '''basic request
        '''
        async with aiohttp.request(method=method, url=url, **kwargs) as r:
            return await r.json(encoding='utf-8')

    def _get_client_secret(self):
        '''Get client_secret
        '''
        audience = 'https://appleid.apple.com'
        alg = 'ES256'
        issued_at_timestamp = int(datetime.datetime.utcnow().timestamp())
        expiration_timestamp = issued_at_timestamp + 86400*180
        headers = dict()
        headers['alg'] = alg
        headers['kid'] = self.key_id
        payload = dict()
        payload['sub'] = self.client_id
        payload['aud'] = audience
        payload['iat'] = issued_at_timestamp
        payload['exp'] = expiration_timestamp
        payload['iss'] = self.team_id
        client_secret = jwt.encode(
            payload=payload,
            headers=headers,
            algorithm=alg,
            key=self.private_key
        )
        return client_secret.decode("utf-8")

    async def create_token(self):
        '''Create token
        '''
        client_secret = self._get_client_secret()
        url = 'https://appleid.apple.com/auth/oauth2/token'
        headers = {'Host': 'appleid.apple.com',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        params = {'client_id': self.client_id, 'client_secret': client_secret,
                  'grant_type': 'client_credentials', 'scope': 'searchadsorg'}
        return await self.request('post', url, params=params, headers=headers)

    async def call(self, method, resource, **kwargs):
        '''basic call api method
        '''
        url = 'https://api.searchads.apple.com/api/%s/%s' % (
            self.version, resource)
        headers = {'Authorization': 'Bearer %s' % (
            self.token)}
        if self.org_id:
            headers['X-AP-Context'] = 'orgId=%s' % self.org_id
        if 'headers' in kwargs:
            kwargs['headers'] = {**headers, **kwargs['headers']}
        else:
            kwargs['headers'] = headers
        return await self.request(method=method.upper(), url=url, **kwargs)

    async def acls(self):
        '''Fetches roles and organizations that the API has access to.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_user_acl?changes=latest_major
        '''
        return await self.call('get', 'acls')

    async def search_apps(self, offset, limit, query, return_owned_apps='false'):
        '''Searches for iOS apps to promote in a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/search_for_ios_apps?changes=latest_major
        '''
        resource = 'search/apps'
        params = {'offset': offset, 'limit': limit,
                  'query': query, 'returnOwnedApps': return_owned_apps}
        return await self.call('get', resource, params=params)

    async def create_campaign(self, **kwargs):
        '''Creates a campaign to promote an app.
        docs: https://developer.apple.com/documentation/apple_search_ads/create_a_campaign?changes=latest_major
        '''
        resource = 'campaigns'
        data = {
            "orgId": self.org_id
        }
        return await self.call('post', resource, json={**data, **kwargs})

    async def find_campaigns(self, offset, limit, order_by=[], conditions=[]):
        '''Fetches campaigns with selector operators.
        docs: https://developer.apple.com/documentation/apple_search_ads/find_campaigns?changes=latest_major
        params:{
            "pagination": {
                "offset": 0,
                "limit": 1000
            },
            "orderBy": [
                {
                    "field": "id",
                    "sortOrder": "ASCENDING"
                }
            ],
            "conditions": [
                {
                    "field": "countriesOrRegions",
                    "operator": "CONTAINS_ALL",
                    "values": [
                        "US","CA"
                    ]
                }
            ]
        }
        '''
        resource = 'campaigns/find'
        data = {'pagination': {'offset': offset, 'limit': limit},
                'orderBy': order_by, 'conditions': conditions}
        return await self.call('post', resource, json=data)

    async def get_campaign(self, campaign_id):
        '''Fetches a specific campaign by campaign identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_a_campaign?changes=latest_major
        '''
        resource = 'campaigns/%s' % campaign_id
        return await self.call('get', resource)

    async def all_campaigns(self, offset, limit):
        '''Fetches all of an organization’s assigned campaigns.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_all_campaigns?changes=latest_major
        '''
        resource = 'campaigns'
        params = {'offset': offset, 'limit': limit}
        return await self.call('get', resource, params=params)

    async def update_campaigns(self, campaign_id, campaign, clear=True):
        '''Updates a campaign with a campaign identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_a_campaign?changes=latest_major
        '''
        resource = 'campaigns/%s' % campaign_id
        data = {
            "clearGeoTargetingOnCountryOrRegionChange": clear,
            "campaign": campaign
        }
        return await self.call('put', resource, json=data)

    async def delete_campaign(self, campaign_id):
        '''Deletes a specific campaign by campaign identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/delete_a_campaign?changes=latest_major
        '''
        resource = 'campaigns/%s' % campaign_id
        return await self.call('delete', resource)

    async def create_adgroup(self, campaign_id, **kwargs):
        '''Creates an ad group as part of a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/create_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups' % campaign_id
        data = {
            "campaignId": campaign_id,
            "orgId": self.org_id,
        }
        return await self.call('post', resource, json={**data, **kwargs})

    async def find_adgroups(self, campaign_id, offset, limit, order_by, conditions):
        '''Fetches ad groups within a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_ad_groups?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/find' % campaign_id
        data = {'pagination': {'offset': offset, 'limit': limit},
                'orderBy': order_by, 'conditions': conditions}
        return await self.call('post', resource, json=data)

    async def get_adgroup(self, campaign_id, adgroup_id):
        '''Fetches a specific ad group with a campaign and ad group identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s' % (campaign_id, adgroup_id)
        return await self.call('get', resource)

    async def all_adgroups(self, campaign_id, offset, limit):
        '''Fetches all ad groups with a campaign identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_all_ad_groups?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups' % (campaign_id)
        params = {'offset': offset, 'limit': limit}
        return await self.call('get', resource, params=params)

    async def update_adgroup(self, campaign_id, adgroup_id, name, cpa, start_time, end_time, auto, model, amount, dimensions):
        '''Updates an ad group with an ad group identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s' % (campaign_id, adgroup_id)
        data = {
            "name": name,
            "cpaGoal": cpa,
            "startTime": start_time,
            "endTime": end_time,
            "automatedKeywordsOptIn": auto,
            "defaultBidAmount": amount,
            "pricingModel": model,
            "targetingDimensions": dimensions
        }
        return await self.call('put', resource, json=data)

    async def update_adgroup_2(self, campaign_id, adgroup_id, name, auto, amount, status, kwargs):
        '''Updates an ad group with an ad group identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s' % (campaign_id, adgroup_id)
        data = {
            "name": name,
            "automatedKeywordsOptIn": auto,
            "defaultBidAmount": amount,
            "status": status
        }
        return await self.call('put', resource, json={**data, **kwargs})

    async def delete_adgroup(self, campaign_id, adgroup_id):
        '''Deletes an ad group with a campaign and ad group identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/delete_an_adgroup?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s' % (campaign_id, adgroup_id)
        return await self.call('delete', resource)

    async def create_targeting_keywords(self, campaign_id, adgroup_id, words):
        '''Creates targeting keywords in ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/create_targeting_keywords?changes=latest_major
        words:[{
                "text": "targeting keyword example 1",
                "matchType": "BROAD",
                "bidAmount": {
                "amount": "100",
                "currency": "USD"
                }
            },
            {
                "text": "targeting keyword example 2",
                "matchType": "EXACT",
                "bidAmount": {
                "amount": "100",
                "currency": "USD"
                }
            }]
        '''
        resource = 'campaigns/%s/adgroups/%s/targetingkeywords/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=words)

    async def find_targeting_keywords(self, campaign_id, offset, limit, order_by, conditions):
        '''Fetches targeting keywords in a campaign’s ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_targeting_keywords_in_a_campaign?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/targetingkeywords/find' % (
            campaign_id)
        data = {'pagination': {'offset': offset, 'limit': limit},
                'orderBy': order_by, 'conditions': conditions}
        return await self.call('post', resource, json=data)

    async def get_targeting_keyword(self, campaign_id, adgroup_id, keyword_id):
        '''Fetches a specific targeting keyword in an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_a_targeting_keyword_in_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/targetingkeywords/%s' % (
            campaign_id, adgroup_id, keyword_id)
        return await self.call('get', resource)

    async def all_targeting_keywords(self, campaign_id, adgroup_id, offset, limit):
        '''Fetches all targeting keywords in ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_all_targeting_keywords_in_an_ad_group?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/targetingkeywords' % (
            campaign_id, adgroup_id)
        params = {'offset': offset, 'limit': limit}
        return await self.call('get', resource, params=params)

    async def update_targeting_keywords(self, campaign_id, adgroup_id, keywords):
        '''Updates targeting keywords in ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_targeting_keywords?changes=latest_major
        keywords:[{
                    "id": "542370642",
                    "status": "PAUSED",
                    "bidAmount": {
                        "amount”: "100",
                        "currency": "USD"
                        }
                    }]
        '''
        resource = 'campaigns/%s/adgroups/%s/targetingkeywords/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('put', resource, json=keywords)

    async def create_negative_keywords(self, campaign_id, keywords):
        '''Creates negative keywords for a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/create_campaign_negative_keywords?changes=latest_major
        keywords:[{
                        "text": "create campaign negative keyword example 1",
                        "matchType": "EXACT"
                    }]
        '''
        resource = 'campaigns/%s/negativekeywords/bulk' % (campaign_id)
        return await self.call('post', resource, json=keywords)

    async def find_negative_keywords(self, campaign_id, offset, limit, order_by, conditions):
        '''Fetches negative keywords for campaigns.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_campaign_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/negativekeywords/find' % campaign_id
        data = {'pagination': {'offset': offset, 'limit': limit},
                'orderBy': order_by, 'conditions': conditions}
        return await self.call('post', resource, json=data)

    async def get_negative_keyword(self, campaign_id, keyword_id):
        '''Fetches a specific negative keyword in a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_a_campaign_negative_keyword?changes=latest_major
        '''
        resource = 'campaigns/%s/negativekeywords/%s' % (
            campaign_id, keyword_id)
        return await self.call('post', resource)

    async def all_negative_keywords(self, campaign_id, offset, limit):
        '''Fetches all negative keywords in a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_all_campaign_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/negativekeywords' % campaign_id
        params = {'offset': offset, 'limit': limit}
        return await self.call('get', resource, params=params)

    async def update_negative_keywords(self, campaign_id, keywords):
        '''Updates negative keywords in a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_campaign_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/negativekeywords/bulk' % (campaign_id)
        return await self.call('put', resource, json=keywords)

    async def delete_negative_keywords(self, campaign_id, keyword_ids):
        '''Deletes negative keywords from a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/delete_campaign_negative_keywords?changes=latest_major
        keyword_ids:[
                    <keywordId>,
                    <keywordId>,
                    <keywordId>
                    ]
        '''
        resource = 'campaigns/%s/negativekeywords/delete/bulk' % (campaign_id)
        return await self.call('post', resource, json=keyword_ids)

    async def create_adgroup_negative_keywords(self, campaign_id, adgroup_id, keywords):
        '''Creates negative keywords in a specific ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/create_ad_group_negative_keywords?changes=latest_major
        keywords:[{
                    "text": "ad group negative keyword 1",
                    "matchType": "BROAD"
                }]
        '''
        resource = 'campaigns/%s/adgroups/%s/negativekeywords/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=keywords)

    async def find_adgroup_negative_keywords(self, campaign_id, offset, limit, order_by, conditions):
        '''Fetches negative keywords in a campaign’s ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_ad_group_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/negativekeywords/find' % campaign_id
        data = {'pagination': {'offset': offset, 'limit': limit},
                'orderBy': order_by, 'conditions': conditions}
        return await self.call('post', resource, json=data)

    async def get_adgroup_negative_keyword(self, campaign_id, adgroup_id, keyword_id):
        '''Fetches a specific negative keyword in an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_an_ad_group_negative_keyword?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/negativekeywords/%s' % (
            campaign_id, adgroup_id, keyword_id)
        return await self.call('get', resource)

    async def all_adgroup_negative_keywords(self, campaign_id, adgroup_id, offset, limit):
        '''Fetches all negative keywords in ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_all_ad_group_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/negativekeywords' % (
            campaign_id, adgroup_id)
        params = {'offset': offset, 'limit': limit}
        return await self.call('get', resource, params=params)

    async def update_adgroup_negative_keywords(self, campaign_id, adgroup_id, keywords):
        '''Updates negative keywords in an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_ad_group_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/negativekeywords/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('put', resource, json=keywords)

    async def delete_adgroup_negative_keywords(self, campaign_id, adgroup_id, keyword_ids):
        '''Deletes negative keywords from an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/delete_ad_group_negative_keywords?changes=latest_major
        '''
        resource = 'campaigns/%s/adgroups/%s/negativekeywords/delete/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=keyword_ids)

    async def search_geolocations(self, country_code, entity, query, offset, limit):
        '''Fetches a list of geolocations for audience refinement.
        docs:https://developer.apple.com/documentation/apple_search_ads/search_for_geolocations?changes=latest_major
        '''
        resource = 'search/geo'
        params = {'countrycode': country_code, 'entity': entity,
                  'limit': limit, 'offset': offset, 'query': query}
        return await self.call('get', resource, params=params)

    async def get_geolocations(self, offset, limit, data):
        '''Gets geolocation details using a geoidentifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_a_list_of_geolocations?changes=latest_major
        data:[{
                "id": "US|CA|Cupertino",
                "entity": "locality",
                "displayName": "Cupertino, California, United States"
                }]
        '''
        resource = 'search/geo'
        params = {'limit': limit, 'offset': offset}
        return await self.call('get', resource, params=params, json=data)

    async def get_creativeappassets(self, adam_id, data):
        '''Fetches assets to use with Creative Sets.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_app_language_device_sizes_and_asset_details
        '''
        resource = 'creativeappassets/%s' % adam_id
        return await self.call('get', resource, json=data)

    async def get_creativeappmappings_devices(self):
        '''Fetches supported app preview device size mappings.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_app_preview_device_sizes
        '''
        resource = 'creativeappmappings/devices'
        return await self.call('get', resource)

    async def create_adgroup_creativesets(self, campaign_id, adgroup_id, data):
        '''Creates a Creative Set and assigns it to an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/create_ad_group_creative_sets
        data:{
                "creativeSet": {
                    "adamId": 427916203,
                    "name": "Create ad group creative set example",
                    "languageCode": "en-US",
                    "assetsGenIds”: [
                    "<assetsGenId>",
                    "<assetsGenId>",
                    "<assetsGenId>",
                    "<assetsGenId>"
                    ]
                }
            }
        '''
        resource = 'campaigns/%s/adgroups/%s/adgroupcreativesets/creativesets' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=data)

    async def find_adgroup_creativesets(self, campaign_id, data):
        '''Fetches all assigned Creative Sets for ad groups.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_ad_group_creative_sets
        '''
        resource = 'campaigns/%s/adgroupcreativesets/find' % campaign_id
        return await self.call('post', resource, json=data)

    async def update_adgroup_creativesets(self, campaign_id, adgroup_id, adgroup_creativeset_id, data):
        '''Updates an ad group Creative Set using an identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_ad_group_creative_sets
        '''
        resource = 'campaigns/%s/adgroup/%s/adgroupcreativeset/%s' % (
            campaign_id, adgroup_id, adgroup_creativeset_id)
        return await self.call('put', resource, json=data)

    async def delete_adgroup_creativesets(self, campaign_id, adgroup_id, adgroup_creativeset_ids):
        '''Deletes Creative Sets from a specified ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/delete_ad_group_creative_sets
        ids:[542317136,542317137,542317138,542317139]
        '''
        resource = 'campaigns/%s/adgroups/%s/adgroupcreativesets/delete/bulk' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=adgroup_creativeset_ids)

    async def get_creativeset_ad_variation(self, creativeset_id, include_deleted_creativeset_assets='true'):
        '''Fetches asset details of a Creative Set ad variation.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_a_creative_set_ad_variation
        '''
        resource = 'creativesets/%s' % creativeset_id
        params = {
            'includeDeletedCreativeSetAssets': include_deleted_creativeset_assets}
        return await self.call('get', resource, params=params)

    async def find_creativesets(self, data):
        '''Fetches all assigned Creative Sets for an organization.
        docs:https://developer.apple.com/documentation/apple_search_ads/find_creative_sets
        '''
        resource = 'creativesets/find'
        return await self.call('post', resource, json=data)

    async def assign_creativesets_to_adgroup(self, campaign_id, adgroup_id, data):
        '''Creates a Creative Set assignment to an ad group.
        docs:https://developer.apple.com/documentation/apple_search_ads/assign_creative_sets_to_an_ad_group
        '''
        resource = 'campaigns/%s/adgroups/%s/adgroupcreativesets' % (
            campaign_id, adgroup_id)
        return await self.call('post', resource, json=data)

    async def update_creativesets(self, creativeset_id, data):
        '''Updates a Creative Set name using an identifier.
        docs:https://developer.apple.com/documentation/apple_search_ads/update_creative_sets
        '''
        resource = 'creativesets/%s' % creativeset_id
        return await self.call('put', resource, json=data)

    async def get_campaign_level_reports(self, data):
        '''Fetches reports for campaigns.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_campaign-level_reports?changes=latest_major
        data:{
                "startTime": "2020-04-08",
                "endTime": "2020-04-09",
                "selector": {
                    "orderBy": [
                        {
                            "field": "countryOrRegion",
                            "sortOrder": "ASCENDING"
                        }
                    ],
                    "conditions": [
                        {
                            "field": "countriesOrRegions",
                            "operator": "CONTAINS_ANY",
                            "values": [
                                "US",
                                "GB"
                            ]
                        },
                        {
                            "field": "countryOrRegion",
                            "operator": "IN",
                            "values": [
                                "US"
                            ]
                        }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": 1000
                    }
                },
                "groupBy": [
                    "countryOrRegion"
                ],
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": true,
                "returnRowTotals": true,
                "returnGrandTotals": true
            }
        '''
        resource = 'reports/campaigns'
        return await self.call('post', resource, json=data)

    async def get_adgroup_level_reports(self, campaign_id, data):
        '''Fetches reports for targeting keywords within a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_keyword-level_reports
        data:{
                "returnRowTotals": true,
                "granularity": "DAILY",
                "timeZone": "UTC",
                "returnGrandTotals": true,
                "startTime": "2020-04-08",
                "selector": {
                    "orderBy": [
                    {
                        "field": "localSpend",
                        "sortOrder": "ASCENDING"
                    }
                    ],
                    "conditions": [
                    {
                        "field": "deleted",
                        "operator": "IN",
                        "values": [
                        "false",
                        "true"
                        ]
                    }
                    ],
                    "pagination": {
                    "offset": 0,
                    "limit": 1000
                    }
                },
                "endTime": "2020-04-09",
                "returnRecordsWithNoMetrics": true
            }
        '''
        resource = 'reports/campaigns/%s/adgroups' % campaign_id
        return await self.call('post', resource, json=data)

    async def get_keyword_level_reports(self, campaign_id, data):
        '''Fetches reports for targeting keywords within a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_keyword-level_reports
        data:{
                "returnRowTotals": true,
                "granularity": "DAILY",
                "timeZone": "UTC",
                "returnGrandTotals": true,
                "startTime": "2020-04-08",
                "selector": {
                    "orderBy": [
                    {
                        "field": "localSpend",
                        "sortOrder": "ASCENDING"
                    }
                    ],
                    "conditions": [
                    {
                        "field": "deleted",
                        "operator": "IN",
                        "values": [
                        "false",
                        "true"
                        ]
                    }
                    ],
                    "pagination": {
                    "offset": 0,
                    "limit": 1000
                    }
                },
                "endTime": "2020-04-09",
                "returnRecordsWithNoMetrics": true
            }
        '''
        resource = 'reports/campaigns/%s/keywords' % campaign_id
        return await self.call('post', resource, json=data)

    async def get_search_term_level_reports(self, campaign_id, data):
        '''Fetches reports for search terms within a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_search_term-level_reports
        data:{
                "startTime": "2020-04-08",
                "endTime": "2020-04-09",
                "timeZone": "ORTZ",
                "selector": {
                    "orderBy": [
                        {
                            "field": "impressions",
                            "sortOrder": "DESCENDING"
                        }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": 1000
                    }
                },
                "groupBy": [
                    "countryOrRegion"
                ],
                "returnRecordsWithNoMetrics": "false",
                "returnRowTotals": true,
                "returnGrandTotals": true
            }
        '''
        resource = 'reports/campaigns/%s/searchterms' % campaign_id
        return await self.call('post', resource, json=data)

    async def get_creative_set_level_reports(self, campaign_id, data):
        '''Fetches reports for Creative Sets within a campaign.
        docs:https://developer.apple.com/documentation/apple_search_ads/get_creative_set-level_reports
        data:{
                "startTime": "2020-04-08",
                "endTime": "2020-04-09",
                "selector": {
                    "orderBy": [
                        {
                            "field": "countryOrRegion",
                            "sortOrder": "ASCENDING"
                        }
                    ],
                    "conditions": [
                        {
                        "field": "countryOrRegion",
                        "operator": "EQUALS",
                        "values": [
                            "US"
                        ]
                    }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": 1000
                    }
                },
                "groupBy": [
                    "countryOrRegion"
                ],
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": false,
                "returnRowTotals": true,
                "returnGrandTotals": true
            }
        '''
        resource = 'reports/campaigns/%s/creativesets' % campaign_id
        return await self.call('post', resource, json=data)
