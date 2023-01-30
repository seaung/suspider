import re
from typing import Any, List

from bs4 import BeautifulSoup


class URL(object):
    def judge(self, link) -> bool:
        if link == None:
            return False
        if link == '/':
            return False
        if link.find('javascript:')==0:
            return False
        if link.find('http') !=- 1 and link.find(self.url) == -1:
            return False
        return True

    def filter(self, link) -> Any:
        if link.find('http')!=0:
            return self.url.rstrip('/') + "/" + link.lstrip('/')
        else:
            return link

    def onclick_filter(self, link) -> str:
        link_pattern = re.compile("[\"'][ ]*\+[ ]*[\"']")
        return re.sub(link_pattern, '', link)


class Dom(URL):
    def __init__(self, content: Any, url: str) -> None:
        self.soup = BeautifulSoup(content, "lxml")
        self.url = url
        self.pattern = re.compile("href=([a-zA-Z0-9'\"+?=.%/_]*)")

    def _is_input_with_onclick(self, tag) -> bool:
        return (tag.name == "input") and (tag.get("type") == "button") and tag.has_attr("onclick")

    def prettify_html(self) -> None:
        print(self.soup.prettify().encode("utf-8", "ignore"))

    def get_url(self) -> List[str]:
        urls = []

        for item in self.soup.find_all("a"):
            if self.judge(item.get("href")):
                urls.append(self.filter(item.get("href")))

        for tag in self.soup.find_all(self._is_input_with_onclick):
            for item in re.findall(self.pattern, tag.get("onclick")):
                if self.judge(self.onclick_filter(item)):
                    urls.append(self.filter(self.onclick_filter(item)))

        return urls
