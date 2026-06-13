from datetime import date, datetime, timedelta
from typing import Any, Optional

import flet as ft

from ui.constants import (
    C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER,
)

USER_ID = 1

_PHRASES = [
    "Każdy trening przybliża Cię do celu.",
    "Konsekwencja pokonuje talent.",
    "Dziś pot, jutro wyniki.",
    "Ciało osiąga to, w co wierzy umysł.",
    "Nie ma skrótów do miejsca, które jest warte odwiedzenia.",
    "Ból jest tymczasowy, duma — wieczna.",
    "Lepszy trening niż żaden trening.",
]


def _phrase_of_day() -> str:
    return _PHRASES[date.today().toordinal() % len(_PHRASES)]


def _stat_card(emoji: str, label: str, value: str, subtitle: str = "") -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(emoji, size=28),
                ft.Container(height=8),
                ft.Text(value, color=C_TEXT, size=36, weight=ft.FontWeight.W_700),
                ft.Text(label, color=C_MUTED, size=12, weight=ft.FontWeight.W_600),
                ft.Text(subtitle, color=C_ACCENT, size=11) if subtitle else ft.Container(),
            ],
            spacing=2,
        ),
        bgcolor=C_CARD,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=28, vertical=24),
        border=ft.border.all(1, C_BORDER),
        expand=True,
    )


def _last_workout_card(last: Optional[dict]) -> ft.Container:
    if last is None or not last.get("started_at"):
        body = ft.Text("Brak treningów", color=C_MUTED, size=15)
    else:
        dt = datetime.fromisoformat(last["started_at"])
        days_ago = (date.today() - dt.date()).days
        if days_ago == 0:
            ago = "dzisiaj"
        elif days_ago == 1:
            ago = "wczoraj"
        else:
            ago = f"{days_ago} dni temu"

        try:
            date_str = dt.strftime("%d %B %Y").lstrip("0")
        except Exception:
            date_str = str(dt.date())

        body = ft.Column(
            controls=[
                ft.Text(date_str, color=C_TEXT, size=20, weight=ft.FontWeight.W_700),
                ft.Container(height=4),
                ft.Text(ago, color=C_ACCENT, size=13, weight=ft.FontWeight.W_600),
            ],
            spacing=0,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("🕐", size=22),
                        ft.Text(
                            "OSTATNI TRENING",
                            color=C_MUTED,
                            size=11,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=16),
                body,
            ],
            spacing=0,
        ),
        bgcolor=C_CARD,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=28, vertical=24),
        border=ft.border.all(1, C_BORDER),
        expand=True,
    )


def _streak_card(workouts: list[dict]) -> ft.Container:
    workout_dates = set()
    for w in workouts:
        if w.get("started_at"):
            workout_dates.add(datetime.fromisoformat(w["started_at"]).date())

    streak = 0
    day = date.today()
    while day in workout_dates:
        streak += 1
        day -= timedelta(days=1)

    if streak == 0:
        value = "0"
        sub = "Zacznij dziś!"
    elif streak == 1:
        value = "1"
        sub = "dzień z rzędu 🔥"
    else:
        value = str(streak)
        sub = f"dni z rzędu 🔥"

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🔥", size=28),
                ft.Container(height=8),
                ft.Text(value, color=C_TEXT, size=36, weight=ft.FontWeight.W_700),
                ft.Text("SERIA", color=C_MUTED, size=12, weight=ft.FontWeight.W_600),
                ft.Text(sub, color=C_ACCENT, size=11),
            ],
            spacing=2,
        ),
        bgcolor=C_CARD,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=28, vertical=24),
        border=ft.border.all(1, C_BORDER),
        expand=True,
    )


def page_home(db: Optional[Any] = None, on_go_to_training: Optional[Any] = None) -> ft.Container:
    user_name = ""
    workouts: list[dict] = []
    last_workout: Optional[dict] = None

    if db is not None:
        try:
            user = db.users.get_by_id(USER_ID)
            if user:
                user_name = user.get("user") or user.get("name") or ""
        except Exception:
            pass
        try:
            workouts = db.workouts.get_history(USER_ID, limit=9999)
            last_workout = workouts[0] if workouts else None
        except Exception:
            pass

    today = date.today()
    total = len(workouts)
    this_month = sum(
        1 for w in workouts
        if w.get("started_at") and
        datetime.fromisoformat(w["started_at"]).date().month == today.month and
        datetime.fromisoformat(w["started_at"]).date().year == today.year
    )

    greeting = f"Witaj, {user_name}!" if user_name else "Witaj!"

    header = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(greeting, color=C_TEXT, size=30, weight=ft.FontWeight.W_700),
                ft.Container(height=4),
                ft.Text(_phrase_of_day(), color=C_MUTED, size=14),
            ],
            spacing=0,
        ),
        bgcolor=C_SURFACE,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=32, vertical=24),
        border=ft.border.all(1, C_BORDER),
    )

    stats_row = ft.Row(
        controls=[
            _stat_card("🏋️", "ŁĄCZNIE", str(total), "wszystkie treningi"),
            _stat_card("📅", "TEN MIESIĄC", str(this_month), "treningi w tym miesiącu"),
            _streak_card(workouts),
        ],
        spacing=16,
    )

    bottom_row = ft.Row(
        controls=[
            _last_workout_card(last_workout),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("💪", size=32),
                        ft.Container(height=8),
                        ft.Text(
                            "Zacznij trening",
                            color=C_BG,
                            size=18,
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=4),
                        ft.Text(
                            "Wybierz ćwiczenie i działaj",
                            color=C_BG,
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=C_ACCENT,
                border_radius=16,
                padding=ft.padding.symmetric(horizontal=28, vertical=24),
                expand=True,
                on_click=lambda e: on_go_to_training() if on_go_to_training else None,
                ink=True,
            ),
        ],
        spacing=16,
    )

    content = ft.Column(
        controls=[
            header,
            ft.Container(height=4),
            stats_row,
            ft.Container(height=4),
            bottom_row,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=32, vertical=28),
    )
