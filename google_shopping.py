import requests
from pprint import pprint
import json
from pathlib import Path
import pandas as pd
# Define credentials
USERNAME = "ratemate_BKQXC"
PASSWORD = "xtfGy3tPUf53H_"
queries = ['iphone', 'ipad', 'macbook', 'nintendo', 'playstation']
           
for query in queries:
        # Structure payload.
        payload = {
        'source': 'google_shopping_search',
        'query': query,
        'parse': True
        }

        # Get response.
        response = requests.request(
            'POST',
            'https://realtime.oxylabs.io/v1/queries',
            auth=(USERNAME, PASSWORD), #Your credentials go here
            json=payload,
        )

        # Instead of response with job status and results url, this will return the
        # JSON response with results.
        # print(response.json())
        print("Loading data...")
        data = response.json()

        # Initialize a list to hold extracted rows
        rows = []

        # Loop through the results and extract the relevant fields
        for item in data['results'][0]['content']['results']['organic']:
            row = {
                'pos': item.get('pos', None),
                'title': item.get('title', None),
                'merchant': item.get('merchant', None).get('name', None),
                'price': item.get('price', None),
                'rating': item.get('rating', None),
                'reviews_count': item.get('reviews_count', None)
            }
            rows.append(row)

        # Convert the list of rows into a DataFrame for a tabular view
        df = pd.DataFrame(rows)

        # # Display the DataFrame
        # print(df)

        # Save files in csv
        output = Path(__file__).parent
        output_path = "google_shopping_organic_"+query+".csv"
        df.to_csv(output / output_path, mode = 'w')
        print(f'Updated file for google_shopping_{query}')

