import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

from test_UserRegistration import UserRegistration
from test_OrderPlacement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod
from test_PaymentProcessing import PaymentProcessing
from test_RestaurantBrowsing import RestaurantDatabase, RestaurantBrowsing

# Utility functions for user data storage
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Food Delivery App")
        self.geometry("600x400")

        # Load user registration data from file
        self.user_data = load_users()

        # Initialize core classes
        self.registration = UserRegistration()
        self.registration.users = self.user_data  # Load existing users into registration system

        self.database = RestaurantDatabase()
        self.browsing = RestaurantBrowsing(self.database)

        # Initially no user logged in
        self.logged_in_email = None

        # Create initial frame
        self.current_frame = None
        self.show_startup_frame()

    def show_startup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartupFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = RegisterFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def login_user(self, email):
        self.logged_in_email = email
        # After login, show main app frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, email)
        self.current_frame.pack(fill="both", expand=True)


class StartupFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Welcome to the Mobile Food Delivery App", font=("Arial", 16)).pack(pady=30)

        tk.Button(self, text="Register", command=self.go_to_register, width=20).pack(pady=10)
        tk.Button(self, text="Login", command=self.go_to_login, width=20).pack(pady=10)

    def go_to_register(self):
        self.master.show_register_frame()

    def go_to_login(self):
        self.master.show_login_frame()


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Register New User", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")
        self.conf_pass_entry = self.create_entry("Confirm Password:", show="*")

        tk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def register_user(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.conf_pass_entry.get()

        result = self.master.registration.register(email, password, confirm_password)
        if result["success"]:
            # Save the updated users to file
            save_users(self.master.registration.users)
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            self.master.show_login_frame()
        else:
            messagebox.showerror("Error", result["error"])

    def go_back(self):
        self.master.show_startup_frame()


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="User Login", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        # Validate login
        # For simplicity, just check if user exists and password matches
        users = self.master.registration.users
        if email in users and users[email]["password"] == password:
            self.master.login_user(email)
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def go_back(self):
        self.master.show_startup_frame()


class MainAppFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {user_email}", font=("Arial", 14)).pack(pady=10)

        self.user_email = user_email
        self.database = master.database
        self.browsing = master.browsing

        # Create user's profile and cart
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

        # Search Frame
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Cuisine:").pack(side="left")
        self.cuisine_var = tk.Entry(search_frame)
        self.cuisine_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_restaurants).pack(side="left")

        tk.Label(search_frame, text="Location:").pack(side="left")
        self.location_var = tk.Entry(search_frame)
        self.location_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search by Location", command=self.search_restaurants_by_location).pack(side="left")

        # Rating search
        tk.Label(search_frame, text="Rating:").pack(side="left")
        self.rating_var = tk.Entry(search_frame)
        self.rating_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search by Rating", command=self.search_restaurants_by_rating).pack(side="left")

        # Results Treeview
        self.results_tree = ttk.Treeview(self, columns=("cuisine", "location", "rating"), show="headings")
        self.results_tree.heading("cuisine", text="Cuisine")
        self.results_tree.heading("location", text="Location")
        self.results_tree.heading("rating", text="Rating")
        self.results_tree.pack(pady=10, fill="x")

        # Buttons for actions
        action_frame = tk.Frame(self)
        action_frame.pack(pady=5)
        tk.Button(action_frame, text="View All Restaurants", command=self.view_all_restaurants).pack(side="left", padx=5)
        tk.Button(action_frame, text="Add Item to Cart", command=self.add_item_to_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="View Cart", command=self.view_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="Checkout", command=self.checkout).pack(side="left", padx=5)

    def search_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        cuisine = self.cuisine_var.get().strip()
        results = self.browsing.search_by_filters(cuisine_type=cuisine if cuisine else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def search_restaurants_by_location(self):
        self.results_tree.delete(*self.results_tree.get_children())
        location = self.location_var.get().strip()
        results = self.browsing.search_by_location(location if location else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def search_restaurants_by_rating(self):
        self.results_tree.delete(*self.results_tree.get_children())
        rating = float(self.rating_var.get().strip()) if self.rating_var.get().strip() else None
        results = self.browsing.search_by_rating(rating if rating else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def view_all_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        results = self.database.get_restaurants()
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def add_item_to_cart(self):
        # For simplicity, let's assume user always adds "Pizza"
        # A more sophisticated approach: Let user select from menu items.
        # We will show a small popup to choose items.
        menu_popup = AddItemPopup(self, self.restaurant_menu, self.cart)
        self.wait_window(menu_popup)

    def remove_item_from_cart(self, item_name):
        """
        Removes an item from the cart.

        Args:
            item_name (str): The name of the item to be removed.
        """
        self.cart.remove_item(item_name)
        messagebox.showinfo("Cart Update", f"Item '{item_name}' removed from cart.")
        self.view_cart()  # Refresh the cart view after removal

    def update_item_quantity_in_cart(self, item_name, new_quantity):
        """
        Updates the quantity of an item in the cart.

        Args:
            item_name (str): The name of the item to update.
            new_quantity (int): The new quantity for the item.
        """
        result = self.cart.update_item_quantity(item_name, new_quantity)
        messagebox.showinfo("Cart Update", result)
        self.view_cart()  # Refresh the cart view after updating quantity

    def view_cart(self):
        cart_view = CartViewPopup(self, self.cart)
        self.wait_window(cart_view)

    def view_order_history(self):
        """
        Displays the user's order history in a new popup window.
        """
        history_popup = OrderHistoryPopup(self, self.user_profile)
        self.wait_window(history_popup)

    def checkout(self):
        # Validate order and proceed if valid
        validation = self.order_placement.validate_order()
        if not validation["success"]:
            messagebox.showerror("Error", validation["message"])
            return

        # Show Checkout Popup
        checkout_popup = CheckoutPopup(self, self.order_placement)
        self.wait_window(checkout_popup)

class OrderHistoryPopup(tk.Toplevel):
    def __init__(self, master, user_profile):
        super().__init__(master)
        self.title("Order History")

        self.user_profile = user_profile
        self.order_history = self.user_profile.order_history

        tree = ttk.Treeview(self, columns=("Order ID", "Date", "Total", "Status"), show="headings")
        tree.heading("Order ID", text="Order ID")
        tree.heading("Date", text="Date")
        tree.heading("Total", text="Total")
        tree.heading("Status", text="Status")

        for order in self.order_history:
            tree.insert("", "end", values=(order["order_id"], order["date"], order["total_amount"], order["status"]))

        tree.pack(pady=10, fill="x")

        # Add filter options
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Filter by:").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.set("Status")  # default value
        tk.OptionMenu(filter_frame, self.filter_var, "Status", "Date").pack(side="left")

        tk.Label(filter_frame, text="Value:").pack(side="left")
        self.filter_value_entry = tk.Entry(filter_frame)
        self.filter_value_entry.pack(side="left")

        tk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).pack(side="left")

    def apply_filter(self):
        filter_by = self.filter_var.get()
        filter_value = self.filter_value_entry.get()
        filtered_orders = self.user_profile.order_history
        if filter_by and filter_value:
            filtered_orders = [order for order in self.user_profile.order_history
                               if order[filter_by] == filter_value]
        for i in self.order_history.tree.get_children():
            self.order_history.tree.delete(i)
        for order in filtered_orders:
            self.order_history.tree.insert("", "end", values=(order["order_id"], order["date"], order["total_amount"], order["status"]))

class AddItemPopup(tk.Toplevel):
    def __init__(self, master, menu, cart):
        super().__init__(master)
        self.title("Add Item to Cart")
        self.menu = menu
        self.cart = cart

        tk.Label(self, text="Select an item to add to cart:").pack(pady=10)

        self.item_var = tk.StringVar()
        self.item_var.set(self.menu.available_items[0] if self.menu.available_items else "")
        tk.OptionMenu(self, self.item_var, *self.menu.available_items).pack(pady=5)

        tk.Label(self, text="Quantity:").pack()
        self.qty_entry = tk.Entry(self)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=5)

        tk.Button(self, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

    def add_to_cart(self):
        item = self.item_var.get()
        qty = int(self.qty_entry.get())
        price = 10.0  # Static price for simplicity
        msg = self.cart.add_item(item, price, qty)
        messagebox.showinfo("Cart", msg)
        self.destroy()


class CartViewPopup(tk.Toplevel):
    def __init__(self, master, cart):
        super().__init__(master)
        self.title("Cart Items")

        self.cart = cart
        self.items = cart.view_cart()
        if not self.items:
            tk.Label(self, text="Your cart is empty").pack(pady=20)
        else:
            for i in self.items:
                item_frame = tk.Frame(self)
                item_frame.pack(pady=5, padx=10)
                tk.Label(item_frame, text=f"{i['name']} x{i['quantity']} = ${i['subtotal']:.2f}").pack(side="left")
                tk.Entry(item_frame, width=5).pack(side="left")  # Quantity input field
                tk.Button(item_frame, text="Update",command=lambda item=i['name']: master.update_item_quantity_in_cart(item,int(self.get_entry_value()))).pack(side="right")
                tk.Button(item_frame, text="Remove",command=lambda item=i['name']: master.remove_item_from_cart(item)).pack(side="right")

        items = cart.view_cart()

    def get_entry_value(self):
        """
        Gets the value from the last quantity input field.
        """
        # This method should be updated to correctly retrieve the value from the entry widget
        # For now, it's a placeholder to show where the logic will go
        return "1"  # Placeholder return


class CheckoutPopup(tk.Toplevel):
    def __init__(self, master, order_placement):
        super().__init__(master)
        self.title("Checkout")
        self.order_placement = order_placement

        order_data = order_placement.proceed_to_checkout()
        tk.Label(self, text="Review your order:", font=("Arial", 12)).pack(pady=10)

        # Show items
        for item in order_data["items"]:
            tk.Label(self, text=f"{item['name']} x{item['quantity']} = ${item['subtotal']:.2f}").pack()

        total = order_data["total_info"]
        tk.Label(self, text=f"Subtotal: ${total['subtotal']:.2f}").pack()
        tk.Label(self, text=f"Tax: ${total['tax']:.2f}").pack()
        tk.Label(self, text=f"Delivery Fee: ${total['delivery_fee']:.2f}").pack()
        tk.Label(self, text=f"Total: ${total['total']:.2f}").pack()

        tk.Label(self, text=f"Delivery Address: {order_data['delivery_address']}").pack(pady=5)

        # Payment method selection
        tk.Label(self, text="Payment Method:").pack(pady=5)
        self.payment_method = tk.StringVar()
        self.payment_method.set("credit_card")
        tk.Radiobutton(self, text="Credit Card", variable=self.payment_method, value="credit_card").pack()
        tk.Radiobutton(self, text="Paypal", variable=self.payment_method, value="paypal").pack()

        tk.Label(self, text="For credit card enter a 16-digit card number:").pack(pady=5)
        self.card_entry = tk.Entry(self)
        self.card_entry.insert(0, "1234567812345678")
        self.card_entry.pack(pady=5)

        tk.Button(self, text="Confirm Order", command=self.confirm_order).pack(pady=10)

    def confirm_order(self):
        # Process order confirmation with the given payment method
        payment_method_obj = PaymentMethod()  # Mock payment method handling in the old code
        # Actually, we have PaymentProcessing class. Let's just rely on PaymentMethod for simplicity here.
        # If you wanted to use PaymentProcessing, you could do so by integrating it as well.
        # For now, we'll simulate PaymentMethod.process_payment by checking if total > 0.
        # In a full scenario, integrate PaymentProcessing similarly.

        # Confirm the order
        result = self.order_placement.confirm_order(payment_method_obj)
        if result["success"]:
            order_id = "ORD123456"  # Simulate an order ID.
            items = self.order_placement.cart.view_cart()
            total = self.order_placement.cart.calculate_total()["total"]
            self.order_placement.save_order_history(order_id, items, total, "pending")
            messagebox.showinfo("Order Confirmed", f"Order ID: {result['order_id']}\nEstimated Delivery: {result['estimated_delivery']}")
            self.destroy()
        else:
            messagebox.showerror("Error", result["message"])


if __name__ == "__main__":
    app = Application()
    app.mainloop()
