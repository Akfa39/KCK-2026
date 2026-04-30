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


def page_calendar():
    return make_placeholder("📅", "Kalendarz", "Tu znajdzie się kalendarz aktywności")


def page_settings():
    return make_placeholder("⚙️", "Ustawienia", "Tu znajdą się opcje konfiguracji aplikacji")


PAGES = [page_home, page_trainings, page_calendar, page_settings]


# Main

def main(page: ft.Page):
    page.title = "Trening App"
    page.bgcolor = C_BG
    page.padding = 0
    page.window_width = 1280
    page.window_height = 720
    page.window_resizable = False

    active_index = 0

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

        content_area.content = PAGES[index]()

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


def run():
    ft.run(main)
