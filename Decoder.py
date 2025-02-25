import struct
import sys
import os

# Try to import tkinter for GUI-based file selection
try:
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
except ImportError:
    Tk = None  # Disable file dialog if tkinter is unavailable

MAGIC = b"POF0"
YOBJ = b"YOBJ"
YANM = b"YANM"
SUPPORTED_EXTENSIONS = {".YOBJ", ".YANM", ".POF0"}


class YCHUNK:
    def __init__(self, filename):
        """Initialize and validate the file."""
        self.filename = filename
        self.RVA = None
        self.PTRs = []  # Store PTR values

        # Ensure the file has a valid extension
        if not self.filename.upper().endswith(tuple(SUPPORTED_EXTENSIONS)):
            raise ValueError(f"Unsupported file type: {self.filename}")

        try:
            self.POF0 = open(self.filename, "rb")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.filename}")
        except IOError:
            raise IOError(f"Error opening file: {self.filename}")

    def ReadChunkData(self):
        """Reads the chunk data while ensuring the file is valid."""
        chunk_type = self.GetChunkType()
        if chunk_type is None:
            raise ValueError("Invalid or unsupported file format.")

        # Read RVA
        self.POF0.seek(4)
        self.RVA = struct.unpack("<i", self.POF0.read(4))[0]

        self.POF0.seek(8)
        self.POF0.seek(self.RVA, 1)  # Move to RVA location
        self.DecodePOF0()

    def GetChunkType(self):
        """Validates and retrieves the chunk type."""
        try:
            self.POF0.seek(0)
            tmp_MAGIC = self.POF0.read(4)
            if tmp_MAGIC not in {YOBJ, YANM, MAGIC}:
                print(f"Invalid file type: {self.filename}")
                return None
            return tmp_MAGIC
        except struct.error:
            return None

    def DecodePOF0(self):
        """Decodes POF0 data while handling unexpected file behavior."""
        TYPE1 = 128
        TYPE2 = 64
        TYPE3 = 192
        TYPE4 = 63
        TYPE5 = 16383

        self.POF0.seek(8, 1)

        while True:
            try:
                byte = self.POF0.read(1)
                if not byte:  # End of file reached
                    print(f"Reached EOF for {self.filename}")
                    break

                FLAG = struct.unpack("<B", byte)[0]
                TMP_FLG = FLAG & TYPE3

                if TMP_FLG == TYPE3:
                    pass

                elif TMP_FLG == TYPE1:
                    extra_byte = self.POF0.read(1)
                    if not extra_byte:
                        break
                    flag2 = struct.unpack("<B", extra_byte)[0]
                    flag3 = (FLAG << 8) | flag2
                    flag4 = flag3 & TYPE5
                    PTR = (flag4 << 2) + 8
                    self.PTRs.append(PTR)  # Store PTR value

                elif TMP_FLG == TYPE2:
                    TMP_FLG2 = FLAG & TYPE4
                    PTR = (TMP_FLG2 << 2) + 8
                    self.PTRs.append(PTR)  # Store PTR value
                    self.POF0.seek(1, 1)

                elif TMP_FLG == 0:
                    print("Decoding complete.")
                    break

            except struct.error:
                print("Error reading file structure.")
                break

    def print_results(self):
        """Prints all PTR values in decimal along with their count."""
        print("\nDecoded PTR values (in decimal):")
        for i, ptr in enumerate(self.PTRs, start=1):
            print(f"{i}: {ptr}")
        print(f"\nTotal PTR count: {len(self.PTRs)}")


def get_file_from_user():
    """Prompt the user for a file via a file dialog if no command-line argument is given."""
    if Tk is None:
        print("Error: tkinter is required for GUI file selection but is not installed.")
        sys.exit(1)

    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = askopenfilename(
        title="Select a .YOBJ, .YANM, or .POF0 file",
        filetypes=[("YOBJ, YANM, POF0 files", "*.YOBJ;*.YANM;*.POF0")],
    )
    return file_path if file_path else None


if __name__ == "__main__":
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    else:
        print("No file provided, opening file selection dialog...")
        file_path = get_file_from_user()

    if not file_path:
        print("No file selected. Exiting.")
        sys.exit(1)

    # Validate if the file exists before processing
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    try:
        chunk = YCHUNK(file_path)
        chunk.ReadChunkData()
        chunk.print_results()  # Print the PTR results
    except Exception as e:
        print(f"Error: {e}")

    input("\nPress Enter to exit...")  # Keeps console open if double-clicked
