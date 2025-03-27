from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
from pathlib import Path


name1 = input()
name2 = input()

# Calculate and report the Structural Similarity Index Metric between two images
img1 = Image.open(Path(__file__).parent.parent / name1).convert("RGB")
img2 = Image.open(Path(__file__).parent.parent / name2).convert("RGB")

img1 = np.array(img1)
img2 = np.array(img2)

ssim_r = ssim(img1[:, :, 0], img2[:, :, 0])
ssim_g = ssim(img1[:, :, 1], img2[:, :, 1])
ssim_b = ssim(img1[:, :, 2], img2[:, :, 2])

ssim_avg = (ssim_r + ssim_g + ssim_b) / 3
print("Average SSIM (RGB):", ssim_avg)

