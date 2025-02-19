import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from cryptography.fernet import Fernet
import base64
import os
import random
import string

# Generate or load encryption key
KEY_FILE = "key.key"

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as file:
            file.write(key)
        return key

key = load_key()
cipher_suite = Fernet(key)

# Database setup
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password TEXT
)
""")
conn.commit()

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def save_password():
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    
    if not website or not username or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    encrypted_password = encrypt_password(password)
    cursor.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                   (website, username, encrypted_password))
    conn.commit()
    
    messagebox.showinfo("Success", "Password saved successfully!")
    website_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

def retrieve_password():
    website = simpledialog.askstring("Retrieve Password", "Enter website:")
    cursor.execute("SELECT username, password FROM passwords WHERE website = ?", (website,))
    result = cursor.fetchone()
    
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password)
        messagebox.showinfo("Password Retrieved", f"Username: {username}\nPassword: {decrypted_password}")
    else:
        messagebox.showerror("Error", "No password found for this website!")

def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    generated_password = "".join(random.choice(characters) for _ in range(12))
    password_entry.delete(0, tk.END)
    password_entry.insert(0, generated_password)

def exit_app():
    conn.close()
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Password Manager")
root.geometry("400x300")

tk.Label(root, text="Website:").pack()
website_entry = tk.Entry(root)
website_entry.pack()

tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Generate Password", command=generate_password).pack()
tk.Button(root, text="Save Password", command=save_password).pack()
tk.Button(root, text="Retrieve Password", command=retrieve_password).pack()
tk.Button(root, text="Exit", command=exit_app).pack()

root.mainloop()
