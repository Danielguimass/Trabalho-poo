import flet as ft
import os
import shutil
import random
from datetime import datetime
import asyncio

from database.db import (
    salvar_produto,
    listar_produtos,
    pegar_produto_por_id,
    adicionar_ao_carrinho,
    listar_carrinho,
    limpar_carrinho
)
from utls.helper import formata_float_str_moeda
from time import sleep

# Define a senha do lojista
SENHA_LOJISTA = "admin123"
# Define a chave Pix Fictícia Fixa
CHAVE_PIX_FIXA = "119988776655"

# Pasta onde as imagens serão salvas
IMAGE_DIR = "product_images"


class ShopApp(ft.Column):
    def __init__(self, page: ft.Page, snackbar_text: ft.Text):
        super().__init__()
        self.page = page
        self.page.clean()
        self.snackbar_text = snackbar_text

        self.page.appbar = ft.AppBar(
            title=ft.Text("POO Shop - Loja Virtual", weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.BLUE_GREY_700
        )

        self.product_name_input = ft.TextField(label="Nome do Produto")
        self.product_price_input = ft.TextField(label="Preço do Produto", keyboard_type=ft.KeyboardType.NUMBER)
        self.product_type_dropdown = ft.Dropdown(
            label="Tipo de Produto",
            options=[
                ft.dropdown.Option("Eletrônico"),
                ft.dropdown.Option("Roupa"),
                ft.dropdown.Option("Alimento"),
                ft.dropdown.Option("Livro"),
                ft.dropdown.Option("Outro"),
            ]
        )
        self.product_detail_input = ft.TextField(label="Detalhe (Marca ou outro):", visible=False)

        # buy_product_id_input já está definido no __init__, então vamos usá-lo
        self.buy_product_id_input = ft.TextField(label="ID do Produto para Comprar",
                                                 keyboard_type=ft.KeyboardType.NUMBER)

        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)

        self.selected_image_path = None
        self.image_preview = ft.Image(width=100, height=100, fit=ft.ImageFit.CONTAIN, visible=False)

        self.show_main_menu()

    def _update_page_content(self, content_controls):
        self.page.clean()
        self.page.add(
            self.page.appbar,
            ft.Container(
                content=ft.Column(
                    content_controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    expand=True
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        )
        self.page.update()

    def show_main_menu(self, e=None):
        menu_content = [
            ft.Text("Bem-vindo(a) à POO Shop!", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.ElevatedButton("1 - Cadastrar Produto", on_click=self.show_cadastro_produto),
            ft.ElevatedButton("2 - Listar Produtos", on_click=self.show_listar_produtos),
            ft.ElevatedButton("3 - Comprar Produto", on_click=self.show_comprar_produto),
            ft.ElevatedButton("4 - Visualizar Carrinho", on_click=self.show_visualizar_carrinho),
            ft.ElevatedButton("5 - Fechar Pedido", on_click=self.show_fechar_pedido),
            ft.ElevatedButton("6 - Sair", on_click=self.exit_app,
                              style=ft.ButtonStyle(bgcolor={ft.ControlState.DEFAULT: ft.Colors.RED_500})),

        ]
        self._update_page_content(menu_content)

    def show_snackbar(self, message: str, color=ft.Colors.GREEN_500):
        self.snackbar_text.value = message
        self.page.snack_bar.bgcolor = color
        self.page.snack_bar.open = True
        self.page.update()

    def show_cadastro_produto(self, e):
        def authenticate_and_show_form(e):
            if self.password_field.value == SENHA_LOJISTA:
                self.show_snackbar("Autenticação bem-sucedida!", ft.Colors.BLUE_600)
                self.show_cadastro_form()
            else:
                self.show_snackbar("Senha incorreta. Acesso negado.", ft.Colors.RED_500)

        self.password_field = ft.TextField(
            label="Senha do Lojista",
            password=True,
            can_reveal_password=True,
            width=300
        )
        auth_content = [
            ft.Text("Autenticação do Lojista", size=20, weight=ft.FontWeight.BOLD),
            self.password_field,
            ft.ElevatedButton("Entrar", on_click=authenticate_and_show_form),
            ft.TextButton("Voltar ao Menu", on_click=self.show_main_menu)
        ]
        self._update_page_content(auth_content)

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selected_image_path = e.files[0].path
            self.image_preview.src = self.selected_image_path
            self.image_preview.visible = True
            self.page.update()
        else:
            self.selected_image_path = None
            self.image_preview.visible = False
            self.show_snackbar("Nenhuma imagem selecionada.", ft.Colors.ORANGE_500)
            self.page.update()

    def show_cadastro_form(self):
        self.selected_image_path = None
        self.image_preview.src = None
        self.image_preview.visible = False

        self.product_name_input = ft.TextField(label="Nome do Produto", width=300)
        self.product_price_input = ft.TextField(label="Preço do Produto", keyboard_type=ft.KeyboardType.NUMBER,
                                                width=300)
        self.product_type_dropdown = ft.Dropdown(
            label="Tipo de Produto",
            options=[
                ft.dropdown.Option("comum", text="Comum"),
                ft.dropdown.Option("eletronico", text="Eletrônico"),
                ft.dropdown.Option("alimento", text="Alimento"),
                ft.dropdown.Option("educacional", text="Educacional"),
                ft.dropdown.Option("beleza", text="Beleza"),
                ft.dropdown.Option("moda", text="Moda"),
            ],
            width=300,
            on_change=self._update_detail_field
        )
        self.product_detail_input = ft.TextField(label="Detalhe (opcional)", width=300, visible=False)

        def pick_image_file(e):
            self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["png", "jpg", "jpeg", "gif"]
            )

        def save_product(e):
            print("Função save_product chamada.")
            try:
                nome = self.product_name_input.value
                preco = float(self.product_price_input.value)
                tipo = self.product_type_dropdown.value
                detalhe = self.product_detail_input.value if self.product_detail_input.visible else None

                print(f"Nome: {nome}, Preço: {preco}, Tipo: {tipo}, Detalhe: {detalhe}")
                image_db_path = None
                if self.selected_image_path:
                    print(f"Caminho da imagem selecionada: {self.selected_image_path}")
                    os.makedirs(IMAGE_DIR, exist_ok=True)

                    file_name_base, file_extension=os.path.splitext(os.path.basename(self.selected_image_path))
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    unique_file_name = f"{file_name_base}_{timestamp}_{random.randint(1000, 9999)}{file_extension}"
                    destination_path = os.path.join(IMAGE_DIR, unique_file_name)

                    print(f"Caminho de destino da imagem: {destination_path}")
                    try:
                        shutil.copy(self.selected_image_path, destination_path)
                        image_db_path = destination_path
                        self.show_snackbar(f"Imagem salva em: {destination_path}", ft.Colors.BLUE_200)
                    except Exception as copy_error:
                        print(f"Erro ao salvar imagem (shutil.copy): {copy_error}")
                        self.show_snackbar(f"Erro ao salvar imagem: {copy_error}", ft.Colors.RED_500)
                        image_db_path = None

                if not nome or not preco or not tipo:
                    print("Validação falhou: nome, preco ou tipo estão vazios.")
                    self.show_snackbar("Por favor, preencha nome, preço e tipo.", ft.Colors.RED_500)
                    return

                print("Chamando salvar_produto...")
                salvar_produto(nome, preco, tipo, detalhe, image_db_path)
                print("Produto salvo no DB com sucesso!")
                self.show_snackbar("Produto cadastrado com sucesso!")

                self.product_name_input.value = ""
                self.product_price_input.value = ""
                self.product_type_dropdown.value = None
                self.product_detail_input.value = ""
                self.product_detail_input.visible = False
                self.selected_image_path = None
                self.image_preview.src = None
                self.image_preview.visible = False
                self.page.update()
                self.show_main_menu()
            except ValueError as ve:
                print(f"Erro de ValueError: {ve}")
                self.show_snackbar("Preço inválido! Digite um número.", ft.Colors.RED_500)
            except Exception as ex:
                print(f"Erro geral inesperado: {ex}")
                self.show_snackbar(f"Erro ao cadastrar: {ex}", ft.Colors.RED_500)

        cadastro_form_content = [
            ft.Text("Cadastro de Novo Produto", size=20, weight=ft.FontWeight.BOLD),
            self.product_name_input,
            self.product_price_input,
            self.product_type_dropdown,
            self.product_detail_input,
            ft.ElevatedButton("Selecionar Imagem", on_click=pick_image_file),
            self.image_preview,
            ft.ElevatedButton("Salvar Produto", on_click=save_product),
            ft.TextButton("Voltar ao Menu", on_click=self.show_main_menu)
        ]
        self._update_page_content(cadastro_form_content)

    def _update_detail_field(self, e):
        selected_type = self.product_type_dropdown.value
        self.product_detail_input.visible = True
        if selected_type == "eletronico":
            self.product_detail_input.label = "Detalhe (Marca ou outro):"
        elif selected_type == "alimento":
            self.product_detail_input.label = "Data de validade (dd/mm/aaaa):"
        elif selected_type == "educacional":
            self.product_detail_input.label = "Área do conhecimento ou Plataforma:"
        elif selected_type == "beleza":
            self.product_detail_input.label = "Indicação (ex: pele, cabelo, tipo de pele):"
        elif selected_type == "moda":
            self.product_detail_input.label = "Tamanho (ex: M, G, 42) ou Material:"
        else:
            self.product_detail_input.visible = False
        self.page.update()

    def show_listar_produtos(self, e):
        products_data = listar_produtos()
        product_rows = []
        if products_data:
            # Cabeçalho para a tabela
            product_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("ID")),
                        ft.DataCell(ft.Text("Foto")),
                        ft.DataCell(ft.Text("Nome")),
                        ft.DataCell(ft.Text("Preço")),
                        ft.DataCell(ft.Text("Tipo")),
                        ft.DataCell(ft.Text("Detalhe")),
                    ],
                )
            )
            for p in products_data:
                image_src = p[5] if p[5] and os.path.exists(p[5]) else None
                image_control = ft.Image(src=image_src, width=50, height=50,
                                         fit=ft.ImageFit.CONTAIN) if image_src else ft.Icon(
                    ft.icons.IMAGE_NOT_SUPPORTED, size=30)

                detalhe_str = p[4] if p[4] else "N/A"
                product_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(p[0]))),
                            ft.DataCell(image_control),
                            ft.DataCell(ft.Text(p[1])),
                            ft.DataCell(ft.Text(formata_float_str_moeda(p[2]))),
                            ft.DataCell(ft.Text(p[3])),
                            ft.DataCell(ft.Text(detalhe_str)),
                        ],
                    )
                )
        else:
            product_rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Nenhum produto cadastrado.", col_span=6))]))

        products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Foto")),
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Preço")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Detalhe")),
            ],
            rows=product_rows,
            width=700,
            show_checkbox_column=False,
            heading_row_color=ft.Colors.BLUE_GREY_100,
            border=ft.border.all(1, ft.Colors.GREY),
            divider_thickness=1
        )

        content = [
            ft.Text("Produtos Cadastrados", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(products_table, padding=10, border_radius=ft.border_radius.all(5)),
            ft.ElevatedButton("Voltar ao Menu", on_click=self.show_main_menu)
        ]
        self._update_page_content(content)



    def add_product_to_cart(self, e):
        try:
            product_id = int(self.buy_product_id_input.value) # Usa o TextField inicializado
            product = pegar_produto_por_id(product_id)
            if product:
                adicionar_ao_carrinho(product[0])
                self.show_snackbar(f"Produto '{product[1]}' adicionado ao carrinho!", ft.Colors.GREEN_600)
                self.buy_product_id_input.value = "" # Limpa o campo
            else:
                self.show_snackbar("Produto não encontrado.", ft.Colors.RED_500)
        except ValueError:
            self.show_snackbar("ID inválido! Digite um número inteiro.", ft.Colors.RED_500)
        except Exception as ex:
            self.show_snackbar(f"Erro ao adicionar ao carrinho: {ex}", ft.Colors.RED_500)
        self.page.update()
