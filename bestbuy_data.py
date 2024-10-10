import os
from io import BytesIO
import gzip
import json
import jmespath
from typing import Dict, List, Union
from parsel import Selector
from urllib.parse import urlencode, quote_plus
from loguru import logger as log
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse
import asyncio
from pathlib import Path
import pandas as pd

# API Key
SCRAPFLY = ScrapflyClient("scp-live-c3636738bf58485b9250a493e60d7723")

# edit data to be scrapped here
queries = ['macbook', 'ipad', 'iphone', 'nintendo switch', 'play station']

BASE_CONFIG = {
    # bypass bestbuy.com web scraping blocking
    "asp": True,
    # set the proxy country to US
    "country": "US",
}

output = Path(__file__).parent
output.mkdir(exist_ok=True)


def parse_sitemaps(response: ScrapeApiResponse) -> List[str]:
    """Parse links for bestbuy sitemap"""
    # Get the content
    content = response.scrape_result['content']

    # If the content is a string, no need to decode or decompress
    if isinstance(content, bytes):
        # Check if the content is gzipped by looking at the magic number
        if content[:2] == b'\x1f\x8b':  # gzip magic number
            log.info("Content is gzipped, decompressing...")
            # It's gzipped, decompress it
            bytes_data = gzip.decompress(content)
            # Convert to a string after decompression
            xml = bytes_data.decode('utf-8')
        else:
            # It's bytes, but not gzipped, so we can decode it directly
            xml = content.decode('utf-8')
    else:
        # The content is already a string, no need to decode
        xml = content

    # Parse the XML content
    selector = Selector(xml)
    data = []
    for url in selector.xpath("//url/loc/text()"):
        data.append(url.get())
    return data


async def scrape_sitemaps(url: str) -> List[str]:
    """scrape link data from bestbuy sitemap"""
    response = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    promo_urls = parse_sitemaps(response)
    log.success(f"scraped {len(promo_urls)} urls from sitemaps")
    return promo_urls


def refine_product(data: Dict) -> Dict:
    """refine the JSON product data"""
    parsed_product = {}
    specifications = data["shop-specifications"]["specifications"]["categories"]
    pricing = data["pricing"]["app"]["data"]["skuPriceDomain"]
    ratings = jmespath.search(
        """{
        featureRatings: aggregateSecondaryRatings,
        positiveFeatures: distillation.positiveFeatures[].{name: name, score: representativeQuote.score, totalReviewCount: totalReviewCount},
        negativeFeatures: distillation.negativeFeatures[].{name: name, score: representativeQuote.score, totalReviewCount: totalReviewCount}
        }""",
        data["reviews"]["app"],
    )
    faqs = []
    for item in data["faqs"]["app"]["questions"]["results"]:
        result = jmespath.search(
            """{
            sku: sku,
            questionTitle: questionTitle,
            answersForQuestion: answersForQuestion[].answerText
            }""",
            item,
        )
        faqs.append(result)

    # define the final parsed product
    parsed_product["specifications"] = specifications
    parsed_product["pricing"] = pricing
    parsed_product["ratings"] = ratings
    parsed_product["faqs"] = faqs

    return parsed_product


def parse_product(response: ScrapeApiResponse) -> Dict:
    """parse product data from bestbuy product pages"""
    selector = response.selector
    data = {}
    data["shop-specifications"] = json.loads(selector.xpath("//script[contains(@id, 'shop-specifications')]/text()").get())
    data["faqs"] = json.loads(selector.xpath("//script[contains(@id, 'content-question')]/text()").get())
    data["pricing"] = json.loads(selector.xpath("//script[contains(@id, 'pricing-price')]/text()").get())
    data["reviews"] = json.loads(selector.xpath("//script[contains(@id, 'ratings-and-reviews')]/text()").get())
 
    parsed_product = refine_product(data)
    return parsed_product


