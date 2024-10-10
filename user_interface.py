from data_processor import process_data, perform_sentiment_analysis
from data_loader import load_data

print('------------------------------------------------------------------------------------------------------------------')
print('------------------------------------------------------------------------------------------------------------------')
print('Welcome to RateMate!')
print('------------------------------------------------------------------------------------------------------------------')

# Offer an option for the users to download the data
def get_user_data_choice():
    print("Please specify how you would like to handle data for each source:")
    choices = {}
    
    # Best Buy Data
    bestbuy_choice = input("Download fresh data from Best Buy? (yes/no): ").strip().lower()
    choices['bestbuy'] = bestbuy_choice == 'yes'
    
    # Google Shopping Data
    google_choice = input("Download fresh data from Google Shopping? (yes/no): ").strip().lower()
    choices['google'] = google_choice == 'yes'
    
    # Walmart Data
    walmart_choice = input("Download fresh data from Walmart? (yes/no): ").strip().lower()
    choices['walmart'] = walmart_choice == 'yes'
    
    # Amazon Data
    print("Note: Processing and downloading Amazon data takes several hours. It is recommended to use existing data.")
    amazon_choice = input("Still download fresh Amazon data? (yes/no): ").strip().lower()
    choices['amazon'] = amazon_choice == 'yes'
    
    return choices


def display_menu():
    menu_options = {
        '1': 'Macbook',
        '2': 'iPhone',
        '3': 'iPad',
        '4': 'Nintendo',
        '5': 'Playstation',
        '6': 'Exit'
    }
    print('------------------------------------------------------------------------------------------------------------------')
    print("Please choose a product to search for or exit the program by entering the corresponding number:")
    for key in menu_options:
        print(f"{key}. {menu_options[key]}")
    return menu_options

def run_interface(data_frames):
    while True:  # Start an infinite loop
        menu_options = display_menu()
        choice = input("Enter your choice: ")

        # Validate user input
        while choice not in menu_options:
            print("Invalid choice. Please enter a number from the menu.")
            choice = input("Enter your choice: ")
        
        if choice == '6':
            print("Exiting the program. Goodbye!")
            break  # Exit the loop, thus terminating the program

        product_name = menu_options[choice]
        print(f"\nYou have selected: {product_name}\n")

        # Process data based on source and display results
        results = process_data(data_frames, product_name)
        for key, result in results.items():
            if 'amazon' in key:
                print(f"\nTop 3 Products from Amazon for {product_name}:")
                print(result)
            elif 'bestbuy_top_cheapest' in key:
                print(f"\nTop 3 Cheapest Products from Best Buy for {product_name}:")
                print(result)
            elif 'google_top_cheapest' in key:
                print(f"\nTop 3 Cheapest Products from Google Shopping for {product_name}:")
                print(result)
            elif 'walmart_top_cheapest' in key:
                print(f"\nTop 3 Cheapest Products from Walmart for {product_name}:")
                print(result) 
 

if __name__ == "__main__":
    # This allows the module to be run for testing
    user_choices = get_user_data_choice()
    data_frames = load_data(user_choices)
    run_interface(data_frames)
