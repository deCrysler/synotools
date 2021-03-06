#!/usr/bin/python
'''
Author : Julien MOTTIN
License : GNU GPL3
Use : 
    Convert videos to h264 / AAC with same quality

Dependencies : ffmpeg modern build, with many codecs...
version : 0.1
'''
import sys
import os
import argparse

from videoutils import *

def h264Encode(input,loglevel,delete_source,suffix="-h264.mp4"):
    inDic = getFFProbeDic(input)
    inDir,inName = os.path.split(input)
    inBase,inExt = os.path.splitext(inName)
    if len(inDic['streams'])>2:
        print yellow + "Warning : input file has more than 2 streams" + nc

    # Grab first video stream & first audio stream
    videoStream = None
    for stream in inDic['streams']:
        if stream['codec_type'] == 'video':
            videoStream = stream
            break    
    audioStream = None
    for stream in inDic['streams']:
        if stream['codec_type'] == 'audio':
            audioStream = stream
            break

    if videoStream is not None and audioStream is not None:

        # First check if transcode required
        if videoStream['codec_name']=='h264' and audioStream['codec_name']=='aac':
            print "INPUT already in h264 / aac not doing anything"

        else:
            # Build output path
            outFileName = inBase + suffix
            outFilePath = os.path.join(inDir,outFileName)
            targetAudBR = min(int(audioStream['bit_rate']),128000)
            audOpt = "-c:a libfaac -b:a %d -ac 2 -ar 48000" % targetAudBR
            inArgs = "-y -loglevel %s -i '%s'" % (loglevel,input)

            # If only audio transcode needed
            if videoStream['codec_name']=='h264':
                vidOpt = "-c:v copy"
                os.system("ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " '" + outFilePath + "'")

            # Video transcoding needed, re-encode whole video
            else:
                targetVidBR = min(int(videoStream['bit_rate']),youtubeVideoBitrate(videoStream['height']))
                vidOpt = "-f mp4 -c:v libx264 -preset fast -b:v " + str(targetVidBR)
                os.system("ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " -pass 1 /dev/null && ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " -pass 2 '" + outFilePath + "'")
                cleanFFMpeg2PassFiles()
                
            if os.path.isfile(outFilePath):
                print outFilePath + " created"
                if delete_source:
                    os.remove(input)
            else:
                print red + "ERROR while creating " + outFilePath + nc


    else:
        print red + "Fail to locate suitable streams in input file" + nc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert video to h264 / aac for compatible use with chromecast')
    parser.add_argument("INPUT",help="INPUT is the source video file to convert")
    parser.add_argument("-l","--loglevel",help="Specify ffmpeg loglevel from quiet|panic|fatal|error|warning|info|verbose")
    parser.add_argument("-d","--delete-source",action="store_true",help="remove INPUT after successful transcode")
    args = vars(parser.parse_args())
    
    if args['loglevel'] is None:
        args['loglevel'] = 'error'

    h264Encode(args['INPUT'], args['loglevel'], args['delete_source'])
