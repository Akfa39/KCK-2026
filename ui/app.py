import calendar as _cal
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Optional, Any
import flet as ft

# Colors
C_BG = "#0D0D0D"
C_SURFACE = "#161616"
C_CARD = "#1E1E1E"
C_ACCENT = "#C8F135"
C_TEXT = "#FFFFFF"
C_MUTED = "#7A7A7A"
C_BORDER = "#2A2A2A"

# Nav
NAV_ITEMS = [
    ("Strona główna", "🏠"),
    ("Moje treningi", "🏋️"),
    ("Kalendarz", "📅"),
    ("Ustawienia", "⚙️"),
]


@dataclass
class AppActions:
    on_home: Optional[Callable] = None
    on_trainings: Optional[Callable] = None
    on_calendar: Optional[Callable] = None
    on_settings: Optional[Callable] = None
    music_player: Optional[Any] = None
    dialogues_player: Optional[Any] = None


# Placeholder

def make_placeholder(emoji, title, subtitle):
    icon_box = ft.Container(
        content=ft.Text(emoji, size=52),
        bgcolor=C_CARD,
        border_radius=50,
        width=120,
        height=120,
        alignment=ft.Alignment(0, 0),
    )

    title_text = ft.Text(title, color=C_TEXT, size=32, weight=ft.FontWeight.W_700)
    subtitle_text = ft.Text(subtitle, color=C_MUTED, size=15)

    column = ft.Column(
        controls=[icon_box, title_text, subtitle_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    return ft.Container(
        content=column,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )


def page_home():
    return make_placeholder("🏠", "Strona główna", "Tu znajdzie się pulpit użytkownika")


def page_trainings():
    return make_placeholder("🏋️", "Moje treningi", "Tu znajdzie się lista twoich treningów")


_MONTH_NAMES = [
    "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
]
_DAY_NAMES = ["Pon", "Wt", "Śr", "Cz", "Pt", "Sob", "Ndz"]


def page_calendar():
    today = date.today()
    cur_year = [today.year]
    cur_month = [today.month]

    def build_grid(year, month):
        weeks = _cal.monthcalendar(year, month)

        header_cells = []
        for i, name in enumerate(_DAY_NAMES):
            is_weekend = i >= 5
            header_cells.append(
                ft.Container(
                    content=ft.Text(
                        name,
                        color=C_ACCENT if is_weekend else C_MUTED,
                        size=12,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.only(bottom=6),
                )
            )

        week_rows = [ft.Row(controls=header_cells, spacing=4)]

        for week in weeks:
            cells = []
            for col_idx, day in enumerate(week):
                if day == 0:
                    cells.append(ft.Container(expand=True, height=44))
                    continue
                is_today = (day == today.day and month == today.month and year == today.year)
                is_weekend = col_idx >= 5

                if is_today:
                    bg, txt_color, weight = C_ACCENT, C_BG, ft.FontWeight.W_700
                elif is_weekend:
                    bg, txt_color, weight = C_CARD, "#8AAB2A", ft.FontWeight.W_400
                else:
                    bg, txt_color, weight = C_CARD, C_TEXT, ft.FontWeight.W_400

                cells.append(
                    ft.Container(
                        content=ft.Text(
                            str(day),
                            color=txt_color,
                            size=14,
                            weight=weight,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        expand=True,
                        height=44,
                        bgcolor=bg,
                        border_radius=8,
                        alignment=ft.Alignment(0, 0),
                        border=ft.border.all(1, C_BORDER) if not is_today else None,
                    )
                )
            week_rows.append(ft.Row(controls=cells, spacing=4))

        return ft.Column(controls=week_rows, spacing=4)

    month_label = ft.Text(
        f"{_MONTH_NAMES[cur_month[0]]} {cur_year[0]}",
        color=C_TEXT,
        size=18,
        weight=ft.FontWeight.W_700,
    )
    grid_container = ft.Container(content=build_grid(cur_year[0], cur_month[0]))

    def refresh(y, m):
        month_label.value = f"{_MONTH_NAMES[m]} {y}"
        grid_container.content = build_grid(y, m)
        month_label.update()
        grid_container.update()

    def go_prev(e):
        m, y = cur_month[0] - 1, cur_year[0]
        if m < 1:
            m, y = 12, y - 1
        cur_month[0], cur_year[0] = m, y
        refresh(y, m)

    def go_next(e):
        m, y = cur_month[0] + 1, cur_year[0]
        if m > 12:
            m, y = 1, y + 1
        cur_month[0], cur_year[0] = m, y
        refresh(y, m)

    nav = ft.Row(
        controls=[
            ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_color=C_MUTED, on_click=go_prev),
            ft.Container(content=month_label, expand=True, alignment=ft.Alignment(0, 0)),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, icon_color=C_MUTED, on_click=go_next),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    calendar_card = ft.Container(
        content=ft.Column(controls=[nav, grid_container], spacing=16),
        bgcolor=C_SURFACE,
        border_radius=16,
        padding=ft.padding.all(24),
        border=ft.border.all(1, C_BORDER),
        expand=True,
    )

    right_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Statystyki", color=C_MUTED, size=12, weight=ft.FontWeight.W_600),
                ft.Divider(color=C_BORDER, height=20),
                ft.Text("Liczba treningów", color=C_MUTED, size=11),
                ft.Container(height=4),
                ft.Text("0", color=C_TEXT, size=28, weight=ft.FontWeight.W_700),
            ],
            spacing=0,
        ),
        bgcolor=C_SURFACE,
        border_radius=16,
        padding=ft.padding.all(20),
        border=ft.border.all(1, C_BORDER),
        width=180,
        alignment=ft.Alignment(-1, -1),
    )

    return ft.Container(
        content=ft.Row(
            controls=[calendar_card, right_panel],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        ),
        expand=True,
        padding=ft.padding.symmetric(horizontal=32, vertical=28),
    )


def _make_volume_row(
        label: str,
        emoji: str,
        player: Optional[Any],
        vol_state: list,
) -> ft.Container:
    initial_value = vol_state[0]

    value_label = ft.Text(
        f"{int(initial_value)}%",
        color=C_ACCENT,
        size=14,
        weight=ft.FontWeight.W_600,
        width=44,
        text_align=ft.TextAlign.RIGHT,
    )

    def on_change(e: ft.ControlEvent):
        raw = float(e.data)
        vol_state[0] = raw
        # print(f"[Slider] on_change → raw={raw}, player={player}") - CheckVolumeChange
        if player:
            player.set_volume(raw / 100)
        value_label.value = f"{int(raw)}%"
        value_label.update()

    slider = ft.Slider(
        value=initial_value,
        min=0,
        max=100,
        divisions=100,
        expand=True,
        active_color=C_ACCENT,
        inactive_color=C_BORDER,
        thumb_color=C_ACCENT,
        on_change=on_change,
    )

    header = ft.Row(
        controls=[
            ft.Text(emoji, size=18),
            ft.Text(
                label,
                color=C_TEXT,
                size=15,
                weight=ft.FontWeight.W_500,
                expand=True,
            ),
            value_label,
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    slider_row = ft.Row(
        controls=[slider],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    card_content = ft.Column(
        controls=[header, slider_row],
        spacing=6,
    )

    return ft.Container(
        content=card_content,
        bgcolor=C_CARD,
        border_radius=14,
        padding=ft.padding.symmetric(horizontal=24, vertical=18),
        border=ft.border.all(1, C_BORDER),
    )


def _page_settings(
        music_player: Optional[Any],
        music_vol: list,
        dialogues_player: Optional[Any],
        dialogues_vol: list,
):
    title = ft.Text(
        "Ustawienia",
        color=C_TEXT,
        size=26,
        weight=ft.FontWeight.W_700,
    )

    subtitle = ft.Text(
        "Dostosuj dźwięk aplikacji",
        color=C_MUTED,
        size=14,
    )

    section_label = ft.Text(
        "🔊  Głośność",
        color=C_MUTED,
        size=12,
        weight=ft.FontWeight.W_600,
    )

    music_row = _make_volume_row("Muzyka", "🎵", music_player, music_vol)
    dialogues_row = _make_volume_row("Dialogi", "🗣️", dialogues_player, dialogues_vol)

    content = ft.Column(
        controls=[
            title,
            subtitle,
            ft.Container(height=24),
            section_label,
            ft.Container(height=8),
            music_row,
            ft.Container(height=12),
            dialogues_row,
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=48, vertical=40),
        alignment=ft.Alignment(-1, -1),
    )


# Main

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

    pages = [
        page_home,
        page_trainings,
        page_calendar,
        lambda: _page_settings(
            actions.music_player, music_vol,
            actions.dialogues_player, dialogues_vol,
        ),
    ]

    content_area = ft.Container(expand=True, bgcolor=C_BG)

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
