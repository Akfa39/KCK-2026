import calendar as _cal
from datetime import date, datetime

import flet as ft

from ui.constants import (
    C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)

_MONTH_NAMES = [
    "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
]
_DAY_NAMES = ["Pon", "Wt", "Śr", "Cz", "Pt", "Sob", "Ndz"]


def page_calendar(db=None):
    today = date.today()
    cur_year = [today.year]
    cur_month = [today.month]

    workout_dates: set[date] = set()
    if db is not None:
        try:
            for r in db.workouts.get_calendar(1):
                if r.get("started_at"):
                    workout_dates.add(datetime.fromisoformat(r["started_at"]).date())
        except Exception:
            pass

    def count_for_month(year, month):
        return sum(1 for d in workout_dates if d.year == year and d.month == month)

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
                    cells.append(ft.Container(expand=True, height=58))
                    continue
                is_today = (day == today.day and month == today.month and year == today.year)
                is_weekend = col_idx >= 5
                is_workout = date(year, month, day) in workout_dates

                if is_today:
                    bg, txt_color, weight = C_ACCENT, C_BG, ft.FontWeight.W_700
                    dot_color = C_BG if is_workout else None
                elif is_weekend:
                    bg, txt_color, weight = C_CARD, "#8AAB2A", ft.FontWeight.W_400
                    dot_color = C_ACCENT if is_workout else None
                else:
                    bg, txt_color, weight = C_CARD, C_TEXT, ft.FontWeight.W_400
                    dot_color = C_ACCENT if is_workout else None

                day_text = ft.Text(
                    str(day),
                    color=txt_color,
                    size=15,
                    weight=weight,
                    text_align=ft.TextAlign.CENTER,
                )

                if dot_color:
                    cell_content = ft.Column(
                        controls=[
                            day_text,
                            ft.Container(
                                width=7,
                                height=7,
                                bgcolor=dot_color,
                                border_radius=4,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                    )
                else:
                    cell_content = day_text

                cells.append(
                    ft.Container(
                        content=cell_content,
                        expand=True,
                        height=58,
                        bgcolor=bg,
                        border_radius=10,
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
    count_label = ft.Text(
        str(count_for_month(cur_year[0], cur_month[0])),
        color=C_TEXT,
        size=28,
        weight=ft.FontWeight.W_700,
    )

    def refresh(y, m):
        month_label.value = f"{_MONTH_NAMES[m]} {y}"
        grid_container.content = build_grid(y, m)
        count_label.value = str(count_for_month(y, m))
        month_label.update()
        grid_container.update()
        count_label.update()

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
                count_label,
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
