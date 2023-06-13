from httpx import Client
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
BASE_URL = 'https://www.rei.com/'
PRODUCT_PAGE_URL = 'https://www.rei.com/c/backpacks?page=22'

@dataclass
class Product:
    name: str
    sku: str
    price: str
    rating: str

@dataclass
class Response:
    body_html: HTMLParser
    next_page: dict

def get_page(client: Client, url: str) -> Response:
    def get_next_page(html: HTMLParser) -> dict[str, str | bool]:
        query = 'a[data-id=pagination-test-link-next]'
        next_page = html.css_first(query)
        return next_page.attributes if next_page else {'href': False}
    headers = {'User-Agent': USER_AGENT}
    resp = client.get(url, headers=headers)
    html = HTMLParser(resp.text)
    next_page = get_next_page(html)
    return Response(body_html=html, next_page=next_page)

def parse_pages(client: Client, url: str) -> list[Response]:
    pages = []
    while True:
        page = get_page(client, url)
        pages.append(page)
        if not page.next_page['href']:
            break
        url = urljoin(url, page.next_page['href'])
        print(url)
    return pages


def parse_detail(html: HTMLParser) -> Product:
    def extract_text(html: HTMLParser, selector: str, index: int) -> str:
        try:
            return html.css(selector)[index].text(strip=True)
        except IndexError:
            return 'none'
    new_product = Product(
        name = extract_text(html, 'h1#product-page-title', 0),
        sku = extract_text(html, 'span.item-number', 0),
        price = extract_text(html, 'span.price-value', 0),
        rating = extract_text(html, 'span.cdr-rating__number_13-3-1', 0)
    )
    return new_product

def detail_page_loop(client: Client, page: Response) -> None:
    base_url = BASE_URL
    product_links = parse_links(page.body_html)
    for link in product_links:
        detail_page = get_page(client, urljoin(base_url, link))
        product = parse_detail(detail_page.body_html)
        print(product)

def parse_links(html: HTMLParser) -> set[str]:
    links = html.css('div#search-results > ul li > a')
    return {link.attrs['href'] for link in links}


def pagination_loop(client: Client) -> None:
    url = PRODUCT_PAGE_URL
    for page in parse_pages(client, url):
        #print(parse_links(page.body_html))
        detail_page_loop(client, page)


def main() -> None:
    with Client() as client:
        pagination_loop(client)

if __name__ == '__main__':
    main()
