import cv2
import mediapipe as mp
import numpy as np
import time

# Input/output paths
input_path = 'testing/deadlift.mp4'
output_path = 'testing/output.mp4'
cap = cv2.VideoCapture(input_path)

# Video writer setup
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# Pose setup
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Tracking variables
down_start_time = None
up_start_time = None
last_duration = None
counter = 0
stage = None


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle


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

            def get(name): return [landmarks[mp_pose.PoseLandmark[name].value].x,
                                   landmarks[mp_pose.PoseLandmark[name].value].y]

            left_shoulder = get("LEFT_SHOULDER")
            left_hip = get("LEFT_HIP")
            left_knee = get("LEFT_KNEE")
            left_ear = get("LEFT_EAR")

            posture_angle = calculate_angle(left_ear, left_shoulder, left_hip)
            angle = calculate_angle(left_shoulder, left_hip, left_knee)

            posture_status = "Good posture" if posture_angle >= 150 else "Fix posture"
            posture_color = (
                0, 255, 0) if posture_angle >= 150 else (0, 0, 255)

            cv2.putText(image, f'Posture: {int(posture_angle)} degrees',
                        tuple(np.multiply(left_shoulder, [
                              frame_width, frame_height - 40]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2, cv2.LINE_AA)
            cv2.putText(image, posture_status,
                        tuple(np.multiply(left_shoulder, [
                              frame_width, frame_height - 10]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2, cv2.LINE_AA)

            cv2.putText(image, str(int(angle)),
                        tuple(np.multiply(
                            left_hip, [frame_width, frame_height]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            if angle < 100:
                if stage != "DOWN":
                    down_start_time = time.time()
                    if up_start_time:
                        last_duration = down_start_time - up_start_time
                stage = "DOWN"
            elif angle > 160:
                if stage == "DOWN":
                    up_start_time = time.time()
                    last_duration = up_start_time - down_start_time
                    counter += 1
                stage = "UP"

        except:
            pass

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

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(
                                      color=(254, 197, 106), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(254, 120, 106), thickness=2, circle_radius=2))

        border_color = (254, 197, 106)
        cv2.rectangle(image, (0, 0), (frame_width,
                      frame_height), border_color, 10)

        try:
            logo = cv2.imread('testing/optimal.jpg')
            if logo is not None:
                logo = cv2.resize(logo, (100, 50))
                y_offset = frame_height - logo.shape[0]
                x_offset = frame_width - logo.shape[1]
                image[y_offset:y_offset + logo.shape[0],
                      x_offset:x_offset + logo.shape[1]] = logo
        except:
            pass

        out.write(image)

    cap.release()
    out.release()
