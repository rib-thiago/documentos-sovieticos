"""Adaptado do coletor Sakharov fornecido pelo usuário; parsers de HTML.

O texto resultante é candidato editorial, não edição crítica validada.
"""
from __future__ import annotations

import argparse

import csv

import hashlib

import json

import re

import sys

import time

from datetime import datetime, timezone

from pathlib import Path

from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

from urllib.robotparser import RobotFileParser

import requests

from bs4 import BeautifulSoup, Tag

from markdownify import markdownify as to_markdown

from requests.adapters import HTTPAdapter

from urllib3.util.retry import Retry

RUSSIAN_URL = (
    "https://leninism.su/books/"
    "4135-politicheskoe-zaveshhanie-lenina-realnost-istorii-i-mify-politiki.html"
)

ENGLISH_INDEX = (
    "https://neodemocracy.blogspot.com/2022/11/"
    "the-reality-of-history-and-myths-of.html"
)

RUSSIAN_PDF = "https://www.revolutionarydemocracy.org/russian/sakharov.pdf"

ENGLISH_PDF_PAGE = "https://disk.yandex.com/i/iQkXgfNijUjrNw"

OLD_ENGLISH_ARTICLE = "https://revolutionarydemocracy.org/archive/LenTest.htm"

STALINISM_MIRROR = (
    "https://stalinism.ru/elektronnaya-biblioteka/"
    "politicheskoe-zaveshchanie-lenina-realnost-istorii-i-mify-politiki.html?showall=1"
)

ENGLISH_TITLES = [
    "Two Concepts of NEP",
    "The First Crisis of the NEP",
    "Prospects Of the Socialist Revolution",
    "The Political Opposition of Lenin and Trotsky",
    "Lenin Core of the Politburo",
    'Stalin - Ascent To "Immediate Power"',
    "Stalin For Position or Position for Stalin?",
    "Lenin And Trotsky - Alienation Is Growing",
    "Lenin And Stalin: The Time of the Greatest Political Proximity",
    "Lenin, Stalin and Trotsky in the Discussion About the Monopoly of Foreign Trade",
    "Lenin and Stalin: Tactical Differences on Questions of Union of the Soviet Republics",
    '"Georgian Conflict" In the History of Relationships Lenin and Stalin',
    "Myth About Lenin's Help to Trotsky",
    "Outlines of Trotsky's New Tactics",
    "XII Congress of the Party: The Choice in Favor of Stalin",
    "Strengthening the Dictatory of the Proletariat Is the Main Condition for the Victory of the Revolution",
    "Cooperation as a Way of Involving the Peasants in the Building of Socialism",
    "Instead Of Conclusion",
]

UA = "Academic-Source-Collector/1.0 (personal research; 1 request/second)"

EXCLUDE = [
    "script", "style", "noscript", "iframe", "form", "button", "nav",
    "header", "footer", "aside", ".pagination", ".pagenav", ".page-links",
    ".article-info", ".post-footer", ".post-header", ".share-buttons",
    ".social-share", ".blog-pager", ".comments", ".comment-form",
    ".breadcrumbs", ".breadcrumb", ".item-page .pagenav",
    ".post-labels", ".post-share-buttons", ".addthis_toolbox",
]

ARTICLE_SELECTORS = [
    '[itemprop="articleBody"]', ".com-content-article__body", ".post-body",
    ".entry-content", ".article-content", ".item-page", "article",
    ".post", "main", "#content",
]

def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9а-яё]+", "", text.casefold().replace("ё", "е"))

def clean_title(text: str) -> str:
    return " ".join(text.split()).strip(" —-|\u00a0")

def slugify(title: str) -> str:
    # Numerically prefixed filenames are authoritative; slug is a convenience.
    s = re.sub(r"[^\w\-]+", "-", title.casefold(), flags=re.UNICODE)
    return s.strip("-_ ")[:90] or "untitled"

def make_session() -> requests.Session:
    ses = requests.Session()
    ses.headers.update({"User-Agent": UA, "Accept-Language": "ru,en;q=0.8"})
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    ses.mount("https://", HTTPAdapter(max_retries=retry))
    return ses

