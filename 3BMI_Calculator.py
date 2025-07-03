import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------ Database Setup ------------------ #
conn = sqlite3.connect('bmi_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bmi_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        weight REAL,
        height REAL,
        bmi REAL,
        category TEXT,
        date TEXT
    )
''')
conn.commit()

# ------------------ BMI Calculation ------------------ #
def calculate_bmi():
    try:
        username = entry_name.get()
        weight = float(entry_weight.get())
        height = float(entry_height.get()) / 100  # Convert cm to meters

        bmi = weight / (height ** 2)
        bmi = round(bmi, 2)
        category = get_bmi_category(bmi)

        label_result.config(text=f"BMI: {bmi} ({category})")

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO bmi_records (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, weight, height, bmi, category, date))
        conn.commit()

        messagebox.showinfo("Success", "BMI data saved successfully!")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid weight and height.")

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# ------------------ View History ------------------ #
def view_history():
    username = entry_name.get()
    if not username:
        messagebox.showerror("Error", "Enter a username to view history.")
        return

    history_win = tk.Toplevel(root)
    history_win.title("BMI History")

    tree = ttk.Treeview(history_win, columns=('Date', 'Weight', 'Height', 'BMI', 'Category'), show='headings')
    tree.heading('Date', text='Date')
    tree.heading('Weight', text='Weight (kg)')
    tree.heading('Height', text='Height (m)')
    tree.heading('BMI', text='BMI')
    tree.heading('Category', text='Category')
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute('SELECT date, weight, height, bmi, category FROM bmi_records WHERE username = ?', (username,))
    records = cursor.fetchall()

    for row in records:
        tree.insert('', tk.END, values=row)

# ------------------ Plot BMI Trend ------------------ #
def plot_trend():
    username = entry_name.get()
    if not username:
        messagebox.showerror("Error", "Enter a username to plot trend.")
        return

    cursor.execute('SELECT date, bmi FROM bmi_records WHERE username = ?', (username,))
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("Info", "No data available to plot.")
        return

    dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in data]
    bmis = [row[1] for row in data]

    trend_win = tk.Toplevel(root)
    trend_win.title("BMI Trend")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dates, bmis, marker='o', linestyle='-', color='blue')
    ax.set_title(f"{username}'s BMI Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("BMI")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=trend_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ------------------ GUI Setup ------------------ #
root = tk.Tk()
root.title("Advanced BMI Calculator")
root.geometry("400x350")

tk.Label(root, text="Username:").pack(pady=5)
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Weight (kg):").pack(pady=5)
entry_weight = tk.Entry(root)
entry_weight.pack()

tk.Label(root, text="Height (cm):").pack(pady=5)
entry_height = tk.Entry(root)
entry_height.pack()

tk.Button(root, text="Calculate BMI", command=calculate_bmi).pack(pady=10)

label_result = tk.Label(root, text="", font=("Arial", 14))
label_result.pack(pady=10)

tk.Button(root, text="View History", command=view_history).pack(pady=5)
tk.Button(root, text="Plot Trend", command=plot_trend).pack(pady=5)

root.mainloop()
