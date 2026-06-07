from pathlib import Path
from typing import Callable, Optional, Type

import flet as ft
from flet_video import Video, VideoMedia, PlaylistMode, VideoConfiguration

from exercise.excerise import Exercise
from ui.constants import (
    C_BG, C_SURFACE, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)

_ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _video_uri(filename: str) -> str:
    return (_ASSETS_DIR / filename).as_uri()


def page_exercise_detail(
        exercise_class: Type[Exercise],
        on_back: Callable,
        on_start: Optional[Callable[[Type[Exercise]], None]] = None,
) -> ft.Stack:

    def start_clicked(e):
        if on_start:
            on_start(exercise_class)

    video = ft.Container(
        content=Video(
            playlist=[VideoMedia(_video_uri(exercise_class.video_file))],
            fit=ft.BoxFit.CONTAIN,
            fill_color=C_SURFACE,
            autoplay=True,
            muted=True,
            playlist_mode=PlaylistMode.LOOP,
            show_controls=False,
            configuration=VideoConfiguration(enable_hardware_acceleration=False),
            expand=True,
        ),
        height=280,
        expand=True,
        bgcolor=C_SURFACE,
    )

    info = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    exercise_class.name,
                    color=C_TEXT,
                    size=24,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(
                        exercise_class.muscle_group,
                        color=C_BG,
                        size=12,
                        weight=ft.FontWeight.W_700,
                    ),
                    bgcolor=C_ACCENT,
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=14, vertical=5),
                ),
                ft.Container(height=24),
                ft.Text(
                    "Opis ćwiczenia",
                    color=C_MUTED,
                    size=12,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(height=6),
                ft.Text(
                    exercise_class.description,
                    color=C_TEXT,
                    size=15,
                ),
                ft.Container(height=36),
                ft.Container(
                    content=ft.Text(
                        "Rozpocznij",
                        color=C_BG,
                        size=16,
                        weight=ft.FontWeight.W_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=C_ACCENT,
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=40, vertical=16),
                    on_click=start_clicked,
                    ink=True,
                ),
                ft.Container(height=80),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=ft.padding.symmetric(horizontal=48, vertical=28),
        alignment=ft.Alignment(-1, -1),
    )

    main = ft.Column(
        controls=[video, info],
        spacing=0,
        expand=True,
    )

    back_button = ft.Container(
        content=ft.Container(
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
            on_click=lambda e: on_back(),
            ink=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color="#66000000",
                offset=ft.Offset(0, 4),
            ),
        ),
        alignment=ft.Alignment(1, 1),
        padding=ft.padding.only(right=32, bottom=24),
        expand=True,
    )

    return ft.Stack(controls=[main, back_button], expand=True)
