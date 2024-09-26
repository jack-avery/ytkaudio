build-win:
# build clean
	rm -r dist/*

# build the app for windows
	pyinstaller --specpath build --collect-data sv_ttk --onefile -n ytkaudio --clean --noconsole src/main.pyw

# include latest ffmpeg
	curl -Lo dist/ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip
	unzip -d dist/ffmpeg dist/ffmpeg.zip
	rm dist/ffmpeg.zip
	mv dist/ffmpeg/ffmpeg-master-latest-win64-lgpl/bin/ffmpeg.exe dist/ffmpeg.exe
	rm -r dist/ffmpeg/
