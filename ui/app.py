from typing import Optional

import flet as ft

from ui.actions import AppActions  # re-exported for backwards compatibility
from ui.constants import C_BG, C_SURFACE, C_ACCENT, C_MUTED, C_BORDER, NAV_ITEMS
from ui.page_home import page_home
from ui.page_trainings import page_trainings
from ui.page_calendar import page_calendar
from ui.page_settings import page_settings
from ui.page_exercise_detail import page_exercise_detail


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

    def open_exercise(exercise_class):
        def go_back():
            content_area.content = page_trainings(open_exercise)
            page.update()

        content_area.content = page_exercise_detail(
            exercise_class,
            on_back=go_back,
            on_start=actions.on_exercise_select,
        )
        page.update()

    def go_to_training():
        switch_tab(1)

    pages = [
        lambda: page_home(actions.db, go_to_training),
        lambda: page_trainings(open_exercise),
        lambda: page_calendar(actions.db),
        lambda: page_settings(
            actions.music_player, music_vol,
            actions.dialogues_player, dialogues_vol,
        ),
    ]

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

        if index == active_index:
            label_color = C_ACCENT
            label_weight = ft.FontWeight.W_600
        else:
            label_color = C_MUTED
            label_weight = ft.FontWeight.W_400

        def on_click(event):
            switch_tab(index)

        tab = ft.Container(
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

        return tab

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
