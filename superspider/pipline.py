import hashlib
import re
from typing import Any


def get_md5(src: Any) -> str:
    m = hashlib.md5()
    m.update(src.encode("utf-8"))
    return m.hexdigest()


def diif_url_from_url(url: str) -> str:
    if url.rfind("#") != -1:
        url = url[0: url.rfind("#")]

    url = url.rstrip("&")
    url = url.rstrip("?")

    pattern = re.compile("\d+")
    url = re.sub(pattern, "d+", url)
    return url


def duplicate(connect: Any, ID: Any, url: str) -> bool:
    value = get_md5(diif_url_from_url(url))
    sql = f"select ID from urls where md5 = {value};"
    if len(connect.execute(sql).fetchall()) > 0:
        return True
    else:
        ID[0] += 1
        sql = f"INSET INTO urls (ID, url, md5) VALUES ({str(ID[0])}, {url}, {value})"
        connect.execute(sql)
        connect.commit()
        return False

