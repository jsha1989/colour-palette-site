import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = r'C:\Users\j.sha\PycharmProjects\colour-palette-generator\static\images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# function to convert rgb colour to hex code
def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


# checks if file is an image file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # get desired number of colours and sensitivity settings
            number_colours = request.form['number_colours']
            print(f"number_colours {number_colours}")
            sensitivity = request.form['sensitivity']
            print(f"sensitivity {sensitivity}")
            return redirect(
                url_for('analyse_image', filename=filename, number_colours=number_colours, sensitivity=sensitivity))
    return render_template("index.html")


@app.route("/result")
def analyse_image():
    filename = request.args['filename']
    number_colours = int(request.args['number_colours'])
    sensitivity = int(request.args['sensitivity'])
    with Image.open(f'{UPLOAD_FOLDER}/{filename}') as image:
        # ensure image is RGB mode
        image = image.convert('RGB')
        # complete list of colours in the image
        image_colours = image.getcolors(image.size[0] * image.size[1])
        # sort by frequency
        sorted_colours = sorted(image_colours, key=lambda tup: tup[0], reverse=True)
        # limit to top 100 colours
        sorted_colours = sorted_colours[:500]
        rgb_colours = []
        hex_colours = []
        # compare each colour with other colours
        for colour in sorted_colours:
            rgb = colour[1]
            # add first colour to rgb_colours list, also convert to hexcode and add to hex_colours list
            if len(rgb_colours) == 0:
                rgb_colours.append(rgb)
                r, g, b, = rgb
                hex = rgb_to_hex(r, g, b)
                hex_colours.append(hex)
            elif len(rgb_colours) > 0:
                similarity_count = 0
                # compare each subsequent colour with colours already on rgb_colours list
                for colour in rgb_colours:
                    red_diff = abs(rgb[0] - colour[0])
                    green_diff = abs(rgb[1] - colour[1])
                    blue_diff = abs(rgb[2] - colour[2])
                    # if difference in red/green/blue is less than sensitivity, increase the similarity counter
                    if rgb not in rgb_colours:
                        if red_diff < sensitivity and green_diff < sensitivity and blue_diff < sensitivity:
                            similarity_count += 1
                # only add the colour to rgb_colours list and hex_colours list if it is not similar to any of the existing colours
                if similarity_count == 0:
                    rgb_colours.append(rgb)
                    r, g, b, = rgb
                    hex = rgb_to_hex(r, g, b)
                    hex_colours.append(hex)
        # slice the desired number of colours
        hex_colours_slice = hex_colours[:number_colours]
        # print(f"hex_colours_slice {hex_colours_slice}")
        return render_template("palette.html", colours=hex_colours_slice, image=filename)


if __name__ == '__main__':
    app.run(debug=True)
