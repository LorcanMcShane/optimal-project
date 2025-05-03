import cv2
import mediapipe as mp
import numpy as np
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
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            # Calculate angle
            angle = calculate_angle(left_shoulder, left_hip, left_knee)

            # Visualize angle
            cv2.putText(image, str(angle),
                        tuple(np.multiply(left_hip, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,
                                                        255, 255), 2, cv2.LINE_AA
                        )

            # counter logic
            if angle < 100:  # down angle gives some leeway so the connection doesnt have to be exactl 180 to be counted as down
                stage = "down"
            if angle > 160 and stage == 'down':  # up angle ensures that the rep doesnt have to go all the way to the top
                stage = "up"
                counter += 1
                print(counter)
        except:
            pass

        # render counter
        # status box
        # renders box to top left of image with the colours specified and the line width specified
        cv2.rectangle(image, (0, 0), (225, 80), (254, 197, 106), -1)
        # repetition data
        cv2.putText(image, 'Reps:', (15, 30), cv2.FONT_ITALIC,
                    1, (0, 0, 0), 1, cv2.LINE_AA)  # label, coordinates,font, size of text, the color, line width, line type
        cv2.putText(image, str(counter), (120, 30), cv2.FONT_ITALIC,
                    1, (255, 255, 255), 2, cv2.LINE_AA)  # label, coordinates,font, size of text, the color, line width, line type

        # stage data up or down
        cv2.putText(image, 'Stage:', (15, 70), cv2.FONT_ITALIC,
                    1, (0, 0, 0), 1, cv2.LINE_AA)  # label, coordinates,font, size of text, the color, line width, line type
        cv2.putText(image, stage, (120, 70), cv2.FONT_ITALIC,
                    1, (255, 255, 255), 2, cv2.LINE_AA)  # label, coordinates,font, size of text, the color, line width, line type

        # render detections (shows detections)
        mp_drawing.draw_landmarks(
            # landmarks are coordinates of all individual points on the body
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(254, 197, 106),
                                   thickness=2, circle_radius=2),  # styles the different lines within the model
            mp_drawing.DrawingSpec(color=(254, 120, 106),
                                   thickness=2, circle_radius=2))  # styles the different lines within the model
        # pose connections are where all the landmarks connect to e.g. nose to left eye
        cv2.imshow('Mediapipe Feed', image)  # image appears on screen

        if cv2.waitKey(10) & 0xFF == ord('q'):  # stops program
            break

    cap.release()  # stops webcam recording
    cv2.destroyAllWindows()  # deletes frame window when done
