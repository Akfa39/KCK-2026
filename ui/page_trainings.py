from typing import Optional, Callable, Type

import flet as ft

from exercise.dumbbell_crunch import DumbbellWeightedCrunch
from exercise.dumbbell_curl import DumbbellCurl
from exercise.dumbbell_french_press import DumbbellFrenchPress
from exercise.dumbbell_good_morning import DumbbellGoodMorning
from exercise.dumbbell_hip_thrust import DumbbellHipThrust
from exercise.dumbbell_leg_curl import DumbbellLegCurl
from exercise.dumbbell_overhead_tricep_extension import DumbbellOverheadTricepExtension
from exercise.dumbbell_plank_pull_through import DumbbellPlankPullThrough
from exercise.dumbbell_woodchop import DumbbellWoodchop
from exercise.excerise import Exercise

from ui.constants import C_BG, C_SURFACE, C_CARD, C_ACCENT, C_TEXT, C_MUTED, C_BORDER

_ALL_EXERCISES: list[Type[Exercise]] = [
    DumbbellCurl,
    DumbbellFrenchPress,
    DumbbellOverheadTricepExtension,
    DumbbellWeightedCrunch,
    DumbbellHipThrust,
    DumbbellLegCurl,
    DumbbellGoodMorning,
    DumbbellWoodchop,
    DumbbellPlankPullThrough,
]

_GROUP_ORDER = [
    "Biceps/Triceps",
    "Nogi",
    "Klatka piersiowa",
]


def _group_exercises() -> dict[str, list[Type[Exercise]]]:
    groups: dict[str, list[Type[Exercise]]] = {}
    for ex in _ALL_EXERCISES:
        g = ex.muscle_group
        groups.setdefault(g, []).append(ex)
    return groups


def _exercise_card(
        exercise_class: Type[Exercise],
        on_select: Optional[Callable[[Type[Exercise]], None]],
) -> ft.Container:
    video_box = ft.Container(
        content=ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, color=C_ACCENT, size=36),
        width=88,
        height=88,
        border_radius=8,
        bgcolor=C_SURFACE,
        border=ft.border.all(1, C_BORDER),
        alignment=ft.Alignment(0, 0),
    )

    name_text = ft.Text(
        exercise_class.name,
        color=C_TEXT,
        size=14,
        weight=ft.FontWeight.W_500,
        expand=True,
    )

    def clicked(e):
        if on_select:
            on_select(exercise_class)

    return ft.Container(
        content=ft.Row(
            controls=[video_box, name_text],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        bgcolor=C_CARD,
        border_radius=12,
        padding=ft.padding.all(10),
        border=ft.border.all(1, C_BORDER),
        expand=True,
        on_click=clicked if on_select else None,
        ink=on_select is not None,
    )


def _section(
        group_name: str,
        exercises: list[Type[Exercise]],
        on_select: Optional[Callable[[Type[Exercise]], None]],
) -> ft.Column:
    header = ft.Text(
        group_name,
        color=C_ACCENT,
        size=13,
        weight=ft.FontWeight.W_700,
    )

    divider = ft.Divider(color=C_BORDER, height=1, thickness=1)

    rows: list[ft.Row] = []
    for i in range(0, len(exercises), 3):
        chunk = exercises[i:i + 3]
        cards = [_exercise_card(ex, on_select) for ex in chunk]
        # fill empty slots so columns stay aligned
        while len(cards) < 3:
            cards.append(ft.Container(expand=True))
        rows.append(ft.Row(controls=cards, spacing=12))

    return ft.Column(
        controls=[header, divider, *rows],
        spacing=10,
    )


def page_trainings(
        on_select: Optional[Callable[[Type[Exercise]], None]] = None,
) -> ft.Container:
    groups = _group_exercises()

    sections: list[ft.Control] = []
    ordered_keys = [g for g in _GROUP_ORDER if g in groups]
    # append any group not in the predefined order
    for g in groups:
        if g not in ordered_keys:
            ordered_keys.append(g)

    for group_name in ordered_keys:
        sections.append(_section(group_name, groups[group_name], on_select))
        sections.append(ft.Container(height=24))

    title = ft.Text(
        "Trening",
        color=C_TEXT,
        size=26,
        weight=ft.FontWeight.W_700,
    )

    subtitle = ft.Text(
        "Wybierz ćwiczenie, które chcesz wykonać",
        color=C_MUTED,
        size=14,
    )

    content = ft.Column(
        controls=[
            title,
            subtitle,
            ft.Container(height=20),
            *sections,
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=32, vertical=28),
        alignment=ft.Alignment(-1, -1),
    )
