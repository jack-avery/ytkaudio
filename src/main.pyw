import logging
import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import sv_ttk
import darkdetect
from yt_dlp import YoutubeDL

import config
import logs

VERSION = "0.0.1"


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.title(f"ytkaudio {VERSION}")
        logging.info(f"ytkaudio {VERSION}")

        self.container = ttk.Frame(padding="5px")
        self.container.pack()

        self.convert_mp3 = tk.BooleanVar()
        self.export_option = tk.StringVar()

        # folder browse button
        self.select_folder_button = ttk.Button(
            self.container, text="Select Output Folder", command=self._get_folder
        )
        logging.debug("built select_folder_button")
        self.select_folder_button.grid(row=0, column=0)
        logging.debug("packed select_folder_button")

        # open folder
        self.open_folder_button = ttk.Button(
            self.container, text="Open", command=self._open_folder
        )
        logging.debug("built open_folder_button")
        self.open_folder_button.grid(row=0, column=1)
        logging.debug("packed open_folder_button")

        # second row: misc options
        self.convert_mp3_toggle = ttk.Checkbutton(
            self.container,
            text="Convert to MP3 automatically?",
            variable=self.convert_mp3,
            command=self._toggle_convert_mp3,
        )
        logging.debug("built convert_mp3_toggle")
        self.convert_mp3_toggle.grid(row=1, column=0, sticky="w", columnspan=2)
        logging.debug("packed convert_mp3_toggle")

        # third row: yt-dlp
        self.input = ttk.Entry(self.container)
        logging.debug("built input")
        self.input.grid(
            row=2,
            column=0,
            sticky="nw",
        )
        logging.debug("packed input")

        # download!
        self.go = ttk.Button(
            self.container, text="Go", command=self._download_video, state=tk.DISABLED
        )
        logging.debug("built go")
        self.go.grid(row=2, column=1, sticky="ne")
        logging.debug("packed go")

        # fourth row: open logfile
        self.open_logfile_button = ttk.Button(
            self.container, text="Open log file", command=self._open_logfile
        )
        logging.debug("built open_logfile_button")
        self.open_logfile_button.grid(row=3, column=0, sticky="nw", columnspan=2)
        logging.debug("packed open_logfile_button")

        sv_ttk.set_theme(darkdetect.theme())
        logging.debug("applied theme")

        self._load_config()
        logging.debug("config loaded")

        self.root.columnconfigure(2, weight=2)
        self.root.rowconfigure(2, weight=1)
        self.root.mainloop()

    def _handle_go_state(self):
        """
        Enable or disable `self.go` depending on whether a folder is selected.
        """
        outfolder = self.config.get("ytkaudio", "outfolder")
        if outfolder != "":
            logging.debug(f"outfolder is {outfolder}: activating go")
            self.go.configure(state=tk.ACTIVE)
        else:
            logging.debug("outfolder empty: disabling go")
            self.go.configure(state=tk.DISABLED)

    def _load_config(self):
        """
        Load the user's configuration from file.
        """
        logging.debug("loading config")
        self.config = config.load()

        self.convert_mp3.set(self.config.get("ytkaudio", "mp3ify"))
        self._handle_go_state()

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
        self._handle_go_state()

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

    def _open_logfile(self):
        """
        Open the logfile for viewing
        """
        self._open(logfile)

    def _open_folder(self):
        """
        Open the output folder for listening
        """
        folder = self.config.get("ytkaudio", "outfolder")
        self._open(folder)

    def _toggle_convert_mp3(self):
        self.config.set("ytkaudio", "mp3ify", str(self.convert_mp3.get()))
        config.save(self.config)

    def _get_ydl_opts(self):
        opts = {
            "format": "bestaudio",
            "outtmpl": f"{self.config.get('ytkaudio', 'outfolder')}"
            + "/[%(uploader)s] %(title)s.%(ext)s",
        }
        if self.config.get("ytkaudio", "mp3ify"):
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
            ]
        return opts

    def _download_video(self):
        url = self.input.get()
        logging.info(f"Downloading {url}")

        with YoutubeDL(self._get_ydl_opts()) as ydl:
            error_code = ydl.download(url)

        logging.debug(f"returned {error_code}")


if __name__ == "__main__":
    logfile = logs.setup()
    app = Application()
