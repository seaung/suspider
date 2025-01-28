import os
import sys
import time
import sqlite3

from sqlite3 import Connection

from PyQt5.QtWidgets import QApplication

from superspider.pipline import get_md5, duplicate
from superspider.downloader import Downloader


class Crawler(object):
    def __init__(self, url: str, max_depth: int = 3, request_delay: float = 1.0) -> None:
        self.urls = [url]
        self.checker_urls = []
        self.id = [0]
        self.max_depth = max_depth
        self.current_depth = 0
        self.request_delay = request_delay
        self.conn = self._connect_db(url=self._normalize(url))

    def _normalize(self, url: str) -> str:
        url = url.rstrip("/") + "/"
        if url.find(":") != -1:
            url = url[0:url.find(":")+1].lower() + "//" + url[url.find(":") + 1:].lstrip("/")
        return url

    def _is_empty(self) -> bool:
        return True if not self.urls else False

    def _connect_db(self, url: str) -> Connection:
        db_file = get_md5(url)
        if os.path.exists(f"./{db_file}.db3"):
            os.remove(f"./{db_file}.db3")

        conn = sqlite3.connect(f"./{db_file}.db3", check_same_thread=False)
        conn.execute("""
        CREATE TABLE urls
            (ID INT PRIMARY KEY  NOT NULL,
            url TEXT       NOT NULL,
            md5 TEXT       NOT NULL,
            depth INT      NOT NULL);""")  # 添加深度字段
        print("create db success")
        return conn

    def crawler(self) -> None:
        app = QApplication(sys.argv)
        while not self._is_empty() and self.current_depth < self.max_depth:
            current_urls = self.urls.copy()
            self.urls = []
            
            for item in current_urls:
                print(f"current item : {item}")
                time.sleep(self.request_delay)  # 添加请求延迟

            downloader = Downloader(app=app, checker_urls=self.checker_urls)
            downloader.run(current_urls)
            app.exec_()

            for item in self.checker_urls:
                normalized_url = self._normalize(item)
                if not duplicate(self.conn, self.id, normalized_url):
                    self.urls.append(normalized_url)
            
            self.current_depth += 1
            self.checker_urls = []

    def start(self) -> None:
        self.crawler()
        self.conn.close()


