import cv2
import mediapipe as mp
import numpy as np

# Initialize mediapipe drawing and pose utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Load video file instead of webcam
# Replace with your MP4 file path
video_path = 'testing\WIN_20250413_23_11_27_Pro.mp4'
cap = cv2.VideoCapture(video_path)

# Set up VideoWriter to save the output (optional)
output_path = 'output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 30, (640, 480)
                      )  # Adjust FPS if needed

# Counter variables
counter = 0
stage = None


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


# Start processing the video
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video or can't read the frame.")
            break

        frame = cv2.resize(frame, (640, 480))  # Resize for consistency

        # Convert the image color space
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        # Convert back to BGR for OpenCV
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Visualize angle
            cv2.putText(image, str(int(angle)),
                        tuple(np.multiply(elbow, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Counter logic
            if angle > 160:
                stage = "down"
            if angle < 30 and stage == 'down':
                stage = "up"
                counter += 1
                print(counter)

        except:
            pass

        # Render info box
        cv2.rectangle(image, (0, 0), (225, 80), (254, 197, 106), -1)

        # Repetition count
        cv2.putText(image, 'Reps:', (15, 30), cv2.FONT_ITALIC, 1,
                    (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (120, 30), cv2.FONT_ITALIC, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)

        # Stage info
        cv2.putText(image, 'Stage:', (15, 70), cv2.FONT_ITALIC, 1,
                    (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage if stage else '-', (120, 70), cv2.FONT_ITALIC, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)

        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(254, 197, 106),
                                   thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(254, 120, 106),
                                   thickness=2, circle_radius=2)
        )

        # Display frame
        cv2.imshow('Mediapipe Feed', image)

        # Save frame to output file (optional)
        out.write(image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release everything
    cap.release()
    out.release()
    cv2.destroyAllWindows()
