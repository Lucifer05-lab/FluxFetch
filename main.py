from flask import Flask, request, Response, render_template, stream_with_context
import yt_dlp
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('url')
        if not video_url:
            return "Please provide a valid URL", 400

        format_type = request.form.get('format') or 'video'
        quality = request.form.get('quality') or '720'

        def generate():
            filename = f"downloaded.%(ext)s"
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best',
                'outtmpl': filename,
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                final_file = ydl.prepare_filename(info)

            # Stream file to user
            with open(final_file, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk

            os.remove(final_file)  # delete after sending

        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Disposition': 'attachment; filename="fluxfetch_download.mp4"',
                'Content-Type': 'application/octet-stream'
            }
        )

    return render_template('index.html')
