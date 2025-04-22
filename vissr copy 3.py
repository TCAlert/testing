import numpy as np
import struct
import matplotlib.pyplot as plt

# File path
file_path = r"C:\Users\deela\Downloads\Nimbus5-THIRCH115_1974m0901t034738_o08442_DR1678.TAP"

import struct
import numpy as np

def read_esmr(file_path):
    with open(file_path, "rb") as f:
        data = f.read()  # Read the entire file into memory
    
    offset = 0
    records = []

    while offset < len(data):
        # Ensure we have enough bytes for the block size header
        if offset + 4 > len(data):
            print(f"Warning: Not enough bytes left for block header at offset {offset}")
            break  

        # Read 4-byte block size header
        block_size = struct.unpack(">I", data[offset:offset+4])[0]  # Big-endian 4-byte int
        print(f"Raw block size at offset {offset}: {block_size}")  # Debugging
        offset += 4
        
        if block_size == 0:
            break  # End of file
        
        # Validate block size
        if block_size > 28000 or block_size < 0:
            print(f"Warning: Bad block size {block_size}, using 28000")
            block_size = 28000
        
        # Ensure enough data remains for block
        if offset + block_size > len(data):
            print(f"Warning: Block size {block_size} exceeds remaining data ({len(data) - offset} bytes)")
            break  

        # Read block data
        block_data = data[offset:offset+block_size]
        offset += block_size

        # Ensure there's enough data left for footer
        if offset + 4 > len(data):
            print(f"Warning: Not enough bytes left to read block footer at offset {offset}")
            break  

        # Read last 4-byte block footer (should match header)
        block_footer = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        if block_size != block_footer:
            print(f"Warning: Block size mismatch {block_size} != {block_footer}")
        
        # Process records (each 280*2 bytes)
        for i in range(0, block_size, 280*2):
            record = np.frombuffer(block_data[i:i+280*2], dtype=">u2")  # Big-endian 16-bit ints
            records.append(record)

    return np.array(records)

# Read and process data
structured_data = read_esmr(file_path)

# Flip bytes (Fortran swaps 2-byte words)
structured_data = structured_data.byteswap().newbyteorder()

# Visualize the data
plt.figure(figsize=(12, 6))
plt.imshow(structured_data, cmap='gray', aspect='auto', vmin = 1500, vmax = 2500)
plt.colorbar(label="Brightness Temperature")
plt.title("Nimbus-5 ESMR Data")
plt.xlabel("Scan Line")
plt.ylabel("Record Number")
plt.show()