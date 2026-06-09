from typing import Callable, Type

import flet as ft

from exercise.excerise import Exercise
from ui.constants import (
    C_BG, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)

PRESET_REPS = [5, 8, 10, 12, 15, 20]


def page_rep_picker(
        exercise_class: Type[Exercise],
        on_start: Callable[[int], None],
        on_back: Callable,
) -> ft.Container:
    selected = [10]
    rep_buttons: list[ft.Container] = []

    def make_rep_button(reps: int) -> ft.Container:
        is_selected = reps == selected[0]

        def on_click(e, r=reps):
            selected[0] = r
            for btn in rep_buttons:
                active = btn.data == selected[0]
                btn.bgcolor = C_ACCENT if active else C_CARD
                btn.border = ft.border.all(2, C_ACCENT) if active else ft.border.all(1, C_BORDER)
                btn.content.color = C_BG if active else C_TEXT
                btn.update()

        return ft.Container(
            data=reps,
            content=ft.Text(
                str(reps),
                color=C_BG if is_selected else C_TEXT,
                size=18,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=C_ACCENT if is_selected else C_CARD,
            border_radius=12,
            border=ft.border.all(2, C_ACCENT) if is_selected else ft.border.all(1, C_BORDER),
            width=72,
            height=60,
            alignment=ft.Alignment(0, 0),
            on_click=on_click,
            ink=True,
        )

    rep_buttons.extend(make_rep_button(r) for r in PRESET_REPS)

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
        on_click=lambda e: on_back(),
        ink=True,
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=16,
            color="#66000000", offset=ft.Offset(0, 4),
        ),
    )

    footer = ft.Row(
        controls=[back_btn],
        alignment=ft.MainAxisAlignment.END,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(exercise_class.name, color=C_TEXT, size=26, weight=ft.FontWeight.W_700),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text(exercise_class.muscle_group, color=C_BG, size=12, weight=ft.FontWeight.W_700),
                    bgcolor=C_ACCENT,
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=14, vertical=5),
                ),
                ft.Container(height=40),
                ft.Text("Ile powtórzeń?", color=C_MUTED, size=13, weight=ft.FontWeight.W_600),
                ft.Container(height=16),
                ft.Row(controls=rep_buttons, spacing=12),
                ft.Container(height=48),
                ft.Container(
                    content=ft.Text(
                        "Rozpocznij", color=C_BG, size=16,
                        weight=ft.FontWeight.W_700, text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=C_ACCENT,
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=48, vertical=16),
                    on_click=lambda e: on_start(selected[0]),
                    ink=True,
                ),
                ft.Container(height=24),
                footer,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        expand=True,
        padding=ft.padding.symmetric(horizontal=80, vertical=60),
    )
