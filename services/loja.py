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
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.clean()


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
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=color,
            duration=2000,
        )
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
                    ft.Icons.IMAGE_NOT_SUPPORTED, size=30)

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
            product_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Nenhum produto cadastrado."), col_span=6)
                    ]
                )
            )

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
            product_id = int(self.buy_product_id_input.value)
            product = pegar_produto_por_id(product_id)
            if product:
                adicionar_ao_carrinho(product[0])
                self.show_snackbar(f"Produto '{product[1]}' adicionado ao carrinho!", ft.Colors.GREEN_600)
                self.buy_product_id_input.value = ""
            else:
                self.show_snackbar("Produto não encontrado.", ft.Colors.RED_500)
        except ValueError:
            self.show_snackbar("ID inválido! Digite um número inteiro.", ft.Colors.RED_500)
        except Exception as ex:
            self.show_snackbar(f"Erro ao adicionar ao carrinho: {ex}", ft.Colors.RED_500)
        self.page.update()


    def show_comprar_produto(self, e):
        products = listar_produtos()

        products_display_controls = [
            ft.Text("Produtos Disponíveis:", size=20, weight=ft.FontWeight.BOLD)
        ]

        if products:
            data_table_rows = []
            for p in products:
                data_table_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(p[0]))),  # ID
                            ft.DataCell(ft.Text(p[1])),  # Nome
                            ft.DataCell(ft.Text(f"R${p[2]:.2f}")),
                        ]
                    )
                )

            products_display_controls.append(
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Nome")),
                        ft.DataColumn(ft.Text("Preço")),
                    ],
                    rows=data_table_rows,
                    heading_row_color=ft.Colors.BLUE_GREY_100,
                    border=ft.border.all(1, ft.Colors.GREY),
                    border_radius=ft.border_radius.all(8),
                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY),
                    horizontal_lines=ft.BorderSide(1, ft.Colors.GREY),
                    sort_column_index=0,
                    sort_ascending=True,
                )
            )
        else:
            products_display_controls.append(ft.Text("Nenhum produto cadastrado ainda."))

        # Conteúdo final da página "Comprar Produto"
        content = [
            ft.Text("Comprar Produto", size=30, weight=ft.FontWeight.BOLD),
            ft.Column(products_display_controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, expand=True), # Agrupa a lista de produtos
            ft.Divider(), # Adiciona um divisor para separar a lista do input
            ft.Text("Digite o ID do produto para adicionar ao carrinho:"),
            self.buy_product_id_input, # Usa o input já inicializado
            ft.ElevatedButton("Adicionar ao Carrinho", on_click=self.add_product_to_cart), # Chama o novo método
            ft.TextButton("Voltar ao Menu", on_click=self.show_main_menu)
        ]
        self._update_page_content(content)

    def show_visualizar_carrinho(self, e):
        cart_items = listar_carrinho()
        cart_rows = []

        if cart_items:
            for item in cart_items:
                total_item = item[2] * item[5]
                cart_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item[1])),  # Nome do produto
                            ft.DataCell(ft.Text(str(item[5]))),  # Quantidade
                            ft.DataCell(ft.Text(formata_float_str_moeda(item[2]))),  # Preço unit.
                            ft.DataCell(ft.Text(formata_float_str_moeda(total_item))),  # Total item
                        ],
                    )
                )

            cart_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Produto")),
                    ft.DataColumn(ft.Text("Qtd.")),
                    ft.DataColumn(ft.Text("Preço Unit.")),
                    ft.DataColumn(ft.Text("Total Item")),
                ],
                rows=cart_rows,
                width=600,
                show_checkbox_column=False,
                heading_row_color=ft.Colors.BLUE_GREY_100,
                border=ft.border.all(1, ft.Colors.GREY),
                divider_thickness=1
            )

            content = [
                ft.Text("Seu Carrinho de Compras", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(cart_table, padding=10, border_radius=ft.border_radius.all(5)),
            ]
        else:
            content = [
                ft.Text("Seu Carrinho de Compras", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Carrinho vazio.", size=16, color=ft.Colors.GREY_700),
            ]

        content.append(ft.ElevatedButton("Voltar ao Menu", on_click=self.show_main_menu))
        self._update_page_content(content)

    def show_fechar_pedido(self, e):
        self.cart_items = listar_carrinho() #teste
        if not self.cart_items:
            self.show_snackbar("Carrinho vazio. Nada para finalizar.", ft.Colors.ORANGE_500)
            self._update_page_content([  
                ft.Text("Carrinho Vazio", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Seu carrinho está vazio. Adicione produtos antes de finalizar."),
                ft.ElevatedButton("Voltar ao Menu", on_click=self.show_main_menu)
            ])
            return

        self.total_value = sum(item[2] * item[5] for item in self.cart_items)

        resume_rows = []
        for item in self.cart_items:
            resume_rows.append(
                ft.Text(f"{item[1]} (x{item[5]}) - Total: {formata_float_str_moeda(item[2] * item[5])}")
            )

        self.payment_method_radio_group = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="pix", label="Pix"),
                    ft.Radio(value="card", label="Cartão de Crédito (Simulado)"),
                    ft.Radio(value="cash", label="Dinheiro (Simulado)"),
                ]
            ),
            value="pix" 
        )

        content = [
            ft.Text("Resumo do Pedido", size=20, weight=ft.FontWeight.BOLD),
            ft.Column(resume_rows),
            ft.Text(f"\nTotal a pagar: {formata_float_str_moeda(self.total_value)}", size=18,
                    weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Escolha o método de pagamento:", size=16),
            self.payment_method_radio_group,
            ft.ElevatedButton("Finalizar Pagamento", on_click=self.process_payment),
            ft.TextButton("Voltar ao Menu", on_click=self.show_main_menu)
        ]
        self._update_page_content(content)
        self.page.update()         

    async def process_payment(self, e):
        selected_method = self.payment_method_radio_group.value
        print(f"Processando pagamento via: {selected_method}")

        if not selected_method:
            self.show_snackbar("Por favor, selecione um método de pagamento.", ft.Colors.ORANGE_500)
            return

        if selected_method == 'pix':
            print("Chamando _simulate_pix_payment")
            self.show_snackbar("Iniciando simulação de pagamento via Pix...", ft.Colors.BLUE_400)
            await self._simulate_pix_payment()
        elif selected_method == 'card':
            self.show_snackbar("Iniciando simulação de pagamento via Cartão de Crédito...",
                               ft.Colors.BLUE_400)
            await self._simulate_card_payment()
        elif selected_method == 'cash':
            self.show_snackbar("Iniciando simulação de pagamento via Dinheiro...", ft.Colors.BLUE_400)
            await self._simulate_cash_payment()
        else:
            self.show_snackbar("Método de pagamento inválido.", ft.Colors.RED_500)
            self.show_main_menu()

    async def _simulate_pix_payment(self):
        print("Dentro de _simulate_pix_payment")

        async def simular_pagamento_concluido(e):
            await self._finalize_order_after_payment("Pix")

        async def cancelar_pagamento(e):
            await self._cancel_order("Pix")
        self._update_page_content(
            [
                ft.Text("--- SIMULAÇÃO DE PAGAMENTO VIA PIX ---", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Valor a pagar: {formata_float_str_moeda(self.total_value)}", size=18),
                ft.Text(f"Chave Pix (fictícia para simulação): {CHAVE_PIX_FIXA}", size=16),
                ft.Text("Ou escaneie o QR Code fictício abaixo:", size=16),
                ft.Container(
                    content=ft.Image(src="https://via.placeholder.com/150?text=QR+Code+Ficticio", width=150,
                                     height=150),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.BLACK)
                ),
                ft.Text("AVISO: ESTE É UM PAGAMENTO SIMULADO E NÃO EFETIVARÁ UMA TRANSFERÊNCIA REAL.",
                        color=ft.Colors.RED_600),
                ft.ElevatedButton(text="Simular Pagamento Concluído", on_click=simular_pagamento_concluido),
                ft.ElevatedButton(text="Cancelar Pagamento", on_click=cancelar_pagamento),
            ]
        )
        print("Conteúdo da página de Pix atualizado.")
        self.page.update() # Para depuração

    async def _simulate_card_payment(self):
        card_number_input = ft.TextField(label="Número do Cartão (simulado)", width=300,keyboard_type=ft.KeyboardType.NUMBER)
        card_expiry_input = ft.TextField(label="Validade (MM/AA)", width=150)
        card_cvv_input = ft.TextField(label="CVV (simulado)", width=100, password=True)

        async def complete_card_payment(e):
            if not card_number_input.value or not card_expiry_input.value or not card_cvv_input.value:
                self.show_snackbar("Por favor, preencha todos os campos do cartão.", ft.Colors.RED_500)
                return
            self.show_snackbar("Processando pagamento com cartão de crédito simulado...", ft.Colors.BLUE_400)
            await asyncio.sleep(1)
            await self._finalize_order_after_payment("Cartão")

        self._update_page_content(
            [
                ft.Text("--- SIMULAÇÃO DE PAGAMENTO VIA CARTÃO DE CRÉDITO ---", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Valor a pagar: {formata_float_str_moeda(self.total_value)}", size=18),
                card_number_input,
                ft.Row([card_expiry_input, card_cvv_input], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Text("AVISO: ESTE É UM PAGAMENTO SIMULADO E NÃO EFETIVARÁ UMA TRANSFERÊNCIA REAL.",
                        color=ft.Colors.RED_600),
                ft.ElevatedButton("Pagar com Cartão", on_click=complete_card_payment),
                ft.ElevatedButton("Cancelar Pagamento",
                                  on_click=lambda e: self._cancel_order("Cartão")),
            ]
        )
        self.page.update()

    async def _simulate_cash_payment(self):
        amount_received_input = ft.TextField(label="Valor Recebido (simulado)", width=300,
                                             keyboard_type=ft.KeyboardType.NUMBER)
        troco_text = ft.Text("")

        async def calculate_and_finalize_cash_payment(e):
            try:
                received = float(amount_received_input.value)
                troco = received - self.total_value
                if troco >= 0:
                    troco_text.value = f"Troco: {formata_float_str_moeda(troco)}"
                    self.show_snackbar("Pagamento em dinheiro simulado concluído.", ft.Colors.GREEN_600)
                    await asyncio.sleep(1)
                    await self._finalize_order_after_payment("Dinheiro")
                else:
                    troco_text.value = "Valor insuficiente."
                    self.show_snackbar("Valor insuficiente. Pagamento em dinheiro simulado negado.", ft.Colors.RED_500)
            except ValueError:
                self.show_snackbar("Valor inválido. Digite um número.", ft.Colors.RED_500)
            self.page.update()

        self._update_page_content(
            [
                ft.Text("--- SIMULAÇÃO DE PAGAMENTO VIA DINHEIRO ---", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Valor a Receber: {formata_float_str_moeda(self.total_value)}", size=18),
                amount_received_input,
                troco_text,
                ft.Text("AVISO: ESTE É UM PAGAMENTO SIMULADO E NÃO EFETIVARÁ UMA TRANSFERÊNCIA REAL.",
                        color=ft.Colors.RED_600),
                ft.ElevatedButton("Confirmar Pagamento", on_click=calculate_and_finalize_cash_payment),
                ft.ElevatedButton("Cancelar Pagamento", on_click=lambda e: self._cancel_order("Dinheiro")),
            ]
        )
        self.page.update()

    async def _simulate_cash_payment(self):
        amount_received_input = ft.TextField(label="Valor Recebido (simulado)", width=300,
                                             keyboard_type=ft.KeyboardType.NUMBER)
        troco_text = ft.Text("")

        async def calculate_and_finalize_cash_payment(e):
            try:
                received = float(amount_received_input.value)
                troco = received - self.total_value
                if troco >= 0:
                    troco_text.value = f"Troco: {formata_float_str_moeda(troco)}"
                    self.show_snackbar("Pagamento em dinheiro simulado concluído.",
                                       ft.Colors.GREEN_600)
                    await asyncio.sleep(1)
                    await self._finalize_order_after_payment("Dinheiro")
                else:
                    troco_text.value = "Valor insuficiente."
                    self.show_snackbar("Valor insuficiente. Pagamento em dinheiro simulado negado.",
                                       ft.Colors.RED_500)
            except ValueError:
                self.show_snackbar("Valor inválido. Digite um número.", ft.Colors.RED_500)
            self.page.update()

        # Remova 'await self.page.run_async(lambda: ...)'
        self._update_page_content(
            [
                ft.Text("--- SIMULAÇÃO DE PAGAMENTO VIA DINHEIRO ---", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Valor a Receber: {formata_float_str_moeda(self.total_value)}", size=18),
                amount_received_input,
                troco_text,
                ft.Text("AVISO: ESTE É UM PAGAMENTO SIMULADO E NÃO EFETIVARÁ UMA TRANSFERÊNCIA REAL.",
                        color=ft.Colors.RED_600),
                ft.ElevatedButton("Confirmar Pagamento", on_click=calculate_and_finalize_cash_payment),
                ft.ElevatedButton("Cancelar Pagamento",
                                  on_click=lambda e: self.page.run_async(self._cancel_order("Dinheiro"))),
            ]
        )
        await self.page.update_async()

    async def _finalize_order_after_payment(self, method_name: str):
        self.show_snackbar(f"Pagamento via {method_name} simulado recebido com sucesso!",
                           ft.Colors.GREEN_600)
        limpar_carrinho()
        self.show_snackbar("Pedido finalizado. Obrigado pela compra!", ft.Colors.GREEN_700)
        await asyncio.sleep(2)
        self.show_main_menu()

    async def _cancel_order(self, method_name: str):
        self.show_snackbar(f"Pagamento via {method_name} cancelado.", ft.Colors.ORANGE_500)
        await asyncio.sleep(1)
        self.show_main_menu()

    def exit_app(self, e):
        try:

            if hasattr(self.page, "window_destroy"):
                self.page.window_destroy()
            elif hasattr(self.page, "window_close"):
                self.page.window_close()
            else:
                raise AttributeError
        except AttributeError:
            self.show_snackbar("Não é possível fechar automaticamente no navegador. Feche a aba.", ft.Colors.ORANGE_500)
