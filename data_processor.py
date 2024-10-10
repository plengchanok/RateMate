import pandas as pd
import matplotlib.pyplot as plt
import json
from textblob import TextBlob  # For sentiment analysis

def process_amazon_data(df):
    # amazon data is being sorted and analysis is being down in amazon_data_process.py
    return df.head(3)

def perform_sentiment_analysis(df):
    df['sentiment'] = df['reviews'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    best_review = df.loc[df['sentiment'].idxmax()]  # Get the review with the highest sentiment score
    return best_review, df

def bestbuy_top_cheapest(df, title):
    if df.empty:
        return pd.DataFrame()

    # Drop rows with essential null values
    df = df.dropna(subset=['price', 'rating', 'rating_count', 'product', 'link'])
    
    # Convert price to float, rating to float, and rating_count to integer
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')
    
    # Normalize the columns
    df['normalized_price'] = normalize_column(df['price'])
    df['normalized_rating'] = normalize_column(df['rating'])
    df['normalized_rating_count'] = normalize_column(df['rating_count'])

    # Define weights
    weight_rating = 0.4
    weight_price = 0.3
    weight_rating_count = 0.3

    # Calculate the combined score based on weights
    df['combined_score'] = (df['normalized_rating'] * weight_rating) + \
                           (1 - df['normalized_price'] * weight_price) + \
                           (df['normalized_rating_count'] * weight_rating_count)  # Subtract price to prioritize lower prices

    # Sort by combined score, not just price, and select top 3
    result = df.sort_values(by='combined_score', ascending=False).head(3)
    
    # Select and rename necessary columns for output
    result = result[['product', 'link', 'price', 'rating', 'rating_count', 'combined_score']]
    
    return result


def google_top_cheapest(df, title):
    if df.empty:
        return pd.DataFrame()

    # Drop rows with essential null values
    df = df.dropna(subset=['price', 'rating', 'reviews_count', 'title'])
    
    # Convert price to float, rating to float, and reviews_count to integer
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')

    # Normalize the columns
    df['normalized_price'] = normalize_column(df['price'])
    df['normalized_rating'] = normalize_column(df['rating'])
    df['normalized_reviews_count'] = normalize_column(df['reviews_count'])

    # Define weights
    weight_rating = 0.4
    weight_price = 0.3
    weight_reviews_count = 0.3

    # Calculate the combined score based on weights
    df['combined_score'] = (df['normalized_rating'] * weight_rating) + \
                           (1 - df['normalized_price'] * weight_price) + \
                           (df['normalized_reviews_count'] * weight_reviews_count)  # Subtract price to prioritize lower prices

    # Sort by combined score, not just price, and select top 3
    result = df.sort_values(by='combined_score', ascending=False).head(3)
    
    # Select and rename necessary columns for output
    result = result[['title', 'price', 'rating', 'reviews_count', 'combined_score']]
    
    return result


def extract_numeric_rating(rating_str):
    try:
        return float(rating_str.strip('()'))
    except ValueError:
        return None

def extract_review_count(review_count_str):
    try:
        return int(review_count_str.replace(' reviews', '').replace(',', ''))
    except ValueError:
        return None
    
def normalize_column(column):
    """ Normalize a pandas series using min-max scaling. """
    return (column - column.min()) / (column.max() - column.min())

def process_walmart_top_cheapest(df):
    if df.empty:
        return pd.DataFrame()

    # Extract numeric values from price, rating, and review_count
    df['numeric_price'] = df['price'].str.extract(r'(\d+\.\d+)').astype(float).fillna(0)
    df['numeric_rating'] = df['rating'].apply(extract_numeric_rating).fillna(0)
    df['numeric_review_count'] = df['review_count'].apply(extract_review_count).fillna(0)

    # Apply sentiment analysis to get a polarity score for each review
    df['sentiment'] = df['reviews'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

    # Normalize price, rating, and review count
    df['normalized_price'] = normalize_column(df['numeric_price'])
    df['normalized_rating'] = normalize_column(df['numeric_rating'])
    df['normalized_sentiment'] = normalize_column(df['sentiment'])

    # Define weights
    weight_rating = 0.3
    weight_price = 0.2
    weight_sentiment = 0.5

    # Calculate the combined score based on weights
    df['combined_score'] = (df['normalized_rating'] * weight_rating) + \
                           (df['normalized_price'] * (1 - weight_price)) + \
                           (df['normalized_sentiment'] * weight_sentiment)

    # Sort products by combined score
    top_products = df.sort_values(by='combined_score', ascending=False).head(3)

    # Select and rename necessary columns for output
    top_products = top_products[['product_name', 'numeric_price', 'numeric_rating', 'combined_score']]
    top_products.rename(columns={'numeric_price': 'price', 'numeric_rating': 'rating'}, inplace=True)
    
    return top_products


# Main data process function where executes multiple above function to get the desire output
def process_data(data_frames, product_name):
    results = {}
    # Processing each dataframe according to the source
    for key, df in data_frames.items():
        if 'product' in df.columns:
            filtered = df[df['product'].str.contains(product_name, case=False, na=False)]
        else:
            filtered = df[df['product_name'].str.contains(product_name, case=False, na=False)]
        
        # Eliminate null values
        filtered = filtered.dropna()

        if key == 'amazon_product_reviews':
            results['amazon'] = process_amazon_data(filtered)
        elif key == 'bestbuy_combined':
            results['bestbuy_top_cheapest'] = bestbuy_top_cheapest(filtered, key)
        elif key == 'google_shopping_combined':
            results['google_top_cheapest'] = google_top_cheapest(filtered, key)
        elif key == 'walmart_products':
            results['walmart_top_cheapest'] = process_walmart_top_cheapest(filtered)

    return results