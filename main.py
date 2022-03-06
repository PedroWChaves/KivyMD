from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivymd.uix.button import MDIconButton, MDFloatingActionButtonSpeedDial
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import (
    MDList,
    TwoLineListItem,
    TwoLineAvatarIconListItem,
    OneLineIconListItem,
    IRightBodyTouch,
    IconLeftWidgetWithoutTouch,
    ImageLeftWidget,
    )

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty, OptionProperty, NumericProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, NoTransition, SlideTransition, CardTransition, SwapTransition, FadeTransition, WipeTransition, FallOutTransition, RiseInTransition

import random as r
import urllib
import os

from dialogs import *
from json_file import *
from database import *
# from imdb_api import *


# FUNÇÕES GLOBAIS
def get_info(movie_info, *args):
    order = ("title", "imdbId", "year", "genres", "priority")
    infos = [movie_info[order.index(arg)] for arg in args]
    return infos if len(infos) > 1 else infos[0]

def get_info_index(*args):
    order = ("title", "imdbId", "year", "genres", "priority")
    infos = [order.index(arg) for arg in args]
    return infos if len(infos) > 1 else infos[0]

def get_texts_from_info(info):
    genres = ""
    for genre in get_info(info, "genres").split(","):
        genres += genre + " / "
    genres = genres[:-2]

    return f'{get_info(info, "year")} - {get_info(info, "title")}', genres

def get_info_from_texts(text, secondary_text):
    year, title = text.split(" - ")
    genres = ",".join(secondary_text.split(" / "))
    return year, title, genres


# DEFINIÇÕES DE CLASSES
class LogInScreen(MDScreen):
    pass

class SignUpScreen(MDScreen):
    pass

class MovieSearchNotFound(MDCard):
    pass

class SearchMovieResultsScreen(MDScreen):
    def on_leave(self, *args):
        self.show_searching()
        self.ids.container.clear_widgets()

    def show_searching(self, *args):
        self.ids.toolbar.title = "Buscando..."
        self.ids.toolbar.right_action_items = [[""]]

    def show_results(self, items):
        self.items = items
        self.ids.toolbar.title = "Resultados da Busca:"
        self.ids.toolbar.right_action_items = [["check", CineFile.get_running_app().select_movie_info]]

        self.ids.container.add_widget(MovieSwiper())

        for item in items:
            self.ids.container.children[0].add_widget(
                MovieSwiperItem(
                    image = item['image'],
                    title = item['title'],
                    description = item['description']
                )
            )

    def show_not_found(self, *args):
        self.ids.toolbar.title = "Não Encontrado"
        self.ids.container.add_widget(MovieSearchNotFound())


class MainScreen(MDScreen):
    pass

class MyScreenManager(ScreenManager):
    screen_dict = {
        "main": "MainScreen()",
        "log_in": "LogInScreen()",
        "sign_up": "SignUpScreen()",
        "movie_results": "SearchMovieResultsScreen()"
    }

    def load_screen(self, profile_data, app):
        if profile_data['accountname']:
            self.add_widget(MainScreen())
            app.screen = self.get_screen("main").ids
            self.current = 'main'
            return True

        self.add_widget(LogInScreen())
        self.current = 'log_in'
        return False

    def change_screen(self, screen, transition="SlideTransition()"):
        if not self.has_screen(screen):
            self.add_widget(eval(self.screen_dict[screen]))

        self.transition = eval(transition)
        self.current = screen

        return self.current_screen

    def get_login_info(self, app, email, password, *args):
        # IMPLEMENTAR FIREBASE
        login_text = email.text
        login_password = password.text

        if login_text in {app.data["profile"]["accountname"], app.data["profile"]["email"]}:
            if login_password == app.data["profile"]["password"]:
                self.change_screen("main", "SlideTransition(direction='left')")
            else:
                # shake effect
                print("senha inválida")

        else:
            # shake effect
            print("perfil não encontrado")

    def get_signup_info(self, app, container, *args):
        data = [child.text for child in container.children[2:-2]]
        
        # IMPLEMENTAR FIREBASE

        if data[1] == data[2]:
            self.change_screen("main", "SlideTransition(direction='left')")
        else:
            print("senhas nao coincidem")


