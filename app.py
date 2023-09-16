from flask import Flask, send_file
import zipfile
import os
import daily_manager
import json

with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)


@app.route('/')
def home_page():
    return "Hey there space cowboy."


@app.route('/daily/<month>', methods=['GET'])
def serve_images(month):
    dm = daily_manager.DailyManager(config['username'],
                                    config['password'])  # Create headless webdriver
    dm.login()  # Login to NDHP dailies
    dm.click_monthly()  # Enter monthly webpage
    dm.cycle_screenshot(month)  # Cycle through months and snapshot requested month

    # Define the path to the folder containing the images
    image_folder = 'daily_images'

    # Create a temporary zip file
    zip_filename = 'images.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(image_folder):
            for file in files:
                # Add each image file to the zip archive
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, image_folder))

    dm.purge_images()
    dm.browser.quit()

    # Send the zip archive as a response
    return send_file(zip_filename, mimetype='application/zip', as_attachment=True)


@app.route('/clear')
def clear():
    os.remove("images.zip")
    return True


@app.route('/uptime')
def uptime():
    return True


if __name__ == '__main__':
    app.run(port=7777)

