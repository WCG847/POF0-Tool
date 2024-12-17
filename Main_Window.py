import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
from LEEncoder import encode_pof0, save_pof0_file
from LEDecoder import decode_pof0

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

        # File Menu
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open File (Decode POF0)", command=self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools Menu
        self.tools_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Encode POF0", command=self.encode_pof0)
        self.tools_menu.add_command(label="Save Decoded to CSV", command=self.save_decoded_to_csv)

        # Help Menu
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # File Path Frame
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
        """Open a file dialog to select a binary file for decoding."""
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.pof0"), ("All Files", "*.*")])
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
            messagebox.showerror("Error", "No file selected for decoding.")
            return

        try:
            # Load the binary data
            with open(file_path, "rb") as file:
                file_data = file.read()

            # Decode the POF0 section
            self.decoded_indices = decode_pof0(file_data)

            # Validate decoded structure
            if not isinstance(self.decoded_indices, dict):
                raise TypeError("Decoded POF0 data is not in expected dictionary format.\nPlease verify the file contents.")

            # Display the results
            self.output_text.config(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Decoded POF0 Indices:\n{'-'*40}\n")
            for idx, value in self.decoded_indices.items():
                self.output_text.insert(tk.END, f"Offset {idx}: Count {value}\n")
            self.output_text.config(state="disabled")

            messagebox.showinfo("Success", "POF0 Decoding Completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode POF0: {str(e)}")

    def save_decoded_to_csv(self):
        """Save decoded POF0 indices to a CSV file."""
        if not hasattr(self, 'decoded_indices') or not self.decoded_indices:
            messagebox.showerror("Error", "No decoded data to save. Please decode a POF0 file first.")
            return

        output_path = filedialog.asksaveasfilename(title="Save Decoded Data to CSV", defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not output_path:
            return

        try:
            with open(output_path, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for offset, count in self.decoded_indices.items():
                    writer.writerow([offset, count])
            messagebox.showinfo("Success", f"Decoded data successfully saved to: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save decoded data: {str(e)}")

    def encode_pof0(self):
        """Prompt user to input CSV and save the encoded POF0 binary."""
        # Step 1: Select input CSV file
        csv_file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not csv_file_path:
            return

        # Step 2: Read offsets from CSV file
        try:
            offset_dict = {}
            duplicates = False
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) != 2:
                        raise ValueError("Invalid CSV format. Each row must contain offset and count.")
                    try:
                        offset = int(row[0], 0)  # Parse as integer (hex or decimal)
                        count = int(row[1])
                        if offset in offset_dict:
                            offset_dict[offset] += count
                            duplicates = True
                        else:
                            offset_dict[offset] = count
                    except ValueError:
                        raise ValueError(f"Invalid data in row: {row}. Offset and count must be integers.")
            if duplicates:
                messagebox.showwarning("Warning", "Duplicate offsets were found and aggregated during encoding.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
            return

        # Step 3: Check if offset_dict is empty
        if not offset_dict:
            messagebox.showerror("Error", "The CSV file was parsed successfully, but it contains no valid rows.\nExpected format: offset,count\nDuplicate offsets will be aggregated.")
            return

        # Step 4: Select output file path
        output_path = filedialog.asksaveasfilename(title="Save POF0 File", defaultextension=".pof0", filetypes=[("POF0 Files", "*.pof0"), ("All Files", "*.*")])
        if not output_path:
            return

        # Step 5: Encode and save POF0 file
        try:
            save_pof0_file(output_path, offset_dict)
            file_size = os.path.getsize(output_path)
            self.output_text.config(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Encoded POF0 file saved to: {output_path} ({file_size} bytes)\n")
            self.output_text.config(state="disabled")
            messagebox.showinfo("Success", f"POF0 file successfully saved to: {output_path} ({file_size} bytes)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encode and save POF0 file: {str(e)}")

    def show_about(self):
        """Show an About dialog."""
        messagebox.showinfo("About POF0 Tool", "POF0 Tool\nVersion 2.0\nDeveloped by WCG847.")

def main():
    root = tk.Tk()
    app = POF0Tool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
