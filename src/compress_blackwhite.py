from dma import *


# Function to extract a matrix of pixels from an image file path
def matrix_blackwhite(path):
    # Open image file
    im = Image.open(path).convert('1')
    # Get shape of image
    n = im.height
    m = im.width

    # Get data of image in a flat list
    data = im.getdata()
    # Initialise the pixels to all black
    pixels = [[BLACK for j in range(m)] for i in range(n)]
    # Fill the pixels with white whenever applicable
    for i in range(n):
        for j in range(m):
            if data[i * m + j] == 255:
                pixels[i][j] = WHITE
    # Return the matrix of pixels
    return pixels


# Function to initialise a .axy file with preliminary information
def initialise_file_blackwhite(n, m, path):
    with open(path, 'wb') as f:
        # Write n and m as plaintext
        f.write(f"{n} {m}\n".encode())


# Function to compress the entire binary image
def compress_blackwhite_image(path, delta, skip):
    print("Compressing...")
    # Extract matrix of pixels
    pixels = matrix_blackwhite(path)
    # Compute distance squared and projection transforms
    D2, P = integer_transforms(pixels, visualise_as_image=True)
    # Compute the DMA
    dma = compute_dma(pixels, delta, True, D2, P)
    # Format the DMA
    x_list, y_list, D2_list = format_dma(dma, D2, skip)
    n = len(pixels)
    m = len(pixels[0])
    destination_path = Path(__file__).parent.parent / "images/compressed_blackwhite.axy"
    initialise_file_blackwhite(n, m, destination_path)
    write_to_file(n, m, x_list, y_list, D2_list, destination_path)
    print("Compression done.")


if __name__ == "__main__":
    source_path = Path(__file__).parent.parent / "images/blackwhite.png"
    compress_blackwhite_image(source_path, 2, 6)
