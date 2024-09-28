import logging
import os
import platform
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import darkdetect
import ffmpeg
import sv_ttk
from yt_dlp import YoutubeDL

import config
import logs

VERSION = "0.1.0"


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.title(f"ytkaudio {VERSION}")
        logging.info(f"ytkaudio {VERSION}")

        self.container = ttk.Frame(padding="3px")
        self.container.pack()

        self.dropdown_selection = tk.StringVar()
        self.dropdown_options = ["Open log file"]

        self.url = tk.StringVar()
        self.export_option = tk.StringVar()

        self.url.trace_add("write", self._handle_url_change)

        ##
        # TOP ROW -- Folder stuff and dropdown for additional options
        ##
        self.row1 = ttk.Frame(self.container, padding="2px")
        self.row1.pack()

        # folder browse button
        self.select_folder_button = ttk.Button(
            self.row1, text="Select Output Folder", command=self._get_folder
        )
        logging.debug("built select_folder_button")
        self.select_folder_button.pack(side="left", padx="1px")
        logging.debug("packed select_folder_button")

        # open folder
        self.open_folder_button = ttk.Button(
            self.row1,
            text="Open Output Folder",
            command=lambda: self._open(self.config.get("ytkaudio", "outfolder")),
        )
        logging.debug("built open_folder_button")
        self.open_folder_button.pack(side="left", padx="1px")
        logging.debug("packed open_folder_button")

        # dropdown menu
        self.dropdown_menu = ttk.OptionMenu(
            self.row1,
            self.dropdown_selection,
            "... ",
            *self.dropdown_options,
            command=self._handle_dropdown_selection,
        )
        logging.debug("built dropdown menu")
        self.dropdown_menu.pack(side="left", padx="1px")
        logging.debug("packed dropdown menu")

        ##
        # MIDDLE ROW -- Input
        ##
        self.row2 = ttk.Frame(self.container, padding="2px")
        self.row2.pack(fill="x")

        self.input = ttk.Entry(self.row2, textvariable=self.url)
        logging.debug("built input")
        self.input.pack(side="top", fill="x")
        logging.debug("packed input")

        ##
        # BOTTOM ROW -- Export option and GO!
        # done in _handle_url_change
        ##
        self.row3 = None

        sv_ttk.set_theme(darkdetect.theme())
        logging.debug("applied theme")

        self.config = config.load()
        logging.debug("config loaded")

        self.root.mainloop()

    def _open(self, item):
        """
        Open a file/folder using the system default application
        """
        logging.debug(f"_open on {item}")
        if platform.system() == "Windows":
            os.startfile(item)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", item])
        else:
            subprocess.Popen(["xdg-open", item])

    def _handle_dropdown_selection(self, selection):
        """
        Handle the user's dropdown selection.
        """
        match selection:
            case "Open log file":
                self._open(logfile)

        self.dropdown_selection.set("... ")

    def _get_folder(self):
        """
        Ask the user for the folder to download files to.
        """
        logging.debug("asking user for folder...")
        folder = filedialog.askdirectory()
        logging.debug(f"user supplied {folder}")

        if folder == "":
            logging.debug("no folder supplied: doing nothing")
            return

        self.config.set("ytkaudio", "outfolder", folder)
        config.save(self.config)

    def _handle_url_change(self, t, e, x):
        url = self.url.get()

        if "youtu.be" not in url and "youtube.com" not in url:
            return

        with YoutubeDL() as ydl:
            meta = ydl.extract_info(url, download=False)

        self.title = f"[{meta['uploader']}] {meta['title']}"

        # There has to be a better way to do this... right???
        formats_with_duplicates = [
            {
                "resolution": f["resolution"],
                "fps": int(f["fps"]),
                "id": f["format_id"],
                "has_audio": f["acodec"] != "none",
                "audio_ext": f["audio_ext"],
            }
            for f in meta["formats"]
            if f["vcodec"] != "none" and f["ext"] == "mp4"
        ]
        self.formats = {
            f"{f['resolution']} @ {f['fps']}fps": {
                "resolution": f["resolution"],
                "fps": f["fps"],
                "id": f["id"],
                "has_audio": f["has_audio"],
                "audio_ext": f["audio_ext"],
            }
            for f in formats_with_duplicates
        }
        self.formats["Audio Only"] = {"id": "bestaudio", "has_audio": True}
        self.formats["Audio Only (MP3)"] = {"id": "bestaudio", "has_audio": True}

        if isinstance(self.row3, ttk.Frame):
            self.row3.destroy()

        self.row3 = ttk.Frame(self.container, padding="2px")

        self.export_dropdown = ttk.OptionMenu(
            self.row3,
            self.export_option,
            "Choose export type...",
            *self.formats.keys(),
            command=lambda _: self.go.configure(state=tk.ACTIVE),
        )
        logging.debug("built export dropdown")
        self.export_dropdown.pack(side="left")
        logging.debug("packed export dropdown")

        self.go = ttk.Button(
            self.row3, text="Go", command=self._download, state=tk.DISABLED
        )
        logging.debug("built go")
        self.go.pack(side="right")
        logging.debug("packed go")

        self.row3.pack(fill="x")

    def ydl_download(self, opts, url):
        logging.info(f"Downloading {url}...")
        with YoutubeDL(opts) as ydl:
            error_code = ydl.download(url)
        logging.debug(f"returned {error_code}")
        return error_code

    def _download(self):
        selected_format = self.export_option.get()
        format = self.formats[selected_format]

        base = f"{self.config.get('ytkaudio', 'outfolder')}/{self.title}"

        opts = {
            "format": format["id"],
            "outtmpl": base + ".%(ext)s",
        }
        if selected_format == "Audio Only (MP3)":
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
            ]

        url = self.input.get()
        self.ydl_download(opts, url)

        if format != "bestaudio" and not format["has_audio"]:
            # also download audio and conjoin with ffmpeg
            # assuming at this point that the downloaded video is an .mp4
            opts = {
                "format": "bestaudio",
                "outtmpl": base + f".{format['audio_ext']}",
            }
            self.ydl_download(opts, url)

            video = ffmpeg.input(f"{base}.mp4")
            audio = ffmpeg.input(f"{base}.{format['audio_ext']}")

            ffmpeg.concat(video, audio, v=1, a=1).output(
                f"{base}-with_audio.mp4"
            ).overwrite_output().run()

            os.remove(f"{base}.{format['audio_ext']}")
            shutil.move(f"{base}-with_audio.mp4", f"{base}.mp4")


if __name__ == "__main__":
    logfile = logs.setup()
    app = Application()
