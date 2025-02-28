import struct as s
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

class YCHUNK:
	def __init__(self, YCHUNK_TYPE):
		self.YCT = open(YCHUNK_TYPE, 'rb')
		self.E = []
		self.TMP_E = []

	def GetChunkType(self):
		POF0 = 'POF0'
		YOBJ = 'YOBJ'
		YANM = 'YANM'
		MAGIC = s.unpack("4s", self.YCT.read(4))[0].decode('ascii')
		if MAGIC == POF0:
			return 1
		if MAGIC == YOBJ:
			return 2
		if MAGIC == YANM:
			return 3
		else:
			raise ValueError(f"{MAGIC} not supported")

	def ReadChunkData(self):
		self.GetChunkType()
		self.YCT.seek(8)
		self.YCT.seek(4, 1)
		POF0PTR = s.unpack("<i", self.YCT.read(4))[0]
		self.YCT.seek(POF0PTR, 1)
		print(f"Navigated to {self.YCT.tell()}")
		self.DecodePOF0()

	def DecodePOF0(self):
		TYPE1 = 128
		TYPE2 = 64
		TYPE3 = 192
		MASK1 = 63
		MASK2 = 16383
		while True:
			try:
				TMP_INDICE = s.unpack("<B", self.YCT.read(1))[0]
				TMP_IND2 = TMP_INDICE & TYPE3
				print(f"converted {TMP_INDICE} to {TMP_IND2}")
				if TMP_IND2 == TYPE3:
					print(f"{TMP_IND2} is TYPE3 PTR")
					self.YCT.seek(4, 1)
					TMP_W3 = s.unpack("<B", self.YCT.read(1))[0]
					self.YCT.seek(-2, 1)
					TMP_W2 = s.unpack("<B", self.YCT.read(1))[0]
					self.YCT.seek(-2, 1)
					TMP_W1 = s.unpack("<B", self.YCT.read(1))[0]
					self.YCT.seek(-2, 1)
					REAL_W = (TMP_INDICE << 24) | (TMP_W1 << 16) | (TMP_W2 << 8) | TMP_W3
					REAL_IND = ((REAL_W << (32 + 2) & 18446744073709551615) >> (32 + 2) & 18446744073709551615) << 2
					print(f"converted {TMP_IND2} to {REAL_IND}")
					self.YCT.seek(3, 1)

				elif TMP_IND2 == TYPE1:
					print(f"{TMP_IND2} is TYPE1 PTR")
					TMP_HW = s.unpack("<B", self.YCT.read(1))[0]
					halfword = (TMP_INDICE << 8) | TMP_HW
					TMP_IND3 = halfword & MASK2
					REAL_IND = TMP_IND3 << 2
					print(f"converted {TMP_IND2} to {REAL_IND}")
				elif TMP_IND2 == TYPE2:
					print(f"{TMP_IND2} is TYPE2 PTR")
					TMP_IND3 = TMP_INDICE & MASK1
					REAL_IND = TMP_IND3 << 2
					print(f"converted {TMP_IND2} to {REAL_IND}")			

				else:
					print(f"{TMP_INDICE} NOT SUPPORTED OR EOF.")
					return
				self.E.append(REAL_IND)
			except s.error:
				print(f"Successfully converted POF0. {self.YCT.tell()} is a EOF")
				return

	def get_file_from_user():
		"""Prompt the user for a file via a file dialog if no command-line argument is given."""
		if Tk is None:
			print("Error: tkinter is required for GUI file selection but is not installed.")
			sys.exit(1)

		root = Tk()
		root.withdraw()  # Hide the root window
		YCHUNK_TYPE = askopenfilename(
			title="Select a .YOBJ, .YANM, or .POF0 file",
			filetypes=[("YOBJ, YANM, POF0 files", "*.YOBJ;*.YANM;*.POF0")],
		)
		return YCHUNK_TYPE if YCHUNK_TYPE else None


if __name__ == "__main__":
    if len(sys.argv) == 2:
        YCHUNK_TYPE = sys.argv[1]
    else:
        print("No file provided, opening file selection dialog...")
        YCHUNK_TYPE = YCHUNK.get_file_from_user()

    if not YCHUNK_TYPE:
        print("No file selected. Exiting.")
        sys.exit(1)

    # Validate if the file exists before processing
    if not os.path.exists(YCHUNK_TYPE):
        print(f"Error: File '{YCHUNK_TYPE}' does not exist.")
        sys.exit(1)

    try:
        chunk = YCHUNK(YCHUNK_TYPE)
        chunk.ReadChunkData()
    except Exception as e:
        print(f"Error: {e}")

    input("\nPress Enter to exit...")  # Keeps console open if double-clicked
		










