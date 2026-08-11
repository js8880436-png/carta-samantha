import os
import json
import secrets
import string
from pathlib import Path

from kivy.app import App
from kivy.animation import Animation
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import platform


# ============================================================
# CARTA SAMANTHA — VERSÃO NOVA
# ============================================================
# Fluxo:
# Criar -> escrever -> escolher código -> escolher capa
# -> selar -> envelope -> código -> abrir -> carta -> memórias
#
# Dados de texto/configuração ficam no diretório privado do app.
# A pasta pública antiga é mantida como fonte de mídia para
# preservar compatibilidade com o projeto anterior.
# ============================================================


APP_NOME = "Carta Samantha"

FOTOS_EXT = (".jpg", ".jpeg", ".png", ".webp")
VIDEOS_EXT = (".mp4", ".mkv", ".3gp", ".mov")


# ============================================================
# CORES
# ============================================================

PAPEL = (0.89, 0.80, 0.64, 1)
PAPEL_CLARO = (0.96, 0.90, 0.76, 1)
PAPEL_CARTA = (0.94, 0.86, 0.69, 1)

MARROM = (0.27, 0.16, 0.08, 1)
MARROM_CLARO = (0.42, 0.28, 0.15, 1)

VINHO = (0.43, 0.10, 0.12, 1)
VERMELHO_SELO = (0.55, 0.08, 0.10, 1)

BRANCO = (1, 0.97, 0.88, 1)


# ============================================================
# CAMINHOS
# ============================================================

def app_dir():
    return Path(App.get_running_app().user_data_dir)


def pasta_dados():
    caminho = app_dir() / "carta"
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def pasta_midia_interna():
    caminho = pasta_dados() / "memorias"
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def pasta_publica_antiga():
    # Compatibilidade com a versão anterior do projeto.
    return Path(
        "/storage/emulated/0/Pictures/ParaAlguemEspecial"
    )


ARQUIVO_CONFIG = pasta_dados() / "config.json"
ARQUIVO_MENSAGEM = pasta_dados() / "mensagem.txt"


# ============================================================
# CONFIGURAÇÃO
# ============================================================

def codigo_novo():
    alfabeto = string.ascii_uppercase + string.digits
    return "SAM-" + "".join(
        secrets.choice(alfabeto) for _ in range(4)
    )


def config_padrao():
    return {
        "finalizado": False,
        "fonte": 24,
        "codigo": codigo_novo(),
        "principal": "",
        "titulo": "Uma carta para você",
    }


def carregar_config():
    pasta_dados()

    if not ARQUIVO_CONFIG.exists():
        config = config_padrao()
        salvar_config(config)
        return config

    try:
        with ARQUIVO_CONFIG.open(
            "r",
            encoding="utf-8"
        ) as arquivo:
            config = json.load(arquivo)

        if not isinstance(config, dict):
            raise ValueError("Configuração inválida")

        base = config_padrao()
        base.update(config)

        if not base.get("codigo"):
            base["codigo"] = codigo_novo()

        return base

    except Exception as erro:
        print("Erro ao carregar configuração:", erro)
        return config_padrao()


