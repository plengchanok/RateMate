import pandas as pd

# Set the path where your CSV files are located
csv_files_google = ["google_shopping_organic_ipad.csv", 
                    "google_shopping_organic_iphone.csv",
                    "google_shopping_organic_macbook.csv",
                    "google_shopping_organic_nintendo.csv",
                    "google_shopping_organic_playstation.csv"]

product_names = ['iPad', 'iPhone', 'Macbook', 'Nintendo', 'PlayStation']

# Read and concatenate all CSV files
combined_csv = pd.concat(
    [pd.read_csv(file, index_col=None).assign(product=product_names[i]) for i, file in enumerate(csv_files_google)],
    ignore_index=True
)

combined_csv['reviews_count'] = combined_csv['reviews_count'].fillna(0)
combined_csv['price'] = combined_csv['price'].fillna(0)
combined_csv['rating'] = combined_csv['rating'].fillna(0)

# Save the concatenated file to a new CSV
combined_csv.to_csv("google_shopping_combined.csv", index=False, mode='w')

# combined_csv

# Set the path where your CSV files are located
csv_files_bestbuy = ["search_ipad.csv", 
                    "search_iphone.csv",
                    "search_macbook.csv",
                    "search_ps.csv",
                    "search_switch.csv"]

product_names = ['iPad', 'iPhone', 'Macbook', 'PlayStation', 'Nintendo']

# Read and concatenate all CSV files
combined_csv = pd.concat(
    [pd.read_csv(file, index_col=None).assign(product=product_names[i]) for i, file in enumerate(csv_files_bestbuy)],
    ignore_index=True
)
combined_csv['rating_count'] = combined_csv['rating_count'].fillna(0)
combined_csv['price'] = combined_csv['price'].fillna(0)
combined_csv['rating'] = combined_csv['rating'].fillna(0)

# # Save the concatenated file to a new CSV
combined_csv.to_csv("bestbuy_combined.csv", index=False, mode = 'w')



