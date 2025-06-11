"""
Visvim Web Scraper GUI Application

This module provides a graphical user interface for the Visvim web scraper and automated checkout system.
It allows users to input product details, PayPal credentials, and schedule automated purchases.

Key Features:
- User authentication
- Product entry management
- PayPal and credit card information input
- Scheduled checkout functionality
- Real-time status updates

Dependencies:
- tkinter
- threading
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from Scraper import main as scraper_main

# GUI Constants
PRIMARY_FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 14, "bold")
ENTRY_WIDTH = 25
BG_COLOR = "#f7f9fc"


class LoginPage(ttk.Frame):
    """
    Login page frame for user authentication.
    
    Attributes:
        on_success (callable): Callback function for successful login
        username_entry (ttk.Entry): Email input field
        password_entry (ttk.Entry): Password input field
    """
    
    def __init__(self, parent, on_success):
        """
        Initialize the login page.
        
        Args:
            parent: Parent widget
            on_success (callable): Callback function for successful login
        """
        super().__init__(parent)
        self.on_success = on_success
        self.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        ttk.Label(self, text="Login", font=HEADER_FONT).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Email:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Continue", command=self.validate_login).pack(pady=20)

    def validate_login(self):
        """Validate login credentials and trigger on_success callback if valid."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both email and password.")
            return
        self.on_success(username, password)
        self.destroy()


class ProductEntry:
    """
    Product entry widget for managing product details.
    
    Attributes:
        product_id (ttk.Entry): Product ID input field
        color (ttk.Entry): Color input field
        size (ttk.Entry): Size input field
    """
    
    def __init__(self, parent, row):
        """
        Initialize product entry fields.
        
        Args:
            parent: Parent widget
            row (int): Grid row position
        """
        self.product_id = ttk.Entry(parent, width=20)
        self.product_id.grid(row=row, column=0, padx=5, pady=2)
        self.color = ttk.Entry(parent, width=20)
        self.color.grid(row=row, column=1, padx=5, pady=2)
        self.size = ttk.Entry(parent, width=20)
        self.size.grid(row=row, column=2, padx=5, pady=2)

    def get_data(self):
        """
        Get the current product data.
        
        Returns:
            dict: Product data including ID, color, and size
        """
        return {
            'id': self.product_id.get().strip(),
            'color': self.color.get().strip(),
            'size': self.size.get().strip()
        }


