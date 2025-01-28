from functools import partial
import sys
from typing import Any, Dict, List, Tuple
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage

from superspider.urls import Dom


class Downloader(object):
    def __init__(self, app: QApplication, checker_urls: List[Any] = [], timeout: int = 30, max_concurrent: int = 3) -> None:
        """初始化下载器对象。

        Args:
            app: QApplication实例
            checker_urls: 已检查过的URL列表
            timeout: 超时时间（秒）
            max_concurrent: 最大并发下载数
        """
        self.app = app
        self.url = ""
        self.urls_result = checker_urls
        self.browser: Dict[int, Tuple[QWebEngineView, bool]] = dict()
        self.timeout = timeout * 1000  # 转换为毫秒
        self.max_concurrent = max_concurrent
        self.pending_urls: List[str] = []

    def _get_path(self, url: str) -> str:
        """获取URL的路径部分。

        Args:
            url: 完整的URL字符串

        Returns:
            str: URL的路径部分
        """
        return url[0:url.rfind("/")]

    def _handle_timeout(self, browser_id: int) -> None:
        """处理浏览器加载超时。

        Args:
            browser_id: 浏览器实例ID
        """
        if browser_id in self.browser:
            web_view, _ = self.browser[browser_id]
            print(f"Loading timeout for URL: {self.url}")
            web_view.stop()
            self._cleanup_browser(browser_id)

    def _handle_load_error(self, browser_id: int, error_code: int) -> None:
        """处理页面加载错误。

        Args:
            browser_id: 浏览器实例ID
            error_code: 错误代码
        """
        print(f"Loading error {error_code} for URL: {self.url}")
        self._cleanup_browser(browser_id)

    def _cleanup_browser(self, browser_id: int) -> None:
        """清理浏览器实例。

        Args:
            browser_id: 浏览器实例ID
        """
        if browser_id in self.browser:
            web_view, _ = self.browser[browser_id]
            web_view.deleteLater()
            del self.browser[browser_id]
            if not self.browser:
                self.app.quit()

    def _loader_finished(self, browser_id: int, success: bool) -> None:
        if not success:
            self._handle_load_error(browser_id, 0)
            return

        if browser_id not in self.browser:
            return

        web_view, _ = self.browser[browser_id]
        self.browser[browser_id] = (web_view, True)

        def handle_html_ready(html: str) -> None:
            try:
                dom = html.encode("utf-8")
                print(f"正在解析页面: {self.url}")
                parsed_urls = parse_dom(dom, self.url)
                if parsed_urls:
                    print(f"在页面 {self.url} 中发现 {len(parsed_urls)} 个URL")
                    # 确保解析到的URL被正确添加到结果列表中
                    for url in parsed_urls:
                        if url not in self.urls_result:
                            print(f"发现新URL: {url}")
                            self.urls_result.append(url)
                else:
                    print(f"页面 {self.url} 中未发现任何URL")
            except Exception as e:
                print(f"Error parsing HTML: {e}")
            finally:
                self._cleanup_browser(browser_id)

        web_view.page().toHtml(handle_html_ready)

    def _start_next_download(self) -> None:
        """开始下载下一个URL。"""
        if self.pending_urls and len(self.browser) < self.max_concurrent:
            url = self.pending_urls.pop(0)
            browser_id = len(self.browser)
            try:
                self.url = self._get_path(url)
                web_view = QWebEngineView()
                web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, False)
                web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

                timer = QTimer(web_view)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda bid=browser_id: self._handle_timeout(bid))
                timer.start(self.timeout)

                loader = partial(self._loader_finished, browser_id)
                web_view.loadFinished.connect(loader)
                web_view.page().loadFinished.connect(lambda ok, bid=browser_id: self._loader_finished(bid, ok))

                web_view.load(QUrl(url))
                self.browser[browser_id] = (web_view, False)
            except Exception as e:
                print(f"Error initializing browser for URL {url}: {e}")
                QTimer.singleShot(0, self._start_next_download)

    def run(self, urls: List[str]) -> List[Any]:
        """运行下载器开始下载URL。

        Args:
            urls: 待下载的URL列表

        Returns:
            List[Any]: 下载结果列表
        """
        self.pending_urls = urls.copy()
        for _ in range(min(self.max_concurrent, len(urls))):
            self._start_next_download()
        return self.urls_result


def parse_dom(content: Any, url: str) -> List[str]:
    """解析DOM内容提取URL。

    Args:
        content: DOM内容
        url: 当前页面URL

    Returns:
        List[str]: 提取的URL列表
    """
    dom = Dom(content, url)
    return dom.get_url()

