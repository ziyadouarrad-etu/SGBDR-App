# 🗄️ SGBDR-App

A **simple yet powerful graphical database management system (DBMS)** built with **Python** and **Tkinter**, supporting **multi-user access control** and **SQLite** databases.  
Users can log in, create databases, manage tables, share access with other users, and export data — all through an intuitive graphical interface.

---

## 🚀 Features

### 🔐 User Management
- User registration and authentication system  
- Secure access per user  
- Permissions table controls which users can access which databases  
- Built-in `admin` account (default password: `test`)

### 💾 Database Management
- Create new SQLite databases on the fly  
- Manage multiple databases per user  
- Share databases with other registered users  
- Delete databases (owner only)

### 📊 Table Operations
- Create tables with custom columns and data types (`TEXT`, `INTEGER`, `REAL`, `BLOB`)  
- View and browse tables with a scrollable UI  
- Insert new records  
- Delete records or entire tables  
- Export tables to `.csv` files for external use  

### 🧩 Technical Highlights
- GUI built using **Tkinter** and **ttk**
- Persistent data using **SQLite**
- Automatic setup of `user_management.db` to store users and permissions
- Modular structure with a `DB` class handling low-level SQL operations
- Lightweight, portable — no external server required

---

## 📂 Project Structure

```
SGBDR-App/
├── APP.py                 # Main application file
├── user_management.db     # Stores users and permissions (auto-created)
├── school.db              # Example user database
└── README.md              # This file
```

---

## 🧠 How It Works

1. **Login/Register:**  
   Each user must log in or create an account.

2. **Dashboard:**  
   After login, users see databases they have access to.  
   - Create a new DB  
   - Open an existing DB  
   - Share a DB with others

3. **Database View:**  
   Inside a DB, users can:
   - View all tables  
   - Create new tables  
   - Delete tables  
   - Open a table to view/edit data

4. **Table View:**  
   Inside a table:
   - Insert new records  
   - Delete selected records  
   - Export data to CSV

---

## ⚙️ Installation

### Requirements
- Python 3.8+
- Tkinter (included with most Python installations)
- SQLite3 (built into Python)
- `ttk` and `csv` are part of the Python standard library

### Steps
```bash
# Clone the repository
git clone https://github.com/ziyadouarrad-etu/SGBDR-App.git
cd SGBDR-App

# Run the application
python APP.py
```

The app will automatically create a user database (`user_management.db`) and an admin account:
- **Username:** `admin`  
- **Password:** `test`

---

## 🛡️ Security Notes
- Passwords are currently stored in plain text (for simplicity).  
  For production use, add hashing (e.g. with `bcrypt`).  
- Permissions are stored in a local SQLite file; concurrent multi-user access is limited to local operations.

---

## 🧩 Future Improvements
- [ ] Password hashing and authentication security  
- [ ] User roles (Admin, Editor, Viewer)  
- [ ] Search and filtering in tables  
- [ ] Edit existing records  
- [ ] Import data from CSV  
- [ ] Dark/Light theme toggle  
- [ ] Migration to PyQt or custom modern UI  

---

## 👤 Author

**Ziyad Ouarrad**  
> Student project — Database Systems (SGBDR)  
> Built with ❤️ using Python + Tkinter

---

## 📄 License

This project is open-source under the **MIT License**.  
Feel free to fork, modify, and use for educational purposes.
