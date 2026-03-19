import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture("T - Trim.mp4")
pose = mp_pose.Pose()
_ , frame = cap.read()
results = pose.process(frame)
landmarks = results.pose_landmarks.landmark

ramie_lewe = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
ramie_prawe = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
nadgarstek_lewy = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
nadgarstek_prawy = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

TOLERANCE = 0.1

if abs(ramie_lewe.y - nadgarstek_lewy.y) < TOLERANCE and abs(ramie_prawe.y - nadgarstek_prawy.y) < TOLERANCE:
    print("T POSE")

nos = landmarks[mp_pose.PoseLandmark.NOSE]

if abs(nadgarstek_lewy.y - nadgarstek_prawy.y) < TOLERANCE and nadgarstek_prawy.y + TOLERANCE > nos.y:
    print("Y POSE")

biodro_lewe = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
biodro_prawe = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

if abs(nadgarstek_lewy.y - nadgarstek_prawy.y) < TOLERANCE and nadgarstek_prawy.y + TOLERANCE > biodro_prawe.y:
    print("I POSE")


