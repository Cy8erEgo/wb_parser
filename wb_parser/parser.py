import json
import re
from dataclasses import dataclass
from random import random
from time import sleep
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from user_agent import generate_user_agent


@dataclass
class WBProduct:
    position: int
    name: str
    vendor_code: int
    url: str
    description: Optional[str] = None


@dataclass
class WBCategory:
    name: str
    url: str


class WBParser:
    _DOMAIN_URL = "https://www.wb.ru"
    _SEARCH_URL = "/catalog/0/search.aspx?search={}&xsearch=true"

    def __init__(self, page_url: str):
        self._session = requests.session()
        self._session.headers = {"User-Agent": generate_user_agent()}
        self._page_url = page_url
        self._soup = self._get_soup(page_url)

    def __del__(self):
        self._session.close()

    def _get_soup(self, url: str):
        return BeautifulSoup(self._session.get(url).text, "html.parser")

    @staticmethod
    def _parse_name(el: Tag) -> str:
        brand = el.select_one("strong.brand-name").text.strip()
        good_name = el.select_one("span.goods-name").text.strip()
        return f"{brand} {good_name}"

    def parse_product_desc(self, vendor_code: int) -> str:
        url = f"{self._DOMAIN_URL}/{vendor_code}/product/data?"
        while True:
            try:
                data = self._session.get(url).json()
                return data["value"]["data"]["productCard"].get("description")
            except json.decoder.JSONDecodeError:
                sleep(random())

    def add_desc_to_product(self, product: WBProduct):
        product.description = self.parse_product_desc(product.vendor_code)

    def parse_products(self, exclude_desc: bool = False) -> List[WBProduct]:
        products = []
        product_elements = self._soup.findAll("div", class_="dtList-inner")

        for i, product_el in enumerate(product_elements, 1):
            url = product_el.select_one("a.j-open-full-product-card")["href"]
            vendor_code = int(url.split("/")[2])
            name = self._parse_name(product_el)
            product = WBProduct(i, name, vendor_code, url)
            products.append(product)

        if not exclude_desc:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(100) as executor:
                executor.map(self.add_desc_to_product, products)

        return products

    @staticmethod
    def _prepare_categories(categories: List[Tag]) -> List[WBCategory]:
        return [WBCategory(c.text.strip(), c["href"]) for c in categories]

    def _parse_categories(self) -> List[WBCategory]:
        return self._prepare_categories(self._soup.select(".i-menu-catalog li a"))

    def _parse_subcategories(self) -> List[WBCategory]:
        return self._prepare_categories(self._soup.select(".sidemenu ul a"))

    def _parse_subcategories_2(self) -> List[WBCategory]:
        scripts = self._soup.select("script:not([type], [src])")
        for script in scripts:
            if "xcatalogShard" in str(script):
                data_regexp = re.search(r'"xData":({[^}]+}?)', str(script))
                if data_regexp:
                    break
        else:
            return []
        data = json.loads(data_regexp.group(1))
        url = "https://wbxcatalog-ru.wildberries.ru/{}/filters?filters=xsubject&{}&locale=ru"
        url = url.format(data["xcatalogShard"], data["xcatalogQuery"])
        json_ = self._session.get(url).json()
        categories = []
        base_url = "/" + "/".join(self._page_url.split("/")[3:])
        for cat_raw in json_["data"]["filters"][0]["items"]:
            name = cat_raw["name"]
            url = f"{base_url}?xsubject={cat_raw['id']}"
            categories.append(WBCategory(name, url))
        return categories

    def parse_categories(self) -> List[WBCategory]:
        if self._soup.select_one("ul.maincatalog-list-2"):
            return self._parse_categories()
        elif self._soup.select_one("ul.sidemenu ul li:not(.selected)"):
            return self._parse_subcategories()
        try:
            catalog_title = self._soup.select_one("h1.catalog-title").text.strip()
            return list(
                filter(lambda c: c.name != catalog_title, self._parse_subcategories_2())
            )
        except AttributeError:
            return []
