import hashlib
import re
from typing import Any


def get_md5(src: Any) -> str:
    """计算字符串的MD5哈希值。

    Args:
        src: 需要计算MD5的源字符串

    Returns:
        str: 计算得到的MD5哈希值
    """
    m = hashlib.md5()
    m.update(src.encode("utf-8"))
    return m.hexdigest()


def diif_url_from_url(url: str) -> str:
    """处理URL字符串，移除锚点和参数，并将数字替换为通配符。

    Args:
        url: 需要处理的URL字符串

    Returns:
        str: 处理后的URL字符串
    """
    if url.rfind("#") != -1:
        url = url[0: url.rfind("#")]

    url = url.rstrip("&")
    url = url.rstrip("?")

    pattern = re.compile(r"\d+")
    url = re.sub(pattern, "d+", url)
    return url


def duplicate(connect: Any, ID: Any, url: str, depth: int = 0) -> bool:
    """检查URL是否已经存在于数据库中，如果不存在则插入。

    Args:
        connect: 数据库连接对象
        ID: 自增ID的引用
        url: 需要检查的URL
        depth: URL的深度，默认为0

    Returns:
        bool: 如果URL已存在返回True，否则返回False
    """
    value = get_md5(diif_url_from_url(url))
    sql = f"SELECT ID FROM urls WHERE md5 = '{value}';"
    if len(connect.execute(sql).fetchall()) > 0:
        return True
    else:
        ID[0] += 1
        sql = f"INSERT INTO urls (ID, url, md5, depth) VALUES ({str(ID[0])}, '{url}', '{value}', {depth})"
        connect.execute(sql)
        connect.commit()
        return False

