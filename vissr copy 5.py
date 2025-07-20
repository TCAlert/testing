import numpy as np
import matplotlib.pyplot as plt

file = r"C:\Users\deela\Downloads\SMS1-VISSR_L1-AOIPS-IR_1974m0902t122025_DD51886-2.TAP"

# Load the file into memory (assuming you already have the file as `tap_bytes`)
with open(file, "rb") as f:
    tap_bytes = f.read()

# Convert to numpy array
byte_array = np.frombuffer(tap_bytes, dtype=np.uint8)

# Parameters from documentation
record_size = 1244  # VIS record size (excluding FORTRAN markers) #4172
image_width = 976  # Width of visible scanline                   #3904
full_record_size = 4 + record_size + 4  # FORTRAN blocked: [4-byte len] + data + [4-byte len]

# Compute number of records in file
num_records = len(byte_array) // full_record_size

# Extract and decode each record
image_lines = []
for i in range(num_records):
    start = i * full_record_size
    middle_start = start + 4  # skip FORTRAN header
    middle_end = middle_start + record_size
    if middle_end + 4 <= len(byte_array):
        block = byte_array[middle_start:middle_end]
        image_line = block[-image_width:]  # Extract last 3904 bytes = image
        image_lines.append(image_line)

# Stack into 2D image
image_array = np.vstack(image_lines)

# Apply 5-bit stretch (0–31 to 0–255)
image_8bit = image_array#np.clip(image_array * 255.0 / 31, 0, 255).astype(np.uint8)

import cmaps as cmap

# Display image
plt.figure(figsize=(16, 9))
plt.imshow(image_8bit,aspect="auto", cmap = cmap.probs2(), vmin = 80, vmax = 220)
plt.title(f"SMS-1 VISSR Visible Image — {image_array.shape[0]} × {image_array.shape[1]}")
plt.axis("off")
plt.show()