async def scrape_products(urls: List[str]) -> List[Dict]:
    """scrapy product data from bestbuy product pages"""
    to_scrape = [ScrapeConfig(url, **BASE_CONFIG) for url in urls]
    data = []
    async for response in SCRAPFLY.concurrent_scrape(to_scrape):
        try:
            product_data = parse_product(response)
            data.append(product_data)
        except:
            pass
            log.debug("expired product page")
    log.success(f"scraped {len(data)} products from product pages")
    return data


def parse_search(response: ScrapeApiResponse):
    """parse search data from search pages"""
    selector = response.selector
    data = []

    for item in selector.xpath("//ol[@class='sku-item-list']/li[@class='sku-item']"):
        name = item.xpath(".//h4[@class='sku-title']/a/text()").get()
        link = item.xpath(".//h4[@class='sku-title']/a/@href").get()

        # Validate that essential fields like 'name' are present
        if not name:
            continue  # Skip appending this product if the name is missing

        price = item.xpath(".//div[@data-testid='customer-price']/span/text()").get()
        price = int(price[price.index("$") + 1:].replace(",", "").replace(".", "")) // 100 if price else None
        original_price = item.xpath(".//div[@data-testid='regular-price']/span/text()").get()
        original_price = int(original_price[original_price.index("$") + 1:].replace(",", "").replace(".", "")) // 100 if original_price else None
        sku = item.xpath(".//div[@class='sku-model']/div[2]/span[@class='sku-value']/text()").get()
        model = item.xpath(".//div[@class='sku-model']/div[1]/span[@class='sku-value']/text()").get()
        rating = item.xpath(".//p[contains(text(),'out of 5')]/text()").get()
        rating_count = item.xpath(".//span[contains(@class,'c-reviews')]/text()").get()
        is_sold_out = bool(item.xpath(".//strong[text()='Sold Out']").get())
        image = item.xpath(".//img[contains(@class,'product-image')]/@src").get()

        # Handle missing links
        full_link = f"https://www.bestbuy.com{link}" if link else None

        data.append({
            "name": name,
            "link": full_link,  # Add only if it exists
            "image": image,
            "sku": sku,
            "model": model,
            "price": price,
            "original_price": original_price,
            "save": f"{round((1 - price / original_price) * 100, 2):.2f}%" if price and original_price else None,
            "rating": float(rating[rating.index(" "):rating.index(" out")].strip()) if rating else None,
            "rating_count": int(rating_count.replace("(", "").replace(")", "").replace(",", "")) if rating_count and rating_count != "Not Yet Reviewed" else None,
            "is_sold_out": is_sold_out,
        })
    total_count = selector.xpath("//span[@class='item-count']/text()").get()
    if total_count:
        total_count = int(total_count.split(" ")[0]) // 18  # convert the total items to pages, 18 items in each page
    else:
        total_count = 1  # Fallback to 1 page if the total count is not found or None
        log.warning("Total count not found, assuming 1 page.")

    return {"data": data, "total_count": total_count}


async def scrape_search(search_query: str, sort: Union["-bestsellingsort", "-Best-Discount"] = None, max_pages=None):
    """scrape search data from bestbuy search"""

    def form_search_url(page_number: int):
        """form the search url"""
        base_url = "https://www.bestbuy.com/site/searchpage.jsp?"
        # search parameters
        params = {
            "st": quote_plus(search_query),
            "sp": sort, # None = best match
            "cp": page_number
        }
        return base_url + urlencode(params)
    
    first_page = await SCRAPFLY.async_scrape(ScrapeConfig(form_search_url(1), **BASE_CONFIG))
    data = parse_search(first_page)
    search_data = data["data"]
    total_count = data["total_count"]

    # get the number of total search pages to scrape
    if max_pages and max_pages < total_count:
        total_count = max_pages

    log.info(f"scraping search pagination, {total_count - 1} more pages")
    # add the remaining pages to a scraping list to scrape them concurrently
    to_scrape = [
        ScrapeConfig(form_search_url(page_number), **BASE_CONFIG)
        for page_number in range(2, total_count + 1)
    ]
    async for response in SCRAPFLY.concurrent_scrape(to_scrape):
        data = parse_search(response)["data"]
        search_data.extend(data)
    
    log.success(f"scraped {len(search_data)} products from search pages")
    return search_data


