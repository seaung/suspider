from functools import partial
from typing import Any, List


class Downloader(object):
    def __init__(self) -> None:
        pass

    def _get_path(self, url: str) -> str:
        return url

    def _loader_finished(self, browser_id, ok):
        pass

    def run(self, urls: List[str]) -> List[Any | str]:
        return []