def salvar_config(config):
    pasta_dados()

    try:
        with ARQUIVO_CONFIG.open(
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(
                config,
                arquivo,
                indent=4,
                ensure_ascii=False
            )
    except Exception as erro:
        print("Erro ao salvar configuração:", erro)


def carregar_mensagem():
    if not ARQUIVO_MENSAGEM.exists():
        return ""

    try:
        return ARQUIVO_MENSAGEM.read_text(
            encoding="utf-8"
        )
    except Exception as erro:
        print("Erro ao carregar mensagem:", erro)
        return ""


def salvar_mensagem(texto):
    pasta_dados()

    ARQUIVO_MENSAGEM.write_text(
        texto,
        encoding="utf-8"
    )


# ============================================================
# FONTE MANUSCRITA
# ============================================================

FONTE_MANUSCRITA = None


def procurar_fonte():
    global FONTE_MANUSCRITA

    candidatos = [
        Path("manuscrita.ttf"),
        Path("manuscrito.ttf"),
        Path("carta.ttf"),
        Path("handwriting.ttf"),
        Path("script.ttf"),
        Path("estilo.ttf"),
        pasta_midia_interna() / "manuscrita.ttf",
        pasta_publica_antiga() / "manuscrita.ttf",
    ]

    for caminho in candidatos:
        try:
            if not caminho.exists():
                continue

            LabelBase.register(
                name="CartaManuscrita",
                fn_regular=str(caminho)
            )

            FONTE_MANUSCRITA = "CartaManuscrita"
            return FONTE_MANUSCRITA

        except Exception as erro:
            print("Erro ao carregar fonte:", erro)

    FONTE_MANUSCRITA = None
    return None


# ============================================================
# MÍDIA
# ============================================================

def caminhos_midia():
    encontrados = []

    fontes = [
        pasta_midia_interna(),
        pasta_publica_antiga(),
    ]

    vistos = set()

    for pasta in fontes:
        try:
            if not pasta.exists():
                continue

            for item in pasta.iterdir():
                if not item.is_file():
                    continue

                ext = item.suffix.lower()

                if ext not in FOTOS_EXT + VIDEOS_EXT:
                    continue

                chave = str(item.resolve())

                if chave in vistos:
                    continue

                vistos.add(chave)
                encontrados.append(item)

        except Exception as erro:
            print("Erro ao listar mídia:", erro)

    return sorted(
        encontrados,
        key=lambda p: p.name.lower()
    )


def fotos():
    return [
        caminho
        for caminho in caminhos_midia()
        if caminho.suffix.lower() in FOTOS_EXT
    ]


def videos():
    return [
        caminho
        for caminho in caminhos_midia()
        if caminho.suffix.lower() in VIDEOS_EXT
    ]


def encontrar_principal():
    config = carregar_config()
    salvo = config.get("principal", "")

    if salvo:
        caminho = Path(salvo)
        if caminho.exists():
            return caminho

    nomes = [
        "principal.jpg",
        "principal.jpeg",
        "principal.png",
        "principal.webp",
    ]

    for base in (
        pasta_midia_interna(),
        pasta_publica_antiga(),
    ):
        for nome in nomes:
            caminho = base / nome
            if caminho.exists():
                return caminho

    lista = fotos()

    if lista:
        return lista[0]

    return None


# ============================================================
# PERMISSÕES ANDROID
# ============================================================

def pedir_permissoes_android():
    if platform != "android":
        return

    try:
        from android.permissions import request_permissions
        from android.permissions import Permission

        permissoes = []

        for nome in (
            "READ_MEDIA_IMAGES",
            "READ_MEDIA_VIDEO",
            "READ_EXTERNAL_STORAGE",
        ):
            if hasattr(Permission, nome):
                permissoes.append(getattr(Permission, nome))

        if permissoes:
            request_permissions(permissoes)

    except Exception as erro:
        print("Permissões Android:", erro)


# ============================================================
# BOTÕES
# ============================================================

class BotaoCarta(Button):

    def __init__(self, selo=False, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*(VERMELHO_SELO if selo else VINHO))

            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18],
            )

            if not selo:
                Color(*PAPEL_CLARO)

                self.borda = Line(
                    rounded_rectangle=(
                        self.x,
                        self.y,
                        self.width,
                        self.height,
                        18,
                    ),
                    width=1.2,
                )

        self.bind(
            pos=self.atualizar,
            size=self.atualizar,
        )

    def atualizar(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

        if hasattr(self, "borda"):
            self.borda.rounded_rectangle = (
                self.x,
                self.y,
                self.width,
                self.height,
                18,
            )


class FundoCarta(Screen):

    def aplicar_fundo(self, layout):
        with layout.canvas.before:
            Color(*PAPEL)

            self.fundo = RoundedRectangle(
                pos=layout.pos,
                size=layout.size,
            )

        layout.bind(
            pos=self.atualizar_fundo,
            size=self.atualizar_fundo,
        )

    def atualizar_fundo(self, instance, value):
        self.fundo.pos = instance.pos
        self.fundo.size = instance.size


# ============================================================
# TELA INICIAL
# ============================================================

class InicioScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[28, 24],
            spacing=16,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="✉",
                font_size=96,
                color=VINHO,
                size_hint_y=0.28,
            )
        )

        layout.add_widget(
            Label(
                text="Carta Samantha",
                font_size=34,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=58,
            )
        )

        layout.add_widget(
            Label(
                text=(
                    "Uma carta feita para ser aberta\n"
                    "como uma lembrança."
                ),
                font_size=19,
                color=MARROM_CLARO,
                halign="center",
            )
        )

        criar = BotaoCarta(
            text="♥  CRIAR CARTA",
            font_size=21,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=82,
        )

        criar.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "criador"
            )
        )

        layout.add_widget(criar)

        abrir = BotaoCarta(
            text="✉  ABRIR UMA CARTA",
            font_size=20,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=76,
        )

        abrir.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "codigo"
            )
        )

        layout.add_widget(abrir)

        self.add_widget(layout)


