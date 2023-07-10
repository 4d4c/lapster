import cv2
import json
import glob


# videos = [
# ]

# for v in videos:
#     video = cv2.VideoCapture(v)
#     success, image = video.read()
#     count = 0
#     while success:
#         if count == 100:
#             cv2.imwrite("laps_images/{}-{}-{}.jpg".format(0, "-".join(v.split("/")[-2:]), count), image)
#             print("[+] Created image")
#             break
#         success,image = video.read()
#         count += 1


with open("laps.json", "r") as laps_file:
    laps_data = json.load(laps_file)

video_sector_frames_data = {}

for lap_name, lap_time in laps_data["laps"].items():
    for point_name, point_time in lap_time.items():
        date = lap_name.split("<br>")[1][:-2] + "*"
        race = lap_name[-1:]
        frame = int(point_time)
        video_filename = glob.glob("../{}*".format(date))[0] + "/{}_race_fps.mp4".format(race)

        x = 0
        if "../46.497/2_race_fps.mp4" in video_filename:
            x = 16
        if "../46.497/1_race_fps.mp4" in video_filename:
            x = 12
        if "../46.552/2_race_fps.mp4" in video_filename:
            x = 31
        if "../46.396/1_race_fps.mp4" in video_filename:
            x = 14
        if "../45.826/1_race_fps.mp4" in video_filename:
            x = 16
        if "../45.826/2_race_fps.mp4" in video_filename:
            x = 13

        if video_filename not in video_sector_frames_data:
            video_sector_frames_data[video_filename] = {}
            video_sector_frames_data[video_filename][point_name] = [frame + x]
        elif point_name not in video_sector_frames_data[video_filename]:
            video_sector_frames_data[video_filename][point_name] = [frame + x]
        else:
            video_sector_frames_data[video_filename][point_name].append(frame + x)


for video_filename, video_sector_frames in video_sector_frames_data.items():
    print(video_filename)
    print(video_sector_frames)

    video = cv2.VideoCapture(video_filename)
    success, image = video.read()
    count = 0
    while success:
        for sector, frames in video_sector_frames.items():
            if count in frames:
                cv2.imwrite("laps_images/{}-{}-{}.jpg".format(sector, "-".join(video_filename.split("/")[-2:]), count), image)
                print("[+] Image created")
        success,image = video.read()
        count += 1
