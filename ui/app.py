from typing import Optional

import flet as ft

from exercise.session import ExerciseSession
from ui.actions import AppActions  # re-exported for backwards compatibility
from ui.constants import C_BG, C_SURFACE, C_ACCENT, C_MUTED, C_BORDER, NAV_ITEMS
from ui.page_exercise_detail import page_exercise_detail
from ui.page_exercise_session import page_exercise_session
from ui.page_home import page_home
from ui.page_calendar import page_calendar
from ui.page_rep_picker import page_rep_picker
from ui.page_settings import page_settings
from ui.page_summary import page_summary
from ui.page_trainings import page_trainings


def main(page: ft.Page, actions: AppActions):
    page.title = "Trening App"
    page.bgcolor = C_BG
    page.padding = 0
    page.window_width = 1280
    page.window_height = 720
    page.window_resizable = False

    active_index = 0

    music_vol: list = [
        round(actions.music_player.get_volume() * 100) if actions.music_player else 50
    ]
    dialogues_vol: list = [
        round(actions.dialogues_player.get_volume() * 100) if actions.dialogues_player else 50
    ]

    _nav_actions = [
        actions.on_home,
        actions.on_trainings,
        actions.on_calendar,
        actions.on_settings,
    ]

    content_area = ft.Container(expand=True, bgcolor=C_BG)

    # ── navigation helpers ──────────────────────────────────────────────────

    def show_trainings():
        content_area.content = page_trainings(open_exercise)
        page.update()

    def go_to_training():
        switch_tab(1)

    # ── exercise flow ───────────────────────────────────────────────────────

    def open_exercise(exercise_class):
        def go_back_to_list():
            show_trainings()

        content_area.content = page_exercise_detail(
            exercise_class,
            on_back=go_back_to_list,
            on_start=lambda ec: open_rep_picker(ec),
        )
        page.update()

    def open_rep_picker(exercise_class):
        def go_back_to_detail():
            open_exercise(exercise_class)

        def start_session(reps: int):
            session = ExerciseSession(
                exercise_class,
                target_reps=reps,
                dialogues_player=actions.dialogues_player,
            )

            def on_complete(result):
                async def _show_summary():
                    content_area.content = page_summary(result, on_back=show_trainings)
                    page.update()
                page.run_task(_show_summary)

            content_area.content = page_exercise_session(
                exercise_class,
                session=session,
                on_complete=on_complete,
                page=page,
            )
            page.update()

        content_area.content = page_rep_picker(
            exercise_class,
            on_start=start_session,
            on_back=go_back_to_detail,
        )
        page.update()

    # ── page list ───────────────────────────────────────────────────────────

    pages = [
        lambda: page_home(actions.db, go_to_training),
        lambda: page_trainings(open_exercise),
        lambda: page_calendar(actions.db),
        lambda: page_settings(
            actions.music_player, music_vol,
            actions.dialogues_player, dialogues_vol,
        ),
    ]

    # ── nav bar ─────────────────────────────────────────────────────────────

    nav_row = ft.Row(spacing=0)

    nav_bar = ft.Container(
        content=nav_row,
        bgcolor=C_SURFACE,
        border=ft.border.only(top=ft.BorderSide(1, C_BORDER)),
        height=68,
    )

    def build_tab(index):
        label = NAV_ITEMS[index][0]
        emoji = NAV_ITEMS[index][1]
        label_color = C_ACCENT if index == active_index else C_MUTED
        label_weight = ft.FontWeight.W_600 if index == active_index else ft.FontWeight.W_400

        def on_click(event):
            switch_tab(index)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(emoji, size=24),
                    ft.Text(label, color=label_color, size=11, weight=label_weight),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=ft.padding.symmetric(vertical=10),
            on_click=on_click,
        )

    def rebuild_nav():
        nav_row.controls.clear()
        for i in range(len(NAV_ITEMS)):
            nav_row.controls.append(build_tab(i))

    def switch_tab(index):
        nonlocal active_index
        active_index = index

        action = _nav_actions[index]
        if action:
            action()

        content_area.content = pages[index]()
        rebuild_nav()
        page.update()

    page.add(
        ft.Column(
            controls=[content_area, nav_bar],
            expand=True,
            spacing=0,
        )
    )

    switch_tab(0)


def run(actions: Optional[AppActions] = None):
    if actions is None:
        actions = AppActions()
    ft.run(lambda page: main(page, actions))