# ============================================================
# MODO CRIADOR
# ============================================================

class CriadorScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[16, 10],
            spacing=7,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="Escrito Para Samantha",
                font_size=29,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=52,
            )
        )

        layout.add_widget(
            Label(
                text="MODO CRIADOR",
                font_size=16,
                color=VINHO,
                size_hint_y=None,
                height=27,
            )
        )

        layout.add_widget(
            Label(
                text="Escreva sua carta",
                font_size=19,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=31,
            )
        )

        self.mensagem = TextInput(
            hint_text=(
                "Escreva aqui tudo o que "
                "você gostaria de dizer..."
            ),
            multiline=True,
            font_size=23,
            padding=[18, 18],
            foreground_color=MARROM,
            background_color=PAPEL_CARTA,
            cursor_color=VINHO,
            size_hint_y=0.33,
        )

        layout.add_widget(self.mensagem)

        layout.add_widget(
            Label(
                text="Tamanho da letra",
                font_size=17,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=28,
            )
        )

        fontes = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=58,
        )

        for tamanho in (18, 22, 26, 31):
            botao = BotaoCarta(
                text="A",
                font_size=tamanho,
                color=BRANCO,
            )

            botao.bind(
                on_release=lambda btn,
                t=tamanho:
                self.escolher_fonte(t)
            )

            fontes.add_widget(botao)

        layout.add_widget(fontes)

        botoes = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=70,
        )

        capa = BotaoCarta(
            text="🖼  CAPA",
            font_size=17,
            bold=True,
            color=BRANCO,
        )

        capa.bind(
            on_release=self.abrir_capa
        )

        botoes.add_widget(capa)

        memorias = BotaoCarta(
            text="📜  MEMÓRIAS",
            font_size=17,
            bold=True,
            color=BRANCO,
        )

        memorias.bind(
            on_release=self.abrir_galeria
        )

        botoes.add_widget(memorias)

        layout.add_widget(botoes)

        codigo = BotaoCarta(
            text="🔐  DEFINIR CÓDIGO",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=68,
        )

        codigo.bind(
            on_release=self.abrir_configuracao
        )

        layout.add_widget(codigo)

        self.status = Label(
            text="",
            font_size=14,
            color=VINHO,
            halign="center",
            size_hint_y=None,
            height=28,
        )

        layout.add_widget(self.status)

        selar = BotaoCarta(
            text="♥  SELAR A CARTA",
            font_size=21,
            bold=True,
            color=BRANCO,
            selo=True,
            size_hint_y=None,
            height=82,
        )

        selar.bind(
            on_release=self.finalizar
        )

        layout.add_widget(selar)

        self.add_widget(layout)

    def on_enter(self):
        procurar_fonte()

        config = carregar_config()

        self.mensagem.text = carregar_mensagem()
        self.mensagem.font_size = config.get(
            "fonte",
            24
        )

        if FONTE_MANUSCRITA:
            try:
                self.mensagem.font_name = FONTE_MANUSCRITA
            except Exception:
                pass

        self.status.text = (
            "Código atual: "
            + str(config.get("codigo", ""))
        )

    def escolher_fonte(self, tamanho):
        self.mensagem.font_size = tamanho

        config = carregar_config()
        config["fonte"] = tamanho
        salvar_config(config)

    def abrir_galeria(self, instance):
        self.manager.current = "galeria"

    def abrir_capa(self, instance):
        self.manager.current = "capa"

    def abrir_configuracao(self, instance):
        self.manager.current = "configuracao"

    def finalizar(self, instance):
        texto = self.mensagem.text.strip()

        if not texto:
            self.status.text = (
                "Escreva a carta antes de selá-la."
            )
            return

        try:
            salvar_mensagem(texto)

            config = carregar_config()
            config["finalizado"] = True

            principal = encontrar_principal()

            if principal:
                config["principal"] = str(principal)

            if not config.get("codigo"):
                config["codigo"] = codigo_novo()

            salvar_config(config)

            self.manager.current = "envelope"

        except Exception as erro:
            self.status.text = (
                "Não foi possível salvar a carta."
            )
            print("Erro ao finalizar:", erro)


