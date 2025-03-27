from compress_greyscale import *


# Function to extract a matrix of pixels from an image file path
def matrix_colour(name):
    im = Image.open(name).convert("RGB")
    n = im.height
    m = im.width

    data = im.getdata()
    pixels_red = []
    pixels_green = []
    pixels_blue = []
    for i in range(n):
        pixels_red.append([])
        pixels_green.append([])
        pixels_blue.append([])
        for j in range(m):
            pixels_red[-1].append(data[i * m + j][0])
            pixels_green[-1].append(data[i * m + j][1])
            pixels_blue[-1].append(data[i * m + j][2])
    return pixels_red, pixels_green, pixels_blue


# Function to compress the entire colour image
def compress_colour_image(path, bucket_count, delta, skip):
    all_pixels = matrix_colour(path)
    buckets = [(i * 256 // bucket_count, (i + 1) * 256 // bucket_count) for i in range(bucket_count)]
    axes = ("red", "green", "blue")
    for i in range(3):
        axis = axes[i]
        print(f"Compressing {axis}...")
        pixels = all_pixels[i]
        colours = []
        bucket_formatted_dmas = []

        # For each bucket, treat it as a binary image and compute the dma
        for i in range(len(buckets)):
            print(f"Bucket {i + 1} of {len(buckets)}...")
            bucket = buckets[i]
            # Update pixels and extract a blackwhite version of this bucket
            blackwhite, colour = convert_bucket_to_blackwhite(pixels, bucket)
            # Compute distance squared and projection transforms
            D2, P = integer_transforms(blackwhite)
            # Compute dma
            dma = compute_dma(blackwhite, delta, True, D2, P)
            # Format the dma
            x_list, y_list, D2_list = format_dma(dma, D2, skip)
            # Store it for writing later
            bucket_formatted_dmas.append((x_list, y_list, D2_list))
            # Store the colour and count
            colours.append((len(x_list), colour))

        n = len(pixels)
        m = len(pixels[0])
        # Initialise the .axy file
        destination_path = Path(__file__).parent.parent / f"images/compressed_{axis}.axy"
        initialise_file_greyscale(n, m, colours, destination_path)
        # Save the bucket dmas in the .axy file
        for formatted_dma in bucket_formatted_dmas:
            write_to_file(n, m, *formatted_dma, destination_path)
        print(f"{axis[0].upper()}{axis[1:]} compression done.")


if __name__ == "__main__":
    source_path = Path(__file__).parent.parent / "images/colour.png"
    compress_colour_image(source_path, 16, 1.5, 3)
