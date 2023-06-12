import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

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

def get_page(client, url):
    headers = {
        'User-Agent': USER_AGENT
    }
    resp = client.get(url, headers=headers)
    html = HTMLParser(resp.text)
    if html.css_first('a[data-id=pagination-test-link-next]'):
        next_page = html.css_first('a[data-id=pagination-test-link-next').attributes
    else:
        next_page = {'href': False}
    return Response(body_html=html, next_page=next_page)

def extract_text(html, selector, index):
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return 'none'

def parse_detail(html):
    new_product = Product(
        name = extract_text(html, 'h1#product-page-title', 0),
        sku = extract_text(html, 'span.item-number', 0),
        price = extract_text(html, 'span.price-value', 0),
        rating = extract_text(html, 'span.cdr-rating__number_13-3-1', 0)
    )
    print(new_product)

def detail_page_loop(client, page):
    base_url = 'https://www.rei.com/'
    product_links = parse_links(page.body_html)
    for link in product_links:
        detail_page = get_page(client, urljoin(base_url, link))
        parse_detail(detail_page.body_html)

def parse_links(html):
    links = html.css('div#search-results > ul li > a')
    return {link.attrs['href'] for link in links}


def pagination_loop(client):
    url = 'https://www.rei.com/c/backpacks'
    while True:
        page = get_page(client, url)
        #print(parse_links(page.body_html))
        detail_page_loop(client, page)
        if page.next_page['href'] is False:
            client.close()
            break
        else:
            url = urljoin(url, page.next_page['href'])
            print(url)


def main():
    client = httpx.Client()
    pagination_loop(client)

if __name__ == '__main__':
    main()
