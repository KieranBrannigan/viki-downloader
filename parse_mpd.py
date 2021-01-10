import argparse
import os
from typing import List
import xml.etree.ElementTree as ET
from subprocess import PIPE, Popen

import requests

def getURL(mpd_file, baseURLs: List[str], quality: str, audio_or_video):

    if audio_or_video == "audio":
        track = "track2"
    elif audio_or_video == "video":
        track = "track1"
    else:
        raise ValueError("audio_or_video should be \"audio\" or \"video\"")

    URLs = [line for line in baseURLs if quality in line and track in line]

    if len(URLs) == 0:
        print(f"Couldn't find that quality version ({quality}) in mpd file: {mpd_file}")
        if takeLowerQuality:
            print("Trying to find with a lower quality")
            nextLower = qualities.index(quality) - 1
            if nextLower < 0:
                # ran out of qualities to try
                print(f"Couldn't find with quality {quality}. This is the lowest quality we can try. Skipping this file.")
                return (None, None)
            else:
                return getURL(mpd_file, baseURLs, qualities[nextLower], audio_or_video)
    else:
        return URLs[0]

def parse_mpd(mpd_file:str, video_quality:str, audio_quality: str):
    """
    mpd_file: full path to the mpd file I.E. -> inputFolder/filename.mpd
    video_quality: string representing one of the qualities specified in qualities list. E.G -> "480p"
    audio_quality: same as video_quality

    """

    print(f"parsing {mpd_file}...")
    with open(mpd_file, 'r') as ReadFile:
        lines = ReadFile.readlines()

    
    baseURLs = [line.strip()[9:-10] for line in lines if "BaseURL" in line]

    audURL = getURL(mpd_file, baseURLs, audio_quality, "audio")
    vidURL = getURL(mpd_file, baseURLs, video_quality, "video")
    
    return vidURL, audURL



def download_file(url, output_file_name):
    print(f"downloading {url} to file {output_file_name}")
    resp = requests.get(url)
    with open(output_file_name, 'wb') as Out:
        Out.write(resp.content)

parser = argparse.ArgumentParser(description='Output vid/audio links from mpd file.')
parser.add_argument('-i', '--input-folder', metavar='N', dest="input_folder", type=str,
                    help='mpd file to be parsed.')
parser.add_argument('-v', '--video-quality', dest='video_quality', default="360p", type=str,
                    help='''video quality: Choose from ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "highest"]
                    (might not be available, 240p, 360p, 480p are usually available)''')
parser.add_argument('-a', '--audio-quality', dest='audio_quality', default="360p", type=str,
                    help='''audio quality: Choose from ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "highest"]
                    (might not be available, 240p, 360p, 480p are usually available)''')
parser.add_argument('-t', '--take-lower-quality', dest='takeLowerQuality', default=True, action="store_true",
                    help='If the desired quality is not available, take the next available quality below the specified quality.')

args = parser.parse_args()
video_quality = args.video_quality
audio_quality = args.audio_quality
input_folder = args.input_folder
takeLowerQuality = args.takeLowerQuality
# ordered list of qualities from lowest to highest
qualities = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
if video_quality.lower() == "highest":
    video_quality = qualities[-1]
if audio_quality.lower() == "highest":
    audio_quality = qualities[-1]

vidPath: str = ""
audPath: str = ""
p = None
for f in filter(lambda x: x.endswith(".mpd"), os.listdir(input_folder)):
    fullpath = os.path.join(input_folder, f)
    vidUrl, audUrl = parse_mpd(fullpath, video_quality, audio_quality)
    if not vidUrl:
        print(f"Could not find video url for mpd file: {f}")
    vidPath = os.path.join("output", "Video_output.mp4")
    audPath = os.path.join("output", "Audio_output.mp4")
    download_file(vidUrl, vidPath)
    download_file(audUrl, audPath)
    output_file = os.path.join("output",f"{os.path.splitext(f)[0]}.mp4")
    args = [
        "ffmpeg"
        , "-i"
        , vidPath
        , "-i"
        , audPath
        , "-acodec"
        , "copy"
        , "-vcodec"
        , "copy"
        , output_file
    ]
    print(f"stitching audio to video with ffmpeg and outputting to {output_file}")
    p = Popen(args, stdout=PIPE, stderr=PIPE)

if p:
    output, err = p.communicate()
    p_status = p.wait()
else:
    quit()

if os.path.isfile(vidPath):
    os.remove(vidPath)
if os.path.isfile(audPath):
    os.remove(audPath)

    
### Adding audio
### ffmpeg -i Video_output.mp4 -i Audio_output.mp4 -acodec copy -vcodec copy PrintCDs1.mp4