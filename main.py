
import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import csv
import os

APP_NAME = "Offline Data Search Tool"
AUTHOR = "Gurkirat Singh"

USERNAME = "admin"
PASSWORD = "admin123"

sources = []

def normalize(v):
    return str(v).strip().lower() if v else ""

def search_db(db, query):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("""
            SELECT firstname, lastname, name, nick, phone, email
            FROM telegram
            WHERE phone = ? OR email = ?
            LIMIT 1
        """, (query, query))
        row = cur.fetchone()
        conn.close()
        return row
    except:
        return None

def search_csv(csvfile, query):
    try:
        with open(csvfile, newline='', encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                phone = normalize(r.get("phone"))
                email = normalize(r.get("email"))
                if phone == query or email == query:
                    return (
                        r.get("firstname") or "",
                        r.get("lastname") or "",
                        r.get("name") or "",
                        "",
                        r.get("phone"),
                        r.get("email")
                    )
    except:
        pass
    return None

def main_app():
    def load_files():
        paths = filedialog.askopenfilenames(
            title="Load Data Files",
            filetypes=[
                ("Supported Files", "*.db *.csv"),
                ("SQLite DB", "*.db"),
                ("CSV Files", "*.csv")
            ]
        )
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if p not in [s["path"] for s in sources]:
                sources.append({"path": p, "type": ext})
        status.config(text=f"{len(sources)} data source(s) loaded", fg="#00ff00")

    def execute_search():
        query = normalize(entry.get())
        output.delete("1.0", tk.END)

        if not query:
            return

        if not sources:
            messagebox.showerror("Error", "No data source loaded")
            return

        found = False

        for src in sources:
            row = search_db(src["path"], query) if src["type"] == ".db" else search_csv(src["path"], query)
            if row:
                found = True
                output.insert(tk.END,
                    f"\n================ MATCH FOUND ================\n"
                    f"SOURCE    : {os.path.basename(src['path'])}\n"
                    f"FIRSTNAME : {row[0]}\n"
                    f"LASTNAME  : {row[1]}\n"
                    f"FULL NAME : {row[2]}\n"
                    f"NICKNAME  : {row[3]}\n"
                    f"PHONE     : {row[4]}\n"
                    f"EMAIL     : {row[5]}\n"
                )

        if not found:
            output.insert(tk.END, "\n[!] NO RECORD FOUND\n")

    root = tk.Tk()
    root.title(APP_NAME)
    root.attributes("-fullscreen", True)
    root.configure(bg="#050505")

    tk.Label(root, text=APP_NAME, fg="#00ffcc", bg="#050505",
             font=("Consolas", 22, "bold")).pack(pady=15)

    tk.Button(root, text="LOAD FILES", bg="#111", fg="#00ffcc",
              command=load_files).pack()

    status = tk.Label(root, text="No data loaded", fg="red", bg="#050505")
    status.pack(pady=5)

    entry = tk.Entry(root, width=60, bg="#111", fg="#00ffcc",
                     insertbackground="#00ffcc", font=("Consolas", 14))
    entry.pack(pady=10)

    tk.Button(root, text="SEARCH", bg="#00ffcc", fg="black",
              command=execute_search).pack(pady=10)

    output = tk.Text(root, bg="#000", fg="#00ff00", font=("Consolas", 11))
    output.pack(expand=True, fill="both", padx=20, pady=15)

    root.mainloop()

def login():
    if user_entry.get() == USERNAME and pass_entry.get() == PASSWORD:
        login_win.destroy()
        main_app()
    else:
        messagebox.showerror("Access Denied", "Invalid credentials")

login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("400x300")
login_win.configure(bg="#0a0a0a")

tk.Label(login_win, text="Offline Data Search Tool",
         fg="#00ffcc", bg="#0a0a0a",
         font=("Consolas", 16, "bold")).pack(pady=20)

tk.Label(login_win, text="Username", fg="white", bg="#0a0a0a").pack()
user_entry = tk.Entry(login_win, bg="#111", fg="#00ffcc")
user_entry.pack()

tk.Label(login_win, text="Password", fg="white", bg="#0a0a0a").pack()
pass_entry = tk.Entry(login_win, show="*", bg="#111", fg="#00ffcc")
pass_entry.pack()

tk.Button(login_win, text="LOGIN", bg="#00ffcc", fg="black",
          command=login).pack(pady=20)

login_win.mainloop()
