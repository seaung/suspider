#from functools import partial
from typing import Any, Dict, List
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from superspider.urls import Dom


class Downloader(object):
    def __init__(self, app: QApplication, checker_urls: List[Any] = []) -> None:
        self.app = app
        self.url = ""
        self.urls_result = checker_urls
        self.browser = dict()

    def _get_path(self, url: str) -> str:
        return url[0:url.rfind("/")]

    def _loader_finished(self, browser_id: Dict[QWebEngineView, bool]) -> None:
        web_view, _ = self.browser[browser_id]
        self.browser[browser_id] = (web_view, True)
        frame = web_view.page()
        dom = frame.toHtml()
        self.urls_result += parse_dom(dom, self.url)
        web_view.loadFinished(False)
        web_view.stop()

        if all([closed for _, closed in self.browser.values()]):
            self.app.quit()

    def run(self, urls: List[str]) -> List[Any | str]:
        for browser_id, url in enumerate(urls):
            self.url = self._get_path(url)
            web_view = QWebEngineView()
            web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, False)
            #loader = partial(self._loader_finished, browser_id)
            web_view.loadFinished(True)
            web_view.load(QUrl(url=url))
            self.browser[browser_id] = (web_view, False)

        return self.urls_result


def parse_dom(content: Any, url: str) -> List[str]:
    dom = Dom(content, url)
    return dom.get_url()

