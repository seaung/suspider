from superspider.pipline import get_md5
from superspider.downloader import Downloader
from superspider.urls import Dom


class Crawler(object):
    def __init__(self, url: str) -> None:
        self.allow_urls = [url]
        self.checker_urls = []
        self.id = [0]

    def start(self) -> None:
        pass
