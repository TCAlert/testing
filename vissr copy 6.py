# Full script to extract and visualize IR imagery from an SSEC-format SMS-1 .TAP file

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def read_bcd_block_size(bcd_bytes):
    """Convert 8-byte ASCII BCD size to integer."""
    try:
        return int(bcd_bytes.decode("ascii"))
    except Exception:
        return None

def unpack_36bit_words_ssec(data):
    """Unpack 11871-byte SSEC record into 2638 36-bit words (4.5 bytes each)."""
    words = []
    for i in range(0, len(data), 9):
        if i + 9 > len(data):
            break
        b = int.from_bytes(data[i:i+9], 'big')
        word1 = (b >> 36) & ((1 << 36) - 1)
        word2 = b & ((1 << 36) - 1)
        words.append(word1)
        words.append(word2)
    return words

def extract_ir_pixels(words):
    """Extract 3822 IR 9-bit pixels from unpacked 36-bit words (words 33 to 988)."""
    pixels = []
    for word in words[32:988]:  # 33rd to 988th (1-based index)
        for shift in (27, 18, 9, 0):
            pixel = (word >> shift) & 0x1FF  # 9 bits
            pixels.append(pixel)
    return np.array(pixels[:3822], dtype=np.uint16)

# --- Main extraction ---
file = r"C:\Users\deela\Downloads\SMS1-VISSR_L1-EHT_1974m0902t030150_DD23552-1.TAP"
file_path = Path(file)
full_scan_lines = []

with open(file_path, "rb") as f:
    f.seek(8 + 132)  # Skip label record (8-byte BCD size + 132-byte label)

    while True:
        size_bytes = f.read(8)
        if len(size_bytes) < 8:
            break  # EOF
        size = read_bcd_block_size(size_bytes)
        if size is None or size <= 0:
            break
        block = f.read(size)
        if len(block) != size:
            break
        words = unpack_36bit_words_ssec(block)
        line = extract_ir_pixels(words)
        full_scan_lines.append(line)

# Stack into image
full_ir_image = np.stack(full_scan_lines)

import satcmaps as cmap
cmaps, vmax, vmin = cmap.irg()
print(vmax, vmin)
# --- Visualization ---
plt.figure(figsize=(12, 12))
plt.imshow(full_ir_image, cmap = cmaps.reversed(), vmin = 15, vmax = 245, aspect='auto')
plt.colorbar(label='Brightness (IR, raw 9-bit)')
plt.title("SMS-1 VISSR IR Imagery — Full Image (1974-09-02, 03:01–03:17 UTC)")
plt.xlabel("Pixels (longitude)")
plt.ylabel("Scan lines (latitude)")
plt.tight_layout()
plt.show()