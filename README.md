# ytkaudio
basic python3 tk interface for downloading audio from YouTube, with a best attempt at being cross-platform.

![image](https://github.com/user-attachments/assets/962dde28-6a40-4a3a-a548-dcaff6d886ae)

## requirements
1. [ffmpeg](https://www.ffmpeg.org/download.html)<br>
> windows users: download [this](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip), and shove it in a folder exposed to PATH. [(?)](https://stackoverflow.com/questions/9546324/adding-a-directory-to-the-path-environment-variable-in-windows)
2. [python](https://www.python.org/downloads/)<br>
> dependencies managed with [poetry](https://python-poetry.org/): `poetry install`<br>
> windows users: try `python3 -m pip install poetry && poetry install`

## usage
> windows users: you can start it with `python3 src/main.pyw`
1. select a folder for `ytkaudio` to dump audio files into.
2. copy the YouTube URL into the text field.
3. click `Go`.

## attributions
* [darkdetect](https://github.com/albertosottile/darkdetect)
* [ffmpeg](https://www.ffmpeg.org/)
* [platformdirs](https://github.com/tox-dev/platformdirs)
* [sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## bug reports
did something break? please [create an issue](https://github.com/jack-avery/ytkaudio/issues) so i can take a look.
