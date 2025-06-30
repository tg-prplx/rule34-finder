import json
import requests as rq
import webbrowser as webb
import logging as log
from config import RULE_34_BACKEND_URL, IMAGE_PLACEHOLDER_URL

class Rule34NewForAnimeGooners:
    def __init__(self):
        self.BASE_URL = RULE_34_BACKEND_URL
        self.IMAGE_PLACEHOLDER_URL = IMAGE_PLACEHOLDER_URL
        self.additional_tags = "-furry -futanari -tentacles -guro -trap -scat -vore"
        self.session = rq.Session()

    def get_link_from_data(self, data: dict, iid: int):
        cur_img = data[iid] if iid < len(data) else data[0]
        if cur_img.get('sample'):
            return cur_img.get('sample_url', self.IMAGE_PLACEHOLDER_URL)
        else:
            log.info("No sample image found, using file URL.")
            return cur_img.get('file_url', self.IMAGE_PLACEHOLDER_URL)

    def sort_data(self, data: dict) -> dict:
        try:
            return sorted(data, key=lambda x: x.get('comment_count', 0), reverse=True)
        except:
            log.warning("Sorting failed, returning data as is.")
            return data

    def make_rule34_request(self, tags: str, limit: int = 50, iid: int = 0, pid: int = 0, open_in_browser: bool = False) -> dict:
        all_tags = f"{tags} {self.additional_tags}".strip()
        params = {
            "page": "dapi",
            "s":    "post",
            "q":    "index",
            "pid":  pid,
            "json": 1,
            "limit": limit,
            "tags": all_tags
        }
        r = self.session.get(self.BASE_URL, params=params, timeout=10)
        if not 200 <= r.status_code < 300:
            raise Exception(f'Invalid request: {r.status_code}')
        try:
            data = r.json()
        except Exception as e:
            log.error("Failed to parse JSON response: %s", e)
            return {}

        if not isinstance(data, list) or not data:
            return self.IMAGE_PLACEHOLDER_URL

        data = self.sort_data(data)
        url = self.get_link_from_data(data, iid)
        
        log.info(f"Request successful: {len(data)} results found for tags '{all_tags}'.")

        if open_in_browser:
            try:
                log.info(f"Opening URL in browser: {url}")
                webb.open(url)
            except Exception as e:
                log.error(f"Failed to open URL in browser: {e}")
            else:
                log.info("URL opened successfully in browser.")

        return data
