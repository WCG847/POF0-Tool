import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from POF0Parser import decode_pof0 
# from Encoder import encode_pof0 

class POF0Tool:
    def __init__(self, root):
        self.root = root
        self.root.title("POF0 Tool")
        self.root.geometry("800x600")
        
        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.tools_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        # self.tools_menu.add_command(label="Encode Little Endian", command=self.encode_little_endian)

        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # File Path Entry
        self.file_frame = tk.Frame(self.root)
        self.file_frame.pack(pady=10, fill=tk.X)

        tk.Label(self.file_frame, text="File:").pack(side=tk.LEFT, padx=5)
        self.file_entry = tk.Entry(self.file_frame, state="readonly", width=80)
        self.file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.browse_button = tk.Button(self.file_frame, text="Browse", command=self.open_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Decode Button
        self.decode_button = tk.Button(self.root, text="Decode POF0", state="disabled", command=self.decode_pof0)
        self.decode_button.pack(pady=10)

        # Output Text Area
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled", height=25)
        self.output_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def open_file(self):
        """Open a file dialog to select a binary file."""
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.*"), ("All Files", "*.*")])
        if file_path:
            self.file_entry.config(state="normal")
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(state="readonly")
            self.decode_button.config(state="normal")

    def decode_pof0(self):
        """Decode the POF0 section from the selected file."""
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "No file selected.")
            return

        try:
            # Load the binary data
            with open(file_path, "rb") as file:
                file_data = file.read()

            # Decode the POF0 section
            decoded_indices = decode_pof0(file_data)

            # Display the results
            self.output_text.config(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Decoded POF0 Indices:\n{'-'*40}\n")
            for idx, value in enumerate(decoded_indices):
                self.output_text.insert(tk.END, f"Index {idx}: {value}\n")
            self.output_text.config(state="disabled")

            messagebox.showinfo("Success", "POF0 Decoding Completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode POF0: {str(e)}")

    # def encode_little_endian(self):
    #     """Encode indices into a Little Endian POF0 structure."""
    #     input_file = filedialog.askopenfilename(title="Select Input File", filetypes=[("Binary Files", "*.*"), ("All Files", "*.*")])
    #     if not input_file:
    #         return  # User canceled file selection

    #     output_file = filedialog.asksaveasfilename(title="Select Output POF0 File", defaultextension=".bin", filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
    #     if not output_file:
    #         return  # User canceled save file selection

    #     try:
    #         # Read the input file
    #         with open(input_file, "rb") as file:
    #             file_data = file.read()

    #         # Encode the file into a POF0 structure
    #         encoded_data = encode_pof0(file_data)

    #         # Write the encoded data to the output file
    #         with open(output_file, "wb") as file:
    #             file.write(encoded_data)

    #         messagebox.showinfo("Success", "File successfully encoded to POF0 structure!")

    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to encode file: {str(e)}")

    def show_about(self):
        """Show an About dialog."""
        messagebox.showinfo("About POF0 Tool", "POF0 Tool\nVersion 1.0\nDeveloped by WCG847.")

def main():
    root = tk.Tk()
    app = POF0Tool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
