from typing import Callable, Type

import flet as ft

from exercise.excerise import Exercise
from ui.constants import C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER


def page_training_report(
    exercise_class: Type[Exercise],
    completed_reps: int,
    target_reps: int,
    on_back: Callable,
) -> ft.Container:
    finished_all = completed_reps >= target_reps

    status_icon = ft.Container(
        content=ft.Icon(
            ft.Icons.CHECK_CIRCLE_ROUNDED if finished_all else ft.Icons.CANCEL_ROUNDED,
            color=C_ACCENT if finished_all else C_MUTED,
            size=96,
        ),
        alignment=ft.Alignment(0, 0),
    )

    status_text = ft.Text(
        "Trening ukończony!" if finished_all else "Trening zakończony",
        color=C_TEXT,
        size=32,
        weight=ft.FontWeight.W_700,
        text_align=ft.TextAlign.CENTER,
    )

    exercise_name_text = ft.Text(
        exercise_class.name,
        color=C_MUTED,
        size=16,
        text_align=ft.TextAlign.CENTER,
    )

    def _stat_card(label: str, value: str, highlight: bool = False) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value,
                        color=C_ACCENT if highlight else C_TEXT,
                        size=40,
                        weight=ft.FontWeight.W_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        label,
                        color=C_MUTED,
                        size=13,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=C_CARD,
            border_radius=16,
            border=ft.border.all(1, C_BORDER),
            padding=ft.padding.symmetric(horizontal=32, vertical=20),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    stats_row = ft.Row(
        controls=[
            _stat_card("Wykonane powtórzenia", str(completed_reps), highlight=True),
            _stat_card("Cel", str(target_reps)),
        ],
        spacing=16,
    )

    back_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.FITNESS_CENTER_ROUNDED, color=C_BG, size=20),
                ft.Text(
                    "Wróć do treningów",
                    color=C_BG,
                    size=16,
                    weight=ft.FontWeight.W_700,
                ),
            ],
            spacing=10,
            tight=True,
        ),
        bgcolor=C_ACCENT,
        border_radius=14,
        padding=ft.padding.symmetric(horizontal=40, vertical=18),
        on_click=lambda e: on_back(),
        ink=True,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color="#66000000",
            offset=ft.Offset(0, 4),
        ),
    )

    content = ft.Column(
        controls=[
            ft.Container(expand=True),
            status_icon,
            ft.Container(height=16),
            status_text,
            ft.Container(height=6),
            exercise_name_text,
            ft.Container(height=48),
            stats_row,
            ft.Container(height=48),
            ft.Row(
                controls=[back_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(expand=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        expand=True,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=48, vertical=32),
        bgcolor=C_BG,
    )
