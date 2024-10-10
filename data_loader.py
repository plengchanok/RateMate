import pandas as pd
import os
import subprocess

def load_data(user_choices):
    data_frames = {}
    
    # Execute scraping scripts according to user choices
    if user_choices['bestbuy']:
        subprocess.run(['python', 'bestbuy_data.py'], check=True)
    
    if user_choices['google']:
        subprocess.run(['python', 'google_shopping.py'], check=True)
    
    if user_choices['walmart']:
        subprocess.run(['python', 'walmart_data.py'], check=True)
    
    if user_choices['amazon']:
        subprocess.run(['python', 'amazon_data_process.py'], check=True)
    
    # Combine data files if any scraping was done
    if any(user_choices.values()):
        subprocess.run(['python', 'combined_script.py'], check=True)

    # Specifically load only the combined data files
    combined_files = {
        'amazon_product_reviews.csv': 'csv',
        'bestbuy_combined.csv': 'csv',
        'google_shopping_combined.csv': 'csv',
        'walmart_products.json': 'json'
    }

    for file_name, file_type in combined_files.items():
        if os.path.exists(file_name):
            if file_type == 'csv':
                df = pd.read_csv(file_name)
            elif file_type == 'json':
                df = pd.read_json(file_name)
            data_frames[file_name.split('.')[0]] = df
    
    return data_frames