# ============================================================
# CONFIGURAÇÃO DO CÓDIGO
# ============================================================

class ConfiguracaoScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[25, 20],
            spacing=14,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="🔐 Código da carta",
                font_size=31,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=60,
            )
        )

        layout.add_widget(
            Label(
                text=(
                    "Escolha o código que será usado\n"
                    "para abrir a carta."
                ),
                font_size=18,
                color=MARROM_CLARO,
                halign="center",
                size_hint_y=None,
                height=60,
            )
        )

        self.codigo = TextInput(
            hint_text="Ex.: SAM-7K4P",
            multiline=False,
            halign="center",
            font_size=25,
            foreground_color=MARROM,
            background_color=PAPEL_CARTA,
            cursor_color=VINHO,
            size_hint_y=None,
            height=68,
        )

        layout.add_widget(self.codigo)

        gerar = BotaoCarta(
            text="✨  GERAR CÓDIGO",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=70,
        )

        gerar.bind(
            on_release=self.gerar
        )

        layout.add_widget(gerar)

        salvar = BotaoCarta(
            text="♥  SALVAR CÓDIGO",
            font_size=19,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=76,
        )

        salvar.bind(
            on_release=self.salvar
        )

        layout.add_widget(salvar)

        self.status = Label(
            text="",
            font_size=16,
            color=VINHO,
            halign="center",
        )

        layout.add_widget(self.status)

        voltar = BotaoCarta(
            text="←  VOLTAR",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=65,
        )

        voltar.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "criador"
            )
        )

        layout.add_widget(voltar)

        self.add_widget(layout)

    def on_enter(self):
        config = carregar_config()
        self.codigo.text = str(
            config.get("codigo", "")
        )
        self.status.text = ""

    def gerar(self, instance):
        self.codigo.text = codigo_novo()

    def salvar(self, instance):
        valor = self.codigo.text.strip().upper()

        if len(valor) < 4:
            self.status.text = (
                "Escolha um código com pelo menos 4 caracteres."
            )
            return

        config = carregar_config()
        config["codigo"] = valor
        salvar_config(config)

        self.status.text = "Código salvo."

        self.manager.current = "criador"


# ============================================================
# GALERIA / MEMÓRIAS
# ============================================================

class GaleriaScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[12, 9],
            spacing=8,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="Memórias da Carta",
                font_size=29,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=50,
            )
        )

        self.status = Label(
            text="",
            font_size=16,
            color=VINHO,
            size_hint_y=None,
            height=32,
        )

        layout.add_widget(self.status)

        scroll = ScrollView()

        self.grade = GridLayout(
            cols=2,
            spacing=10,
            padding=5,
            size_hint_y=None,
        )

        self.grade.bind(
            minimum_height=self.grade.setter(
                "height"
            )
        )

        scroll.add_widget(self.grade)
        layout.add_widget(scroll)

        voltar = BotaoCarta(
            text="←  VOLTAR",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=68,
        )

        voltar.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "criador"
            )
        )

        layout.add_widget(voltar)

        self.add_widget(layout)

    def on_enter(self):
        self.carregar()

    def carregar(self):
        self.grade.clear_widgets()

        arquivos = caminhos_midia()

        self.status.text = (
            str(len(arquivos))
            + " memória(s) encontradas"
        )

        for caminho in arquivos:
            ext = caminho.suffix.lower()

            if ext in FOTOS_EXT:
                item = Image(
                    source=str(caminho),
                    size_hint_y=None,
                    height=190,
                    allow_stretch=True,
                    keep_ratio=True,
                )

                self.grade.add_widget(item)

            elif ext in VIDEOS_EXT:
                item = BotaoCarta(
                    text="▶\nVÍDEO",
                    font_size=25,
                    color=BRANCO,
                    size_hint_y=None,
                    height=190,
                )

                item.bind(
                    on_release=lambda btn,
                    arquivo=caminho:
                    self.abrir_video(arquivo)
                )

                self.grade.add_widget(item)

    def abrir_video(self, caminho):
        app = self.manager

        video = app.get_screen("video")
        video.carregar(str(caminho))

        app.current = "video"


# ============================================================
# ESCOLHA DA CAPA
# ============================================================

class CapaScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[15, 12],
            spacing=10,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="Escolha a foto de capa",
                font_size=29,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=52,
            )
        )

        self.status = Label(
            text="Toque em uma foto para usar como capa.",
            font_size=16,
            color=VINHO,
            size_hint_y=None,
            height=34,
        )

        layout.add_widget(self.status)

        scroll = ScrollView()

        self.grade = GridLayout(
            cols=2,
            spacing=10,
            padding=5,
            size_hint_y=None,
        )

        self.grade.bind(
            minimum_height=self.grade.setter(
                "height"
            )
        )

        scroll.add_widget(self.grade)
        layout.add_widget(scroll)

        voltar = BotaoCarta(
            text="←  VOLTAR",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=68,
        )

        voltar.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "criador"
            )
        )

        layout.add_widget(voltar)

        self.add_widget(layout)

    def on_enter(self):
        self.carregar()

    def carregar(self):
        self.grade.clear_widgets()

        lista = fotos()

        if not lista:
            self.status.text = (
                "Nenhuma foto encontrada."
            )
            return

        self.status.text = (
            "Toque na foto que será a capa."
        )

        for caminho in lista:
            caixa = BoxLayout(
                orientation="vertical",
                spacing=5,
                size_hint_y=None,
                height=245,
            )

            imagem = Image(
                source=str(caminho),
                size_hint_y=None,
                height=190,
                allow_stretch=True,
                keep_ratio=True,
            )

            escolher = BotaoCarta(
                text="USAR COMO CAPA",
                font_size=14,
                bold=True,
                color=BRANCO,
                size_hint_y=None,
                height=48,
            )

            escolher.bind(
                on_release=lambda btn,
                arquivo=caminho:
                self.escolher(arquivo)
            )

            caixa.add_widget(imagem)
            caixa.add_widget(escolher)

            self.grade.add_widget(caixa)

    def escolher(self, caminho):
        config = carregar_config()
        config["principal"] = str(caminho)
        salvar_config(config)

        self.status.text = (
            "Capa escolhida."
        )


# ============================================================
# ENVELOPE
# ============================================================

class EnvelopeScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[25, 22],
            spacing=14,
        )

        self.aplicar_fundo(layout)

        self.envelope = Label(
            text="✉",
            font_size=150,
            color=VINHO,
            size_hint_y=0.48,
        )

        layout.add_widget(self.envelope)

        self.titulo = Label(
            text="Carta selada",
            font_size=33,
            bold=True,
            color=MARROM,
            size_hint_y=None,
            height=58,
        )

        layout.add_widget(self.titulo)

        self.info = Label(
            text=(
                "O envelope está fechado.\n"
                "A carta está pronta para ser entregue."
            ),
            font_size=19,
            color=MARROM_CLARO,
            halign="center",
        )

        layout.add_widget(self.info)

        abrir = BotaoCarta(
            text="♥  ABRIR ENVELOPE",
            font_size=21,
            bold=True,
            color=BRANCO,
            selo=True,
            size_hint_y=None,
            height=82,
        )

        abrir.bind(
            on_release=self.abrir
        )

        layout.add_widget(abrir)

        self.add_widget(layout)

    def on_enter(self):
        self.envelope.opacity = 1
        self.titulo.opacity = 1
        self.info.opacity = 1

    def abrir(self, instance):
        anim = Animation(
            opacity=0,
            duration=0.22
        )

        anim.bind(
            on_complete=self.finalizar_animacao
        )

        anim.start(self.envelope)

    def finalizar_animacao(self, *args):
        self.manager.current = "codigo"


# ============================================================
# CÓDIGO
# ============================================================

class CodigoScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[28, 25],
            spacing=12,
        )

        self.aplicar_fundo(layout)

        layout.add_widget(
            Label(
                text="✉",
                font_size=86,
                color=VINHO,
                size_hint_y=0.20,
            )
        )

        layout.add_widget(
            Label(
                text="Você recebeu uma carta",
                font_size=29,
                bold=True,
                color=MARROM,
                size_hint_y=None,
                height=53,
            )
        )

        layout.add_widget(
            Label(
                text="Digite o código para abri-la.",
                font_size=18,
                color=MARROM_CLARO,
                halign="center",
                size_hint_y=None,
                height=45,
            )
        )

        self.codigo = TextInput(
            hint_text="Código",
            password=True,
            multiline=False,
            halign="center",
            font_size=25,
            foreground_color=MARROM,
            background_color=PAPEL_CARTA,
            cursor_color=VINHO,
            size_hint_y=None,
            height=68,
        )

        layout.add_widget(self.codigo)

        entrar = BotaoCarta(
            text="♥  ABRIR CARTA",
            font_size=21,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=82,
        )

        entrar.bind(
            on_release=self.verificar
        )

        layout.add_widget(entrar)

        self.status = Label(
            text="",
            font_size=16,
            color=VINHO,
            halign="center",
        )

        layout.add_widget(self.status)

        voltar = BotaoCarta(
            text="←  VOLTAR",
            font_size=17,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=62,
        )

        voltar.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "inicio"
            )
        )

        layout.add_widget(voltar)

        self.add_widget(layout)

    def on_enter(self):
        self.codigo.text = ""
        self.status.text = ""

    def verificar(self, instance):
        digitado = self.codigo.text.strip().upper()
        config = carregar_config()

        correto = str(
            config.get("codigo", "")
        ).strip().upper()

        if not correto:
            self.status.text = (
                "Esta carta ainda não possui código."
            )
            return

        if digitado == correto:
            self.codigo.text = ""
            self.manager.current = "carta"
        else:
            self.status.text = "Código incorreto."


# ============================================================
# CARTA ABERTA
# ============================================================

class CartaScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[14, 12],
            spacing=9,
        )

        self.aplicar_fundo(layout)

        self.capa = Image(
            size_hint_y=0.28,
            allow_stretch=True,
            keep_ratio=True,
        )

        layout.add_widget(self.capa)

        config = carregar_config()

        self.titulo = Label(
            text=config.get(
                "titulo",
                "Uma carta para você"
            ),
            font_size=28,
            bold=True,
            color=MARROM,
            size_hint_y=None,
            height=52,
        )

        layout.add_widget(self.titulo)

        scroll = ScrollView()

        self.texto = Label(
            text="",
            font_size=24,
            color=MARROM,
            halign="left",
            valign="top",
            text_size=(None, None),
            size_hint_y=None,
        )

        self.texto.bind(
            texture_size=self.texto.setter(
                "size"
            )
        )

        scroll.add_widget(self.texto)
        layout.add_widget(scroll)

        botoes = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=70,
        )

        memorias = BotaoCarta(
            text="📜  MEMÓRIAS",
            font_size=17,
            bold=True,
            color=BRANCO,
        )

        memorias.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "memorias"
            )
        )

        botoes.add_widget(memorias)

        inicio = BotaoCarta(
            text="←  INÍCIO",
            font_size=17,
            bold=True,
            color=BRANCO,
        )

        inicio.bind(
            on_release=lambda *_:
            setattr(
                self.manager,
                "current",
                "inicio"
            )
        )

        botoes.add_widget(inicio)

        layout.add_widget(botoes)

        self.add_widget(layout)

    def on_enter(self):
        config = carregar_config()

        self.texto.text = carregar_mensagem()
        self.texto.font_size = config.get(
            "fonte",
            24
        )

        if FONTE_MANUSCRITA:
            try:
                self.texto.font_name = FONTE_MANUSCRITA
            except Exception:
                pass

        principal = encontrar_principal()

        if principal and principal.exists():
            self.capa.source = str(principal)
            self.capa.opacity = 1
        else:
            self.capa.source = ""
            self.capa.opacity = 0


# ============================================================
# MEMÓRIAS DO DESTINATÁRIO
# ============================================================

class MemoriasScreen(GaleriaScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def voltar_para_carta(self, instance):
        self.manager.current = "carta"


# ============================================================
# VÍDEO
# ============================================================

class VideoScreen(FundoCarta):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[12, 12],
            spacing=10,
        )

        self.aplicar_fundo(layout)

        self.video = Video(
            state="stop",
            options={
                "eos": "stop",
            },
        )

        layout.add_widget(self.video)

        voltar = BotaoCarta(
            text="←  VOLTAR ÀS MEMÓRIAS",
            font_size=18,
            bold=True,
            color=BRANCO,
            size_hint_y=None,
            height=70,
        )

        voltar.bind(
            on_release=self.voltar
        )

        layout.add_widget(voltar)

        self.add_widget(layout)

    def carregar(self, caminho):
        self.video.state = "stop"
        self.video.source = caminho
        self.video.state = "play"

    def voltar(self, instance):
        self.video.state = "stop"
        self.video.source = ""
        self.manager.current = "memorias"


# ============================================================
# APLICATIVO
# ============================================================

class CartaSamanthaApp(App):

    title = APP_NOME

    def build(self):
        pasta_dados()
        pasta_midia_interna()

        pedir_permissoes_android()
        procurar_fonte()

        sm = ScreenManager(
            transition=FadeTransition(
                duration=0.18
            )
        )

        sm.add_widget(
            InicioScreen(name="inicio")
        )

        sm.add_widget(
            CriadorScreen(name="criador")
        )

        sm.add_widget(
            ConfiguracaoScreen(
                name="configuracao"
            )
        )

        sm.add_widget(
            GaleriaScreen(name="galeria")
        )

        sm.add_widget(
            CapaScreen(name="capa")
        )

        sm.add_widget(
            EnvelopeScreen(name="envelope")
        )

        sm.add_widget(
            CodigoScreen(name="codigo")
        )

        sm.add_widget(
            CartaScreen(name="carta")
        )

        sm.add_widget(
            MemoriasScreen(name="memorias")
        )

        sm.add_widget(
            VideoScreen(name="video")
        )

        return sm


if __name__ == "__main__":
    CartaSamanthaApp().run()
