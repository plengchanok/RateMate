import pandas as pd
import json
import random
from textblob import TextBlob

def load_sampled_jsonl(file_path, sample_rate=0.1):
    data = []
    total_lines = 0
    sampled_lines = 0
    
    # Open the file
    with open(file_path, 'r') as file:
        # Iterate over each line
        for line in file:
            total_lines += 1
            # Sample lines according to the sample_rate
            if random.random() < sample_rate:
                # Load the JSON from line
                data.append(json.loads(line))
                sampled_lines += 1
    
    print(f"Processed {total_lines} lines.")
    print(f"Sampled {sampled_lines} lines.")
    return pd.DataFrame(data)

# Specify the sample rate (e.g., 10%)
sample_rate = 0.1

# Load the datasets
print("Loading products data...")
products_sample = load_sampled_jsonl("meta_Electronics.jsonl", sample_rate=sample_rate)
print("Loading reviews data...")
reviews_sample = load_sampled_jsonl("Electronics.jsonl", sample_rate=sample_rate)

# Merge both DataFrames with a common key 'parent_asin' for products and 'parent_asin' for reviews
print("Merging data...")
merged_data = pd.merge(reviews_sample, products_sample, left_on='parent_asin', right_on='parent_asin', how='inner')
print("Merge completed.")

# Specify columns to keep
columns_to_keep = ['parent_asin', 'average_rating', 'price', 'rating', 'text', 'description', 'categories', 'main_category', 'details']
filtered_data = merged_data[columns_to_keep]

def contains_keyword(description_list, keyword):
    """ Check if any string in the list contains the keyword. """
    if not isinstance(description_list, list):
        return False  # or handle conversion if necessary
    return any(keyword.lower() in str(desc).lower() for desc in description_list)

################################################################################################################################
# Extract Macbook data

def is_brand_apple(details):
    return details.get('Brand', '').lower() == 'apple'

# Apply filters for MacBook, Computers category, and Apple brand
macbook_related = filtered_data[
    (filtered_data['text'].str.contains('macbook', case=False, na=False) |
    filtered_data['description'].apply(lambda desc_list: contains_keyword(desc_list, 'macbook'))) &
    (filtered_data['main_category'] == 'Computers') &
    filtered_data['details'].apply(is_brand_apple)
]
# macbook_related.head()

# Calculate sentiment polarity
def calculate_sentiment(text):
    return TextBlob(text).sentiment.polarity

macbook_related['sentiment_score'] = macbook_related['text'].apply(calculate_sentiment)

# Normalize ratings, price, and sentiment score
max_rating = macbook_related['average_rating'].max()
min_price = macbook_related['price'].min()
max_sentiment = macbook_related['sentiment_score'].max()

macbook_related['normalized_rating'] = macbook_related['average_rating'] / max_rating
macbook_related['normalized_price'] = 1 - (macbook_related['price'] - min_price) / (macbook_related['price'].max() - min_price)
macbook_related['normalized_sentiment'] = macbook_related['sentiment_score'] / max_sentiment

# Weight the components
weight_rating = 0.3
weight_price = 0.2
weight_sentiment = 0.5

# Calculate combined score
macbook_related['combined_score'] = (macbook_related['normalized_rating'] * weight_rating +
                                     macbook_related['normalized_price'] * weight_price +
                                     macbook_related['normalized_sentiment'] * weight_sentiment)

# Sort by combined score in descending order and print the top 3 entries
macbook_related_sorted = macbook_related.sort_values(by='combined_score', ascending=False)

df_macbook = pd.DataFrame(macbook_related_sorted[['text', 'normalized_rating', 'price', 'sentiment_score', 'combined_score']])

# Add 'product' column with 'iPhone' as the value for all rows
df_macbook['product'] = 'Macbook'

df_macbook = df_macbook.drop_duplicates()

################################################################################################################################
# Extract iPhone data
iphone_related = filtered_data[
    (filtered_data['text'].str.contains('iphone', case=False, na=False) |
    filtered_data['description'].apply(lambda desc_list: contains_keyword(desc_list, 'iphone')))&
    filtered_data['details'].apply(is_brand_apple)
]

iphone_related['sentiment_score'] = iphone_related['text'].apply(calculate_sentiment)

# Normalize ratings, price, and sentiment score
max_rating = iphone_related['average_rating'].max()
min_price = iphone_related['price'].min()
max_sentiment = iphone_related['sentiment_score'].max()

iphone_related['normalized_rating'] = iphone_related['average_rating'] / max_rating
iphone_related['normalized_price'] = 1 - (iphone_related['price'] - min_price) / (iphone_related['price'].max() - min_price)
iphone_related['normalized_sentiment'] = iphone_related['sentiment_score'] / max_sentiment

# Weight the components
weight_rating = 0.3
weight_price = 0.2
weight_sentiment = 0.5

# Calculate combined score
iphone_related['combined_score'] = (iphone_related['normalized_rating'] * weight_rating +
                                     iphone_related['normalized_price'] * weight_price +
                                     iphone_related['normalized_sentiment'] * weight_sentiment)

# Sort by combined score in descending order
iphone_related_sorted = iphone_related.sort_values(by='combined_score', ascending=False)

df_iphone = pd.DataFrame(iphone_related_sorted[['text', 'normalized_rating', 'price', 'sentiment_score', 'combined_score']])

# Add 'product' column with 'iPhone' as the value for all rows
df_iphone['product'] = 'iPhone'

df_iphone = df_iphone.drop_duplicates()

