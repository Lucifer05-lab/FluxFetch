from flask import Flask, request, Response, render_template, stream_with_context
import youtube_dl

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('url')
        if not video_url:
            return "Please provide a valid URL", 400

        def generate():
            ydl_opts = {
                'format': 'best',
                'outtmpl': '-',  # Output to stdout (stream)
                'quiet': True,
                'no_warnings': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                filename = ydl.prepare_filename(info_dict)

                # Stream the actual video file
                ydl_opts['outtmpl'] = filename
                ydl_opts['quiet'] = False
                ydl_opts['no_warnings'] = False

                # Download video to file first (for simplicity)
                ydl.download([video_url])

                # Now read the file and yield chunks
                with open(filename, 'rb') as f:
                    chunk = f.read(8192)
                    while chunk:
                        yield chunk
                        chunk = f.read(8192)

        return Response(stream_with_context(generate()), headers={
            'Content-Disposition': 'attachment; filename="downloaded_video.mp4"',
            'Content-Type': 'application/octet-stream'
        })

    return render_template('index.html')
