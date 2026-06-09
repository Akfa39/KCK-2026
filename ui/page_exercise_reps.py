from typing import Callable, Type

import flet as ft

from exercise.excerise import Exercise
from ui.constants import C_BG, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER


def page_exercise_reps(
    exercise_class: Type[Exercise],
    on_back: Callable,
    on_confirm: Callable[[int], None],
) -> ft.Stack:
    selected = [12]

    def _make_btn(n: int) -> ft.Container:
        is_sel = n == selected[0]
        return ft.Container(
            content=ft.Text(
                str(n),
                color=C_BG if is_sel else C_TEXT,
                size=22,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=C_ACCENT if is_sel else C_CARD,
            border_radius=16,
            border=ft.border.all(2, C_ACCENT if is_sel else C_BORDER),
            width=96,
            height=96,
            alignment=ft.Alignment(0, 0),
            ink=True,
            data=n,
        )

    buttons = [_make_btn(n) for n in range(8, 21)]

    buttons_row = ft.Row(
        controls=buttons,
        wrap=True,
        spacing=12,
        run_spacing=12,
    )

    def on_btn_click(e):
        n = e.control.data
        selected[0] = n
        for btn in buttons:
            is_sel = btn.data == n
            btn.bgcolor = C_ACCENT if is_sel else C_CARD
            btn.border = ft.border.all(2, C_ACCENT if is_sel else C_BORDER)
            btn.content.color = C_BG if is_sel else C_TEXT
        buttons_row.update()

    for btn in buttons:
        btn.on_click = on_btn_click

    main = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    exercise_class.name,
                    color=C_MUTED,
                    size=14,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(height=6),
                ft.Text(
                    "Wybierz liczbę powtórzeń",
                    color=C_TEXT,
                    size=30,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Container(height=4),
                ft.Text(
                    "Minimum 8  •  Maksimum 20",
                    color=C_MUTED,
                    size=13,
                ),
                ft.Container(height=36),
                buttons_row,
                ft.Container(height=48),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "Dalej",
                                color=C_BG,
                                size=17,
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=C_BG, size=20),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    bgcolor=C_ACCENT,
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=40, vertical=18),
                    on_click=lambda e: on_confirm(selected[0]),
                    ink=True,
                ),
            ],
            spacing=0,
        ),
        expand=True,
        padding=ft.padding.symmetric(horizontal=48, vertical=36),
    )

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
            spread_radius=0,
            blur_radius=16,
            color="#66000000",
            offset=ft.Offset(0, 4),
        ),
        right=32,
        bottom=24,
    )

    return ft.Stack(controls=[main, back_btn], expand=True)
