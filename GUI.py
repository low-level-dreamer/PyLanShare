import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from client import discover_devices, scp_transfer, send_file_p2p
from tkinterdnd2 import DND_FILES, TkinterDnD

import config
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

        self.file_label = tk.Label(right_frame, text="No file selected", width=80)
        self.file_label.pack(pady=10)

        # self.browse_btn = tk.Button(right_frame, text="Browse File", command=self.browse_file)
        # self.browse_btn.pack(pady=10)

        self.drop_frame = tk.Frame(right_frame, bg = "lightgray", width = 400, height = 250)  # Increased size
        self.drop_frame.pack(padx = 20, pady = 20)
        self.drop_frame.pack_propagate(False)  # Important: maintains the frame size

        self.drop_label = tk.Label(self.drop_frame, text = "Drop files here",
                                   bg = "lightgray", fg = "gray", font = ("Arial", 12))
        self.drop_label.pack(expand = True)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Fix button names
        self.send_btn = tk.Button(right_frame, text = "Send", command = self.send_file)
        self.send_btn.pack(pady = 20)

        self.send_p2p_btn = tk.Button(right_frame, text = "Send P2P", command = self.send_file_p2p)  # Different name
        self.send_p2p_btn.pack(pady = 20)

        self.status_label = tk.Label(right_frame, text="", fg="blue")
        self.status_label.pack(pady=10)

        self.refresh_servers()

    def handle_drop(self,event):
        files = root.tk.splitlist(event.data)
        for file_path in files:
            self.selected_file = file_path
            self.file_label.config(text=file_path)

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
    def send_file_p2p(self):
        if not self.selected_server:
            messagebox.showerror("Error", "Please select a server.")
            return
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file.")
            return
        self.status_label.config(text = "Transferring...")
        self.root.update()
        success = send_file_p2p(self.selected_server["local_ip"],config.P2P_PORT,self.selected_file)
        if success:
            self.status_label.config(text="Transfer successful!", fg="green")
        else:
            self.status_label.config(text="Transfer failed.", fg="red")
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
    root = TkinterDnD.Tk()
    app = FileTransferGUI(root)
    root.mainloop()