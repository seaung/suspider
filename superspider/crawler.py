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
        print(f"开始爬取，最大深度设置为: {self.max_depth}")
        while not self._is_empty() and self.current_depth < self.max_depth:
            current_urls = self.urls.copy()
            self.urls = []
            
            print(f"\n当前爬取深度: {self.current_depth}")
            print(f"本轮需要处理的URL数量: {len(current_urls)}")
            
            for item in current_urls:
                print(f"正在处理URL: {item}")
                time.sleep(self.request_delay)  # 添加请求延迟

            downloader = Downloader(app=app, checker_urls=self.checker_urls)
            downloader.run(current_urls)
            app.exec_()

            # 处理新发现的URL
            for item in self.checker_urls:
                normalized_url = self._normalize(item)
                # 将URL存入数据库，如果是新URL则加入待爬取列表
                if not duplicate(self.conn, self.id, normalized_url, self.current_depth + 1):
                    self.urls.append(normalized_url)
            
            self.current_depth += 1
            self.checker_urls = []

    def start(self) -> None:
        # 确保第一个URL被插入数据库
        initial_url = self.urls[0]
        duplicate(self.conn, self.id, initial_url, 0)
        self.crawler()
        self.conn.close()


