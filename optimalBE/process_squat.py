import cv2
import mediapipe as mp
import numpy as np
import time
import os
import gridfs
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.optimalDB
fs = gridfs.GridFS(db)


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360 - angle if angle > 180 else angle


def process_squat(video_id):
    video_file = fs.get(ObjectId(video_id))
    input_path = 'temp_video.mp4'
    output_path = 'optimalBE/output.mp4'

    with open(input_path, 'wb') as f:
        f.write(video_file.read())

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    counter = 0
    stage = None
    down_start_time = None
    up_start_time = None
    last_duration = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                left_ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]

                posture_angle = calculate_angle(
                    left_ear, left_shoulder, left_hip)
                angle = calculate_angle(left_hip, left_knee, left_ankle)

                posture_status = "Good posture" if posture_angle >= 150 else "Fix posture"
                posture_color = (
                    0, 255, 0) if posture_angle >= 150 else (0, 0, 255)

                cv2.putText(image, f'Posture: {int(posture_angle)} deg',
                            tuple(np.multiply(left_shoulder, [
                                  width, height - 40]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2)

                cv2.putText(image, posture_status,
                            tuple(np.multiply(
                                left_hip, [width, height - 10]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2)

                # Counter logic
                if angle < 30:
                    depth_status = "Great Depth, ATG"
                    depth_color = (0, 255, 0)
                elif angle < 60:
                    if stage != "DOWN":
                        down_start_time = time.time()
                        if up_start_time:
                            last_duration = down_start_time - up_start_time
                    stage = "DOWN"
                    depth_status = "Good Depth, Parallel"
                    depth_color = (255, 255, 0)
                elif angle > 150:
                    if stage == "DOWN":
                        up_start_time = time.time()
                        last_duration = up_start_time - down_start_time
                        counter += 1
                    stage = "UP"

                cv2.putText(image, depth_status, (300, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, depth_color, 2)

            except:
                pass

            # HUD
            cv2.rectangle(image, (0, 0), (225, 120), (254, 197, 106), -1)
            cv2.putText(image, 'Reps:', (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
            cv2.putText(image, str(counter), (120, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.putText(image, 'Stage:', (15, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
            cv2.putText(image, str(stage) if stage else "-", (120, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.putText(image, 'Time:', (15, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
            if last_duration is not None:
                cv2.putText(image, f'{last_duration:.2f}s', (120, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Landmarks + border
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=(254, 197, 106), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(254, 120, 106), thickness=2, circle_radius=2))

            cv2.rectangle(image, (0, 0), (width, height), (254, 197, 106), 10)
            out.write(image)

    cap.release()
    out.release()
    os.remove(input_path)
