from math import *
from pathlib import Path
from copy import deepcopy
from utility import *


# Function to read the DMA data from binary .axy file
def read_from_file_greyscale(path):
    with open(path, 'rb') as f:
        # Read shape directly as text
        n, m = list(map(int, f.readline().split()))
        # Read the lengths and colours directly as text
        colours = list(map(int, f.readline().split()))
        for i in range(2, len(colours), 2):
            colours[i] += colours[i - 2]
        # Read the byte array
        byte_array = f.read()

    # Compute length of fixed-length encoding
    limit = n * m * (n * n + m * m) + n * m + m
    byte_size = (limit.bit_length() + 7) // 8  # Byte size needed per value
    # Decode bytes into numbers (little-endian)
    x_list, y_list, D2_list, colour = [], [], [], []
    ind = 0
    for i in range(0, len(byte_array), byte_size):
        if i // byte_size >= colours[ind]:
            ind += 2
        t = int.from_bytes(byte_array[i:i+byte_size], 'little')
        # Extract x, y and D2 from t
        colour.append(colours[ind + 1])
        y_list.append(t % m)
        t //= m
        x_list.append(t % n)
        t //= n
        D2_list.append(t)
    # Return all the DMA data
    return n, m, x_list, y_list, D2_list, colour


# Function to reconstruct the greyscale image from DMA data
def reconstruct_greyscale(n, m, x_list, y_list, D2_list, colour, extent, path, blur_path):
    count = len(D2_list)
    # Initialise all pixels to False (white)
    pixels = [[0 for j in range(m)] for i in range(n)]
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
                    pixels[x][y] = colour[point]
                except IndexError:
                    pass

    # Flatten and save the pixels in an image
    save_image(pixels, 'L', path)

    # Save the blurred version too
    blurred_pixels = smooth(pixels, extent)
    save_image(blurred_pixels, 'L', blur_path)


# Function to visualise the recovered skeleton
def visualise_skeleton_greyscale(n, m, x_list, y_list, colour, path):
    t = len(x_list)
    # Initialise all pixels to 255 (white)
    pixels = [[255 for j in range(m)] for i in range(n)]
    c = 0
    # Colour all the skeleton points
    for point in range(t):
        c += 1
        i = x_list[point]
        j = y_list[point]
        pixels[i][j] = colour[point]

    # Flatten and save the pixels in an image
    save_image(pixels, 'L', path)


# Function to local maximum blur the image
def smooth(pixels, extent):
    n = len(pixels)
    m = len(pixels[0])
    blurred = deepcopy(pixels)
    offsets = [(dx, dy) for dx in range(-extent, extent) for dy in range(-extent, extent)]
    # For each pixel
    for x0 in range(n):
        for y0 in range(m):
            a = 0
            count = 0
            # Take maximum of its neighbours
            for offset in offsets:
                x = x0 + offset[0]
                y = y0 + offset[1]
                if 0 <= x < n and 0 <= y < m:
                    count += 1
                    a = max(a, pixels[x][y])
            # Set the pixel to this maximum
            blurred[x0][y0] = a
    return blurred


# Function to extract and present all the compressed data in original form
def extract_compressed_greyscale(path, extent):
    print("Reconstructing...")
    n, m, x, y, D2, colour = read_from_file_greyscale(path)
    destination_path = Path(__file__).parent.parent / "images/reconstructed_grey.png"
    blurred_path = Path(__file__).parent.parent / "images/reconstructed_grey_blurred.png"
    reconstruct_greyscale(n, m, x, y, D2, colour, extent, destination_path, blurred_path)
    skeleton_path = Path(__file__).parent.parent / "images/skeleton_grey.png"
    visualise_skeleton_greyscale(n, m, x, y, colour, skeleton_path)
    print("Reconstruction done.")


if __name__ == "__main__":
    source_path = Path(__file__).parent.parent / "images/compressed_grey.axy"
    extract_compressed_greyscale(source_path, 2)
