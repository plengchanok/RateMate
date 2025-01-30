# Description

This project is designed to analyze product data from multiple sources such as Amazon, Best Buy, Google Shopping, and Walmart. It provides insights into the top products based on various metrics including price, ratings, review counts, and sentiment analysis. The tool is aimed at helping users make informed purchasing decisions by identifying the best value products across these platforms.

# Features
- **Data Loading**: Load product data from various formats including CSV and JSON.
- **Data Processing**: Normalize data and calculate combined scores based on weighted metrics for price, rating, and reviews.
- **Sentiment Analysis**: Analyze customer reviews to assess product sentiment.
- **Top Product Identification**: Identify and display the top products based on combined scores and sentiment.

# Setup

To run this project, you will need Python installed on your machine along with several packages.

## Prerequisites
- Python 3.10 or above
- Pandas
- NumPy
- Matplotlib
- TextBlob
- Requests
- Pathlib
- BeautifulSoup

## Installation
1. Install required Python packages:
    ```
    pip install pandas numpy matplotlib textblob
    pip install loguru
    pip install scrapfly-sdk
    pipx install poetry
    pip install jmespath
    pip install parsel
    ```
2. You might need to install the corpora for TextBlob if you're using it for the first time:
    ```
    python -m textblob.download_corpora
    ```

# Usage

To run the program in the UI we designed, execute the main script from the command line in the directory you downloaded. A new window will pop up in the background of your current window:

Follow the instructions prompted to proceed with our program. You can always choose to exit the program when at the main menu.

There will be an option for you to get updated scraped data. Check the box to run the data Python files you want and choose a product you want to see analyzed using the dropdown box, then click the search button right below it. It might take several minutes to run if you choose to download all the data (you can always check back in the terminal to see progress).

All data files will be automatically saved in the same directory as the Python files you are running. This program uses four processed data files from scraped data. Each file contains combined information for five products (iPhone, iPad, MacBook, Nintendo Switch, and PlayStation) from each source (previously extracted files already exist in the directory):
1. `amazon_product_reviews.csv`
2. `bestbuy_combined.csv`
3. `google_shopping_combined.csv`
4. `walmart_products.json`

# Data Sources

1. **Best Buy**: Data is scraped using Scrapfly.io and Python to scrape property listing data from BestBuy.com. This scraper retrieves:
   - Product pages for product data.
   - Search pages for product data on search pages.
2. **Amazon**: Data is directly downloaded from UCSD Professor Julian McAuley's Lab (1996–2023). Two data files are used:
   - "Electronics.jsonl" (product review information)
   - "meta_Electronics.jsonl" (product detail information)
   Both files are merged based on `parent_asin`. Customer opinion data is used for sentiment analysis combined with scores of pricing and rating to find which product-review combination has the best-rated quality.
3. **Google Shopping**: Data is scraped using requests and Oxylabs API with "Electronics" as a search keyword and geolocation set to the United States. This dataset provides lists of searched products, their merchant, title, price, ratings, and number of reviews.
4. **Walmart**: Data is scraped using BeautifulSoup and ScraperAPI. It includes a list of product information with multiple review texts for specific products. This dataset allows deep sentiment analysis of user reviews combined with ratings and review counts to generate a combined score.

# Functions Description

- `load_data()`: Loads data from files stored in the same directory as the script.
- `process_data(data_frames, product_name)`: Processes data to find top products based on specified criteria.
- `process_amazon_data(df)`: Retrieves top three Amazon reviews with product information (processed in `amazon_data_process.py`).
- `bestbuy_top_cheapest(df, title)`, `google_top_cheapest(df, title)`: Process Best Buy and Google Shopping data to find top three products with best combination scores of ratings, prices, and review counts/rating counts.
- `process_walmart_top_cheapest(df)`: Processes Walmart data to find top three products according to price, rating, and review sentiment.
- `perform_sentiment_analysis(df)`: Analyzes sentiments of product reviews.

# License

This project is licensed under the MIT License.
