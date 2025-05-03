import cv2
import mediapipe as mp
import numpy as np
import time

# Load input video
input_path = 'testing/benchpress_video.mp4'
cap = cv2.VideoCapture(input_path)

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Define VideoWriter for output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('testing/output.mp4', fourcc,
                      fps, (frame_width, frame_height))

# Mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

counter = 0
stage = None
down_start_time = None
up_start_time = None
last_duration = None


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle > 180.0 else angle


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
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            foot_angle = calculate_angle(l_hip, l_knee, l_ankle)

            cv2.putText(image, str(int(angle)),
                        tuple(np.multiply(
                            l_elbow, [frame_width, frame_height]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            if angle < 90:
                if stage != "DOWN":
                    down_start_time = time.time()
                    if up_start_time:
                        last_duration = down_start_time - up_start_time
                        print(f"UP to DOWN duration: {last_duration:.2f} s")
                stage = "DOWN"

            elif angle > 160:
                if stage == "DOWN":
                    up_start_time = time.time()
                    last_duration = up_start_time - down_start_time
                    print(f"DOWN to UP duration: {last_duration:.2f} s")
                    counter += 1
                stage = "UP"

            if foot_angle <= 90:
                foot_status, foot_color = "Great feet position", (0, 255, 0)
            elif foot_angle <= 120:
                foot_status, foot_color = "Good feet position", (255, 255, 0)
            else:
                foot_status, foot_color = "Fix Foot Placement", (0, 0, 255)

            cv2.putText(image, f'Foot: {int(foot_angle)}°',
                        tuple(np.multiply(
                            l_knee, [frame_width, frame_height - 40]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, foot_color, 2)
            cv2.putText(image, foot_status,
                        tuple(np.multiply(
                            l_ankle, [frame_width, frame_height - 10]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, foot_color, 2)

        except:
            pass

        # Status panel
        cv2.rectangle(image, (0, 0), (225, 120), (254, 197, 106), -1)
        cv2.putText(image, 'Reps:', (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        cv2.putText(image, str(counter), (120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, 'Stage:', (15, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        cv2.putText(image, stage if stage else "-", (120, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(image, 'Time:', (15, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        if last_duration is not None:
            cv2.putText(image, f'{last_duration:.2f}s', (120, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Pose landmarks and borders
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(254, 197, 106),
                                   thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(254, 120, 106), thickness=2, circle_radius=2))
        cv2.rectangle(image, (0, 0), (frame_width, frame_height),
                      (254, 197, 106), 10)

        # Logo overlay (optional)
        logo = cv2.imread('testing/optimal.jpg')
        if logo is not None:
            logo = cv2.resize(logo, (100, 50))
            image[-logo.shape[0]:, -logo.shape[1]:] = logo

        # Write to output video
        out.write(image)

cap.release()
out.release()
cv2.destroyAllWindows()
