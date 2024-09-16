import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import shutil
import datetime
import subprocess
import sys
import time

# Define global variables
passwords = {}
locked_folders = set()  # To keep track of locked folders
current_folder = None
root = None  # Will be initialized in setup_ui()

def create_folder():
    dialog = AnimatedDialog(root, "Create Folder", 350, 250)
    # Labels and Entry widgets
    tk.Label(dialog, text="Folder Name:", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=10)
    folder_name_entry = tk.Entry(dialog, bg="#3a3a3a", fg="#f0f0f0", font=("Segoe UI", 12))
    folder_name_entry.pack(pady=5, fill=tk.X, padx=20)

    tk.Label(dialog, text="Password:", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=10)
    folder_password_entry = tk.Entry(dialog, show='*', bg="#3a3a3a", fg="#f0f0f0", font=("Segoe UI", 12))
    folder_password_entry.pack(pady=5, fill=tk.X, padx=20)

    # Buttons Frame
    button_frame = tk.Frame(dialog, bg="#2e2e2e")
    button_frame.pack(pady=15)

    def on_submit():
        folder_name = folder_name_entry.get().strip()
        folder_password = folder_password_entry.get().strip()

        if not folder_name or not folder_name.isalnum():
            messagebox.showerror("Error", "Folder name must be alphanumeric and not empty.", parent=dialog)
            return

        if not folder_password or len(folder_password) < 8 or not any(char.isdigit() for char in folder_password) or not any(char.isalpha() for char in folder_password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, with a mix of letters and numbers.", parent=dialog)
            return

        if not os.path.exists(folder_name):
            try:
                os.makedirs(folder_name)
                passwords[folder_name] = folder_password
                update_menu()
                messagebox.showinfo("Success", f"Folder '{folder_name}' created successfully.", parent=dialog)
                dialog.destroy_with_fade()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}", parent=dialog)
        else:
            messagebox.showerror("Error", "Folder already exists.", parent=dialog)

    def on_cancel():
        dialog.destroy_with_fade()

    # Create buttons with enhanced styles
    submit_btn = create_styled_button(button_frame, "Submit", on_submit, "#4CAF50", "#45a049")
    submit_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = create_styled_button(button_frame, "Cancel", on_cancel, "#F44336", "#E53935")
    cancel_btn.pack(side=tk.LEFT, padx=10)

def lock_folder():
    global current_folder
    if not current_folder:
        messagebox.showerror("Error", "No folder selected.", parent=root)
        return

    if current_folder in locked_folders:
        messagebox.showinfo("Info", "Folder is already locked.", parent=root)
        return

    dialog = AnimatedDialog(root, "Lock Folder", 350, 200)

    tk.Label(dialog, text=f"Locking Folder: '{current_folder}'", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=10)
    tk.Label(dialog, text="Enter Password:", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=5)
    password_entry = tk.Entry(dialog, show='*', bg="#3a3a3a", fg="#f0f0f0", font=("Segoe UI", 12))
    password_entry.pack(pady=5, fill=tk.X, padx=20)

    # Buttons Frame
    button_frame = tk.Frame(dialog, bg="#2e2e2e")
    button_frame.pack(pady=15)

    def on_submit():
        password = password_entry.get().strip()

        if not password or len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, with a mix of letters and numbers.", parent=dialog)
            return

        if password != passwords.get(current_folder):
            messagebox.showerror("Error", "Incorrect password.", parent=dialog)
            return

        try:
            with open(f"{current_folder}.lock", 'w') as lock_file:
                lock_file.write(password)
            locked_folders.add(current_folder)
            update_menu()
            messagebox.showinfo("Success", f"Folder '{current_folder}' is now locked.", parent=dialog)
            dialog.destroy_with_fade()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to lock folder: {e}", parent=dialog)

    def on_cancel():
        dialog.destroy_with_fade()

    # Create buttons with enhanced styles
    lock_btn = create_styled_button(button_frame, "Lock Folder", on_submit, "#FFC107", "#FFB300")
    lock_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = create_styled_button(button_frame, "Cancel", on_cancel, "#F44336", "#E53935")
    cancel_btn.pack(side=tk.LEFT, padx=10)