class ScraperApp:
    """
    Main application window for the scraper tool.
    
    Attributes:
        root (tk.Tk): Root window
        status_var (tk.StringVar): Status message variable
        product_entries (list): List of ProductEntry instances
        current_row (int): Current row in product list
    """
    
    def __init__(self, root):
        """
        Initialize the main application window.
        
        Args:
            root (tk.Tk): Root window
        """
        self.root = root
        self.root.title("Product Scraper Tool")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)

        self.status_var = tk.StringVar(value="Idle.")

        # Header
        self.header = ttk.Label(root, text="Welcome to Product Scraper", font=HEADER_FONT)
        self.header.pack(pady=10)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize pages (tabs)
        self.product_tab = ttk.Frame(self.notebook)
        self.paypal_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.product_tab, text="Products")
        self.notebook.add(self.paypal_tab, text="PayPal")

        # Product Form Setup
        self.product_entries = []
        self.current_row = 0
        self.setup_product_tab()

        # PayPal Setup
        self.setup_paypal_tab()

        # Footer: status + submit
        footer = ttk.Frame(root)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.status_label = ttk.Label(footer, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(footer, text="Run Scraper", command=self.submit).pack(side=tk.RIGHT, padx=10)

    def setup_product_tab(self):
        """Set up the product entry tab with scrollable product list."""
        ttk.Label(self.product_tab, text="Enter Product Details", font=PRIMARY_FONT).pack(pady=5)

        canvas_frame = ttk.Frame(self.product_tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, height=300)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.product_list_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.product_list_frame, anchor="nw")

        self.product_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Headers
        headers = ["Product ID", "Color", "Size"]
        for i, text in enumerate(headers):
            ttk.Label(self.product_list_frame, text=text, width=20, background="#e8eef1").grid(row=0, column=i)

        # Add default row
        self.add_product()

        # Add product button
        ttk.Button(self.product_tab, text="Add Product", command=self.add_product).pack(pady=10)

    def setup_paypal_tab(self):
        """Set up the PayPal configuration tab with payment details form."""
        ttk.Label(self.paypal_tab, text="PayPal Credit Details", font=PRIMARY_FONT).pack(pady=10)

        form_frame = ttk.Frame(self.paypal_tab)
        form_frame.pack(pady=20)

        # PayPal Account Details
        ttk.Label(form_frame, text="PayPal Email:", width=15, anchor="e").grid(row=0, column=0, padx=5, pady=5)
        self.paypal_email_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_email_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="PayPal Password:", width=15, anchor="e").grid(row=1, column=0, padx=5, pady=5)
        self.paypal_password_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH, show="*")
        self.paypal_password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Credit Card Details
        ttk.Label(form_frame, text="Card Number:", width=15, anchor="e").grid(row=2, column=0, padx=5, pady=5)
        self.card_number_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.card_number_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="CVV:", width=15, anchor="e").grid(row=3, column=0, padx=5, pady=5)
        self.paypal_cvv_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_cvv_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Expiry:", width=15, anchor="e").grid(row=4, column=0, padx=5, pady=5)
        self.paypal_expiry_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_expiry_entry.grid(row=4, column=1, padx=5, pady=5)

        # Personal Information
        ttk.Label(form_frame, text="First Name:", width=15, anchor="e").grid(row=5, column=0, padx=5, pady=5)
        self.paypal_first_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_first_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Last Name:", width=15, anchor="e").grid(row=6, column=0, padx=5, pady=5)
        self.paypal_last_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_last_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Address:", width=15, anchor="e").grid(row=7, column=0, padx=5, pady=5)
        self.paypal_address_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_address_entry.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="City:", width=15, anchor="e").grid(row=8, column=0, padx=5, pady=5)
        self.paypal_city_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_city_entry.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="State:", width=15, anchor="e").grid(row=9, column=0, padx=5, pady=5)
        self.paypal_state_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_state_entry.grid(row=9, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Zip_code:", width=15, anchor="e").grid(row=10, column=0, padx=5, pady=5)
        self.paypal_zip_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_zip_entry.grid(row=10, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Phone:", width=15, anchor="e").grid(row=11, column=0, padx=5, pady=5)
        self.paypal_phone_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_phone_entry.grid(row=11, column=1, padx=5, pady=5)

        # Timer
        ttk.Label(form_frame, text="Time [Format: YYYY-MM-DD HH:MM:SS]:", width=15, anchor="e").grid(row=12, column=0, padx=5, pady=5)
        self.paypal_time_entry = ttk.Entry(form_frame, width=ENTRY_WIDTH)
        self.paypal_time_entry.grid(row=12, column=1, padx=5, pady=5)

    def add_product(self):
        """Add a new product entry row to the product list."""
        self.current_row += 1
        pe = ProductEntry(self.product_list_frame, self.current_row)
        self.product_entries.append(pe)

    def submit(self):
        """Validate and submit the form data to start the scraping process."""
        products = [e.get_data() for e in self.product_entries if any(e.get_data().values())]
        if not products:
            messagebox.showwarning("Input Error", "Please enter at least one product.")
            return

        paypal_email = self.paypal_email_entry.get().strip()
        paypal_password = self.paypal_password_entry.get().strip()
        card_number = self.card_number_entry.get().strip()
        cvv = self.paypal_cvv_entry.get().strip()
        expiry = self.paypal_expiry_entry.get().strip()
        first_name = self.paypal_first_entry.get().strip()
        last_name = self.paypal_last_entry.get().strip()
        address = self.paypal_address_entry.get().strip()
        city = self.paypal_city_entry.get().strip()
        state = self.paypal_state_entry.get().strip()
        zip_code = self.paypal_zip_entry.get().strip()
        phone = self.paypal_phone_entry.get().strip()
        time = self.paypal_time_entry.get().strip()

        if not card_number or not cvv or not expiry or not first_name or not last_name or not address or not city or not state or not zip_code or not phone:
            messagebox.showwarning("Input Error", "Please fill in all PayPal credit details.")
            return

        if not paypal_email or not paypal_password:
            messagebox.showwarning("Input Error", "Please enter PayPal credentials.")
            return
        
        card_info = {
            'number': card_number,
            'cvv': cvv,
            'expiry': expiry,
            'first_name': first_name,
            'last_name': last_name,
        }

        personal_info = {
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'phone': phone
        }

        threading.Thread(
            target=self.run_scraper,
            args=(products, paypal_email, paypal_password, card_info, personal_info, time),
            daemon=True
        ).start()

    def run_scraper(self, products, paypal_email, paypal_password, card_info, personal_info, time):
        """
        Run the scraper in a separate thread.
        
        Args:
            products (list): List of product dictionaries
            paypal_email (str): PayPal account email
            paypal_password (str): PayPal account password
            card_info (dict): Credit card information
            personal_info (dict): Personal information
            time (str): Target time for checkout
        """
        try:
            ids = [p['id'] for p in products]
            sizes = [p['size'] for p in products]
            colors = [p['color'] for p in products]

            self.status_var.set("Running scraper...")
            scraper_main(self.username, self.password, ids, sizes, colors, paypal_email, paypal_password, card_info, personal_info, time)
            self.status_var.set("Scraper finished.")
            messagebox.showinfo("Success", "Scraper completed successfully.")
        except Exception as e:
            self.status_var.set("Error during scraping.")
            messagebox.showerror("Scraper Error", str(e))

    def set_credentials(self, username, password):
        """
        Set user credentials and update header.
        
        Args:
            username (str): User's email
            password (str): User's password
        """
        self.username = username
        self.password = password
        self.header.config(text=f"Product Scraper - Logged in as {username}")


if __name__ == '__main__':
    root = tk.Tk()
    app = None

    def on_login_success(username, password):
        """Initialize main application after successful login."""
        global app
        app = ScraperApp(root)
        app.set_credentials(username, password)

    LoginPage(root, on_login_success)
    root.mainloop()

