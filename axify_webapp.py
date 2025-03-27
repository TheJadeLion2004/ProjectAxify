from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import cv2
import requests
import os
import time
from flask_mail import Mail, Message
import subprocess
import numpy as np
import shutil
from pathlib import Path
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random string

# IP Camera URL
IP_CAMERA_URL = "http://<INSERT IP ADDRESS HERE>/video"
IP_FRAME_URL = "http://<INSERT IP ADDRESS HERE>/photo.jpg"
CAPTURED_IMAGE_PATH = "images/captured_image.jpg"
PROCESSED_IMAGE_PATH = "images"
FINAL_IMAGE_PATH = "images/reconstructed_colour_blurred.png"

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '<INSERT EMAIL ADDRESS HERE>'  # Your email
app.config['MAIL_PASSWORD'] = '<INSERT APP PASSWORD HERE>'  # App password
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)

@app.route('/images/<filename>')
def images(filename):
    return send_from_directory('images', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        response = requests.get(IP_FRAME_URL, timeout=5)
        if response.status_code != 200:
            flash("Failed to capture image.")
            return redirect(url_for('index'))

        # Step 2: Convert response content to OpenCV format
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Step 3: Auto-detect rotation based on dimensions
        height, width, _ = frame.shape
        if height < width:  # If landscape, rotate
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame, 1)

        # Step 4: Save the corrected image
        cv2.imwrite(CAPTURED_IMAGE_PATH, frame)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))

    return render_template('confirm.html', image_url=url_for('images', filename="captured_image.jpg"))

@app.route('/confirm', methods=['POST'])
def confirm():
    # Get user's email
    email = request.form.get('email')
    if email:
        send_results_email(email, PROCESSED_IMAGE_PATH)

    return render_template('success.html', processed_image_url=url_for('images', filename=FINAL_IMAGE_PATH, t=time.time()))

@app.route('/process', methods=['POST'])
def process():
    email = request.form.get('email')
    image_path = CAPTURED_IMAGE_PATH

    if not email or not image_path:
        flash("Missing email or image.")
        return redirect(url_for('index'))

    # Process the image
    process_image()

    # Send email with results
    send_results_email(email, PROCESSED_IMAGE_PATH)

    flash("Image processed successfully! Results sent to your email.")
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

def process_image():
    """ Processing function """
    # Delete the images directory and recreate it to avoid any corruption of data
    dir_path = Path(__file__).parent / "images"
    im = Image.open(dir_path / "captured_image.jpg")
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    im.save(dir_path / "captured_image.jpg")

    # Run all three subprocesses on the captured image
    subprocess.run(["python3", "src/generate.py"])
    print("BLACK/WHITE PROCESSING:")
    subprocess.run(["python3", "src/compress_blackwhite.py"])
    subprocess.run(["python3", "src/reconstruct_blackwhite.py"])
    print("GREYSCALE PROCESSING:")
    subprocess.run(["python3", "src/compress_greyscale.py"])
    subprocess.run(["python3", "src/reconstruct_greyscale.py"])
    print("COLOUR PROCESSING:")
    subprocess.run(["python3", "src/compress_colour.py"])
    subprocess.run(["python3", "src/reconstruct_colour.py"])


def send_results_email(email, results_dir):
    """Send an email with multiple image attachments from a directory."""
    try:
        msg = Message("Your Axified Images!", recipients=[email])
        msg.body = "Greetings from Project Axify! Thanks for visiting our stall. Here's all the axified images generated from your photo:\n"

        # Loop through all files in the results directory
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)

            # Attach only image files (PNG, JPG, JPEG) or any other needed formats
            if filename.endswith(('.png',)) and os.path.isfile(file_path):
                with app.open_resource(file_path) as fp:
                    msg.attach(filename, "image/png", fp.read())  # Change MIME type if needed

        mail.send(msg)
        print(f"Email sent to {email} with {len(os.listdir(results_dir))} attachments.")

    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
