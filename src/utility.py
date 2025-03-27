from PIL import Image


# Pixel value constants used in the code
BLACK = False
WHITE = True
INF = 1 << 31


# Function to save an image from pixels
def save_image(pixels, mode, path):
    n = len(pixels)
    m = len(pixels[0])
    data = []
    for i in range(n):
        for j in range(m):
            data.append(pixels[i][j])
    im = Image.new(mode=mode, size=(m, n))
    im.putdata(data)
    im.save(path)