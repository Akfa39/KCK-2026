import cv2
import mediapipe as mp

# Inicjalizacja MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

TOLERANCE = 0.1

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Kamera (0 = domyślna)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Konwersja BGR -> RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detekcja pozy
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Rysowanie szkieletu
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # Pobranie wymiarów obrazu
        h, w, _ = frame.shape

        landmarks = results.pose_landmarks.landmark

        ramie_lewe = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        ramie_prawe = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nadgarstek_lewy = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        nadgarstek_prawy = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        nos = landmarks[mp_pose.PoseLandmark.NOSE]

        biodro_lewe = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        biodro_prawe = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        # Iteracja po punktach
        for idx, lm in enumerate(results.pose_landmarks.landmark):
            x, y, z = lm.x, lm.y, lm.z

            # Konwersja do pikseli
            cx, cy = int(x * w), int(y * h)

            # Wyświetlanie punktów na obrazie
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            # Wypisanie w konsoli
            # if abs(ramie_lewe.y - nadgarstek_lewy.y) < TOLERANCE and abs(
            #         ramie_prawe.y - nadgarstek_prawy.y) < TOLERANCE:
            #     print("T POSE")
            # else:
            #     print("nie ma tpose")

            # if idx == 15:
            #     print(f"Nadgarstek {idx}: x={x:.3f}, y={y:.3f}, z={z:.3f}")
            #
            # if idx == 2:
            #     print(f"Oko {idx}: x={x:.3f}, y={y:.3f}, z={z:.3f}")

            # if abs(nadgarstek_lewy.y - nadgarstek_prawy.y) < TOLERANCE and nadgarstek_prawy.y < nos.y - TOLERANCE:
            #     print("Y POSE")
            # else:
            #     print("nie ma ypose")

            if abs(nadgarstek_lewy.y - nadgarstek_prawy.y) < TOLERANCE and nadgarstek_prawy.y + TOLERANCE > biodro_prawe.y:
                print("I POSE")
            else:
                print("nie ma ipose")
            # Opcjonalnie: podpis na ekranie
            cv2.putText(frame, str(idx), (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Wyświetlanie obrazu
    cv2.imshow("Pose Tracking", frame)

    # Wyjście klawiszem q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()