import struct

def encode_pof0(offset_dict):
    """
    Encodes offsets and values into a binary POF0 section.

    Args:
        offset_dict (dict): A dictionary where keys are offsets and values are the counts.

    Returns:
        bytes: Encoded binary data containing the POF0 section.
    """

    # Constants
    POF0_MAGIC = b'POF0'
    POF0_HEADER_SIZE = 8

    # Buffer for encoded indices
    encoded_indices = bytearray()

    # Iterate over offsets and encode based on size
    for offset, count in offset_dict.items():
        for _ in range(count):
            if 0 <= offset <= 0x3F:  # Fits in 6 bits (0x40 flag)
                encoded_indices.append(0x40 | (offset & 0x3F))
            elif 0 <= offset <= 0x3FFF:  # Fits in 14 bits (0x80 flag)
                encoded_indices.append(0x80 | ((offset >> 8) & 0x3F))
                encoded_indices.append(offset & 0xFF)
            elif 0 <= offset <= 0x3FFFFF:  # Fits in 22 bits (0xC0 flag)
                encoded_indices.append(0xC0 | ((offset >> 16) & 0x3F))
                encoded_indices.append((offset >> 8) & 0xFF)
                encoded_indices.append(offset & 0xFF)
                encoded_indices.append(0x00)  # Reserved byte for alignment
            else:
                raise ValueError(f"Offset {offset} is out of range for POF0 encoding.")

    # Prepare header
    pof0_size = len(encoded_indices)
    pof0_header = POF0_MAGIC + struct.pack('<I', pof0_size)

    # Combine header and indices into final binary output
    return pof0_header + encoded_indices


def save_pof0_file(output_path, offset_dict):
    """
    Saves the encoded POF0 section into a binary file.

    Args:
        output_path (str): Path to save the output binary file.
        offset_dict (dict): Dictionary containing offsets and their counts.
    """
    encoded_pof0 = encode_pof0(offset_dict)
    with open(output_path, 'wb') as file:
        file.write(encoded_pof0)