class Tab(FloatLayout, MDTabsBase):
    pass

class MDCardElev(MDCard, FakeRectangularElevationBehavior):
    pass

class MenuItem(OneLineIconListItem):
    icon = StringProperty()

class RightCheck(BoxLayout):
    text = StringProperty()
    group = StringProperty()

class LeftCheck(BoxLayout):
    text = StringProperty()
    group = StringProperty()

class SpeedDialButton(MDFloatingActionButtonSpeedDial):
    autoclose = None
    close_time = 5

    def buttons(self, *args):
        return {
            "      Deletar      ": "delete",
            "Procurar IMDb": "movie-search",
            "      Sortear      ": "dice-3",
            "      Ordenar     ": "format-list-numbered",
            "    Adicionar    ": "playlist-plus",
        }

    def set_close_time(self, option):
        options = (5, 0.55)
        self.close_time = options[option]

    def close(self, *args):
        self.close_stack()
        self.autoclose = None

    def on_open(self, *args):
        self.autoclose = Clock.schedule_once(self.close, self.close_time)

    def on_close(self, *args):
        if self.autoclose:
            self.autoclose.cancel()
            self.autoclose = None
    
# LISTA ONDE FICAM OS FILMES
class MovieList(MDList):
    def add_item_info(self, index, info):
        item = list(reversed(self.children))[index]
        item.add_data_icons(info)

    def add_many_item_infos(self, index, infos):
        items = list(reversed(self.children))[index:index+len(infos)]

        for x, item in enumerate(items):
            item.add_data_icons(infos[x])

    def edit_item_info(self, index, info):
        item = list(reversed(self.children))[index]
        item.add_data(info)

    def edit_many_item_infos(self, start, end, infos):
        items = list(reversed(self.children))[start:end]

        for x, item in enumerate(items):
            item.add_data(infos[x])

    def delete_item_info(self, index=-1):
        item = list(reversed(self.children))[index]
        item.delete_data_icons()

    def delete_many_item_infos(self, start, end):
        items = list(reversed(self.children))[start:end]

        for item in items:
            item.delete_data_icons()

    def delete_to_end_infos(self, start):
        items = list(reversed(self.children))[start:]

        for item in items:
            item.delete_data_icons()

    def delete_from_start_infos(self, end):
        items = list(reversed(self.children))[:end]

        for item in items:
            item.delete_data_icons()

    def clear_item_infos(self):
        items = self.children

        for item in items:
            item.delete_data_icons()

    def add_item_widget(self):
        self.add_widget(MovieListItem())

    def add_many_item_widgets(self, num_widgets):
        for x in range(num_widgets):
            self.add_widget(MovieListItem())

    def delete_item_widget(self, index=-1):
        self.remove_widget(list(reversed(self.children))[index])

    def delete_many_item_widgets(self, start, end):
        for item in list(reversed(self.children))[start:end]:
            self.remove_widget(item)

    def delete_to_end_widgets(self, start):
        for item in list(reversed(self.children))[start:]:
            self.remove_widget(item)

    def delete_from_start_widgets(self, end):
        for item in list(reversed(self.children))[:end]:
            self.remove_widget(item)

    def clear_item_widgets(self):
        to_delete = self.children.copy()
        for item in to_delete:
            self.remove_widget(item)

    def order_list(self, database, order):
        new_order = database.get_table(order)
        self.add_many_item_infos(0, new_order)

    def select_random(self, app, *args):
        selected = r.choice(self.children)
        while selected.isempty():
            selected = r.choice(self.children)

        selected.select(app)
        return selected

    def select_item(self, app, item_name):
        if not item_name:
            return None

        for child in self.children:
            if child.text == item_name:
                child.select(app)
                return child
        else:
            return None

