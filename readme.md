# Project Axify

## Overview
Axify is an image compression and restoration software written in Python, as part of a project under the Mathematics Club, IIT Madras.

## Requirements

- Python3 
- A video stream on an IP address (we have used the [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&pcampaignid=web_share) app for this purpose)

## Usage

Follow these steps to run the image compression pipeline:

1. Clone the repository to your machine.
2. Set up a video stream on an IP address.
3. In `axify_webapp.py`, paste the IP address to replace `<INSERT IP ADDRESS HERE>` on lines 17 and 18.
4. In `templates/index.html`, paste the IP address to replace `<INSERT IP ADDRESS HERE>` on line 13.
5. In `axify_webapp.py`, paste your email address to replace `<INSERT EMAIL ADDRESS HERE>` on line 27. Paste your app password to replace `<INSERT APP PASSWORD HERE>` on line 28. You could also use your own password, but for security reasons an app password is recommended.
6. Run `python3 axify_webapp.py` or execute `axify_webapp.py` from your IDE. Open the port (like `http://127.0.0.1:5000`) that appears in the output to launch the web app.
7. Use the web app's UI to navigate.