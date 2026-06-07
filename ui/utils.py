import flet as ft

from ui.constants import C_TEXT, C_MUTED, C_CARD


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