def parse_reviews(response: ScrapeApiResponse) -> List[Dict]:
    """parse review data from the review API responses"""
    data = json.loads(response.scrape_result['content'])
    total_count = data["totalPages"]
    review_data = data["topics"]
    return {"data": review_data, "total_count": total_count}


async def scrape_reviews(skuid: int, max_pages: int=None) -> List[Dict]:
    """scrape review data from the reviews API"""
    first_page = await SCRAPFLY.async_scrape(ScrapeConfig(
        f"https://www.bestbuy.com/ugc/v2/reviews?page=1&pageSize=20&sku={skuid}&sort=MOST_RECENT",
        **BASE_CONFIG
    ))
    data = parse_reviews(first_page)
    review_data = data["data"]
    total_count = data["total_count"]

    # get the number of total review pages to scrape
    if max_pages and max_pages < total_count:
        total_count = max_pages

    log.info(f"scraping reviews pagination, {total_count - 1} more pages")
    # add the remaining pages to a scraping list to scrape them concurrently
    to_scrape = [
        ScrapeConfig(
            f"https://www.bestbuy.com/ugc/v2/reviews?page={page_number}&pageSize=20&sku={skuid}&sort=MOST_RECENT",
            **BASE_CONFIG
        )
        for page_number in range(2, total_count + 1)
    ]
    async for response in SCRAPFLY.concurrent_scrape(to_scrape):
        data = parse_reviews(response)["data"]
        review_data.extend(data)

    log.success(f"scraped {len(review_data)} reviews from the reviews API")
    return review_data



'''
Here's the code for scrapping data for products
'''

async def run(query):
    # enable scrapfly cache/debug?
    BASE_CONFIG["cache"] = True
    BASE_CONFIG["debug"] = True

    print("running BestBuy scrape and saving results directory")

    # for saving csv files
    search_path = output / f"search_{query}.json"
    products_path = output / "products.json"
    review_path = output / "review.json"

    # sitemap_data = await scrape_sitemaps(
    #     # sample scraper for one sitemap, other sitemaps can be found at:
    #     # https://www.bestbuy.com/robots.txt
    #     url="https://sitemaps.bestbuy.com/sitemaps_promos.xml"
    # )

    # with open(output.joinpath("promos.json"), "w", encoding="utf-8") as file:
    #     json.dump(sitemap_data, file, indent=2, ensure_ascii=False)


    # scrape search pages, edit query here
    search_data = await scrape_search(
        search_query = query,
        max_pages=3
    )
    with open(output.joinpath(f"search_{query}.json"), "w", encoding="utf-8") as file:
        json.dump(search_data, file, indent=2, ensure_ascii=False)

    # Load search JSON data from file
    def load_json(path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    search_data = load_json(search_path)

    def json_to_dataframe(json_data):
        return pd.json_normalize(json_data)

    # Convert search JSON data to DataFrames
    search_df = json_to_dataframe(search_data)

    # Save search DataFrames to CSV files
    if query == 'play station':
        search_filename = 'search_ps.csv'
    elif query == 'nintendo switch':
        search_filename = 'search_switch.csv'
    else:
        search_filename = f"search_{query}.csv"
    search_df.to_csv(output / search_filename, index=False)

    # product_data = await scrape_products(
    #     # note that the parsing logic for hidden data can differ based on the product type
    #     urls = search_df.link
    # )
    # with open(output.joinpath("products.json"), "w", encoding="utf-8") as file:
    #     json.dump(product_data, file, indent=2, ensure_ascii=False)
    #
    #
    # review_data = await scrape_reviews(
    #     skuid=search_df.sku,
    #     max_pages=3
    # )
    # with open(output.joinpath("reviews.json"), "w", encoding="utf-8") as file:
    #     json.dump(review_data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    for query in queries:
        asyncio.run(run(query))