################################################################################################################################
# Extract ipad data
ipad_related = filtered_data[
    (filtered_data['text'].str.contains('ipad', case=False, na=False) |
    filtered_data['description'].apply(lambda desc_list: contains_keyword(desc_list, 'ipad')))&
    filtered_data['details'].apply(is_brand_apple)
]

ipad_related['sentiment_score'] = ipad_related['text'].apply(calculate_sentiment)

# Normalize ratings, price, and sentiment score
max_rating = ipad_related['average_rating'].max()
min_price = ipad_related['price'].min()
max_sentiment = ipad_related['sentiment_score'].max()

ipad_related['normalized_rating'] = ipad_related['average_rating'] / max_rating
ipad_related['normalized_price'] = 1 - (ipad_related['price'] - min_price) / (ipad_related['price'].max() - min_price)
ipad_related['normalized_sentiment'] = ipad_related['sentiment_score'] / max_sentiment

# Weight the components
weight_rating = 0.3
weight_price = 0.2
weight_sentiment = 0.5

# Calculate combined score
ipad_related['combined_score'] = (ipad_related['normalized_rating'] * weight_rating +
                                     ipad_related['normalized_price'] * weight_price +
                                     ipad_related['normalized_sentiment'] * weight_sentiment)

# Sort by combined score in descending order
ipad_related_sorted = ipad_related.sort_values(by='combined_score', ascending=False)

df_ipad = pd.DataFrame(ipad_related_sorted[['text', 'normalized_rating', 'price', 'sentiment_score', 'combined_score']])

# Add 'product' column with 'iPhone' as the value for all rows
df_ipad['product'] = 'iPad'

df_ipad = df_ipad.drop_duplicates()

################################################################################################################################
# Extract Nintendo data
def is_brand_nintendo(details):
    return details.get('Brand', '').lower() == 'nintendo'

nintendo_related = filtered_data[
    (filtered_data['text'].str.contains('nintendo', case=False, na=False) |
     filtered_data['description'].apply(lambda desc_list: contains_keyword(desc_list, 'nintendo'))) &
    filtered_data['details'].apply(is_brand_nintendo)
]

nintendo_related['sentiment_score'] = nintendo_related['text'].apply(calculate_sentiment)

# Normalize ratings, price, and sentiment score
max_rating = nintendo_related['average_rating'].max()
min_price = nintendo_related['price'].min()
max_price = nintendo_related['price'].max()
max_sentiment = nintendo_related['sentiment_score'].max()

nintendo_related['normalized_rating'] = nintendo_related['average_rating'] / max_rating

# Normalize price
price_range = max_price - min_price
if price_range != 0:
    nintendo_related['normalized_price'] = 1 - (nintendo_related['price'] - min_price) / price_range
else:
    nintendo_related['normalized_price'] = 0

nintendo_related['normalized_sentiment'] = nintendo_related['sentiment_score'] / max_sentiment

# Weight the components
weight_rating = 0.3
weight_price = 0.2
weight_sentiment = 0.5

# Calculate combined score
nintendo_related['combined_score'] = (nintendo_related['normalized_rating'] * weight_rating +
                                     nintendo_related['normalized_price'] * weight_price +
                                     nintendo_related['normalized_sentiment'] * weight_sentiment)

# Sort by combined score in descending order
nintendo_related_sorted = nintendo_related.sort_values(by='combined_score', ascending=False)

df_nintendo = pd.DataFrame(nintendo_related_sorted[['text', 'normalized_rating', 'price', 'sentiment_score', 'combined_score']])

# Add 'product' column with 'iPhone' as the value for all rows
df_nintendo['product'] = 'Nintendo'

df_nintendo = df_nintendo.drop_duplicates()

################################################################################################################################
# Extract PlayStation data

def is_brand_ps(details):
    return details.get('Brand', '').lower() == 'sony'

ps_related = filtered_data[
    (filtered_data['text'].str.contains('playstation', case=False, na=False) |
     filtered_data['description'].apply(lambda desc_list: contains_keyword(desc_list, 'playstation'))) &
    filtered_data['details'].apply(is_brand_ps)
]

ps_related['sentiment_score'] = ps_related['text'].apply(calculate_sentiment)

# Normalize ratings, price, and sentiment score
max_rating = ps_related['average_rating'].max()
min_price = ps_related['price'].min()
max_sentiment = ps_related['sentiment_score'].max()

ps_related['normalized_rating'] = ps_related['average_rating'] / max_rating
ps_related['normalized_price'] = 1 - (ps_related['price'] - min_price) / (ps_related['price'].max() - min_price)
ps_related['normalized_sentiment'] = ps_related['sentiment_score'] / max_sentiment

# Weight the components
weight_rating = 0.3
weight_price = 0.2
weight_sentiment = 0.5

# Calculate combined score
ps_related['combined_score'] = (ps_related['normalized_rating'] * weight_rating +
                                     ps_related['normalized_price'] * weight_price +
                                     ps_related['normalized_sentiment'] * weight_sentiment)

# Sort by combined score in descending order
ps_related_sorted = ps_related.sort_values(by='combined_score', ascending=False)

df_ps = pd.DataFrame(ps_related_sorted[['text', 'normalized_rating', 'price', 'sentiment_score', 'combined_score']])

# Add 'product' column with 'iPhone' as the value for all rows
df_ps['product'] = 'PlayStation'

df_ps = df_ps.drop_duplicates()

# Combine the DataFrames into one
combined_df = pd.concat([df_macbook, df_iphone, df_ipad, df_nintendo, df_ps], ignore_index=True)

# # Save the combined DataFrame to a CSV file
# combined_df.to_csv('combined_product_reviews.csv', index=False)

combined_df.to_csv('amazon_product_reviews1.csv', index=False)

