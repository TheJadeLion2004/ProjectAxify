import math
import numpy as np
from pathlib import Path
from PIL import Image


# Function to compute the histogram of a greyscale image
def hist(img):
    row, col = img.shape
    y = np.zeros(256, dtype=int)
    for i in range(row):
        for j in range(col):
            y[img[i, j]] += 1
    return y


# Function to create a binary image according to the threshold
def regenerate_image(img, threshold):
    return (img >= threshold).astype(np.uint8) * 255


# Function to count the number of pixels in a histogram
def count_pixel(h):
    return np.sum(h)


# Function to compute the sum of frequencies in a given range
def weight(h, s, e):
    return np.sum(h[s:e])


# Function to compute the average intensity in a given range
def mean(h, s, e):
    w = weight(h, s, e)
    if w == 0:
        return 0
    indices = np.arange(s, e)
    return np.sum(h[s:e] * indices) / float(w)


# Function to compute the intensity variance in a given range
def variance(h, s, e):
    m = mean(h, s, e)
    w = weight(h, s, e)
    if w == 0:
        return 0
    indices = np.arange(s, e)
    return np.sum(h[s:e] * (indices - m) ** 2) / float(w)


# Function to compute the optimal threshold (with minimum within-class variance)
def threshold(h):
    cnt = count_pixel(h)
    threshold_values = {}

    for i in range(1, len(h)):
        vb = variance(h, 0, i)
        wb = weight(h, 0, i) / float(cnt)
        mb = mean(h, 0, i)

        vf = variance(h, i, len(h))
        wf = weight(h, i, len(h)) / float(cnt)
        mf = mean(h, i, len(h))

        V2w = wb * vb + wf * vf
        V2b = wb * wf * (mb - mf) ** 2

        if not math.isnan(V2w):
            threshold_values[i] = V2w

    return threshold_values


# Function to find threshold that minimises within-class variance
def get_optimal_threshold(threshold_values):
    min_V2w = min(threshold_values.values())
    optimal_threshold = [k for k, v in threshold_values.items() if v == min_V2w]
    return optimal_threshold[0]


# Function to make the optimal thresholded binary image
def make_image(img):
    img = np.asarray(img)
    h = hist(img)

    threshold_values = threshold(h)
    op_thres = get_optimal_threshold(threshold_values)

    return regenerate_image(img, op_thres).flatten()


# Function to generate a colour png
def colour(path):
    im = Image.open(path)
    nim = Image.new(mode="RGB", size=im.size)
    nim.putdata(im.getdata())
    nim.save(Path(__file__).parent.parent / "images/colour.png")
    data = im.getdata()
    red_data = [(a[0], 0, 0) for a in data]
    nim.putdata(red_data)
    nim.save(Path(__file__).parent.parent / "images/red.png")
    green_data = [(0, a[0], 0) for a in data]
    nim.putdata(green_data)
    nim.save(Path(__file__).parent.parent / "images/green.png")
    blue_data = [(0, 0, a[0]) for a in data]
    nim.putdata(blue_data)
    nim.save(Path(__file__).parent.parent / "images/blue.png")


# Function to generate a black and white png
def black_white(path):
    im = Image.open(path).convert("L")
    nim = Image.new(mode="1", size=im.size)
    nim.putdata(make_image(im))
    nim.save(Path(__file__).parent.parent / "images/blackwhite.png")


# Function to generate a greyscale png
def grey(path):
    im = Image.open(path).convert("L")
    nim = Image.new(mode="L", size=im.size)
    nim.putdata(im.getdata())
    nim.save(Path(__file__).parent.parent / "images/grey.png")


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "images/captured_image.jpg"
    black_white(path)
    grey(path)
    colour(path)
