from superspider.crawler import Crawler


if __name__ == "__main__":
    url = "https://www.bmabk.com/index.php/post/category/mst"
    Crawler(url).start()