def unlock_folder():
    global current_folder
    if not current_folder:
        messagebox.showerror("Error", "No folder selected.", parent=root)
        return

    if current_folder not in locked_folders:
        messagebox.showinfo("Info", "Folder is not locked.", parent=root)
        return

    dialog = AnimatedDialog(root, "Unlock Folder", 350, 200)

    tk.Label(dialog, text=f"Unlocking Folder: '{current_folder}'", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=10)
    tk.Label(dialog, text="Enter Password:", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=5)
    password_entry = tk.Entry(dialog, show='*', bg="#3a3a3a", fg="#f0f0f0", font=("Segoe UI", 12))
    password_entry.pack(pady=5, fill=tk.X, padx=20)

    # Buttons Frame
    button_frame = tk.Frame(dialog, bg="#2e2e2e")
    button_frame.pack(pady=15)

    def on_submit():
        password = password_entry.get().strip()
        try:
            with open(f"{current_folder}.lock", 'r') as lock_file:
                stored_password = lock_file.read().strip()
        except FileNotFoundError:
            messagebox.showerror("Error", "Lock file not found.", parent=dialog)
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read lock file: {e}", parent=dialog)
            return

        if password != stored_password:
            messagebox.showerror("Error", "Incorrect password.", parent=dialog)
            return

        try:
            os.remove(f"{current_folder}.lock")
            locked_folders.discard(current_folder)
            update_menu()
            messagebox.showinfo("Success", f"Folder '{current_folder}' is now unlocked.", parent=dialog)
            dialog.destroy_with_fade()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unlock folder: {e}", parent=dialog)

    def on_cancel():
        dialog.destroy_with_fade()

    # Create buttons with enhanced styles
    unlock_btn = create_styled_button(button_frame, "Unlock Folder", on_submit, "#2196F3", "#1976D2")
    unlock_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = create_styled_button(button_frame, "Cancel", on_cancel, "#F44336", "#E53935")
    cancel_btn.pack(side=tk.LEFT, padx=10)

def delete_folder():
    global current_folder
    if not current_folder:
        messagebox.showerror("Error", "No folder selected.", parent=root)
        return

    if current_folder in locked_folders:
        messagebox.showerror("Error", "Unlock the folder before deleting.", parent=root)
        return

    dialog = AnimatedDialog(root, "Delete Folder", 350, 200)

    # Password Label and Entry
    tk.Label(dialog, text="Enter Password to Delete:", bg="#2e2e2e", fg="#f0f0f0", font=("Segoe UI", 12)).pack(pady=10)
    password_entry = tk.Entry(dialog, show='*', bg="#3a3a3a", fg="#f0f0f0", font=("Segoe UI", 12))
    password_entry.pack(pady=5, fill=tk.X, padx=20)

    # Buttons Frame
    button_frame = tk.Frame(dialog, bg="#2e2e2e")
    button_frame.pack(pady=15)

    def on_submit():
        password = password_entry.get().strip()

        if password != passwords.get(current_folder):
            messagebox.showerror("Error", "Incorrect password.", parent=dialog)
            return

        try:
            shutil.rmtree(current_folder)
            passwords.pop(current_folder, None)
            update_menu()
            messagebox.showinfo("Success", f"Folder '{current_folder}' deleted successfully.", parent=dialog)
            dialog.destroy_with_fade()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete folder: {e}", parent=dialog)

    def on_cancel():
        dialog.destroy_with_fade()

    # Create buttons with enhanced styles
    delete_btn = create_styled_button(button_frame, "Delete", on_submit, "#F44336", "#E53935")
    delete_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = create_styled_button(button_frame, "Cancel", on_cancel, "#9E9E9E", "#757575")
    cancel_btn.pack(side=tk.LEFT, padx=10)

