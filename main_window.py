import tkinter as tk
from tkinter import filedialog, ttk
from Import.chunk import ReadChunkData

class POF0Viewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POF0 Chunk Viewer")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        # TOC list
        self.toc_list = tk.Listbox(frame, width=20)
        self.toc_list.pack(side=tk.LEFT, fill=tk.Y)
        toc_scroll = tk.Scrollbar(frame, orient="vertical", command=self.toc_list.yview)
        toc_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.toc_list.config(yscrollcommand=toc_scroll.set)

        # Hex viewer
        self.text = tk.Text(frame, wrap=tk.NONE)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yscroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.text.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=yscroll.set)

        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.configure(xscrollcommand=xscroll.set)

        menu = tk.Menu(self)
        self.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.load_file)

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        with open(path, "rb") as f:
            entries, memory = ReadChunkData(f)

        self.toc_list.delete(0, tk.END)
        self.text.delete("1.0", tk.END)

        mem_bytes = memory.getvalue()
        hex_lines = []
        addr_to_tag = {}

        for i in range(0, len(mem_bytes), 16):
            chunk = mem_bytes[i:i+16]
            hex_repr = " ".join(f"{b:02X}" for b in chunk)
            line = f"{i:08X}  {hex_repr}\n"
            tag_name = f"addr_{i}"
            addr_to_tag[i] = tag_name
            self.text.insert(tk.END, line)
            self.text.tag_add(tag_name, f"{i//16 + 1}.0", f"{i//16 + 1}.end")

        for addr in entries:
            line = addr // 16 + 1
            self.text.tag_configure(f"addr_{(addr//16)*16}", background="yellow")
            self.toc_list.insert(tk.END, f"0x{addr:08X}")

app = POF0Viewer()
app.mainloop()
