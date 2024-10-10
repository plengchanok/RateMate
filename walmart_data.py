import json
import os

import requests
from bs4 import BeautifulSoup


def scrape_walmart_product(url, api_key):
    payload = {"api_key": api_key, "url": url, "render": "true"}
    html = requests.get("http://api.scraperapi.com", params=payload)

    product_info = {}
    soup = BeautifulSoup(html.text, features="html.parser")

    # Scrape product information
    try:
        product_info['product_name'] = soup.find("h1", attrs={"itemprop": "name"}).text
    except AttributeError:
        product_info['product_name'] = "Not found"

    try:
        product_info['rating'] = soup.find("span", class_="rating-number").text
    except AttributeError:
        product_info['rating'] = "Not found"

    try:
        product_info['review_count'] = soup.find("a", attrs={"itemprop": "ratingCount"}).text
    except AttributeError:
        product_info['review_count'] = "Not found"

    image_divs = soup.findAll("div", attrs={"data-testid": "media-thumbnail"})
    all_image_urls = []
    for div in image_divs:
        image = div.find("img", attrs={"loading": "lazy"})
        if image:
            image_url = image["src"]
            all_image_urls.append(image_url)
    product_info['all_image_urls'] = all_image_urls

    try:
        product_info['price'] = soup.find("span", attrs={"itemprop": "price"}).text
    except AttributeError:
        product_info['price'] = "Not found"

    next_data = soup.find("script", {"id": "__NEXT_DATA__"})
    if next_data:
        parsed_json = json.loads(next_data.string)

        try:
            description_1 = parsed_json["props"]["pageProps"]["initialData"]["data"]["product"]["shortDescription"]
            product_info['description_1_text'] = BeautifulSoup(description_1, 'html.parser').text
        except KeyError:
            product_info['description_1_text'] = "Not found"

        try:
            description_2 = parsed_json["props"]["pageProps"]["initialData"]["data"]["idml"]["longDescription"]
            product_info['description_2_text'] = BeautifulSoup(description_2, 'html.parser').text
        except KeyError:
            product_info['description_2_text'] = "Not found"

        # Extract reviews from __NEXT_DATA__
        try:
            reviews_data = parsed_json["props"]["pageProps"]["initialData"]["data"]["reviews"]["customerReviews"]
            reviews = []
            for review in reviews_data:
                review_text = ""
                if "reviewText" in review:
                    review_text = review["reviewText"]
                elif "text" in review:
                    review_text = review["text"]

                reviews.append({
                    "text": review_text,
                    "rating": review.get("rating", ""),
                    "author": review.get("userNickname", ""),
                    "date": review.get("submissionTime", "")
                })
            product_info['reviews'] = reviews
        except KeyError:
            product_info['reviews'] = []
    else:
        product_info['description_1_text'] = "Not found"
        product_info['description_2_text'] = "Not found"
        product_info['reviews'] = []

    return product_info


def append_product_data_to_json(product_data, file_path='walmart_products.json'):
    if not os.path.isfile(file_path):
        # If the file doesn't exist, create it with an empty list
        with open(file_path, 'w') as f:
            json.dump([], f)

    # Read existing data
    with open(file_path, 'r') as f:
        existing_data = json.load(f)

    # Append the new product data
    existing_data.append(product_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

    print(f"Appended product data successfully. Total products: {len(existing_data)}")


# Usage
url = "https://www.walmart.com/ip/2021-Apple-10-2-inch-iPad-Wi-Fi-64GB-Space-Gray-9th-Generation/483978365"
api_key = "0ea986ceb0ae971a5a9b06600c56323b"  # Replace with your actual API key

product_data = scrape_walmart_product(url, api_key)
append_product_data_to_json(product_data)

# Print the total number of products and reviews in the JSON file
with open('walmart_products.json', 'r') as f:
    all_data = json.load(f)
    total_reviews = sum(len(product.get('reviews', [])) for product in all_data)
    print(f"\nTotal products in the JSON file: {len(all_data)}")
    print(f"Total reviews across all products: {total_reviews}")
