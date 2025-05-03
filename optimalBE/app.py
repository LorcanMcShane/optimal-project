import cv2
import time
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import os


app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb://127.0.0.1:27017")

db = client.optimalDB
fs = gridfs.GridFS(db)

exercises = db.optimal
users = db.users
sbd = db.sbd

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


@app.route("/api/v1.0/exercises", methods=["GET"])
def show_all_exercises():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))

    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))

    data_to_return = []
    for exercise in exercises.find().skip(page_start).limit(page_size):
        exercise['_id'] = str(exercise['_id'])
        data_to_return.append(exercise)
    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/every_exercise", methods=["GET"])
def show_every_exercises():

    data_to_return = []
    for exercise in exercises.find():
        exercise['_id'] = str(exercise['_id'])
        data_to_return.append(exercise)
    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/exercises/<string:id>", methods=["GET"])
def show_one_exercise(id):
    exercise = exercises.find_one({'id': id})

    if exercise is not None:
        exercise['_id'] = str(exercise['_id'])
        return make_response(jsonify(exercise), 200)
    else:
        return make_response(jsonify({"error": "Exercise not found"}), 404)


@app.route("/api/v1.0/users", methods=["GET"])
def show_user():
    data_to_return = []
    for user in users.find():
        user['_id'] = str(users['_id'])
        data_to_return.append(user)
    return make_response(jsonify(data_to_return), 200)


@app.route('/api/v1.0/users/prSquat', methods=['patch'])
def update_pr_squat():
    query = {"name": "Lorcan M"}
    newvalues = {"$set": {"prSquat": request.form['prSquat']}}
    result = (users.update_one(query, newvalues))

    return jsonify({
        "matched": result.matched_count,
        "modified": result.modified_count,
        "acknowledged": result.acknowledged
    }), 200


@app.route('/api/v1.0/users/prBenchPress', methods=['patch'])
def update_pr_benchpress():
    query = {"name": "Lorcan M"}
    newvalues = {"$set": {"prBenchPress": request.form['prBenchPress']}}
    result = (users.update_one(query, newvalues))

    return jsonify({
        "matched": result.matched_count,
        "modified": result.modified_count,
        "acknowledged": result.acknowledged
    }), 200


@app.route('/api/v1.0/users/prDeadlift', methods=['patch'])
def update_pr_deadlift():
    query = {"name": "Lorcan M"}
    newvalues = {"$set": {"prDeadlift": request.form['prDeadlift']}}
    result = (users.update_one(query, newvalues))

    return jsonify({
        "matched": result.matched_count,
        "modified": result.modified_count,
        "acknowledged": result.acknowledged
    }), 200


@app.route("/api/v1.0/sbd", methods=["GET"])
def show_sbd():
    data_to_return = []
    for z in sbd.find():
        z['_id'] = str(z['_id'])
        data_to_return.append(z)
    return make_response(jsonify(data_to_return), 200)


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


def setup_video(video):
    input_path = 'temp_video.mp4'
    output_path = 'processed_video.mp4'
    video.save(input_path)

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    return cap, out, input_path, output_path, width, height


def process_frame(frame, pose):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return results, image


def format_video(image, counter, stage, last_duration, results, width, height):
    # info box
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

    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(254, 197, 106),
                               thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(254, 120, 106),
                               thickness=2, circle_radius=2)
    )
    cv2.rectangle(image, (0, 0), (width, height), (254, 197, 106), 10)

    logo = cv2.imread('images/optimal.jpg')
    if logo is not None:
        logo = cv2.resize(logo, (100, 50))
        image[-logo.shape[0]:, -logo.shape[1]:] = logo


