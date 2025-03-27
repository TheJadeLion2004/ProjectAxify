from math import *
from pathlib import Path
from utility import *


# Function to read the DMA data from binary .axy file
def read_from_file_blackwhite(path):
    with open(path, 'rb') as f:
        # Read shape directly as text
        n, m = list(map(int, f.readline().split()))
        # Read the byte array
        byte_array = f.read()

    # Compute length of fixed-length encoding
    limit = n * m * (n * n + m * m) + n * m + m
    byte_size = (limit.bit_length() + 7) // 8
    # Decode bytes into numbers (little-endian)
    x_list, y_list, D2_list = [], [], []
    for i in range(0, len(byte_array), byte_size):
        t = int.from_bytes(byte_array[i:i+byte_size], 'little')
        y_list.append(t % m)
        t //= m
        x_list.append(t % n)
        t //= n
        D2_list.append(t)
    # Return all the DMA data
    return n, m, x_list, y_list, D2_list


# Function to reconstruct the binary image from DMA data
def reconstruct_blackwhite(n, m, x_list, y_list, D2_list, path):
    count = len(D2_list)
    # Initialise all pixels to False (white)
    pixels = [[False for j in range(m)] for i in range(n)]
    for point in range(count):
        # Extract coordinates and distance squared transform at that point
        d = ceil(sqrt(D2_list[point]))
        x0 = x_list[point]
        y0 = y_list[point]
        # Colour in the circle around (x0, y0) to True (black)
        for x in range(max(0, x0 - d), min(n, x0 + d)):
            l = 0
            r = 0
            if d >= abs(x - x0):
                l = ceil(sqrt(d ** 2 - (x - x0) ** 2))
                r = floor(sqrt(d ** 2 - (x - x0) ** 2))
            for y in range(max(0, y0 - d, y0 - l), min(m, y0 + d, y0 + r)):
                if (x - x0) ** 2 + (y - y0) ** 2 > d ** 2:
                    continue
                try:
                    pixels[x][y] = True
                except IndexError:
                    pass

    # Flatten and save the pixels in an image
    for i in range(n):
        for j in range(m):
            pixels[i][j] = not pixels[i][j]
    save_image(pixels, '1', path)


# Function to visualise the recovered skeleton
def visualise_skeleton_blackwhite(n, m, x_list, y_list, path):
    t = len(x_list)
    # Initialise all pixels to False (white)
    pixels = [[False for j in range(m)] for i in range(n)]
    c = 0
    # Colour all the skeleton points True (black)
    for point in range(t):
        c += 1
        x = x_list[point]
        y = y_list[point]
        pixels[x][y] = True

    # Flatten and save the pixels in an image
    for i in range(n):
        for j in range(m):
            pixels[i][j] = not pixels[i][j]
    save_image(pixels, '1', path)


# Function to extract and present all the compressed data in original form
def extract_compressed_blackwhite(path):
    print("Reconstructing...")
    # Read from the .axy file
    n, m, x, y, D2 = read_from_file_blackwhite(path)
    # Reconstruct the binary image
    destination_path = Path(__file__).parent.parent / "images/reconstructed_blackwhite.png"
    reconstruct_blackwhite(n, m, x, y, D2, destination_path)
    # Create a visualisation of the skeleton
    skeleton_path = Path(__file__).parent.parent / "images/skeleton_blackwhite.png"
    visualise_skeleton_blackwhite(n, m, x, y, skeleton_path)
    print("Reconstruction done.")

if __name__ == "__main__":
    source_path = Path(__file__).parent.parent / "images/compressed_blackwhite.axy"
    extract_compressed_blackwhite(source_path)
