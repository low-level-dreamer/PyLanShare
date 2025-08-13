import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from client import discover_devices, scp_transfer

class FileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyLanShare GUI")
        self.selected_file = None
        self.selected_server = None
        self.servers = []

        # Left: Server list
        self.server_listbox = tk.Listbox(root, width=40)
        self.server_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.server_listbox.bind('<<ListboxSelect>>', self.on_server_select)

        # Right: File selection
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.file_label = tk.Label(right_frame, text="No file selected", width=40)
        self.file_label.pack(pady=10)

        self.browse_btn = tk.Button(right_frame, text="Browse File", command=self.browse_file)
        self.browse_btn.pack(pady=10)

        self.send_btn = tk.Button(right_frame, text="Send", command=self.send_file)
        self.send_btn.pack(pady=20)

        self.status_label = tk.Label(right_frame, text="", fg="blue")
        self.status_label.pack(pady=10)

        self.refresh_servers()

    def refresh_servers(self):
        self.servers = discover_devices()
        self.server_listbox.delete(0, tk.END)
        for server in self.servers:
            display = f"{server['server_name']} ({server['local_ip']}:{server['port']}) [{server['os']}]"
            self.server_listbox.insert(tk.END, display)

    def on_server_select(self, event):
        idx = self.server_listbox.curselection()
        if idx:
            self.selected_server = self.servers[idx[0]]

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=file_path)

    def send_file(self):
        if not self.selected_server:
            messagebox.showerror("Error", "Please select a server.")
            return
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file.")
            return
        username = self.selected_server.get("username") or simpledialog.askstring("Username", "Enter username:")
        password = simpledialog.askstring("Password", "Enter password:", show='*')
        self.status_label.config(text="Transferring...")
        self.root.update()
        success = scp_transfer(
            self.selected_file,
            self.selected_server['local_ip'],
            self.selected_server['port'],
            self.selected_server['download_dir'],
            username,
            password
        )
        if success:
            self.status_label.config(text="Transfer successful!", fg="green")
        else:
            self.status_label.config(text="Transfer failed.", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferGUI(root)
    root.mainloop()