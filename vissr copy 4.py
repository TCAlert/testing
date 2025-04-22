import numpy as np
import matplotlib.pyplot as plt

def read_nimbus_thir_image(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    # Read as bytes, ensure it's 4-byte aligned
    byte_data = np.frombuffer(data, dtype=np.uint8)
    if len(byte_data) % 4 != 0:
        byte_data = np.pad(byte_data, (0, 4 - len(byte_data) % 4))
    
    # Convert to 32-bit unsigned ints
    word_data = byte_data.view(np.uint32)
    print(f"Total words in file: {len(word_data)}")

    index = 0
    image_rows = []

    while index < len(word_data) - 1:
        # Read TAP headers
        tap1 = word_data[index]
        tap2 = word_data[index + 1]

        if tap1 == 0 and tap2 == 0:
            print(f"End of file detected at index {index}")
            break

        print(f"Reading record at index {index} (TAP Header: {tap1}, {tap2})")
        index += 2  # Move past TAP header

        # **Extract Orbit Documentation (First Record)**
        orbit_doc_size = 42  # Safe minimum
        if index + orbit_doc_size > len(word_data):
            print("Error: Orbit documentation exceeds file size")
            break

        print(f"Extracting Orbit Documentation from {index} to {index + orbit_doc_size}")
        index += orbit_doc_size  # Move past orbit doc

        # **Extract Data Record Header**
        num_nadir_angles = 31
        data_record_header_size = 7 + num_nadir_angles
        if index + data_record_header_size > len(word_data):
            print("Error: Data record header exceeds file size")
            break

        print(f"Extracting Data Record Header from {index} to {index + data_record_header_size}")
        index += data_record_header_size  # Move past data record header

        # **Extract Swath Data Properly**
        num_swaths = 5  
        for swath_idx in range(num_swaths):
            if index >= len(word_data) - 2:
                print(f"End of file while reading swath {swath_idx}")
                break

            swath_header = word_data[index]
            swath_size = word_data[index + 1]  # The next word should indicate size

            # ✅ **Fix: Ignore invalid sizes**
            if swath_size < 40 or swath_size > 500:  # Real swaths fall in this range
                print(f"Skipping invalid swath size {swath_size} at index {index}")
                index += 2  # Move to next possible swath
                continue

            print(f"Swath {swath_idx + 1}: Extracting {swath_size} pixels from index {index + 2}")

            # Read swath data
            swath_data = word_data[index + 2: index + 2 + swath_size]

            if len(swath_data) != swath_size:
                print(f"Error: Swath data size mismatch ({len(swath_data)} instead of {swath_size})")
                break

            image_rows.append(swath_data)
            index += 2 + swath_size  # Move past swath data

        # Skip trailing TAP header
        index += 2

    if not image_rows:
        print("Error: No image data found!")

    # Convert to 2D image array
    image_array = np.array(image_rows)
    print(f"Final image shape: {image_array.shape}")
    return image_array

def plot_image(image_array):
    if image_array.size == 0:
        print("Error: Empty image data!")
        return
    
    plt.imshow(image_array, cmap='hot', aspect='auto')
    plt.colorbar(label='Temperature')
    plt.title("Nimbus THIR Reconstructed Satellite Image")
    plt.xlabel("Pixel (Sample Index)")
    plt.ylabel("Swath (Line)")
    plt.show()

# Example usage
file_path = r"C:\Users\deela\Downloads\Nimbus5-THIRCH115_1974m0901t034738_o08442_DR1678.TAP"  # Replace with actual file path
swath_data_list = read_nimbus_thir_image(file_path)
plot_image(swath_data_list)