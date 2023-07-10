#!/usr/bin/env python3

from itertools import groupby
import cv2
import glob
import os
import pytesseract
import re
import sys
import json
import datetime
from tqdm import tqdm


def read_lap_file(lap_time_filename):
    kart = 0
    lap_times = []

    with open(lap_time_filename, "r") as in_file:
        for line in in_file:
            if line == "\n":
                continue
            if "KART" in line:
                kart = int(line.split("----- ")[1])
                continue
            lap_times.append(int(line.strip().replace(":", "").replace(".", "").split("--")[0]))

    return kart, lap_times


def calculate_frames(snapshot_folder, lap_times, lap_time_filename, kart):
    frames = []
    laps_json = {}
    group_lap_times = []
    all_frame_files = glob.glob(os.path.join(snapshot_folder, "vlcsnap-*.png"))

    for lap_time in lap_times:
        if lap_time <= 47500:
            group_lap_times.append(1)
        else:
            group_lap_times.append(0)

    count_dups = [(value, sum(1 for _ in group)) for value, group in groupby(group_lap_times)]
    for screenshot_filename in tqdm(all_frame_files):
        image = cv2.imread(screenshot_filename, cv2.IMREAD_GRAYSCALE)
        thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        x, y, w, h = 5, 5, 70, 25
        roi = thresh[y:y + h, x:x + w]
        data = pytesseract.image_to_string(roi, config="--psm 8")

        frame = re.sub("[^0-9]", "", data)
        frames.append(frame)

    lap_frames = []
    screenshot_counter = 0
    for group in count_dups:
        if group[0] == 0:
            continue

        for _ in range(0, group[1]):
            lap_frames.append(frames[screenshot_counter:screenshot_counter+15])
            screenshot_counter += 12

        screenshot_counter += 3

    lap_index = 0
    for lap_time in lap_times:
        if lap_time <= 47500:
            lap_name = "{}.{}<br>{}-{}-{}".format(
                str(lap_time)[:2],
                str(lap_time)[2:],
                lap_time_filename.split("/")[4].split("--")[0],
                lap_time_filename.split("/")[5].split("_")[0],
                kart
            )
            if len(lap_frames[lap_index]) == 15:
                laps_json[lap_name] = dict(zip([x for x in range(0, len(lap_frames[lap_index]))], lap_frames[lap_index]))
            lap_index += 1

    with open(os.path.join("/".join(lap_time_filename.split("/")[:-1]), "{}_race_laps.json".format(lap_time_filename.split("/")[-1][0])), "w") as out_file:
        out_file.write(json.dumps(laps_json, indent=4))

    video_lap_time = 0

    with open(lap_time_filename, "w") as out_file:
        out_file.write("KART ------- {}\n\n".format(kart))
        for lap_time in tqdm(lap_times):
            lap_time_seconds_to_min = str(datetime.timedelta(milliseconds=lap_time))[2:-3]
            if video_lap_time != 0:
                video_time_seconds_to_min = str(datetime.timedelta(milliseconds=video_lap_time))[2:-3]
            else:
                video_time_seconds_to_min = "00:00.000"
            out_file.write("{} -- {}\n".format(lap_time_seconds_to_min, video_time_seconds_to_min))

            if lap_time <= 47500:
                lap_name = "{}.{}--{}-{}".format(
                    str(lap_time)[:2],
                    str(lap_time)[2:],
                    lap_time_filename.split("/")[4].split("--")[0],
                    lap_time_filename.split("/")[5].split("_")[0]
                )

                os.system("ffmpeg -loglevel quiet -stats -y -i {} -ss {} -to {} -c:v copy '/{}' >/dev/null".format(
                    os.path.join("/".join(lap_time_filename.split("/")[:-1]), lap_time_filename.split("/")[5].split("_")[0] + "_race.mp4"),
                    str(datetime.timedelta(milliseconds=video_lap_time - 3000))[:-3].split(".")[0],
                    str(datetime.timedelta(milliseconds=video_lap_time + lap_time + 3000))[:-3].split(".")[0],
                    os.path.join("/".join(lap_time_filename.split("/")[:-2]), "Best laps", lap_name + ".mp4")
                ))
            video_lap_time += lap_time


def main():
    snapshot_folder = sys.argv[1]
    lap_time_filename = sys.argv[2]
    kart, lap_times = read_lap_file(lap_time_filename)
    calculate_frames(snapshot_folder, lap_times, lap_time_filename, kart)


if __name__ == '__main__':
    main()
