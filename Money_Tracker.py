import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize SQLite database
conn = sqlite3.connect('finance_tracker.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS transactions (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             date TEXT,
             category TEXT,
             amount REAL,
             type TEXT,
             user_id INTEGER
             )''')
conn.commit()
conn.close()

# GUI Class
class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("900x600")

        # Initialize components
        self.label_title = tk.Label(self.root, text="Personal Finance Tracker", font=("Arial", 24))
        self.label_title.pack(pady=20)

        self.frame_balance = tk.Frame(self.root)
        self.frame_balance.pack(pady=10)

        self.label_balance = tk.Label(self.frame_balance, text="Balance: $0.00", font=("Arial", 16))
        self.label_balance.pack(side=tk.LEFT, padx=10)

        self.btn_refresh = tk.Button(self.frame_balance, text="Refresh", command=self.refresh_balance)
        self.btn_refresh.pack(side=tk.LEFT, padx=10)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(pady=20)

        self.btn_add_transaction = tk.Button(self.frame_buttons, text="Add Transaction", command=self.add_transaction)
        self.btn_add_transaction.grid(row=0, column=0, padx=10)

        self.btn_view_transactions = tk.Button(self.frame_buttons, text="View Transactions", command=self.view_transactions)
        self.btn_view_transactions.grid(row=0, column=1, padx=10)

        self.btn_generate_report = tk.Button(self.frame_buttons, text="Generate Report", command=self.generate_report)
        self.btn_generate_report.grid(row=0, column=2, padx=10)

        self.frame_transactions = tk.Frame(self.root)
        self.frame_transactions.pack(pady=20)

        self.label_transactions = tk.Label(self.frame_transactions, text="Transactions", font=("Arial", 18))
        self.label_transactions.pack()

        self.listbox_transactions = tk.Listbox(self.frame_transactions, width=100, height=15)
        self.listbox_transactions.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=800, height=400)
        self.canvas.pack()

        self.plot_data()

        # Initialize balance on startup
        self.refresh_balance()

    def add_transaction(self):
        # Create a new window for adding transactions
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Transaction")
        self.add_window.geometry("400x300")

        # Labels and Entry fields
        tk.Label(self.add_window, text="Category:").pack()
        self.entry_category = tk.Entry(self.add_window)
        self.entry_category.pack()

        tk.Label(self.add_window, text="Amount:").pack()
        self.entry_amount = tk.Entry(self.add_window)
        self.entry_amount.pack()

        tk.Label(self.add_window, text="Type (Income/Expense):").pack()
        self.entry_type = ttk.Combobox(self.add_window, values=["Income", "Expense"])
        self.entry_type.pack()

        tk.Button(self.add_window, text="Add", command=self.save_transaction).pack()

    def save_transaction(self):
        # Validate inputs
        category = self.entry_category.get()
        amount = self.entry_amount.get()
        transaction_type = self.entry_type.get()

        if not category or not amount or not transaction_type:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        # Insert transaction into database
        conn = sqlite3.connect('finance_tracker.db')
        c = conn.cursor()

        user_id = 1  # Assuming single user for simplicity

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO transactions (date, category, amount, type, user_id) VALUES (?, ?, ?, ?, ?)",
                  (date, category, amount, transaction_type, user_id))
        conn.commit()
        conn.close()

        # Close the add window and update UI
        self.add_window.destroy()
        self.refresh_balance()
        self.view_transactions()

    def view_transactions(self):
        # Clear listbox first
        self.listbox_transactions.delete(0, tk.END)

        # Fetch and display transactions
        conn = sqlite3.connect('finance_tracker.db')
        c = conn.cursor()

        user_id = 1  # Assuming single user for simplicity

        c.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
        transactions = c.fetchall()

        conn.close()

        # Display transactions in listbox
        for transaction in transactions:
            self.listbox_transactions.insert(tk.END, f"{transaction[1]} - {transaction[3]} ({transaction[4]})")

    def generate_report(self):
        # Generate and display a simple report using matplotlib
        conn = sqlite3.connect('finance_tracker.db')
        c = conn.cursor()

        user_id = 1  # Assuming single user for simplicity

        c.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? GROUP BY type", (user_id,))
        data = c.fetchall()

        conn.close()

        if data:
            labels = [entry[0] for entry in data]
            values = [entry[1] for entry in data]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(labels, values)
            ax.set_xlabel('Transaction Type')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Expense vs. Income')

            # Embedding plot into tkinter GUI
            self.plot_widget = FigureCanvasTkAgg(fig, master=self.canvas)
            self.plot_widget.draw()
            self.plot_widget.get_tk_widget().pack()

    def plot_data(self):
        # Example plot (replace with actual data from SQLite database)
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['Expenses', 'Income', 'Savings']
        sizes = [25, 45, 30]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Embedding plot into tkinter GUI
        self.plot_widget = FigureCanvasTkAgg(fig, master=self.canvas)
        self.plot_widget.draw()
        self.plot_widget.get_tk_widget().pack()

    def refresh_balance(self):
        # Calculate and display balance
        conn = sqlite3.connect('finance_tracker.db')
        c = conn.cursor()

        user_id = 1  # Assuming single user for simplicity

        c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='Income'", (user_id,))
        income = c.fetchone()[0] or 0

        c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='Expense'", (user_id,))
        expenses = c.fetchone()[0] or 0

        conn.close()

        balance = income - expenses
        self.label_balance.config(text=f"Balance: ${balance:.2f}")


# Main function to start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
