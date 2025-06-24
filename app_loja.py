import flet as ft
from database.db import criar_tabelas
from services.loja import ShopApp

def main(page: ft.Page):
    page.title = "POO Shop"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT

    snackbar_text = ft.Text("")
    snackbar = ft.SnackBar(content=snackbar_text)


    page.snack_bar = snackbar



    criar_tabelas()

    shop_app = ShopApp(page, snackbar_text)
    page.add(shop_app)

    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)