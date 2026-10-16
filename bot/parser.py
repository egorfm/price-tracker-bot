"""Extract product title and price from a page.

Strategy (works on many shops without per-site selectors):
1. JSON-LD (schema.org Product -> offers.price)
2. <meta> tags (og:price:amount, product:price:amount, itemprop=price)
"""
import json
import re

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ru,en;q=0.8",
}


class ParseError(Exception):
    pass


def to_float(raw) -> float:
    s = re.sub(r"[^\d,.]", "", str(raw))
    if not s:
        raise ValueError(f"no digits in {raw!r}")
    if "," in s and "." in s:
        if s.rfind(".") > s.rfind(","):
            s = s.replace(",", "")
        else:
            s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        s = head + tail if len(tail) == 3 else head + "." + tail
    return float(s)


def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _from_jsonld(soup: BeautifulSoup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        for obj in _walk(data):
            types = obj.get("@type")
            types = types if isinstance(types, list) else [types]
            if "Product" not in types:
                continue
            offers = obj.get("offers")
            for offer in offers if isinstance(offers, list) else [offers]:
                if not isinstance(offer, dict):
                    continue
                raw = offer.get("price") or offer.get("lowPrice")
                if raw is not None:
                    return obj.get("name"), to_float(raw)
    return None


def _from_meta(soup: BeautifulSoup):
    for attrs in (
        {"property": "product:price:amount"},
        {"property": "og:price:amount"},
        {"itemprop": "price"},
    ):
        tag = soup.find(["meta", "span"], attrs=attrs)
        if tag:
            raw = tag.get("content") or tag.get_text()
            if raw:
                return None, to_float(raw)
    return None


def parse_html(html: str) -> tuple[str, float]:
    soup = BeautifulSoup(html, "html.parser")
    found = _from_jsonld(soup) or _from_meta(soup)
    if not found:
        raise ParseError("Не удалось найти цену на странице")
    title, price = found
    if not title:
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else None) or (
            soup.title.string.strip() if soup.title and soup.title.string else "Без названия"
        )
    return title[:120], price


def fetch_product(url: str) -> tuple[str, float]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ParseError(f"Не удалось загрузить страницу: {e}") from e
    return parse_html(resp.text)