def open_folder():
    global current_folder
    if not current_folder:
        messagebox.showerror("Error", "No folder selected.", parent=root)
        return

    try:
        if sys.platform == "win32":
            os.startfile(current_folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", current_folder])
        else:
            subprocess.Popen(["xdg-open", current_folder])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open folder: {e}", parent=root)

def update_menu():
    menu_listbox.delete(0, tk.END)
    for folder in os.listdir():
        if os.path.isdir(folder):
            status = "(Locked)" if folder in locked_folders else "(Unlocked)"
            menu_listbox.insert(tk.END, f"{folder} {status}")

def get_creation_date(folder):
    timestamp = os.path.getctime(folder)
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def get_folder_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def setup_ui():
    global root, menu_listbox, info_label

    root = tk.Tk()
    root.title("Secure Folder Manager")
    root.geometry("900x600")
    root.resizable(True, True)
    root.configure(bg="#121212")  # Darker background for modern look

    # Set transparency
    root.attributes("-alpha", 0.98)  # 98% opaque

    # Menu Frame
    menu_frame = tk.Frame(root, bg="#1e1e1e", padx=15, pady=15, relief=tk.RAISED, borderwidth=2)
    menu_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

    # Folder List Frame
    list_frame = tk.Frame(menu_frame, bg="#1e1e1e")
    list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    menu_label = tk.Label(list_frame, text="Folders", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="#ffffff")
    menu_label.pack(pady=(0, 10))

    menu_listbox = tk.Listbox(list_frame, bg="#2e2e2e", fg="#ffffff", font=("Segoe UI", 12), selectbackground="#3a3a3a", selectmode=tk.SINGLE, height=15, bd=0, highlightthickness=0)
    menu_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    menu_listbox.bind('<<ListboxSelect>>', on_folder_select)

    menu_scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
    menu_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    menu_listbox.config(yscrollcommand=menu_scroll.set)
    menu_scroll.config(command=menu_listbox.yview)

    # Info Panel Frame
    info_frame = tk.Frame(menu_frame, bg="#1e1e1e", padx=15, pady=15, relief=tk.SUNKEN, borderwidth=2)
    info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=15)

    info_label = tk.Label(info_frame, text="Folder Info", font=("Segoe UI", 16, "bold"), bg="#1e1e1e", fg="#ffffff")
    info_label.pack(pady=(0, 10))

    global folder_info_label
    folder_info_label = tk.Label(info_frame, text="", font=("Segoe UI", 12), bg="#1e1e1e", fg="#ffffff", justify=tk.LEFT, anchor="w")
    folder_info_label.pack(fill=tk.BOTH, expand=True, padx=5)

    # Buttons Frame
    button_frame = tk.Frame(root, bg="#121212", pady=15)
    button_frame.pack(pady=10, fill=tk.X, padx=50)

    create_btn = create_styled_button(button_frame, "Create Folder", create_folder, "#4CAF50", "#45a049")
    create_btn.pack(pady=5, fill=tk.X)

    lock_btn = create_styled_button(button_frame, "Lock Folder", lock_folder, "#FFC107", "#FFB300")
    lock_btn.pack(pady=5, fill=tk.X)

    unlock_btn = create_styled_button(button_frame, "Unlock Folder", unlock_folder, "#2196F3", "#1976D2")
    unlock_btn.pack(pady=5, fill=tk.X)

    delete_btn = create_styled_button(button_frame, "Delete Folder", delete_folder, "#F44336", "#E53935")
    delete_btn.pack(pady=5, fill=tk.X)

    open_btn = create_styled_button(button_frame, "Open Folder", open_folder, "#800080", "#C71585")  
    open_btn.pack(pady=5, fill=tk.X)

    exit_btn = create_styled_button(button_frame, "Exit", root.quit, "#FFA500", "#FF8C00")  
    exit_btn.pack(pady=5, fill=tk.X)

    # Initialize menu
    update_menu()

    root.mainloop()

def create_styled_button(parent, text, command, color, hover_color):
    """
    Creates a button with enhanced styles including gradient effect and hover animation.
    """
    btn = tk.Button(parent, text=text, font=("Segoe UI", 12, "bold"), bg=color, fg="white", bd=0, relief=tk.FLAT, command=command, padx=20, pady=10, activebackground=hover_color)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_color))
    btn.bind("<Leave>", lambda e: btn.configure(bg=color))
    btn.configure(cursor="hand2")  # Change cursor on hover
    return btn

class AnimatedDialog(tk.Toplevel):
    """
    A custom Toplevel window with fade-in and fade-out animations.
    """
    def __init__(self, parent, title, width, height):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg="#2e2e2e")
        self.transient(parent)  # Keep dialog on top
        self.grab_set()  # Make the dialog modal
        self.attributes("-alpha", 0.0)  # Start fully transparent
        self.fade_in()

        # Center the dialog relative to parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 0.98:
            alpha += 0.02
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_in)
        else:
            self.attributes("-alpha", 1.0)

    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.02
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_out)
        else:
            self.destroy()

    def destroy_with_fade(self):
        self.fade_out()

def on_folder_select(event):
    global current_folder
    selection = menu_listbox.curselection()
    if selection:
        selected = menu_listbox.get(selection[0])
        current_folder = selected.split(" ")[0]  # Extract folder name from the listbox entry

        # Get folder details
        folder_creation_date = get_creation_date(current_folder)
        folder_size = get_folder_size(current_folder)

        # Update info panel
        folder_info = (
            f"Folder Name: {current_folder}\n"
            f"Creation Date: {folder_creation_date}\n"
            f"Size: {folder_size} bytes\n"
        )
        folder_info_label.config(text=folder_info)

if __name__ == "__main__":
    setup_ui()
