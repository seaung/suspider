import re
from typing import Any, List, Optional
from urllib.parse import urljoin, urlparse, unquote

from bs4 import BeautifulSoup


class URL(object):
    def __init__(self) -> None:
        """初始化URL对象，设置允许的URL方案和文件扩展名。"""
        self.url = ""
        self.allowed_schemes = ["http", "https"]
        self.allowed_extensions = [".html", ".htm", ".php", ".asp", ".aspx", ".jsp"]
        self.blocked_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".mp3", ".mp4", ".zip"]

    def judge(self, link: Optional[str]) -> bool:
        """判断URL是否符合爬取规则。

        Args:
            link: 待判断的URL字符串

        Returns:
            bool: 如果URL符合爬取规则返回True，否则返回False
        """
        if not link or link == "/":
            return False

        # 过滤javascript和特殊协议
        if link.startswith(("javascript:", "mailto:", "tel:", "ftp:", "data:")):
            return False

        # 解析URL
        try:
            parsed = urlparse(link)
            if parsed.scheme and parsed.scheme not in self.allowed_schemes:
                return False

            # 检查文件扩展名
            if parsed.path:
                ext = parsed.path.lower()
                if any(ext.endswith(x) for x in self.blocked_extensions):
                    return False

                # 检查是否为允许的扩展名
                if ext and not any(ext.endswith(x) for x in self.allowed_extensions):
                    return False

            # 检查是否为外部链接
            if link.find("http") != -1 and link.find(self.url) == -1:
                return False

            return True
        except Exception:
            return False

    def filter(self, link: str) -> str:
        """对URL进行规范化处理。

        Args:
            link: 待处理的URL字符串

        Returns:
            str: 规范化后的URL字符串，如果处理失败返回空字符串
        """
        try:
            link = unquote(link)  # URL解码
            if not link.startswith("http"):
                return urljoin(self.url.rstrip("/") + "/", link.lstrip("/"))
            return link
        except Exception:
            return ""

    def onclick_filter(self, link: str) -> str:
        """处理onclick事件中的URL拼接。

        Args:
            link: 包含在onclick事件中的URL字符串

        Returns:
            str: 处理后的URL字符串，如果处理失败返回空字符串
        """
        try:
            link_pattern = re.compile("[\"\'][ ]*\+[ ]*[\"\']")
            link = re.sub(link_pattern, "", link)
            return link.strip("'\"")
        except Exception:
            return ""


class Dom(URL):
    def __init__(self, content: Any, url: str) -> None:
        """初始化Dom对象。

        Args:
            content: HTML内容
            url: 当前页面的URL
        """
        super().__init__()
        self.soup = BeautifulSoup(content, "lxml")
        self.url = url
        self.pattern = re.compile("href=([a-zA-Z0-9'\"+?=.%/_]*)")

    def _is_input_with_onclick(self, tag: Any) -> bool:
        """判断标签是否为带有onclick事件的input按钮。

        Args:
            tag: BeautifulSoup标签对象

        Returns:
            bool: 如果是带有onclick事件的input按钮返回True，否则返回False
        """
        return (tag.name == "input") and (tag.get("type") == "button") and tag.has_attr("onclick")

    def prettify_html(self) -> None:
        """以美化格式打印HTML内容。"""
        print(self.soup.prettify().encode("utf-8", "ignore"))

    def get_url(self) -> List[str]:
        """从HTML内容中提取所有符合条件的URL。

        Returns:
            List[str]: 提取到的URL列表
        """
        urls = set()  # 使用集合去重

        # 提取<a>标签中的href
        for item in self.soup.find_all("a"):
            href = item.get("href")
            if self.judge(href):
                urls.add(self.filter(href))

        # 提取form表单中的action
        for form in self.soup.find_all("form"):
            action = form.get("action")
            if self.judge(action):
                urls.add(self.filter(action))

        # 提取script标签中的src
        for script in self.soup.find_all("script"):
            src = script.get("src")
            if self.judge(src):
                urls.add(self.filter(src))

        # 提取link标签中的href
        for link in self.soup.find_all("link"):
            href = link.get("href")
            if self.judge(href):
                urls.add(self.filter(href))

        # 提取onclick事件中的URL
        for tag in self.soup.find_all(self._is_input_with_onclick):
            for item in re.findall(self.pattern, tag.get("onclick")):
                filtered_url = self.onclick_filter(item)
                if self.judge(filtered_url):
                    urls.add(self.filter(filtered_url))

        return list(urls)
