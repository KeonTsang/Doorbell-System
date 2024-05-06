from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Serve static files from the 'videos' directory
@app.route('/static/<path:filename>')
def serve_video(filename):
    return send_from_directory('statuc', filename)

# Home route displays the list of videos
@app.route('/')
def index():
    # Get the list of video filenames in the 'videos' directory
    video_files = os.listdir('static')
    return render_template('index.html', video_files=video_files)

if __name__ == "__main__":
    app.run(debug=True)
