from functools import partial
from typing import Any, List


class Downloader(object):
    def __init__(self, app: Any, checker_urls: List[Any] = []) -> None:
        self.app = app
        self.url = ""
        self.urls_result = checker_urls
        self.browser = dict()

    def _get_path(self, url: str) -> str:
        return url[0:url.rfind("/")]

    def _loader_finished(self, browser_id) -> None:
        web_view, _ = self.browser[browser_id]
        self.browser[browser_id] = (web_view, True)

    def run(self, urls: List[str]) -> List[Any | str]:
        for browser_id, url in enumerate(urls):
            self.url = self._get_path(url)
        return []
