#!/usr/bin/env python3

from itertools import groupby
import glob
import os
import re
import sys


def get_transformed_filename(prefix: str, path: str) -> str:
    dirname, basename = os.path.split(path)

    match = re.match(r'GOPR(\d{4})(\..*)', basename)
    if match:
        return os.path.join(dirname, f'{prefix}{int(match[1]):04}_00{match[2]}')

    match = re.match(r'G[PHXL](\d{2})(\d{4})(\..*)', basename)
    if match:
        return os.path.join(dirname, f'{prefix}{int(match[2]):04}_{int(match[1]):02}{match[3]}')

    return path


def try_rename_file(prefix: str, path: str) -> None:
    target_path = get_transformed_filename(prefix, path)

    if target_path != path:
        os.rename(path, target_path)


def rename_gopro_file(prefix: str, path: str) -> None:
    # https://github.com/AMDmi3/gopro-rename/blob/master/gopro-rename
    for entry in os.listdir(path):
        if entry == '.' or entry == '..':
            continue
        elif os.path.isfile(os.path.join(path, entry)):
            try_rename_file(prefix, os.path.join(path, entry))


def create_laps_template_file(path):
    with open(os.path.join(path, "1_race_laps.txt"), "w") as out_file:
        out_file.write("KART ------- \n\n")
    with open(os.path.join(path, "2_race_laps.txt"), "w") as out_file:
        out_file.write("KART ------- \n\n")


def get_prefix_key(text):
    return re.findall(r"\d{4}-\d{2}-\d{2}-(\d{4})_\d{2}.MP4", text)[0]


def sort_race_videos(path):
    race_count = 1
    for group, items in groupby(glob.glob(os.path.join(path, "*.MP4")), key=get_prefix_key):
        tmp_concat_file_filename = os.path.join(path, "tmp_concat_file.txt")
        with open(tmp_concat_file_filename, "w") as tmp_concat_file:
            for item in items:
                tmp_concat_file.write("file " + item + "\n")

        os.system("ffmpeg -loglevel quiet -stats -y -f concat -safe 0 -i {} -c copy {}".format(
            tmp_concat_file_filename,
            os.path.join(path, str(race_count) + "_race_tmp.mp4")
        ))

        race_count += 1
        os.remove(tmp_concat_file_filename)


def cut_race_videos(path):
    race_count = 1
    for filename in glob.glob(os.path.join(path, "*_race_tmp.mp4")):
        start_time = input("\033[96mInput START time for race {}: \033[0m".format(race_count))
        end_time = input("\033[96mInput   END time for race {}: \033[0m".format(race_count))

        os.system("ffmpeg -loglevel quiet -stats -y -i {} -ss {} -to {} -c:v copy {}".format(
            filename,
            start_time if len(start_time) == 5 else "0" + start_time,
            end_time if len(end_time) == 5 else "0" + end_time,
            os.path.join(path, str(race_count) + "_race.mp4")
        ))
        race_count += 1

        try:
            os.remove(filename)
        except:
            pass


def add_frame_count(path):
    race_count = 1

    for filename in glob.glob(os.path.join(path, "*_race.mp4")):
        os.system(
            "ffmpeg -loglevel quiet -stats -y -i {} -vf \"drawtext=fontfile=Arial.ttf: "
            "text='%{{frame_num}}': start_number=1: x=10: y=10: fontcolor=black: "
            "fontsize=20: box=1: boxcolor=white: boxborderw=60\" -preset ultrafast -c:a copy {}".format(
                filename,
                filename.replace("race.mp4", "race_fps.mp4")
            )
        )
        race_count += 1


def main():
    prefix = sys.argv[1]
    path = sys.argv[2]
    create_laps_template_file(path)
    rename_gopro_file(prefix, path)

    sort_race_videos(path)
    cut_race_videos(path)
    add_frame_count(path)


if __name__ == '__main__':
    sys.exit(main())
