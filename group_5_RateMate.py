import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from data_processor import process_data
from data_loader import load_data

# Define colors
DARK_BLUE = "#010232"
RED = "#be306d"


# Load and resize logo
def load_logo():
    logo_img = Image.open("ratemate_logo.png")
    logo_img = logo_img.resize((300, 70), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(logo_img)


# Main Application Class
class RateMateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RateMate")
        self.root.geometry("800x600")
        self.root.configure(bg=DARK_BLUE)

        # Add logo
        self.logo = load_logo()
        logo_label = tk.Label(root, image=self.logo, bg=DARK_BLUE)
        logo_label.pack(pady=10)

        # Create main frame
        main_frame = tk.Frame(root, bg=DARK_BLUE)
        main_frame.pack(fill='both', expand=True)

        # Data source options
        self.data_choices = {
            'bestbuy': tk.BooleanVar(),
            'google': tk.BooleanVar(),
            'walmart': tk.BooleanVar(),
            'amazon': tk.BooleanVar()
        }

        for source in self.data_choices:
            checkbutton = tk.Checkbutton(main_frame, text=f"Download fresh data from {source.capitalize()}?",
                                         variable=self.data_choices[source], bg=DARK_BLUE, fg='white',
                                         selectcolor=RED)
            checkbutton.pack(anchor='w')

            if source == 'amazon':
                tk.Label(main_frame, text="Amazon data will be too large to download, suggest not to download it",
                         bg=DARK_BLUE, fg='white').pack(anchor='w')

        # Product selection with dropdown
        products = ["Macbook", "iPhone", "iPad", "Nintendo", "Playstation"]

        tk.Label(main_frame, text="Select a product:", bg=DARK_BLUE, fg='white').pack(pady=10)

        self.product_var = tk.StringVar(value=products[0])

        product_dropdown = ttk.Combobox(main_frame, textvariable=self.product_var, values=products)
        product_dropdown.pack()

        # Search button
        search_button = tk.Button(main_frame, text="Search", command=self.run_interface, bg=RED, fg='white')
        search_button.pack(pady=20)

        # Output text area with scrollbar
        output_frame = tk.Frame(main_frame)
        output_frame.pack(pady=10)

        self.output_text = tk.Text(output_frame, height=20, width=130, bg=RED, fg='white')
        scrollbar = ttk.Scrollbar(output_frame, orient='vertical', command=self.output_text.yview)

        self.output_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.output_text.pack(side='left', fill='both', expand=True)

    def run_interface(self):
        product_name = self.product_var.get()

        user_choices = {key: var.get() for key, var in self.data_choices.items()}

        try:
            # Load data
            data_frames = load_data(user_choices)

            # Process data
            results = process_data(data_frames, product_name)

            # Displaying results in the text widget
            self.output_text.delete(1.0, tk.END)  # Clear previous results

            for key, result in results.items():
                self.output_text.insert(tk.END, f"{key.capitalize()}:\n{result}\n\n")

        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error processing data: {str(e)}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = RateMateApp(root)
    root.mainloop()