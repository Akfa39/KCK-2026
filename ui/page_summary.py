from typing import Callable

import flet as ft

from exercise.session import SessionResult
from ui.constants import (
    C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)


def _format_duration(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m {s % 60}s"


def _accuracy_label(accuracy: float) -> tuple[str, str]:
    if accuracy >= 85:
        return "Świetna forma! 💪", C_ACCENT
    if accuracy >= 65:
        return "Dobra robota!", C_ACCENT
    return "Pracuj nad techniką", C_MUTED


def _stat_card(emoji: str, label: str, value: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(emoji, size=26),
                ft.Container(height=8),
                ft.Text(value, color=C_TEXT, size=28, weight=ft.FontWeight.W_700),
                ft.Container(height=4),
                ft.Text(label, color=C_MUTED, size=11, weight=ft.FontWeight.W_600),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=C_CARD,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=32, vertical=24),
        border=ft.border.all(1, C_BORDER),
        expand=True,
    )


def page_summary(
        result: SessionResult,
        on_back: Callable,
) -> ft.Container:
    accuracy = (
        (result.total_feedbacks - result.incorrect_feedbacks) / result.total_feedbacks * 100
        if result.total_feedbacks > 0 else 0.0
    )
    acc_label, acc_color = _accuracy_label(accuracy)
    completed_all = result.reps_done >= result.target_reps

    header_emoji = "🏆" if completed_all else "💪"
    header_text = "Trening ukończony!" if completed_all else "Sesja zakończona"

    stats_row = ft.Row(
        controls=[
            _stat_card(
                "🔁",
                "POWTÓRZENIA",
                f"{result.reps_done} / {result.target_reps}",
            ),
            _stat_card(
                "⏱️",
                "CZAS",
                _format_duration(result.duration_seconds),
            ),
            _stat_card(
                "🎯",
                "POPRAWNOŚĆ",
                f"{accuracy:.0f}%",
            ),
        ],
        spacing=16,
    )

    content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(header_emoji, size=40),
                    ft.Container(width=12),
                    ft.Text(
                        header_text,
                        color=C_TEXT,
                        size=30,
                        weight=ft.FontWeight.W_700,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=8),
            ft.Text(result.exercise_name, color=C_MUTED, size=14),
            ft.Container(height=36),
            stats_row,
            ft.Container(height=28),
            ft.Text(
                acc_label,
                color=acc_color,
                size=16,
                weight=ft.FontWeight.W_600,
            ),
            ft.Container(height=40),
            ft.Container(
                content=ft.Text(
                    "Wróć do ćwiczeń",
                    color=C_BG,
                    size=16,
                    weight=ft.FontWeight.W_700,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=C_ACCENT,
                border_radius=14,
                padding=ft.padding.symmetric(horizontal=48, vertical=16),
                on_click=lambda e: on_back(),
                ink=True,
            ),
        ],
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=80, vertical=60),
        alignment=ft.Alignment(-1, -1),
    )
