import cv2
import mediapipe as mp
import numpy as np
import time

down_start_time = None  # Concentric start time
up_start_time = None  # Eccentric start time
last_duration = None


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose  # represents mediapipes pose
# VIDEO FEED
cap = cv2.VideoCapture(0)  # 0 represents webcam

# counter variables
counter = 0  # tally up and down
stage = None  # to determine up or down


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle


# media pipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()  # ret is return frame is the image

        # detection
        # reorder color arrays so media pipe can understand
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # recoloring
        image.flags.writeable = False  # recoloring

        # makes detections
        results = pose.process(image)
        image.flags.writeable = True
        # reorder again so it returns to BGR so opencv can read it
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            # Calculate angle
            angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            feet_placement_angle = calculate_angle(
                left_hip, left_knee, left_ankle)

            # Visualize angle
            cv2.putText(image, str(angle),
                        tuple(np.multiply(left_elbow, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,
                                                        255, 255), 2, cv2.LINE_AA
                        )

            # counter logic
            if angle < 90:  # DOWN position
                if stage != "DOWN":
                    down_start_time = time.time()
                    if up_start_time:  # Previously UP
                        up_to_down_duration = down_start_time - up_start_time
                        last_duration = up_to_down_duration  # store for display
                        print(
                            f"UP to DOWN duration: {last_duration:.2f} seconds")
                stage = "DOWN"

            elif angle > 160:  # UP position
                if stage == "DOWN":
                    up_start_time = time.time()
                    down_to_up_duration = up_start_time - down_start_time
                    last_duration = down_to_up_duration  # store for display
                    print(f"DOWN to UP duration: {last_duration:.2f} seconds")
                    counter += 1
                stage = "UP"

            if feet_placement_angle <= 70:
                feet_placement_status = "Great feet position"
                feet_placement_color = (0, 255, 0)  # Green

            elif feet_placement_angle <= 90:
                feet_placement_status = "Good feet position"
                feet_placement_color = (255, 255, 0)  # Yellow
            else:
                feet_placement_status = "Fix Foot Placement"
                feet_placement_color = (0, 0, 255)  # Red

            cv2.putText(image, f'Foot Placement: {int(feet_placement_angle)} degrees',
                        tuple(np.multiply(
                            left_knee, [image.shape[1], image.shape[0] - 40]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, feet_placement_color, 2, cv2.LINE_AA)

            # Display feet placement status
            cv2.putText(image, feet_placement_status,
                        tuple(np.multiply(
                            left_ankle, [image.shape[1], image.shape[0] - 10]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, feet_placement_color, 2, cv2.LINE_AA)

        except:
            pass

        # render counter
        # status box
        # renders box to top left of image with the colours specified and the line width specified
        # render counter
        # extend box for time display
        cv2.rectangle(image, (0, 0), (225, 120), (254, 197, 106), -1)

        # repetition data
        cv2.putText(image, 'Reps:', (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (120, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2, cv2.LINE_AA)

        # stage data
        cv2.putText(image, 'Stage:', (15, 70), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(stage) if stage else "-", (120, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # time between reps display
        cv2.putText(image, 'Time:', (15, 110), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 0), 1, cv2.LINE_AA)

        if last_duration is not None:
            cv2.putText(image, f'{last_duration:.2f}s', (120, 110), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)

        # render detections (shows detections)
        mp_drawing.draw_landmarks(
            # landmarks are coordinates of all individual points on the body
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(254, 197, 106),
                                   thickness=2, circle_radius=2),  # styles the different lines within the model
            mp_drawing.DrawingSpec(color=(254, 120, 106),
                                   thickness=2, circle_radius=2))  # styles the different lines within the model
        # pose connections are where all the landmarks connect to e.g. nose to left eye
        # Define the border color (same as box color)
        border_color = (254, 197, 106)

        # Draw the border
        border_thickness = 10  # Thickness of the border
        cv2.rectangle(image, (0, 0),
                      (image.shape[1], image.shape[0]), border_color, border_thickness)

        # Load the image you want to display
        logo = cv2.imread('testing/optimal.jpg')
        logo = cv2.resize(logo, (100, 50))

        # Get the dimensions of both the frame and the image
        frame_height, frame_width, _ = image.shape
        logo_height, logo_width, _ = logo.shape

        # Define the position (bottom right corner)
        x_offset = frame_width - logo_width
        y_offset = frame_height - logo_height

        # Place the logo on the frame
        image[y_offset:y_offset + logo_height,
              x_offset:x_offset + logo_width] = logo

        cv2.imshow('Mediapipe Feed', image)  # image appears on screen

        if cv2.waitKey(10) & 0xFF == ord('q'):  # stops program
            break

    cap.release()  # stops webcam recording
    cv2.destroyAllWindows()  # deletes frame window when done
