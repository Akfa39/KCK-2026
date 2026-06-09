from typing import Callable, Type

import flet as ft

from exercise.excerise import Exercise
from exercise.session import ExerciseSession, PLACEHOLDER_BYTES
from ui.constants import (
    C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)


def page_exercise_session(
        exercise_class: Type[Exercise],
        session: ExerciseSession,
        on_complete: Callable,
        page: ft.Page = None,
) -> ft.Column:

    # ── camera images ──────────────────────────────────────────────
    front_img = ft.Image(
        src=PLACEHOLDER_BYTES,
        fit=ft.BoxFit.CONTAIN,
        expand=True,
    )
    side_img = ft.Image(
        src=PLACEHOLDER_BYTES,
        fit=ft.BoxFit.CONTAIN,
        expand=True,
    )

    front_box = ft.Container(
        content=front_img,
        expand=True,
        bgcolor=C_SURFACE,
        border_radius=ft.border_radius.only(top_left=12, bottom_left=12),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
    side_box = ft.Container(
        content=side_img,
        expand=True,
        bgcolor=C_SURFACE,
        border_radius=ft.border_radius.only(top_right=12, bottom_right=12),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.border.only(left=ft.BorderSide(1, C_BORDER)),
    )

    cameras_row = ft.Row(
        controls=[front_box, side_box],
        spacing=0,
        expand=True,
    )

    # ── countdown overlay ──────────────────────────────────────────
    countdown_text = ft.Text(
        "",
        color=C_TEXT,
        size=120,
        weight=ft.FontWeight.W_700,
        text_align=ft.TextAlign.CENTER,
        visible=False,
    )
    countdown_overlay = ft.Container(
        content=countdown_text,
        bgcolor="#CC000000",
        expand=True,
        alignment=ft.Alignment(0, 0),
        visible=False,
    )

    camera_stack = ft.Stack(
        controls=[cameras_row, countdown_overlay],
        expand=True,
    )

    # ── header ─────────────────────────────────────────────────────
    rep_label = ft.Text(
        f"0 / {session._target_reps}",
        color=C_TEXT,
        size=22,
        weight=ft.FontWeight.W_700,
    )

    def stop_clicked(e):
        session.stop()

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(exercise_class.name, color=C_TEXT, size=16, weight=ft.FontWeight.W_600, expand=True),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Powtórzenia:", color=C_MUTED, size=13),
                            rep_label,
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text("Zakończ", color=C_BG, size=13, weight=ft.FontWeight.W_700),
                    bgcolor=C_ACCENT,
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    on_click=stop_clicked,
                    ink=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=C_SURFACE,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
    )

    # ── feedback bar ───────────────────────────────────────────────
    feedback_text = ft.Text(
        "Przygotuj się...",
        color=C_MUTED,
        size=15,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    feedback_bar = ft.Container(
        content=feedback_text,
        bgcolor=C_SURFACE,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(top=ft.BorderSide(1, C_BORDER)),
        alignment=ft.Alignment(0, 0),
    )

    # ── update callback (called from background thread) ────────────
    def on_update(front_bytes, side_bytes, feedback, reps, countdown):
        async def _apply():
            front_img.src = front_bytes
            side_img.src = side_bytes
            rep_label.value = f"{reps} / {session._target_reps}"

            if countdown:
                countdown_text.value = countdown
                countdown_text.color = "#50FF80" if countdown == "START!" else C_TEXT
                countdown_overlay.visible = True
                feedback_text.value = "Przygotuj się..."
                feedback_text.color = C_MUTED
            else:
                countdown_overlay.visible = False
                if feedback:
                    feedback_text.value = feedback.message
                    feedback_text.color = C_ACCENT if feedback.correct else "#FF5555"

            page.update()

        if page:
            page.run_task(_apply)

    session.start(on_update=on_update, on_complete=on_complete)

    return ft.Column(
        controls=[header, camera_stack, feedback_bar],
        spacing=0,
        expand=True,
    )
