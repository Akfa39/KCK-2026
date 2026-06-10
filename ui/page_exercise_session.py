import base64
import threading
import time
from typing import Callable, Type

import cv2
import flet as ft

from cv.pose_detector import PoseDetector
from exercise.excerise import Exercise, PoseFrame
from ui.constants import C_BG, C_SURFACE, C_ACCENT, C_TEXT, C_MUTED, C_BORDER

CAMERA_INDICES = [0, 1]


def _encode_frame(frame) -> str:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf).decode()


def _camera_placeholder(label: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.VIDEOCAM_OFF_ROUNDED, color=C_MUTED, size=72),
                ft.Container(height=14),
                ft.Text(label, color=C_MUTED, size=15, weight=ft.FontWeight.W_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=C_SURFACE,
        border_radius=16,
        border=ft.border.all(1, C_BORDER),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )


def page_exercise_session(
    exercise_class: Type[Exercise],
    reps: int,
    page: ft.Page,
    on_back: Callable,
) -> ft.Stack:
    stop_event = threading.Event()
    exercise_instance = exercise_class()

    # shared state between vision threads
    frames: dict = {}
    landmarks: dict = {}
    frames_lock = threading.Lock()

    front_idx = CAMERA_INDICES[0]
    side_idx = CAMERA_INDICES[1]

    # --- camera UI ---
    cam_images = [
        ft.Image(src="", fit=ft.BoxFit.CONTAIN, expand=True),
        ft.Image(src="", fit=ft.BoxFit.CONTAIN, expand=True),
    ]
    cam_containers = [
        ft.Container(
            content=_camera_placeholder("Kamera przednia"),
            expand=True,
            border_radius=16,
            bgcolor=C_SURFACE,
            border=ft.border.all(1, C_BORDER),
        ),
        ft.Container(
            content=_camera_placeholder("Kamera boczna"),
            expand=True,
            border_radius=16,
            bgcolor=C_SURFACE,
            border=ft.border.all(1, C_BORDER),
        ),
    ]

    reps_label = ft.Text(
        f"0 / {reps}",
        color=C_ACCENT,
        size=22,
        weight=ft.FontWeight.W_700,
    )
    feedback_label = ft.Text(
        "",
        color=C_TEXT,
        size=13,
    )

    # --- vision threads (mirror of _pose_session vision_loop) ---
    def _vision_loop(detector: PoseDetector):
        detector.start()
        idx = detector.camera_index
        while not stop_event.is_set():
            frame, lm = detector.read()
            if frame is not None:
                with frames_lock:
                    frames[idx] = frame
                    landmarks[idx] = lm
            time.sleep(0.01)
        detector.stop()

    # --- display + analysis loop (runs after countdown) ---
    def _display_loop():
        while not stop_event.is_set():
            with frames_lock:
                cur_frames = dict(frames)
                cur_landmarks = dict(landmarks)

            pose_frame = PoseFrame(
                front=cur_landmarks.get(front_idx),
                side=cur_landmarks.get(side_idx),
            )

            feedback = exercise_instance.analyze(pose_frame)
            fb_color = (0, 200, 0) if feedback.correct else (0, 0, 220)

            updated = False
            for i, cam_idx in enumerate([front_idx, side_idx]):
                if cam_idx not in cur_frames:
                    continue
                display = cur_frames[cam_idx].copy()
                if cam_idx == front_idx:
                    cv2.putText(display, feedback.message, (10, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, fb_color, 2)
                    cv2.putText(display, f"Powt: {exercise_instance.reps}/{reps}",
                                (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                cam_images[i].src_base64 = _encode_frame(display)
                if cam_containers[i].content is not cam_images[i]:
                    cam_containers[i].content = cam_images[i]
                updated = True

            if updated:
                reps_label.value = f"{exercise_instance.reps} / {reps}"
                feedback_label.value = feedback.message
                try:
                    page.update()
                except Exception:
                    break

            if exercise_instance.reps >= reps:
                reps_label.value = f"{reps} / {reps} — Gotowe!"
                try:
                    page.update()
                except Exception:
                    pass
                break

            time.sleep(0.033)

    # --- countdown overlay ---
    countdown_text = ft.Text(
        "5",
        color=C_ACCENT,
        size=140,
        weight=ft.FontWeight.W_700,
        text_align=ft.TextAlign.CENTER,
    )
    countdown_label_ctrl = ft.Text(
        "Przygotuj się!",
        color=C_TEXT,
        size=22,
        weight=ft.FontWeight.W_600,
        text_align=ft.TextAlign.CENTER,
    )
    countdown_overlay = ft.Container(
        content=ft.Column(
            controls=[countdown_label_ctrl, countdown_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        ),
        bgcolor="#DD000000",
        expand=True,
        alignment=ft.Alignment(0, 0),
        border_radius=16,
        visible=True,
    )

    def _countdown_and_start():
        # start camera threads immediately so they warm up during countdown
        detectors = [PoseDetector(i) for i in CAMERA_INDICES]
        for d in detectors:
            threading.Thread(target=_vision_loop, args=(d,), daemon=True).start()

        time.sleep(0.4)
        for n in [5, 4, 3, 2, 1]:
            if stop_event.is_set():
                return
            countdown_text.value = str(n)
            try:
                page.update()
            except Exception:
                return
            time.sleep(1)

        if stop_event.is_set():
            return
        countdown_label_ctrl.value = ""
        countdown_text.value = "START!"
        countdown_text.size = 110
        try:
            page.update()
        except Exception:
            return
        time.sleep(0.8)

        if stop_event.is_set():
            return
        countdown_overlay.visible = False
        try:
            page.update()
        except Exception:
            return

        threading.Thread(target=_display_loop, daemon=True).start()

    threading.Thread(target=_countdown_and_start, daemon=True).start()

    # --- layout ---
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            exercise_class.name,
                            color=C_TEXT,
                            size=18,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            f"Cel: {reps} powtórzeń",
                            color=C_MUTED,
                            size=12,
                        ),
                    ],
                    spacing=2,
                ),
                ft.Container(expand=True),
                ft.Column(
                    controls=[
                        reps_label,
                        feedback_label,
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=C_SURFACE,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.all(1, C_BORDER),
    )

    cameras_row = ft.Row(
        controls=cam_containers,
        spacing=16,
        expand=True,
    )

    cameras_stack = ft.Stack(
        controls=[cameras_row, countdown_overlay],
        expand=True,
    )

    body = ft.Column(
        controls=[header, cameras_stack],
        spacing=16,
        expand=True,
    )

    def go_back(e=None):
        stop_event.set()
        on_back()

    back_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, color=C_BG, size=18),
                ft.Text("Wróć", color=C_BG, size=14, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=C_ACCENT,
        border_radius=30,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        on_click=go_back,
        ink=True,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color="#66000000",
            offset=ft.Offset(0, 4),
        ),
        right=32,
        bottom=24,
    )

    outer = ft.Container(
        content=body,
        expand=True,
        padding=ft.padding.symmetric(horizontal=32, vertical=20),
    )

    return ft.Stack(controls=[outer, back_btn], expand=True)