def soup_from(data: bytes) -> BeautifulSoup:
    # Requests/BS4 can usually infer UTF-8, but these pages declare it anyway.
    return BeautifulSoup(data, "html.parser")

def is_relevant_ru_page(url: str, base: str) -> bool:
    return urlparse(url).path.rstrip("/") == urlparse(base).path.rstrip("/")

def find_ru_toc(soup: BeautifulSoup) -> dict[int, str]:
    titles: dict[int, str] = {}
    for a in soup.select('a[href*="start="]'):
        href = urljoin(RUSSIAN_URL, a.get("href", ""))
        if not is_relevant_ru_page(href, RUSSIAN_URL):
            continue
        values = parse_qs(urlparse(href).query).get("start", [])
        if len(values) != 1 or not values[0].isdigit():
            continue
        i = int(values[0])
        if 0 <= i < 60:
            title = clean_title(a.get_text(" ", strip=True))
            if len(title) > 5 and i not in titles:
                titles[i] = title
    # first page is the cover/title, linked without 'start' in some templates
    titles.setdefault(0, 'Титульные сведения и предисловие')
    return titles

def find_english_urls(soup: BeautifulSoup) -> list[tuple[str, str]]:
    anchors = soup.select("a[href]")
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name in ENGLISH_TITLES:
        wanted = normalized(name)
        match = None
        for a in anchors:
            raw = clean_title(a.get_text(" ", strip=True))
            link = urljoin(ENGLISH_INDEX, a.get("href", ""))
            host = urlparse(link).netloc.lower()
            if host != "neodemocracy.blogspot.com":
                continue
            if normalized(raw) == wanted:
                match = link
                break
        if match and match not in seen:
            result.append((name, match))
            seen.add(match)
        elif not match:
            print(f"  WARNING missing English link from index: {name}", file=sys.stderr)
    return result

def choose_article(soup: BeautifulSoup) -> Tag:
    # Prefer site-provided content containers; retain headings and footnotes.
    candidates: list[tuple[float, Tag]] = []
    for rank, selector in enumerate(ARTICLE_SELECTORS):
        for tag in soup.select(selector):
            txt = tag.get_text(" ", strip=True)
            if len(txt) < (20 if rank < 4 else 250):
                continue
            links = len(tag.select("a"))
            paras = len(tag.select("p"))
            # A large title/navigation box is not the actual chapter text.
            score = len(txt) / (1 + links * 0.002) + paras * 5 - rank * 200
            candidates.append((score, tag))
        if candidates and rank < 4:
            # Trusted narrowly scoped container is more valuable than huge <body>
            return max(candidates, key=lambda x: x[0])[1]
    if candidates:
        return max(candidates, key=lambda x: x[0])[1]
    if not soup.body:
        raise ValueError("No HTML body present")
    return soup.body

def clean_article(soup: BeautifulSoup, source_url: str) -> str:
    import copy
    original = choose_article(soup)
    element = copy.deepcopy(original)
    for selector in EXCLUDE:
        for node in element.select(selector):
            node.decompose()
    # Drop TOC links and navigation in Joomla's all-pages/paginated articles.
    for node in element.select('a[href]'):
        href = urljoin(source_url, node.get("href", ""))
        q = parse_qs(urlparse(href).query)
        if is_relevant_ru_page(href, RUSSIAN_URL) and (
            "start" in q or "showall" in q
        ):
            parent = node.parent
            if parent and parent.name in ("li", "option"):
                parent.decompose()
            else:
                node.decompose()
    for node in element.select("img"):
        src = node.get("src", "")
        if src:
            node["src"] = urljoin(source_url, src)
    for node in element.select("a[href]"):
        node["href"] = urljoin(source_url, node["href"])
    # Joomla's page counter is navigation, not a statement in the book.
    for node in list(element.find_all(["div", "p", "span"])):
        if re.fullmatch(r"Страница\s+\d+\s+из\s+\d+", node.get_text(" ", strip=True)):
            node.decompose()
    md = to_markdown(str(element), heading_style="ATX", bullets="-")
    md = re.sub(r"\n{4,}", "\n\n\n", md).strip() + "\n"
    if len(md) < 20:
        raise ValueError(f"Extracted only {len(md)} characters: {source_url}")
    return md
