import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class HomeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Home UI")
        self.root.geometry("400x300")

        # Title
        title_label = tk.Label(root, text="Welcome to Our Projects", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Buttons for each project
        btn1 = tk.Button(root, text="Note Organization", font=("Arial", 12), width=20, command=self.open_project1)
        btn1.pack(pady=10)

        btn2 = tk.Button(root, text="Project 2", font=("Arial", 12), width=20, command=self.open_project2)
        btn2.pack(pady=10)

        btn3 = tk.Button(root, text="Project 3", font=("Arial", 12), width=20, command=self.open_project3)
        btn3.pack(pady=10)

    def open_project1(self):
        self.run_file("note.py")   # 改成你的文件名

    def open_project2(self):
        self.run_file("project2.py")

    def open_project3(self):
        self.run_file("project3.py")

    def run_file(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))  # home.py所在目录
        filepath = os.path.join(base_path, filename)

        if os.path.exists(filepath):
            subprocess.Popen(["python", filepath])
        else:
            messagebox.showerror("Error", f"{filename} not found!\nChecked path: {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeUI(root)
    root.mainloop()
