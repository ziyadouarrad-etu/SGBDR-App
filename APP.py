import sqlite3 as sql
import csv
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import os

USER_DB = "user_management.db"

# Simplified styling
BG_DARK = '#2c3e50'
BG_LIGHT = '#ecf0f1'
BTN_PRIMARY = '#3498db'
BTN_SUCCESS = '#27ae60'
BTN_DANGER = '#e74c3c'


def init_user_db():
    """Initialize user database"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     username TEXT PRIMARY KEY,
                     password TEXT NOT NULL
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS permissions
                 (
                     id         INTEGER PRIMARY KEY AUTOINCREMENT,
                     db_name    TEXT,
                     username   TEXT,
                     created_by TEXT,
                     UNIQUE (db_name, username)
                 )''')
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ("admin", "test"))
    conn.commit()
    conn.close()


def login(username, password):
    """Check login credentials"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == password


def create_user(username, password):
    """Create new user"""
    try:
        conn = sql.connect(USER_DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sql.IntegrityError:
        return False


def get_user_dbs(username):
    """Get databases user can access"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT db_name, created_by FROM permissions WHERE username = ?", (username,))
    dbs = [{"name": row[0], "creator": row[1]} for row in c.fetchall()]
    conn.close()
    return dbs


def add_permission(db_name, username, created_by):
    """Grant database access to user"""
    try:
        conn = sql.connect(USER_DB)
        c = conn.cursor()
        c.execute("INSERT INTO permissions (db_name, username, created_by) VALUES (?, ?, ?)",
                  (db_name, username, created_by))
        conn.commit()
        conn.close()
        return True
    except sql.IntegrityError:
        return False


def get_all_users():
    """Get all usernames"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


def get_db_users(db_name):
    """Get users with access to database"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT username FROM permissions WHERE db_name = ?", (db_name,))
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


def revoke_permission(db_name, username):
    """Remove user access"""
    conn = sql.connect(USER_DB)
    c = conn.cursor()
    c.execute("DELETE FROM permissions WHERE db_name = ? AND username = ?", (db_name, username))
    conn.commit()
    conn.close()


class DB:
    """Database wrapper"""

    def __init__(self, name):
        self.conn = sql.connect(name + '.db')
        self.c = self.conn.cursor()

    def create_table(self, table, cols):
        col_str = ', '.join([f"{col} {dtype}" for col, dtype in cols.items()])
        self.c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_str})")
        self.conn.commit()

    def insert(self, table, data):
        cols = ', '.join([f'"{col}"' for col in data.keys()])
        vals = ', '.join(['?' for _ in data])
        self.c.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", tuple(data.values()))
        self.conn.commit()

    def fetch_all(self, table):
        self.c.execute(f"SELECT * FROM {table}")
        return self.c.fetchall()

    def get_columns(self, table):
        self.c.execute(f"PRAGMA table_info({table})")
        return [col[1] for col in self.c.fetchall()]

    def get_tables(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.c.fetchall()]

    def drop_table(self, table):
        self.c.execute(f"DROP TABLE IF EXISTS {table}")
        self.conn.commit()

    def export_csv(self, table):
        self.c.execute(f"SELECT * FROM {table}")
        rows = self.c.fetchall()
        cols = [desc[0] for desc in self.c.description]
        with open(f"{table}.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(rows)

    def close(self):
        self.conn.close()


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DB Manager")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_LIGHT)
        self.user = None
        self.current_db = None

    def run(self):
        self.root.mainloop()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def btn(self, parent, text, cmd, color=BTN_PRIMARY):
        """Create styled button"""
        return tk.Button(parent, text=text, command=cmd, bg=color, fg='white',
                         font=('Arial', 10), relief='flat', padx=12, pady=6)

    def header(self, text):
        """Create header"""
        h = tk.Frame(self.root, bg=BG_DARK, height=60)
        h.pack(fill=tk.X)
        tk.Label(h, text=text, font=('Arial', 16, 'bold'), fg='white', bg=BG_DARK).pack(pady=15)
        return h

    def login_screen(self):
        self.clear()
        self.header("Database Management System")

        frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(frame, text="Login", font=('Arial', 14, 'bold'), bg='white').grid(row=0, column=0, columnspan=2,
                                                                                   pady=10)

        tk.Label(frame, text="Username:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        user_entry = tk.Entry(frame, width=25)
        user_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Password:", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        pass_entry = tk.Entry(frame, show='*', width=25)
        pass_entry.grid(row=2, column=1, pady=5)

        error_label = tk.Label(frame, text="", font=('Arial', 9), bg='white', fg='red')
        error_label.grid(row=4, column=0, columnspan=2, pady=5)

        def try_login():
            if login(user_entry.get(), pass_entry.get()):
                self.user = user_entry.get()
                self.db_screen()
            else:
                error_label.config(text="Invalid credentials")

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        self.btn(btn_frame, "Login", try_login, BTN_SUCCESS).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Register", self.register_screen).pack(side=tk.LEFT, padx=5)

        self.root.bind('<Return>', lambda e: try_login())
        user_entry.focus()

    def register_screen(self):
        self.clear()
        self.header("Register")

        frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(frame, text="Create Account", font=('Arial', 14, 'bold'), bg='white').grid(row=0, column=0,
                                                                                            columnspan=2, pady=10)

        tk.Label(frame, text="Username:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        user_entry = tk.Entry(frame, width=25)
        user_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Password:", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        pass_entry = tk.Entry(frame, show='*', width=25)
        pass_entry.grid(row=2, column=1, pady=5)

        error_label = tk.Label(frame, text="", font=('Arial', 9), bg='white', fg='red')
        error_label.grid(row=4, column=0, columnspan=2, pady=5)

        success_label = tk.Label(frame, text="", font=('Arial', 9), bg='white', fg='green')
        success_label.grid(row=5, column=0, columnspan=2, pady=5)

        def try_register():
            if not user_entry.get() or not pass_entry.get():
                error_label.config(text="Fill all fields")
                success_label.config(text="")
                return
            if create_user(user_entry.get(), pass_entry.get()):
                success_label.config(text="Account created! Redirecting to login...")
                error_label.config(text="")
                self.root.after(1500, self.login_screen)
            else:
                error_label.config(text="Username already exists")
                success_label.config(text="")

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        self.btn(btn_frame, "Register", try_register, BTN_SUCCESS).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Back", self.login_screen).pack(side=tk.LEFT, padx=5)

    def db_screen(self):
        self.clear()
        self.header(f"Welcome, {self.user}")

        canvas = tk.Canvas(self.root, bg=BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_LIGHT)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        dbs = get_user_dbs(self.user)
        for db in dbs:
            db_frame = tk.Frame(scroll_frame, bg='white', relief='raised', bd=1, padx=15, pady=10)
            db_frame.pack(fill=tk.X, padx=20, pady=5)

            info = tk.Frame(db_frame, bg='white')
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=db['name'], font=('Arial', 12, 'bold'), bg='white').pack(anchor='w')
            tk.Label(info, text=f"Created by: {db['creator']}",
                     font=('Arial', 9), bg='white', fg='gray').pack(anchor='w')

            btns = tk.Frame(db_frame, bg='white')
            btns.pack(side=tk.RIGHT)
            self.btn(btns, "Open", lambda d=db['name']: self.open_db(d)).pack(side=tk.LEFT, padx=2)
            self.btn(btns, "Share", lambda d=db['name']: self.access_screen(d)).pack(side=tk.LEFT, padx=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.root, bg=BG_LIGHT)
        btn_frame.pack(pady=10)
        self.btn(btn_frame, "New Database", self.create_db).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Logout", self.login_screen, BTN_DANGER).pack(side=tk.LEFT, padx=5)

    def create_db(self):
        name = simpledialog.askstring("New DB", "Database name:")
        if name:
            db = DB(name)
            db.close()
            add_permission(name, self.user, self.user)
            self.db_screen()

    def access_screen(self, db_name):
        self.clear()
        self.header(f"Share: {db_name}")

        canvas = tk.Canvas(self.root, bg=BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_LIGHT)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        all_users = get_all_users()
        current_users = get_db_users(db_name)

        for user in all_users:
            if user != self.user:
                frame = tk.Frame(scroll_frame, bg='white', relief='raised', bd=1, padx=15, pady=10)
                frame.pack(fill=tk.X, padx=20, pady=5)

                info = tk.Frame(frame, bg='white')
                info.pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(info, text=user, font=('Arial', 11, 'bold'), bg='white').pack(anchor='w')

                has_access = user in current_users
                status = "Has Access" if has_access else "No Access"
                color = BTN_SUCCESS if has_access else 'gray'
                tk.Label(info, text=status, font=('Arial', 9), bg='white', fg=color).pack(anchor='w')

                btns = tk.Frame(frame, bg='white')
                btns.pack(side=tk.RIGHT)

                if has_access:
                    self.btn(btns, "Revoke", lambda u=user: self.revoke(db_name, u),
                             BTN_DANGER).pack(side=tk.LEFT, padx=2)
                else:
                    self.btn(btns, "Grant Access", lambda u=user: self.grant(db_name, u),
                             BTN_SUCCESS).pack(side=tk.LEFT, padx=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.btn(self.root, "Back", self.db_screen).pack(pady=10)

    def grant(self, db_name, username):
        add_permission(db_name, username, self.user)
        self.access_screen(db_name)

    def revoke(self, db_name, username):
        revoke_permission(db_name, username)
        self.access_screen(db_name)

    def open_db(self, name):
        self.current_db = name
        self.table_list_screen()

    def table_list_screen(self):
        self.clear()
        self.header(f"DB: {self.current_db}")

        frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        db = DB(self.current_db)
        tables = db.get_tables()
        db.close()

        tk.Label(frame, text="Tables", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=10)

        for table in tables:
            t_frame = tk.Frame(frame, bg=BG_LIGHT, padx=10, pady=8)
            t_frame.pack(fill=tk.X, pady=3)
            tk.Label(t_frame, text=table, font=('Arial', 10), bg=BG_LIGHT).pack(side=tk.LEFT)
            self.btn(t_frame, "Open", lambda t=table: self.table_screen(t), BTN_SUCCESS).pack(side=tk.RIGHT)

        btn_frame = tk.Frame(self.root, bg=BG_LIGHT)
        btn_frame.pack(pady=10)
        self.btn(btn_frame, "New Table", self.create_table).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Share DB", lambda: self.access_screen(self.current_db)).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Delete DB", self.delete_db, BTN_DANGER).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Back", self.db_screen).pack(side=tk.LEFT, padx=5)

    def create_table(self):
        name = simpledialog.askstring("New Table", "Table name:")
        if name:
            self.table_create_screen(name)

    def table_create_screen(self, table_name):
        self.clear()
        self.header(f"Create: {table_name}")

        frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cols_frame = tk.Frame(frame, bg='white')
        cols_frame.pack(fill=tk.X, pady=10)

        col_entries = []

        def add_col():
            row = tk.Frame(cols_frame, bg=BG_LIGHT, padx=10, pady=5)
            row.pack(fill=tk.X, pady=2)
            name_ent = tk.Entry(row, width=20)
            name_ent.pack(side=tk.LEFT, padx=5)
            type_var = tk.StringVar(value="TEXT")
            ttk.Combobox(row, textvariable=type_var, values=["TEXT", "INTEGER", "REAL", "BLOB"],
                         state="readonly", width=10).pack(side=tk.LEFT, padx=5)
            col_entries.append((name_ent, type_var))

        error_label = tk.Label(frame, text="", font=('Arial', 9), bg='white', fg='red')
        error_label.pack(pady=5)

        def create():
            cols = {e[0].get(): e[1].get() for e in col_entries if e[0].get()}
            if cols:
                try:
                    db = DB(self.current_db)
                    db.create_table(table_name, cols)
                    db.close()
                    self.table_list_screen()
                except Exception as e:
                    error_label.config(text=f"Error: {str(e)}")
            else:
                error_label.config(text="Add at least one column")

        add_col()

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=10)
        self.btn(btn_frame, "Add Column", add_col).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Create", create, BTN_SUCCESS).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Back", self.table_list_screen).pack(side=tk.LEFT, padx=5)

    def delete_db(self):
        try:
            os.remove(f"{self.current_db}.db")
            conn = sql.connect(USER_DB)
            c = conn.cursor()
            c.execute("DELETE FROM permissions WHERE db_name = ?", (self.current_db,))
            conn.commit()
            conn.close()
            self.db_screen()
        except Exception as e:
            pass

    def table_screen(self, table):
        self.clear()
        self.header(f"Table: {table}")

        frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        db = DB(self.current_db)
        data = db.fetch_all(table)
        cols = db.get_columns(table)
        db.close()

        tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        for row in data:
            tree.insert('', tk.END, values=row)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self.root, bg=BG_LIGHT)
        btn_frame.pack(pady=10)
        self.btn(btn_frame, "Add Record", lambda: self.add_record(table, cols)).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Delete Table", lambda: self.delete_table(table)).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Export CSV", lambda: self.export(table)).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Delete Record", lambda: self.delete_record(tree, table, cols)).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Back", self.table_list_screen).pack(side=tk.LEFT, padx=5)

    def add_record(self, table, cols):
        win = tk.Toplevel(self.root)
        win.title("Add Record")
        win.geometry("400x500")
        win.configure(bg=BG_LIGHT)

        frame = tk.Frame(win, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        entries = {}
        for col in cols:
            tk.Label(frame, text=col, bg='white').pack(anchor='w', pady=2)
            ent = tk.Entry(frame, width=30)
            ent.pack(fill=tk.X, pady=5)
            entries[col] = ent

        error_label = tk.Label(frame, text="", font=('Arial', 9), bg='white', fg='red')
        error_label.pack(pady=5)

        def save():
            data = {col: ent.get() for col, ent in entries.items()}
            try:
                db = DB(self.current_db)
                db.insert(table, data)
                db.close()
                win.destroy()
                self.table_screen(table)
            except Exception as e:
                error_label.config(text=f"Error: {str(e)}")

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=15)
        self.btn(btn_frame, "Save", save).pack(side=tk.LEFT, padx=5)
        self.btn(btn_frame, "Cancel", win.destroy).pack(side=tk.LEFT, padx=5)

    def delete_table(self, table):
        try:
            db = DB(self.current_db)
            db.drop_table(table)
            db.close()
            self.table_list_screen()
        except Exception as e:
            pass

    def export(self, table):
        try:
            db = DB(self.current_db)
            db.export_csv(table)
            db.close()
        except Exception as e:
            pass

    def delete_record(self, tree, table, cols):
        selected = tree.selection()
        if not selected:
            return
        try:
            db = DB(self.current_db)
            for item in selected:
                values = tree.item(item, 'values')
                conditions = {cols[i]: values[i] for i in range(len(cols))}
                where_clause = ' AND '.join([f"{col}=?" for col in conditions.keys()])
                db.c.execute(f"DELETE FROM {table} WHERE {where_clause}", tuple(conditions.values()))
            db.conn.commit()
            db.close()
            self.table_screen(table)
        except Exception as e:
            pass


# Run app
init_user_db()
app = App()
app.login_screen()
app.run()