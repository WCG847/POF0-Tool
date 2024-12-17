import struct

def decode_pof0(file_data):
    """
    Decodes the POF0 section from a binary file, based on the Yuke's SYM game logic.

    Args:
        file_data (bytes): The binary file data containing the POF0 section.
    
    Returns:
        dict: A dictionary of offsets and their final values.
    """
    
    
    # Constants
    POF0_MAGIC = b'POF0'
    POF0_HEADER_SIZE = 8
    
    # Locate the POF0 section
    pof0_start = file_data.find(POF0_MAGIC)
    if pof0_start == -1:
        raise ValueError("POF0 magic header not found in the file.")
    
    # Read POF0 size
    header_offset = pof0_start + len(POF0_MAGIC)
    if len(file_data) < header_offset + 4:
        raise ValueError("File truncated; cannot read POF0 size.")
    
    pof0_size = struct.unpack_from('<I', file_data, header_offset)[0]
    indices_start = header_offset + 4
    
    # Validate indices section
    if len(file_data) < indices_start + pof0_size:
        raise ValueError("File truncated; POF0 indices exceed file size.")
    
    # Extract indices data
    pof0_indices = file_data[indices_start:indices_start + pof0_size]
    print(f"POF0 Indices: {pof0_indices}")
    
    # Initialize decoded output
    output_array = {}
    current_index = 0
    data_length = len(pof0_indices)
    
    while current_index < data_length:
        byte_value = pof0_indices[current_index]
        flag_bits = byte_value & 0xC0
        
        if flag_bits == 0xC0:
            if current_index + 4 > data_length:
                raise ValueError("Insufficient data for C0 flag decoding.")
            
            local_value = (
                (byte_value << 16) |
                (pof0_indices[current_index + 1] << 8) |
                pof0_indices[current_index + 2] |
                pof0_indices[current_index + 3]
            )
            current_index += 4
            offset = local_value >> 22
            output_array[offset] = output_array.get(offset, 0) + 1
        
        elif flag_bits == 0x80:
            if current_index + 2 > data_length:
                raise ValueError("Insufficient data for 80 flag decoding.")
            
            local_value = (pof0_indices[current_index] << 8) | pof0_indices[current_index + 1]
            current_index += 2
            offset = local_value & 0x3FFF
            output_array[offset] = output_array.get(offset, 0) + 1
        
        elif flag_bits == 0x40:
            current_index += 1
            offset = byte_value & 0x3F
            output_array[offset] = output_array.get(offset, 0) + 1
        
        else:
            current_index += 1
    
    return output_array
