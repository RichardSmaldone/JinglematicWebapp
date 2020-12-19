import os
from flask import Flask, flash, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
from processing import jinglematic



app=Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'jinglematic/uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['mp3', 'aac', 'm4a', 'flac'])
# "Audio files",".mp3 .wav .flac .m4a .aac"
# ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'flac', 'm4a', 'aac'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('The elves want you to select a file first.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            #flash(howdy(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            music_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #jinglematic(music_file)
            #send_file(jinglematic(music_file))
            #send_from_directory(jinglematic(music_file))
            output_file = jinglematic(music_file)
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename=output_file, as_attachment=True)
            #return redirect('/')
        else:
            flash('Allowed file types are mp3, aac, mp4, flac.')
            return redirect(request.url)


if __name__ == "__main__":
    app.run(host = '127.0.0.1',port = 5000, debug = False)

