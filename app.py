
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import glob
import threading

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def cleanup_old_files():
    """Remove files older than 10 minutes to save disk space."""
    import time
    for f in glob.glob(f'{DOWNLOAD_FOLDER}/*'):
        if os.path.isfile(f) and time.time() - os.path.getmtime(f) > 600:
            try:
                os.remove(f)
            except Exception:
                pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url', '').strip()
    site = request.form.get('site', 'youtube')
    format_type = request.form.get('format', 'mp4')

    if not url:
        return "Error: No URL provided.", 400

    # Run cleanup in background
    threading.Thread(target=cleanup_old_files, daemon=True).start()

    try:
        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).60s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            # Best video + audio merged into mp4
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).60s.%(ext)s',
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
            }

        # Instagram cookies workaround (optional — user can add their cookies)
        # Uncomment and add your cookies file path if needed:
        # ydl_opts['cookiefile'] = 'instagram_cookies.txt'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # For mp3, the extension changes after postprocessing
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'

            if not os.path.exists(filename):
                # Try to find the file (title may be sanitized differently)
                candidates = glob.glob(f'{DOWNLOAD_FOLDER}/*')
                candidates.sort(key=os.path.getmtime, reverse=True)
                if candidates:
                    filename = candidates[0]
                else:
                    return "Error: File not found after download.", 500

        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )

    except yt_dlp.utils.DownloadError as e:
        err = str(e)
        if 'Private' in err or 'login' in err.lower():
            return "Error: This content is private or requires login. For Instagram Stories, you need to provide session cookies.", 403
        return f"Download failed: {err}", 500
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
