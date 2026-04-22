import sys
import cv2
import mediapipe as mp
import statistics as s

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

TOLERANCE = 0.1

def recognize_letter(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

    if abs(left_shoulder.y - left_wrist.y) < TOLERANCE and abs(right_shoulder.y - right_wrist.y) < TOLERANCE:
        return "T"

    elif abs(left_wrist.y - right_wrist.y) < TOLERANCE and s.mean([left_wrist.y, right_wrist.y])  < nose.y:
        return "Y"

    elif abs(left_wrist.y - right_wrist.y) < TOLERANCE and s.mean([left_wrist.y, right_wrist.y]) + TOLERANCE > s.mean([left_hip.y, right_hip.y]):
        return "I"

    elif abs(right_wrist.x - right_shoulder.x) < TOLERANCE and abs(left_wrist.y - left_shoulder.y) < TOLERANCE and right_wrist.y < right_shoulder.y:
        return "L"

    return "Nie rozpoznano"

def main():
    video_source = 0
    if len(sys.argv) > 1:
        video_source = sys.argv[1]

    cap = cv2.VideoCapture(video_source)

    with mp_pose.Pose() as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                letter = recognize_letter(results.pose_landmarks.landmark)

                cv2.putText(image, f'Litera: {letter}', (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.FILLED)

            cv2.imshow('Human alphabet', image)

            if cv2.waitKey(10) & 0xFF in [ord('q'), ord('Q')]:
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()