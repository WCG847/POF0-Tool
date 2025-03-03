import struct as s
import sys
import os

class POF0Encoder:
    def __init__(self, input_file):
        """Initialize with a YOBJ/YANM file to scan for relocations."""
        self.input_file = input_file
        self.offsets = []
        self.encoded_data = bytearray()

    def find_pointer_offsets(self):
        """Scan file for possible pointer locations (aligned to 4 bytes)."""
        with open(self.input_file, "rb") as f:
            data = f.read()
        
        file_size = len(data)

        # Scan for 4-byte aligned offsets that point inside the file
        for i in range(8, file_size - 4, 4):  # Start from 0x08 (not 0x00)
            value = s.unpack("<I", data[i:i+4])[0]  # Read as little-endian
            if 8 <= value < file_size:  # Must be inside file bounds
                self.offsets.append(i)

        self.offsets = sorted(set(self.offsets))  # Remove duplicates and sort
        print(f"Identified {len(self.offsets)} relocations.")

    def relative_offsets(self):
        """Convert absolute offsets to relative offsets from base 0x08."""
        return [offset - 8 for offset in self.offsets]

    def encode_offsets(self):
        """Encode offsets using POF0 variable-length encoding."""
        prev_offset = 0
        for offset in self.relative_offsets():
            rel_offset = offset - prev_offset
            prev_offset = offset

            if rel_offset < 0x40:
                self.encoded_data.append(0x40 | (rel_offset & 0x3F))
            elif rel_offset < 0x4000:
                self.encoded_data.append(0x80 | ((rel_offset >> 8) & 0x3F))
                self.encoded_data.append(rel_offset & 0xFF)
            else:
                self.encoded_data.append(0xC0 | ((rel_offset >> 24) & 0x3F))
                self.encoded_data.append((rel_offset >> 16) & 0xFF)
                self.encoded_data.append((rel_offset >> 8) & 0xFF)
                self.encoded_data.append(rel_offset & 0xFF)

    def write_pof0(self, output_file):
        """Write the new POF0 section to a file."""
        with open(output_file, "wb") as f:
            f.write(b"POF0")  # Magic identifier
            f.write(s.pack("<I", len(self.encoded_data) + 8))  # POF0 size
            f.write(b"\x00\x00\x00\x00")  # Reserved bytes
            f.write(self.encoded_data)  # Encoded offsets
        print(f"New POF0 written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python encoder.py <input YOBJ/YANM file> <output POF0 file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    try:
        # Create a new encoder, scan file, and generate POF0
        encoder = POF0Encoder(input_file)
        encoder.find_pointer_offsets()
        encoder.encode_offsets()
        encoder.write_pof0(output_file)

    except Exception as e:
        print(f"Error: {e}")
