from data_loader import load_data
from user_interface import run_interface

def main():
    # Load data
    data_frames = load_data()

    # Run the user interface and process requests
    run_interface(data_frames)

if __name__ == "__main__":
    main()