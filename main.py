from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format_type = request.form['format']
        quality = request.form['quality']

        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format_type == 'audio' else f'bestvideo[height<={quality}]+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format_type == 'audio' else []
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format_type == 'audio':
                    filename = filename.rsplit(".", 1)[0] + ".mp3"

            return send_file(filename, as_attachment=True)
        except Exception as e:
            return f"An error occurred: {e}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