# ITEM DA LISTA
class MovieListItem(TwoLineAvatarIconListItem):
    rightIcon = leftIcon = None

    def isempty(self):
        return not self.get_texts()[0]

    def add_data(self, data):
        self.text, self.secondary_text = get_texts_from_info(data)

    def add_data_icons(self, data):
        self.text, self.secondary_text = get_texts_from_info(data)
        self.rightIcon = MovieListItemRightIcon()
        self.leftIcon = MovieListItemLeftIcon()
        self.add_widget(self.rightIcon)
        self.add_widget(self.leftIcon)

    def delete_data(self):
        self.text = self.secondary_text = ""

    def delete_data_icons(self):
        self.text = self.secondary_text = ""
        if self.rightIcon and self.leftIcon:
            self.children[0].remove_widget(self.rightIcon)
            self.children[1].remove_widget(self.leftIcon)
            self.rightIcon = self.leftIcon = None

    def get_texts(self):
        return self.text, self.secondary_text

    def get_data(self):
        return get_info_from_texts(self.text, self.secondary_text)

    def select(self, app):
        self.bg_color = app.theme_cls.accent_light

        if app.theme_cls.theme_style == "Dark":
            self.text_color = app.theme_cls.opposite_text_color
            self.secondary_text_color = app.theme_cls.opposite_secondary_text_color
            self.leftIcon.text_color = app.theme_cls.bg_darkest
            self.rightIcon.text_color = app.theme_cls.bg_darkest

    def deselect(self, app):
        self.bg_color = app.theme_cls.bg_normal

        if app.theme_cls.theme_style == "Dark":
            self.text_color = app.theme_cls.text_color
            self.secondary_text_color = app.theme_cls.secondary_text_color
            self.leftIcon.text_color = app.theme_cls.opposite_bg_darkest
            self.rightIcon.text_color = app.theme_cls.opposite_bg_darkest

    def change_icon(self, new_icon):
        if not self.rightIcon: return
        self.rightIcon.icon = new_icon

# ICONE DA ESQUERDA
class MovieListItemLeftIcon(IconLeftWidgetWithoutTouch):
    pass

# ICONE DA DIRETA
class MovieListItemRightIcon(IRightBodyTouch, MDIconButton):
    def right_icon_callback(self, app):
        if self.icon == "dots-vertical":
            app.open_menu(self)

        elif self.icon == "checkbox-blank-outline":
            if self.parent.parent == app.selected:
                self.text_color = "black"
            elif app.theme_cls.theme_style == "Dark":
                self.text_color = app.theme_cls.accent_light
            else:
                self.text_color = app.theme_cls.accent_dark
            self.icon = "checkbox-marked"

            app.selected_items.append(self.parent.parent)

        elif self.icon == "checkbox-marked":
            self.icon = "checkbox-blank-outline"
            if self.parent.parent == app.selected:
                self.text_color = "black"
            else:
                self.text_color = app.theme_cls.opposite_bg_darkest

            app.selected_items.remove(self.parent.parent)


class CardMovieItem(TwoLineListItem):
    def get_data(self):
        return get_info_from_texts(self.text, self.secondary_text)

    def get_texts(self):
        return self.text, self.secondary_text

    def set_texts(self, text, secondary_text=""):
        self.text = text
        self.secondary_text = secondary_text

    def clear_texts(self):
        self.text = text
        self.secondary_text = secondary_text


class MovieSwiper(MDSwiper):
    pass

class MovieSwiperItem(MDSwiperItem):
    title = StringProperty()
    image = StringProperty()
    description = StringProperty()


