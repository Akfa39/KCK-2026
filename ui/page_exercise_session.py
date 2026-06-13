import base64
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional, Type

import cv2
import flet as ft

from cv.pose_detector import PoseDetector
from exercise.excerise import Exercise, PoseFrame
from ui.constants import C_BG, C_SURFACE, C_ACCENT, C_TEXT, C_MUTED, C_BORDER

CAMERA_INDICES = [0, 2]
ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _encode_frame(frame) -> str:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return "data:image/jpeg;base64," + base64.b64encode(buf).decode()


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
    on_finish: Optional[Callable[[int], None]] = None,
    dialogues_player: Optional[Any] = None,
) -> ft.Stack:
    stop_event = threading.Event()
    exercise_instance = exercise_class()

    # shared state between vision threads
    frames: dict = {}
    landmarks: dict = {}
    frames_lock = threading.Lock()

    front_idx = CAMERA_INDICES[0]
    side_idx = CAMERA_INDICES[1]

    last_audio_file = [None]

    def _play_feedback_audio(audio_file: str):
        if not audio_file or not dialogues_player:
            return
        if audio_file == last_audio_file[0]:
            return
        last_audio_file[0] = audio_file
        try:
            dialogues_player.play(str(ASSETS_DIR / audio_file))
        except Exception:
            pass

    def _update():
        try:
            page.session.connection.loop.call_soon_threadsafe(page.update)
        except Exception:
            pass

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

    hold_label = ft.Text(
        "Przytrzymaj pozycję",
        color=C_MUTED,
        size=12,
    )
    hold_progress_bar = ft.ProgressBar(
        value=0,
        color=C_ACCENT,
        bgcolor=C_BORDER,
        border_radius=8,
        height=8,
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
            _play_feedback_audio(feedback.audio_file)

            updated = False
            for i, cam_idx in enumerate([front_idx, side_idx]):
                if cam_idx not in cur_frames:
                    continue
                display = cur_frames[cam_idx].copy()

                cam_images[i].src = _encode_frame(display)
                if cam_containers[i].content is not cam_images[i]:
                    cam_containers[i].content = cam_images[i]
                updated = True

            if updated:
                reps_label.value = f"{exercise_instance.reps} / {reps}"
                feedback_label.value = feedback.message
                hold_progress_bar.value = exercise_instance.hold_progress
                _update()

            if exercise_instance.reps >= reps:
                reps_label.value = f"{reps} / {reps} — Gotowe!"
                _update()
                time.sleep(1.5)
                if not stop_event.is_set():
                    stop_event.set()
                    if on_finish:
                        page.session.connection.loop.call_soon_threadsafe(
                            lambda: on_finish(reps)
                        )
                break

            time.sleep(0.0167)

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
            _update()
            time.sleep(1)

        if stop_event.is_set():
            return
        countdown_label_ctrl.value = ""
        countdown_text.value = "START!"
        countdown_text.size = 110
        _update()
        time.sleep(0.8)

        if stop_event.is_set():
            return
        countdown_overlay.visible = False
        _update()

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

    hold_progress_container = ft.Container(
        content=ft.Column(
            controls=[hold_label, hold_progress_bar],
            spacing=4,
        ),
        bgcolor=C_SURFACE,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=24, vertical=10),
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
        controls=[header, hold_progress_container, cameras_stack],
        spacing=16,
        expand=True,
    )

    def go_back(e=None):
        stop_event.set()
        on_back()

    def end_training(e=None):
        stop_event.set()
        if on_finish:
            on_finish(exercise_instance.reps)
        else:
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
        left=32,
        bottom=24,
    )

    end_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.STOP_ROUNDED, color=C_BG, size=18),
                ft.Text("Zakończ trening", color=C_BG, size=14, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor="#E53935",
        border_radius=30,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        on_click=end_training,
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

    return ft.Stack(controls=[outer, back_btn, end_btn], expand=True)
