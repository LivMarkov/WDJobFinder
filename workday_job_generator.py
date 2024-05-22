from workday_job import WDJob

from typing import Dict, Union, Iterator

import requests
from requests.cookies import RequestsCookieJar

class WDJobGenerator:
    QUERY_LIMIT = 20

    def __init__(self,
                 base_careers_site_address: str,
                 careers_page_name: str,
                 wd_company_name: str,
                 position_filter: dict) -> None:
        self._base_careers_site_address = base_careers_site_address
        self._careers_page_name = careers_page_name
        self._wd_company_name = wd_company_name
        self._position_filter = position_filter

    def get_careers_url(self) -> str:
        return f'{self._base_careers_site_address}/{self._careers_page_name}'

    def get_site_cookies(self) -> RequestsCookieJar:
        return requests.get(self.get_careers_url()).cookies

    def generate_headers(self, calypso_token: str) -> Dict[str, str]:
        return {
            'Accept': 'application/json',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': self._base_careers_site_address,
            'Referer': self.get_careers_url(),
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.'
                          '0.0.0 Safari/537.36',
            'X-Calypso-Csrf-Token': calypso_token
        }

    @staticmethod
    def generate_payload(limit: int, offset: int, position_filter: dict) -> Dict[str, Union[str, int]]:
        return {"appliedFacets": position_filter, "limit": limit, "offset": offset, "searchText": ""}

    def get_job_api_url(self) -> str:
        return f'{self._base_careers_site_address}/wday/cxs/{self._wd_company_name}/{self._careers_page_name}/jobs'

    def get_job_details_url(self, job_url_suffix: str) -> str:
        return f'{self._base_careers_site_address}/wday/cxs/{self._wd_company_name}/{self._careers_page_name}/{job_url_suffix}'

    def get_position_data(self, site_cookies: RequestsCookieJar, job_url_suffix: str) -> dict:
        headers = self.generate_headers(calypso_token=site_cookies['CALYPSO_CSRF_TOKEN'])
        position_details_response = requests.get(self.get_job_details_url(job_url_suffix), headers=headers,
                                                 cookies=site_cookies)
        return position_details_response.json()

    def __iter__(self) -> Iterator[WDJob]:
        site_cookies: RequestsCookieJar = self.get_site_cookies()

        headers = self.generate_headers(calypso_token=site_cookies['CALYPSO_CSRF_TOKEN'])
        data = self.generate_payload(limit=self.QUERY_LIMIT, offset=0, position_filter=self._position_filter)

        job_query_response = requests.post(self.get_job_api_url(), headers=headers, json=data, cookies=site_cookies)
        jobs = job_query_response.json()

        position_count = jobs['total']
        for position in jobs['jobPostings']:
            try:
                position_data = self.get_position_data(site_cookies, position['externalPath'])
                yield WDJob(title=position['title'],
                            location=position['locationsText'],
                            url=self.get_job_details_url(position['externalPath']),
                            description=position_data['jobPostingInfo']['jobDescription'])
            except requests.exceptions.RequestException as e:
                print(f'exception occurred with {position=}, error:\n{e}')

        for offset in range(self.QUERY_LIMIT, position_count, self.QUERY_LIMIT):
            data = self.generate_payload(limit=self.QUERY_LIMIT, offset=offset, position_filter=self._position_filter)
            job_query_response = requests.post(self.get_job_api_url(), headers=headers, json=data,
                                               cookies=site_cookies)
            jobs = job_query_response.json()
            for position in jobs['jobPostings']:
                try:
                    position_data = self.get_position_data(site_cookies, position['externalPath'])
                    yield WDJob(title=position['title'],
                                location=position['locationsText'],
                                url=self.get_job_details_url(position['externalPath']),
                                description=position_data['jobPostingInfo']['jobDescription'])
                except requests.exceptions.RequestException as e:
                    print(f'exception occur with {position=}, error:\n{e}')