def posture_format(left_ear, left_shoulder, left_hip, image, width, height):
    posture_angle = calculate_angle(left_ear, left_shoulder, left_hip)
    posture_status = "Good posture" if posture_angle >= 150 else "Fix posture"
    posture_color = (0, 255, 0) if posture_angle >= 150 else (0, 0, 255)

    cv2.putText(image, f'Posture: {int(posture_angle)} deg',
                tuple(np.multiply(left_shoulder, [
                      width, height - 40]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2)

    cv2.putText(image, posture_status,
                tuple(np.multiply(left_hip, [width, height - 10]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2)

# processing section


def process_exercise(video, logic_fn):
    cap, out, input_path, output_path, width, height = setup_video(video)
    counter = stage = down_start_time = up_start_time = last_duration = None
    counter = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results, image = process_frame(frame, pose)
            try:
                counter, stage, down_start_time, up_start_time, last_duration = logic_fn(
                    results, image, width, height, counter, stage, down_start_time, up_start_time, last_duration
                )
            except:
                pass
            format_video(image, counter, stage, last_duration,
                         results, width, height)
            out.write(image)

    cap.release()
    out.release()
    os.remove(input_path)
    return send_file(output_path, as_attachment=True, mimetype='video/mp4')

# exercise logic


def squat_logic(results, image, width, height, counter, stage, down_start, up_start, duration):
    landmarks = results.pose_landmarks.landmark
    def get(name): return [landmarks[mp_pose.PoseLandmark[name].value].x,
                           landmarks[mp_pose.PoseLandmark[name].value].y]
    hip, knee, ankle = get("LEFT_HIP"), get("LEFT_KNEE"), get("LEFT_ANKLE")
    shoulder, ear = get("LEFT_SHOULDER"), get("LEFT_EAR")

    angle = calculate_angle(hip, knee, ankle)
    posture_format(ear, shoulder, hip, image, width, height)

    if angle < 30:
        depth_status, color = "Great Depth, ATG", (0, 255, 0)
    elif angle < 60:
        if stage != "DOWN":
            down_start = time.time()
            if up_start:
                duration = down_start - up_start
        stage = "DOWN"
        depth_status, color = "Good Depth, Parallel", (255, 255, 0)
    elif angle > 150 and stage == "DOWN":
        up_start = time.time()
        duration = up_start - down_start
        counter += 1
        stage = "UP"

    cv2.putText(image, depth_status, (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    return counter, stage, down_start, up_start, duration


def benchpress_logic(results, image, width, height, counter, stage, down_start, up_start, duration):
    landmarks = results.pose_landmarks.landmark
    def get(name): return [landmarks[mp_pose.PoseLandmark[name].value].x,
                           landmarks[mp_pose.PoseLandmark[name].value].y]

    shoulder, elbow, wrist = get("LEFT_SHOULDER"), get(
        "LEFT_ELBOW"), get("LEFT_WRIST")
    hip, knee, ankle = get("LEFT_HIP"), get("LEFT_KNEE"), get("LEFT_ANKLE")

    arm_angle = calculate_angle(shoulder, elbow, wrist)
    leg_angle = calculate_angle(hip, knee, ankle)

    if arm_angle < 90:
        if stage != "DOWN":
            down_start = time.time()
            if up_start:
                duration = down_start - up_start
        stage = "DOWN"
    elif arm_angle > 160 and stage == "DOWN":
        up_start = time.time()
        duration = up_start - down_start
        counter += 1
        stage = "UP"

    foot_status, color = (
        ("Great feet position", (0, 255, 0)) if leg_angle <= 90 else
        ("Good feet position", (255, 255, 0)) if leg_angle <= 120 else
        ("Fix Foot Placement", (0, 0, 255))
    )

    cv2.putText(image, str(int(arm_angle)), tuple(np.multiply(elbow, [width, height]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(image, f'Knee Angle: {int(leg_angle)}deg',
                tuple(np.multiply(knee, [width, height - 40]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(image, foot_status,
                tuple(np.multiply(ankle, [width, height - 10]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return counter, stage, down_start, up_start, duration


def deadlift_logic(results, image, width, height, counter, stage, down_start, up_start, duration):
    landmarks = results.pose_landmarks.landmark
    def get(name): return [landmarks[mp_pose.PoseLandmark[name].value].x,
                           landmarks[mp_pose.PoseLandmark[name].value].y]

    shoulder, hip, knee, ear = get("LEFT_SHOULDER"), get(
        "LEFT_HIP"), get("LEFT_KNEE"), get("LEFT_EAR")
    angle = calculate_angle(shoulder, hip, knee)
    posture_format(ear, shoulder, hip, image, width, height)

    if angle < 100:
        if stage != "DOWN":
            down_start = time.time()
            if up_start:
                duration = down_start - up_start
        stage = "DOWN"
    elif angle > 160 and stage == "DOWN":
        up_start = time.time()
        duration = up_start - down_start
        counter += 1
        stage = "UP"

    cv2.putText(image, str(int(angle)), tuple(np.multiply(hip, [width, height]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return counter, stage, down_start, up_start, duration


# routing section

@app.route('/api/v1.0/check/squat', methods=['POST'])
def handle_squat():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    return process_exercise(request.files['video'], squat_logic)


@app.route('/api/v1.0/check/benchpress', methods=['POST'])
def handle_benchpress():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    return process_exercise(request.files['video'], benchpress_logic)


@app.route('/api/v1.0/check/deadlift', methods=['POST'])
def handle_deadlift():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    return process_exercise(request.files['video'], deadlift_logic)


print("Backend running...")

if __name__ == "__main__":
    app.run(debug=True)
