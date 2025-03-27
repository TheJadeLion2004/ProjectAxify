from copy import deepcopy
from dma import *


# Function to extract a matrix of pixels from an image file path
def matrix_greyscale(path):
    im = Image.open(path).convert('L')
    n = im.height
    m = im.width

    data = im.getdata()
    pixels = []
    for i in range(n):
        pixels.append([])
        for j in range(m):
            pixels[-1].append(data[i * m + j])
    return pixels


# Function to segment pixels and extract a bucket
def convert_bucket_to_blackwhite(pixels, bucket):
    select_pixels = deepcopy(pixels)
    count = 0
    total = 0
    n = len(pixels)
    m = len(pixels[0])
    # Check each pixel if it's in the bucket range
    for i in range(n):
        for j in range(m):
            if bucket[0] <= pixels[i][j] < bucket[1]:
                select_pixels[i][j] = BLACK
                count += 1
                total += pixels[i][j]
            else:
                select_pixels[i][j] = WHITE
    # Find the average colour of the bucket
    if count == 0:
        colour = 0
    else:
        colour = total // count
    # Change all pixels of that bucket to average colour
    for i in range(n):
        for j in range(m):
            if bucket[0] <= pixels[i][j] < bucket[1]:
                pixels[i][j] = colour
    # Return the binary image and colour
    return select_pixels, colour


# Function to initialise a .axy file with preliminary information
def initialise_file_greyscale(n, m, colours, path):
    with open(path, 'wb') as f:
        # Write n and m as plaintext
        f.write(f"{n} {m}\n".encode())
        for colour in colours:
            f.write(f"{colour[0]} {colour[1]} ".encode())
        f.write(f"\n".encode())


# Function to compress the entire greyscale image
def compress_greyscale_image(path, bucket_count, delta, skip):
    print("Compressing...")
    # Extract matrix of pixels
    pixels = matrix_greyscale(path)

    # Bucketise the image into equal buckets
    buckets = [(i * 256 // bucket_count, (i + 1) * 256 // bucket_count) for i in range(bucket_count)]
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
    destination_path = Path(__file__).parent.parent / "images/compressed_grey.axy"
    initialise_file_greyscale(n, m, colours, destination_path)
    # Save the bucket dmas in the .axy file
    for formatted_dma in bucket_formatted_dmas:
        write_to_file(n, m, *formatted_dma, destination_path)

    # Save the segmented image separately
    segmented_path = Path(__file__).parent.parent / "images/segmented_grey.png"
    im = Image.new(mode="L", size=(m, n))
    data = []
    for i in range(n):
        for j in range(m):
            data.append(pixels[i][j])
    im.putdata(data)
    im.save(segmented_path)
    print("Compression done.")


if __name__ == "__main__":
    source_path = Path(__file__).parent.parent / "images/grey.png"
    compress_greyscale_image(source_path, 16, 2, 3)
