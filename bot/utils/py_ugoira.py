#!/bin/usr/env python

'''
Code sourced from https://github.com/altbdoor/py-ugoira by altbdoor
Many thanks, and I'm so sorry to what I did to this code.
I swear, it was pretty when I got it.
'''

import logging
import os
import shlex
import subprocess
import sys
import urllib.request
from argparse import ArgumentParser
from tempfile import gettempdir
from zipfile import ZipFile

from pixivpy_async import AppPixivAPI
from pixivpy_async.utils import JsonDict

logger = logging.getLogger("py_ugoira")

async def get_ugoira_frames(pixiv_id, output_path, api:AppPixivAPI, verbose=False):
    base_pixiv_url = f'https://app-api.pixiv.net/'
    meta_pixiv_url = f'https://www.pixiv.net/ajax/illust/{pixiv_id}/ugoira_meta'
    user_agent = 'PixivAndroidApp/5.0.234 (Android 11; Pixel 5)'

    data:JsonDict = await api.ugoira_metadata(pixiv_id)
    logger.debug(data)
    zipdata_url = data.ugoira_metadata.zip_urls.medium

    zipdata = urllib.request.Request(zipdata_url)
    zipdata.add_header('Referer', base_pixiv_url)
    zipdata.add_header('User-Agent', user_agent)

    ugoira_zipfile = os.path.join(gettempdir(), f'ugoira_{pixiv_id}.zip')
    chunk_size = 4 * 1024

    with urllib.request.urlopen(zipdata) as res, open(ugoira_zipfile, 'wb') as out_file:
        while True:
            chunk = res.read(chunk_size)
            if chunk:
                out_file.write(chunk)
            else:
                break

    verbose_print(verbose, 'Extracting ugoira zip file')
    with ZipFile(ugoira_zipfile, 'r') as zip_ref:
        zip_ref.extractall(output_path)

    verbose_print(verbose, 'Deleting ugoira zip file')
    os.remove(ugoira_zipfile)

    verbose_print(verbose, 'Creating FFmpeg concat demuxer file')

    # https://superuser.com/questions/617392/ffmpeg-image-sequence-with-various-durations
    ffconcat_file = os.path.join(output_path, 'ffconcat.txt')
    with open(ffconcat_file, 'w') as out_file:
        out_file.write('ffconcat version 1.0\n\n')

        # https://video.stackexchange.com/questions/20588/ffmpeg-flash-frames-last-still-image-in-concat-sequence
        ugoira_frames = data.ugoira_metadata.frames.copy()
        last_frame = ugoira_frames[-1].copy()
        last_frame['delay'] = 1
        ugoira_frames.append(last_frame)

        for frame in ugoira_frames:
            frame_file = frame['file']
            frame_duration = frame['delay'] / 1000
            frame_duration = round(frame_duration, 4)

            out_file.write(
                f'file {frame_file}\n'
                f'duration {frame_duration}\n\n'
            )

    is_process_success = True
    verbose_print(verbose, 'Get ugoira frames done')

    return True


def convert_ugoira_frames(frames_path, video_output, ffmpeg_path, ffmpeg_args, interpolate=False, verbose=False):
    interpolate_arg = '-filter:v "minterpolate=\'fps=60\'"'
    if not interpolate:
        interpolate_arg = ''

    call_str = (
        f'"{ffmpeg_path}" -hide_banner -y '
        '-i ffconcat.txt '
        f'{interpolate_arg} '
        f'{ffmpeg_args} '
        f'"{video_output}" '
    )
    call_stack = shlex.split(call_str)

    verbose_print(verbose, f'Running FFmpeg with argument: \n{call_str}')

    subprocess.call(
        call_stack,
        cwd=os.path.abspath(frames_path),
        #shell=True
    )

    verbose_print(verbose, 'Convert ugoira frames done')


def verbose_print(verbose, message):
    if verbose:
        print(message)


def parse_args():
    parser = ArgumentParser(
        description=(
            'Python script to download and convert an ugoira animation on '
            'Pixiv, and convert it to a video via FFmpeg.'
        )
    )
    parser.add_argument(
        '--pixiv_id', type=int, required=False,
        help=(
            'The pixiv ID for the ugoira illustration. Required if the '
            '--process argument is "all" or "getframes".'
        ),
    )
    parser.add_argument(
        '--frames_path', type=str, required=False,
        help=(
            'The path to where the image frames and ffconcat.txt is. Required '
            'if the --process argument is "convertframes".'
        ),
    )

    process_choices = ('all', 'getframes', 'convertframes', )
    parser.add_argument(
        '--process', type=str, required=False, default='all',
        choices=process_choices,
        help=(
            'The process that should take place. "all" will execute both '
            '"getframes" and "convertframes". "getframes" will only obtain the '
            'ugoira frames, and generate a FFmpeg concat demuxer file. '
            '"convertframes" will only convert the ugoira frames into a video '
            'type of your choice through FFmpeg.'
        ),
    )

    parser.add_argument(
        '--video_output', type=str, required=False, default='output.webm',
        help=(
            'The output filename for the converted video. Defaults to '
            '"output.webm".'
        ),
    )
    parser.add_argument(
        '--interpolate', action='store_true',
        help=(
            'Attempts to interpolate the frames to 60 frames per second. Note, '
            'it only works well with some ugoira, and would take a longer time '
            'to finish conversion. Use with care.'
        ),
    )
    parser.add_argument(
        '--ffmpeg_path', type=str, required=False, default='ffmpeg',
        help='The path to the FFmpeg executable.',
    )
    parser.add_argument(
        '--ffmpeg_args', type=str, required=False,
        default='-c:v libvpx -crf 10 -b:v 2M -an',
        help=(
            'The arguments for FFmpeg. Defaults to '
            '"-c:v libvpx -crf 10 -b:v 2M -an", which is VP8 WEBM with a '
            'variable bitrate of 2 MBit/s, with no audio.'
        ),
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Forces the system to print out verbose process messages.',
    )

    args = parser.parse_args()
    msg_required = 'the following arguments are required:'

    if args.process in ('all', 'getframes', ) and not args.pixiv_id:
        parser.error(f'{msg_required} --pixiv_id')

    if args.process == 'convertframes' and not args.frames_path:
        parser.error(f'{msg_required} --frames_path')

    return args


if __name__ == '__main__':
    args = parse_args()

    exec_path = os.path.dirname(sys.argv[0])
    ugoira_path = None

    if args.process in ('all', 'getframes', ):
        ugoira_path = os.path.join(exec_path, f'ugoira_{args.pixiv_id}')
        is_success = get_ugoira_frames(
            args.pixiv_id,
            ugoira_path,
            None,
            args.verbose,
        )

        if not is_success:
            print(f'Unable to get ugoira data for ID {args.pixiv_id}')
            #sys.exit(1)

    if args.process in ('all', 'convertframes', ):
        if ugoira_path is None:
            ugoira_path = args.frames_path

        convert_ugoira_frames(
            ugoira_path,
            args.video_output,
            args.ffmpeg_path,
            args.ffmpeg_args,
            args.interpolate,
            args.verbose,
        )