# APLICATIVO EM SI
class CineFile(MDApp):
    # CONSTANTES
    JSON = "configs.json"
    DB = "movies_data.db"
    DBTABLE = "pedro_minha_lista"
    baselink = "imdb-api.com/pt-BR/API"

    # VARIAVEIS GLOBAIS
    dialog = None
    snackbar = None

    selected = None

    on_selection = False
    selected_items = []

    def change_toolbar(self, obj): # TEMPORARY
        toolbar = self.screen.toolbar
        toolbar.left_action_items = [[""]]
        toolbar.right_action_items = [[""]]

    # INICIALIZAÇÃO, FINALIZAÇÃO E REINICIALIZAÇÃO (adicionar)
    def build(self):
        # self.path = self.user_data_dir + "/"
        self.path = "files/"
        self.data, self.load_error = load_json(self.path, self.JSON)

        self.theme_cls.primary_palette = self.data['color']
        self.theme_cls.primary_hue = self.data['color_hue']
        self.theme_cls.accent_palette = self.data['accent']
        self.theme_cls.accent_hue = self.data['accent_hue']
        self.theme_cls.theme_style = self.data['theme']

        self.api_key = self.data['profile']['api_key'] # MUDAR DE LUGAR

        if platform == "win":
            Window.size = (337.5, 600)

        Builder.load_file('base_widgets.kv')
        Builder.load_file('dialogs.kv')

        return Builder.load_file('main_app.kv')

    def on_start(self):
        screen_mg = self.root.ids.screen_mg
        if screen_mg.load_screen(self.data['profile'], self):
            
            self.moviesdb = SQLdb(self.path + self.DB)#, self.DBTABLE)
            self.moviesdb.create_table(self.DBTABLE, """(
                title text,
                imdbId text,
                year integer,
                genres text,
                priority integer
            )""")
            
            self.load_movies(self.moviesdb.get_table())
            self.load_selected()

            self.load_menu(
                Detalhes = "movie-open-settings", 
                IMDb = "movie-search",
                Editar = "pencil", 
                Remover = "delete",
                Desmarcar = "checkbox-marked",
                EasterEgg = "egg-easter"
            )
            # preload(*args) -> coisas que demoram pra carregar

            if self.load_error:
                self.open_dialog(message_dialog,
                    "Erro no Arquivo JSON",
                    f'Não foi possível carregar o arquivo "{self.JSON}", um novo será gerado\n\n{self.load_error}'
                    )

            del self.load_error

            Window.bind(on_request_close=self.on_request_close)


    def on_request_close(self, *args):
        save_json(self.data, self.path, self.JSON)
        self.moviesdb.close()
        return False


    def restart_app(self):
        pass


    # LISTA PRINCIPAL
    def load_movies(self, movies_info):
        lista = self.screen.lista_filmes
        lista.add_many_item_widgets(len(movies_info)+3) # OPÇÃO DE LIMITAR OS FILMES CARREGADOS
        lista.order_list(self.moviesdb, self.data["current_order"]) # ALTERAR


    def add_movie_item(self, obj):
        movie_info = self.dialog.get_info(True)

        if not get_info(movie_info, "title"):
            return

        # GET INFO FROM IMDB
        # if get_imdb:
            # results = search_imdb_movie(title)
            # index = show_imdb_results() if show_options else 0

            # movie_info = self.get_info_imdb(results, index, movie_info, allow_substitute)

        # ADD MOVIE TO LIST
        lista = self.screen.lista_filmes
        if not lista.children[0].isempty():
            lista.add_item_widget()    
        lista.add_item_info(self.moviesdb.get_table_len()[0][0], movie_info)

        # ADD MOVIE TO DB
        self.moviesdb.add_one_to_table(movie_info)


    def edit_movie_item(self, obj, rowid):
        movie_info = self.dialog.get_info(True)

        if not get_info(movie_info, "title") or not rowid:
            return

        # GET INFO FROM IMDB
        # if get_imdb:
            # results = search_imdb_movie(title)
            # index = show_imdb_results() if show_options else 0

            # movie_info = self.get_info_imdb(results, index, movie_info, allow_substitute)

        # EDIT MOVIE IN LIST
        lista = self.screen.lista_filmes
        lista.edit_item_info(list(reversed(lista.children)).index(obj), movie_info)

        # EDIT MOVIE IN DB
        c1, c2, c3, c4, c5 = self.get_info(movie_info, "title", "imdbId", "year", "genres", "priority")
        self.moviesdb.update_entry(rowid,
            title=c1,
            imdbId=c2,
            year=c3,
            genres=c4,
            priority=c5
        )

    def delete_movie_item(self, obj, close_dialog):
        # REMOVE MOVIE IN LIST
        self.screen.lista_filmes.remove_widget(obj)

        # REMOVE MOVIE IN DB
        self.moviesdb.delete_entry(self.find_rowid_in_database(obj))

        if close_dialog:
            self.close_dialog()


    def order_list(self, *args):
        order, sort = self.dialog.get_info(True)

        if not order or not sort:
            return

        query = "ORDER BY "
        for x in range(len(sort)):
            if sort[x][0] == "-":
                sort[x] = sort[x][1:4].upper()
            else:
                sort[x] = sort[x][:4].upper()

            query += f"{order[x]} {sort[x]}, "

        query = query[:-2]
        if query == self.data["current_order"]:
            return
        
        lista = self.screen.lista_filmes
        lista.clear_item_infos()
        lista.order_list(self.moviesdb, query)
        self.selected.deselect(self)
        self.load_selected()
            
        self.data["current_order"] = query

    # IMDB INFO
    def get_info_imdb(self, movie_info): # MUDAR
        if "" in get_info(movie_info, "imdbId", "year", "genres"):
            pass # FAZER REQUEST PARA PEGAR AS INFORMAÇÕES FALTANTES

        if not get_info(movie_info, "priority"):
            movie_info[get_info_index("priority")] = 1

        return movie_info

    # MENU
    def load_menu(self, **kwargs):
        items = [
            {
                "text": key,
                "viewclass": "MenuItem",
                "icon": value,
                "on_release": lambda x=key: self.menu_callback(x, self.menu.caller),
            } for key, value in kwargs.items()
        ]

        self.menu = MDDropdownMenu(
            items = items,
            width_mult=3,
            max_height="196dp",
            border_margin="4dp",
            background_color=self.theme_cls.bg_light,
            radius=["2dp"]
        )

    def open_menu(self, button):
        if button.parent.parent == self.selected:
            self.menu.max_height = "245dp"
        else:
            self.menu.max_height = "196dp"

        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, item, obj):
        self.menu.dismiss()
        filme = obj.parent.parent

        if item == "Detalhes":
            self.open_dialog(movie_detail_dialog, filme)

        elif item == "IMDb":
            title = " ".join(reversed(filme.get_texts()[0].split(" - "))) #titulo 2011
            self.search_movie(title)
            current_screen = self.root.ids.screen_mg.change_screen("movie_results", "RiseInTransition()")
            current_screen.show_searching()

        elif item == "Editar":
            self.open_dialog(edit_movie_dialog, filme)

        elif item == "Remover":
            self.open_dialog(confirmation_dialog,
                "Você tem certeza que deseja excluir esse item?",
                self.delete_movie_item, filme, True
                )

        elif item == "Desmarcar":
            if self.selected == filme:
                filme.deselect(self)
                self.selected = None
                self.data["selected"] = ""
                self.screen.card_sorteador.set_texts("Nenhum Filme Sorteado")

        elif item == "EasterEgg": # CRIAR UMA FUNÇÃO PROPRIA PRO MINI GAME
            self.screen.avatar.icon = "emoticon-cool-outline"


    # SPEED DIAL
    def speed_dial_callback(self, instance):
        if self.on_selection:
            return

        self.screen.speed_dial.close_stack()
        button = instance.icon

        if button == "playlist-plus": # Adicionar
            self.open_dialog(add_movie_dialog)

        elif button == "movie-search": # Procurar IMDb
            pass

        elif button == "dice-3": # Sortear
            self.select_random_movie()

        elif button == "format-list-numbered": # Ordenar lista
            self.open_dialog(list_order_dialog)

        elif button == "delete": # Deletar
            self.select_movies_delete()

    # SPEED DIAL BUTTONS
    def select_random_movie(self):
        lista = self.screen.lista_filmes
        if self.selected:
            self.selected.deselect(self)

        self.selected = lista.select_random(self)
        self.data["selected"] = self.selected.text

        self.screen.card_sorteador.set_texts(self.selected.text, self.selected.secondary_text)

        # SCROLL PARA O FILME SORTEADO
        self.screen.scroll_filmes.scroll_to(self.selected, 210, True)

    def select_movies_delete(self):
        self.selection_mode(True)

        self.open_snackbar(lambda x: self.open_dialog(confirmation_dialog,
            "Você tem certeza que deseja excluir os itens selecionados?",
            self.confirm_delete
            )
        )

    def confirm_delete(self, *args):
        for item in self.selected_items:
            self.delete_movie_item(item, False)

        self.close_snackbar()
        self.close_dialog()

    # def select_movies_edit(self, obj=None): # TROCAR PARA select_movies_change_prio()
    #     self.selection_mode(True)
    #     self.open_snackbar(self.confirm_edit)

    # def confirm_edit(self, obj): # TALVEZ REMOVER ESSA OPÇÃO DE EDITAR VARIOS
    #     if not self.selected_items:
    #         self.close_snackbar()
    #         return

    #     titulos = [item.text[7:].replace(" ", "_") for item in self.selected_items]
    #     to_edit = []

    #     for item in self.moviesdb.get_table(): # ATUALIZAR
    #         if item[1] in titulos:
    #             to_edit.append(item)
    #             titulos.remove(item[1])

    #         if not titulos:
    #             break

        #abre dialogo de edição --isso que fode

        #edita filme em MovieListItem
        #edita filme em self.moviesdb

        # self.close_snackbar()


    # SNACKBAR
    def open_snackbar(self, confirm_selection):
        self.snackbar = Snackbar(
            text='    Confirmar Seleção:',
            bg_color = self.theme_cls.bg_light,
            auto_dismiss = False,
            size_hint_y = 0.08,
        )
        
        self.snackbar.buttons = [
            MDIconButton(
                icon="close",
                pos_hint = {"center_y": 0.5, "right": 1},
                text_color=self.theme_cls.opposite_text_color,
                on_release=self.close_snackbar,
            ),
            MDIconButton(
                icon="check",
                pos_hint = {"center_y": 0.5, "right": 1},
                text_color=self.theme_cls.opposite_text_color,
                on_release=confirm_selection,
            ),
        ]
        self.snackbar.open()

    def close_snackbar(self, *args):
        self.selected_items = []
        self.snackbar.dismiss()
        self.selection_mode(False)


    # DIALOGS
    def open_dialog(self, func, *args): # abre dialogs padroes
        if not self.dialog:
            self.dialog = func(self.get_running_app(), *args)
            self.dialog.open()

    def close_dialog(self, *args): # fecha dialogs e reseta pra "None"
        self.dialog.dismiss()
        self.dialog = None

    def close_and_open_dialog(self, func, *args):
        self.close_dialog()
        self.dialog = func(self.get_running_app(), *args)
        self.dialog.open()


    # CONFIGURAÇÕES APP
    def selection_mode(self, on):
        self.on_selection = on

        if on:
            for movie in self.screen.lista_filmes.children:
                movie.change_icon("checkbox-blank-outline")

        else:
            for movie in self.screen.lista_filmes.children:
                movie.change_icon("dots-vertical")
                if not movie.isempty():
                    movie.rightIcon.text_color = self.theme_cls.opposite_bg_darkest
                if movie == self.selected:
                    movie.rightIcon.text_color = "black"


    def load_selected(self):
        selected_name = self.data["selected"]
        self.selected = self.screen.lista_filmes.select_item(self, selected_name)

        if self.selected:
            self.screen.card_sorteador.set_texts(self.selected.text, self.selected.secondary_text)

            # SCROLL PARA O FILME SORTEADO
            self.screen.scroll_filmes.scroll_to(self.selected, 210, True)
        else:
            self.screen.card_sorteador.set_texts("Nenhum Filme Sorteado")       


    # BACKEND
    def find_in_db_obj(self, obj):
        movie = obj.get_data()
        movie_info = self.moviesdb.search_table(
            year=movie[0],
            title=movie[1]
            )

        return movie_info[1:], movie_info[0]


    def find_in_database(self, filme):
        ano, titulo = filme.text.split(" - ")
        return self.moviesdb.search_table(title=titulo, year=ano)


    def find_rowid_in_database(self, filme):
        ano, titulo = filme.text.split(" - ")
        return self.moviesdb.search_table(title=titulo, year=ano)[0]


    def get_info(self, *args):
        return get_info(*args)


    # CONFIGS
    def check_internet(self, obj):
        req = UrlRequest(url="https://www.google.com", timeout=5,
            on_success=lambda x, y: self.internet_on(obj),
            on_error=lambda x, y: self.internet_off(obj)
            )

    def internet_on(self, obj, *args):
        obj.icon = "wifi-check"

    def internet_off(self, obj, *args):
        obj.icon = "wifi-off"

    def edit_account(self, *args):
        profile_info = self.dialog.get_info(True)

        self.data['profile']['nickname'] = profile_info[0]
        self.data['profile']['accountname'] = profile_info[1]
        self.data['profile']['api_key'] = profile_info[2]
        self.data['profile']['profile_icon'] = profile_info[3]

        self.screen.nickname.text = profile_info[0]
        self.screen.accountname.text = "@" + profile_info[1]
        self.screen.profile_icon.icon = profile_info[3]

    def change_theme(self, *args):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

        if self.selected:
            self.selected.bg_color = self.theme_cls.accent_light
            if self.theme_cls.theme_style == "Dark":
                self.selected.text_color = self.theme_cls.opposite_text_color
                self.selected.secondary_text_color = self.theme_cls.opposite_secondary_text_color
                self.selected.leftIcon.text_color = self.theme_cls.bg_darkest
                self.selected.rightIcon.text_color = self.theme_cls.bg_darkest

        self.data['theme'] = self.theme_cls.theme_style

    def show_files_dir(self, *args):
        self.open_dialog(message_dialog,
                "Diretorio de Arquivos",
                os.path.abspath(self.path) + "\n" +
                os.path.abspath(self.user_data_dir)
                )

    def save_files(self, *args):
        save_json(self.data, self.path, self.JSON)



    def select_movie_info(self, *args):
        current_screen = self.root.ids.screen_mg.current_screen

        index = current_screen.ids.container.children[0].get_current_index()
        movie_id = current_screen.items[index]["id"]

        self.open_dialog(which_movie_info_dialog, movie_id)


    def display_movie_info(self, movie_id):
        info_type, aditional = self.dialog.get_info(True)

        self.search_movie_info(movie_id, info_type, aditional)
        current_screen = self.root.ids.screen_mg.change_screen("movie_results", "RiseInTransition()")
        current_screen.show_searching()




    # IMDb API
    def info_type(self, *args):
        return {
            'Basic': ('title', 'year', 'id', 'image', 'genres', 'runtimeStr'),

            'Complete': ('title', 'originalTitle', 'type', 'year', 'image', 'runtimeStr', 'plot', 'plotLocal', 'directors',
                'directorList', 'writers', 'writerList', 'stars', 'starList', 'actorList', 'genres', 'genreList', 'contentRating',
                'imDbRating', 'imDbRatingVotes', 'keywords', 'keywordList', 'similars'),

            'Aditional': ('fullActor', 'fullCast', 'posters', 'images', 'trailer', 'ratings', 'wikipedia'),

            'All': ('id', 'title', 'originalTitle', 'fullTitle', 'type', 'year', 'image', 'releaseDate', 'runtimeMins', 'runtimeStr',
                'plot', 'plotLocal', 'plotLocalIsRtl', 'awards', 'directors', 'directorList', 'writers', 'writerList', 'stars',
                'starList', 'actorList', 'fullCast', 'genres', 'genreList', 'companies', 'companyList', 'countries', 'countryList',
                'languages', 'languageList', 'contentRating', 'imDbRating', 'imDbRatingVotes', 'metacriticRating', 'ratings',
                'wikipedia', 'posters', 'images', 'trailer', 'boxOffice', 'tagline', 'keywords', 'keywordList', 'similars',
                'tvSeriesInfo', 'tvEpisodeInfo', 'errorMessage'),

            'None': ()
            }


    # basic function for making get requests to the API
    def make_request(self, url, sucess_func, *args):
        req = UrlRequest(url="https://" + urllib.parse.quote(url), timeout=5,
            on_success=lambda x, y: sucess_func(x, y, *args),
            on_redirect=self.redirect,
            on_failure=self.failure,
            on_error=self.error)


    # request returned wanted json
    def process_result(func):

        def wrapper(self, req, result, *args):
            print("sucess!") # remover ou mudar ação

            if result['errorMessage']:
                self.root.ids.screen_mg.change_screen("main")
                self.open_dialog(message_dialog, "Erro ao buscar filme", result["errorMessage"])
                return 

            return func(self, result, *args)

        return wrapper


    @process_result
    def get_movies(self, results):

        # for result in results['results']:
        #     print(result['title'])
        #     print(result['id'])
        #     print(result['image'])
        #     print(result['description'])
        #     print("")

        current_screen = self.root.ids.screen_mg.get_screen("movie_results")
        if results["results"]:
            current_screen.show_results(results["results"])
        else:
            current_screen.show_not_found()


    @process_result
    def get_movie_info(self, result, info_type):
        infos = self.info_type()[info_type] + self.info_type()["Aditional"]
        print(infos, '\n')

        for key, value in result.items():
            if value and key in infos:
                print(f"{key}: {value}")


    @process_result
    def get_api_calls(self, result):
        print(result)


    # request redirected
    def redirect(self, *args):
        print("redirect")
        for arg in args:
            print(arg)


    # request failed
    def failure(self, *args):
        print("failure")
        for arg in args:
            print(arg)


    # request gave an error
    def error(self, obj, message, *args):
        print("error")
        error_dict = {
            11001: "Verifique sua conexão com a internet"
        }

        if message.args[-1] == "The read operation timed out":
            print("timeout error")
            # self.make_request(obj.url[8:], obj.on_success)
            # print(obj.url[8:])
            # print(obj.on_success)
            # obj.run()

        # else:
        self.root.ids.screen_mg.change_screen("main")
        self.open_dialog(message_dialog, "Erro ao buscar filme", error_dict.get(message.args[0], str(message)))


    def search_movie(self, title):
        url = "/".join((self.baselink, "SearchMovie", self.api_key, title))
        self.make_request(url, self.get_movies)


    def search_movie_info(self, movie_id, info_type, aditional):
        url = "/".join((self.baselink, "Title", self.api_key, movie_id, ",".join(aditional)))
        self.make_request(url, self.get_movie_info, info_type)


    def get_remaining_requests(self, *args):
        url = "/".join(("imdb-api.com/API/Usage", self.api_key))
        self.make_request(url, self.get_api_calls)



if __name__ == "__main__":
    CineFile().run()
