from reconstruct_greyscale import *


# Function to read the DMA data from binary .axy file
def read_from_file_colour(paths):
    all_axes_data = []
    for path in paths:
        all_axes_data.append(read_from_file_greyscale(path))
    return all_axes_data


# Function to reconstruct the greyscale image from DMA data
def reconstruct_colour(all_axes_data, extent, path, blur_path):
    n = all_axes_data[0][0]
    m = all_axes_data[0][1]
    all_axes_pixels = [[[0, 0, 0] for j in range(m)] for i in range(n)]
    all_axes_blurred = [[[0, 0, 0] for j in range(m)] for i in range(n)]
    for i in range(3):
        pixels = [[0 for y in range(m)] for x in range(n)]
        n, m, x_list, y_list, D2_list, colour = all_axes_data[i]
        count = len(D2_list)
        for point in range(count):
            d = ceil(sqrt(D2_list[point]))
            x0 = x_list[point]
            y0 = y_list[point]
            for x in range(max(0, x0 - d), min(n, x0 + d)):
                l = 0
                r = 0
                if d ** 2 >= (x - x0) ** 2:
                    l = ceil(sqrt(d ** 2 - (x - x0) ** 2))
                    r = floor(sqrt(d ** 2 - (x - x0) ** 2))
                for y in range(max(0, y0 - d, y0 - l), min(m, y0 + d, y0 + r)):
                    if (x - x0) ** 2 + (y - y0) ** 2 > d ** 2:
                        continue
                    try:
                        pixels[x][y] = colour[point]
                    except IndexError:
                        pass
        blurred_pixels = smooth(pixels, extent)
        for x in range(n):
            for y in range(m):
                all_axes_pixels[x][y][i] = pixels[x][y]
                all_axes_blurred[x][y][i] = blurred_pixels[x][y]
    for x in range(n):
        for y in range(m):
            all_axes_pixels[x][y] = tuple(all_axes_pixels[x][y])
            all_axes_blurred[x][y] = tuple(all_axes_blurred[x][y])

    # Flatten and save the pixels in an image
    save_image(all_axes_pixels, 'RGB', path)

    # Save the blurred version too
    save_image(all_axes_blurred, 'RGB', blur_path)


# Function to extract and present all the compressed data in original form
def extract_compressed_colour(paths, extent):
    print("Reconstructing...")
    all_axes_data = read_from_file_colour(paths)
    destination_path = Path(__file__).parent.parent / "images/reconstructed_colour.png"
    blurred_path = Path(__file__).parent.parent / "images/reconstructed_colour_blurred.png"
    reconstruct_colour(all_axes_data, extent, destination_path, blurred_path)
    print("Reconstruction done.")


if __name__ == "__main__":
    source_paths = [Path(__file__).parent.parent / "images/compressed_red.axy",
                    Path(__file__).parent.parent / "images/compressed_green.axy",
                    Path(__file__).parent.parent / "images/compressed_blue.axy"]
    extract_compressed_colour(source_paths, 1)
