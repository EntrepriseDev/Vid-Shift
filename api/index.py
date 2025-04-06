from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid

app = Flask(
    __name__,
    template_folder=os.path.join(current_dir, '../templates'),
    static_folder=os.path.join(current_dir, '../static')
)

# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Get video info
@app.route('/info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL manquante'}), 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = [
                {
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution') or f.get('height', ''),
                    'format_note': f.get('format_note', ''),
                    'filesize': f.get('filesize') or 0
                }
                for f in info.get('formats', [])
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none'
            ]

            return jsonify({
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'duration': info['duration'],
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Download video
@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')

    if not url or not format_id:
        return jsonify({'error': 'URL ou format_id manquant'}), 400

    filename = f"video_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join('downloads', filename)

    os.makedirs('downloads', exist_ok=True)

    try:
        with yt_dlp.YoutubeDL({'format': format_id, 'outtmpl': output_path}) as ydl:
            ydl.download([url])

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
