import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# === VIDEO FEED from MP4 ===
video_path = 'testing\IMG_7861.mp4'  # <-- Update if needed
cap = cv2.VideoCapture(video_path)

# Get video dimensions and FPS for saving
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# === OUTPUT VIDEO WRITER ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID' for .avi
out = cv2.VideoWriter('squat_output.mp4', fourcc, fps, (width, height))

# Counter variables
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
            print("Finished video or failed to read frame.")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            angle = calculate_angle(left_hip, left_knee, left_ankle)

            # Display the angle
            cv2.putText(image, str(int(angle)),
                        tuple(np.multiply(
                            left_knee, [width, height]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Counter logic
            if angle < 60:
                stage = "down"
            if angle > 150 and stage == 'down':
                stage = "up"
                counter += 1
                print(f"Rep Count: {counter}")

        except:
            pass

        # Draw rep counter box
        cv2.rectangle(image, (0, 0), (225, 80), (254, 197, 106), -1)
        cv2.putText(image, 'Reps:', (15, 30), cv2.FONT_ITALIC,
                    1, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (120, 30), cv2.FONT_ITALIC,
                    1, (255, 255, 255), 2, cv2.LINE_AA)

        # Draw stage
        cv2.putText(image, 'Stage:', (15, 70), cv2.FONT_ITALIC,
                    1, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage if stage else '-', (120, 70),
                    cv2.FONT_ITALIC, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Draw pose
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(254, 197, 106),
                                   thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(254, 120, 106),
                                   thickness=2, circle_radius=2)
        )

        cv2.imshow('Mediapipe Feed', image)
        out.write(image)  # Write processed frame to output

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
out.release()
cv2.destroyAllWindows()
