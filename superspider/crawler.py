import os
import sys
import sqlite3

from sqlite3 import Connection

from PyQt5.QtWidgets import QApplication

from superspider.pipline import get_md5, duplicate
from superspider.downloader import Downloader


class Crawler(object):
    def __init__(self, url: str) -> None:
        self.urls = [url]
        self.checker_urls = []
        self.id = [0]
        self.conn = self._connect_db(url=url)

    def _normalize(self, url: str) -> str:
        url = url.rstrip("/") + "/"
        if url.find(":") != -1:
            url = url[0:url.find(":")+1].lower() + "//" + url[url.find(":") + 1:].lstrip("/")
        return url

    def _is_empty(self) -> bool:
        return True if not self.urls else False

    def _connect_db(self, url: str) -> Connection:
        db_file = get_md5(url)
        if os.path.exists(f"./db/{db_file}.db3"):
            os.remove(f"./db/{db_file}.db3")

        conn = sqlite3.connect(f"./db/{db_file}.db3", check_same_thread=False)
        conn.execute("")
        return conn

    def crawler(self) -> None:
        app = QApplication(sys.argv)
        while not self._is_empty():
            for item in self.urls:
                print(f"current item : {item}")

            downloader = Downloader(app=app, checker_urls=self.checker_urls)
            downloader.run(self.urls)
            app.exec_()
            self.urls = []
            for item in self.checker_urls:
                if not duplicate(self.conn, self.id, item):
                    self.urls.append(item)

            self.urls = []

    def start(self) -> None:
        self.crawler()
        self.conn.close()

