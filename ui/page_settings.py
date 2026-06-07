from typing import Optional, Any

import flet as ft

from ui.constants import C_ACCENT, C_TEXT, C_MUTED, C_CARD, C_BORDER


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


def page_settings(
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
