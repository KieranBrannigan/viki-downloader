# viki-downloader
Python selenium scripts for batch downloading subtitles and video files

Link downlaoder:
    Give the url to the viki show. Then click the episodes tab, then click enter to run.
    Will download all the links for the show and export link on each line of txt file.

Will use http://www.lilsubs.com/ to enter the url for each show, and then click "Download" button.
This should open some options. 3 buttons for downloading video, and a selection of buttons to download the subtitles for available languages.
The subs download button will start the download immediately, but the video buttons will move to a new tab where there is a button with href equal to the video file. Maybe we can download straight from the video file, or we can open it and click the download button in there.

When the download is finished it will download the video and subs to the output folder.
Maybe we can improve performance by opening a new tab for each episode. Or perhaps spawn a new process which handles the next link.
For now it will just work with one tab/process.

TODO: maybe we should add the video file links to an outputted file which can then be used as input for downloading the files.