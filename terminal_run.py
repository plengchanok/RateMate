### A1 Group 5 ###
# Name: Elaine Cao
# AndrewID: yilingca

# Name: Jane Wu
# AndrewID: sjanew2

# Name: Pleng Witayaweerasak
# AndrewID: pwitayaw

# Name: Shreyas Nopany
# AndrewID: snopany

from data_loader import load_data
from user_interface import run_interface

def main():
    # Load data
    data_frames = load_data()

    # Run the user interface and process requests
    run_interface(data_frames)

if __name__ == "__main__":
    main()