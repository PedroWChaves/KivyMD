from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFloatingActionButton, MDIconButton, MDFlatButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import (
    MDList,
    TwoLineRightIconListItem,
    TwoLineAvatarIconListItem,
    OneLineIconListItem,
    IRightBodyTouch,
    IconLeftWidgetWithoutTouch,
    )

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty, OptionProperty, NumericProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout


import random as r
from operator import itemgetter


from dialogs import *
from json_file import *
from database import *


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
class Tab(FloatLayout, MDTabsBase):
    pass

class MDCardElev(MDCard, FakeRectangularElevationBehavior):
    pass

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass

class RightIcon(IRightBodyTouch, MDIconButton):
    pass

class MenuItem(OneLineIconListItem):
    icon = StringProperty()

class Check(BoxLayout):
    text = StringProperty()
    group = StringProperty()


# LISTA ONDE FICAM OS FILMES
class MovieList(MDList):
    def add_item_info(self, index, info):
        item = list(reversed(self.children))[index]
        item.add_data_icons(info)

    def add_many_item_infos(self, index, infos):
        items = list(reversed(self.children))[index:index+len(infos)]

        for x, item in enumerate(items):
            item.add_data_icons(infos[x])

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
        selected.select(app)
        return selected


class MovieListItem(TwoLineAvatarIconListItem):
    rightIcon = leftIcon = None

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

class MovieListItemLeftIcon(IconLeftWidgetWithoutTouch):
    pass

class MovieListItemRightIcon(RightIcon):
    pass



# APLICATIVO EM SI
class CineFile(MDApp):
    # CONSTANTES
    FILE = "configs.json"

    # VARIAVEIS GLOBAIS
    speed_buttons = {
        "  Deletar  ": "delete",
        "   Editar   ": "pencil",
        "  Ordenar ": "format-list-numbered",
        "  Sortear  ": "dice-3",
        "Adicionar": "playlist-plus",
    }

    dialog = None
    snackbar = None

    selected = None
    close_speed_dial = None

    alterations = False
    on_selection = False

    selected_items = []


    # INICIALIZAÇÃO, FINALIZAÇÃO E REINICIALIZAÇÃO (adicionar)
    def build(self):
        self.path = "" #self.user_data_dir + "/"
        self.data, self.load_error = load_json(self.path, self.FILE)

        self.theme_cls.primary_palette = self.data['configs']['color']
        self.theme_cls.primary_hue = self.data['configs']['color_hue']
        self.theme_cls.accent_palette = self.data['configs']['accent']
        self.theme_cls.accent_hue = self.data['configs']['accent_hue']
        self.theme_cls.theme_style = self.data['configs']['theme']

        Window.bind(on_request_close=self.on_request_close)

        if platform == "win":
            Window.size = (337.5, 600)

        return Builder.load_file('design.kv')


    def on_start(self):
        self.moviesdb = SQLdb("movies_data.db", "pedro_minha_lista")
        self.load_movies(self.moviesdb.get_table())

        # preload(*args) -> coisas que demoram pra carregar
        # create_item_menu(menu_items)
        menu_items = {
            "Detalhes": "movie-search", 
            "Editar": "pencil", 
            "Remover": "delete",
            "Desmarcar": "checkbox-marked",
            "Easter Egg": "egg-easter",
            }

        self.menu = MDDropdownMenu(
            items = [
                {
                    "text": list(menu_items.keys())[i],
                    "viewclass": "MenuItem",
                    "icon": list(menu_items.values())[i],
                    "on_release": lambda x=list(menu_items.keys())[i]: self.menu_callback(x, self.menu.caller),
                } for i in range(len(menu_items))
            ],
            width_mult=3,
            max_height=147,
            border_margin="4dp",
            background_color=self.theme_cls.bg_light,
            radius=["2dp"]
        )

        # if self.load_error:
        #     self.open_dialog(file_error_dialog, self.load_error)

        # del self.load_error


    def on_request_close(self, *args):
        save_json(self.data, self.path, self.FILE)
        self.moviesdb.close()
        return False


    def restart_app(self):
        pass


    # LISTA PRINCIPAL
    def load_movies(self, movies_info):
        lista = self.root.ids.lista_filmes
        lista.add_many_item_widgets(len(movies_info)+0)
        lista.order_list(self.moviesdb, self.data["configs"]["current_order"])


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
        if query == self.data["configs"]["current_order"]:
            return
        
        lista = self.root.ids.lista_filmes
        lista.clear_item_infos()
        lista.order_list(self.moviesdb, query)
            
        self.data["configs"]["current_order"] = query


    def add_movie_from_dialog(self, obj):
        movie_info = self.dialog.get_info(True)

        if not get_info(movie_info, "title"): # TALVEZ TRANSFORMAR NUMA FUNÇÃO PROPRIA DE COMPLETAR movie_info
            return

        if not get_info(movie_info, "imdbId"):
            pass # FAZER REQUEST PARA PEGAR O ID

        if "" in get_info(movie_info, "year", "genres"):
            pass # FAZER REQUEST PARA PEGAR AS INFORMAÇÕES FALTANTES

        if not get_info(movie_info, "priority"):
            movie_info[get_info_index("priority")] = 1

        # self.add_movie(movie_info) # ATUALIZAR
        # self.moviesdb.add_one_to_table(movie_info)

    def right_icon_callback(self, obj):
        if obj.icon == "dots-vertical":
            self.menu_bind(obj)

        elif obj.icon == "checkbox-blank-outline":
            if obj.parent.parent == self.selected:
                obj.text_color = "black"
            elif self.theme_cls.theme_style == "Dark":
                obj.text_color = self.theme_cls.accent_light
            else:
                obj.text_color = self.theme_cls.accent_dark
            obj.icon = "checkbox-marked"

            self.selected_items.append(obj.parent.parent)
            #print([item.text[7:].replace(" ", "_") for item in self.selected_items])

        elif obj.icon == "checkbox-marked":
            obj.text_color = self.theme_cls.opposite_bg_darkest
            obj.icon = "checkbox-blank-outline"

            self.selected_items.remove(obj.parent.parent)

    def movie_detail_callback(self, filme):
        self.close_dialog(None)
        self.open_dialog(edit_movie_dialog, filme)

    def edit_callback(self, filme):
        dialog = self.dialog.ids.spacer_top_box.children[0].ids
        movie_info = []

        for key in dialog.keys():
            text = dialog[key].text if dialog[key].text else "---"
            try:
                #print(text)
                movie_info.append(int(text))
            except ValueError:
                movie_info.append(text.replace(" ", "_"))

        if movie_info[1] == "---":
            return

        data_index = self.find_index_in_database(filme)
        # self.moviesdb.update_entry(data_index, movie_info) # CORRIGIR movie_info
        # filme.text, filme.secondary_text = get_item_list_texts(movie_info)

        self.close_dialog(None)


    # MENU (3 pontos no CustomItemList)
    # Configura o lugar que o menu vai aparecer (ao lado do item selecionado)
    def menu_bind(self, button):
        if button.parent.parent == self.selected:
            self.menu.max_height = 196
        else:
            self.menu.max_height = 147

        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, item, obj):
        self.menu.dismiss()
        filme = obj.parent.parent

        if item == "Detalhes":
            self.open_dialog(movie_detail_dialog, filme)

        elif item == "Editar":
            self.open_dialog(edit_movie_dialog, filme)

        elif item == "Remover":  # CONFERIR SE TA FUNFANDO CERTIN
            self.root.ids.lista_filmes.remove_widget(filme)
            self.moviesdb.delete_entry(self.find_index_in_database(filme))

        elif item == "Desmarcar": # TALVEZ TRANSFORMAR NUMA FUNÇÃO PRA ECONIMIZAR ESPAÇO JA QUE USA MAIS DE UMA VEZ
            if self.selected == filme:
                self.selected.bg_color = self.theme_cls.bg_normal
                if self.theme_cls.theme_style == "Dark":
                    self.selected.text_color = self.theme_cls.text_color
                    self.selected.secondary_text_color = self.theme_cls.secondary_text_color
                    self.selected.ids.movie_icon.text_color = self.theme_cls.opposite_bg_darkest
                    self.selected.ids.icon_id.text_color = self.theme_cls.opposite_bg_darkest
                self.selected = None

        elif item == "Easter Egg": # CRIAR UMA FUNÇÃO PROPRIA PRO MINI GAME
            self.root.ids.avatar.icon = "emoticon-cool-outline"


    # SPEED DIAL
    def speed_dial_callback(self, instance):
        if self.on_selection:
            return

        self.root.ids.speed_dial.close_stack()
        button = instance.icon

        if button == "playlist-plus": # Adicionar
            self.open_dialog(add_movie_dialog)

        elif button == "pencil": # Editar
            self.select_movies_edit()

        elif button == "dice-3": # Sortear
            self.select_random_movie()

        elif button == "format-list-numbered": # Ordenar lista
            self.open_dialog(list_order_dialog)

        elif button == "delete": # Deletar
            self.select_movies_delete()

    def speed_dial_selection_mode(self, *args):
        if self.on_selection:
            self.root.ids.speed_dial.close_stack()
        else:
            self.close_speed_dial = Clock.schedule_once(self.speed_dial_auto_close, 8.45)

    def speed_dial_auto_close(self, *args):
        self.root.ids.speed_dial.close_stack()
        self.close_speed_dial = None

    def speed_dial_cancel_auto_close(self, *args):
        if self.close_speed_dial:
            self.close_speed_dial.cancel()
            self.close_speed_dial = None


    # SPEED DIAL BUTTONS
    def select_movies_delete(self):
        self.selection_mode(True)
        self.open_snackbar(self.confirm_delete)

    def select_movies_edit(self, obj=None):
        self.selection_mode(True)
        self.open_snackbar(self.confirm_edit)

    def select_random_movie(self):
        lista = self.root.ids.lista_filmes
        if self.selected:
            self.selected.deselect(self)
        self.selected = lista.select_random(self)

        # CARD NA TAB DO SORTEADOR
        self.root.ids.card_selected.text = self.selected.text
        self.root.ids.card_selected.secondaty_text = self.selected.secondary_text

        # SCROLL PARA O FILME SORTEADO
        self.root.ids.scroll_filmes.scroll_to(self.selected, 210, True)

    def confirm_delete(self, obj):
        if not self.selected_items:
            self.close_snackbar(None)
            return

        titulos = [item.text[7:].replace(" ", "_") for item in self.selected_items]
        to_remove = []

        for item in self.moviesdb.get_table(): # ATUALIZAR
            if item[1] in titulos:
                to_remove.append(item)
                titulos.remove(item[1])

            if not titulos:
                break

        for item in to_remove:
            self.moviesdb.delete_entry(item)

        for item in self.selected_items:
            self.root.ids.lista_filmes.remove_widget(item)

        self.close_snackbar(None)

    def confirm_edit(self, obj): # TALVEZ REMOVER ESSA OPÇÃO DE EDITAR VARIOS
        if not self.selected_items:
            self.close_snackbar(None)
            return

        titulos = [item.text[7:].replace(" ", "_") for item in self.selected_items]
        to_edit = []

        for item in self.moviesdb.get_table(): # ATUALIZAR
            if item[1] in titulos:
                to_edit.append(item)
                titulos.remove(item[1])

            if not titulos:
                break

        #abre dialogo de edição --isso que fode

        #edita filme em MovieListItem
        #edita filme em self.moviesdb

        self.close_snackbar(None)


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

    def close_snackbar(self, obj):
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
        if self.dialog:
            self.close_dialog()

        self.dialog = func(self.get_running_app(), *args)
        self.dialog.open()


    # CONFIGURAÇÕES APP
    def change_theme(self, obj):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
            #obj.icon = "weather-sunny"
        else:
            self.theme_cls.theme_style = "Light"
            #obj.icon = "weather-night"

        if self.selected:
            self.selected.bg_color = self.theme_cls.accent_light
            if self.theme_cls.theme_style == "Dark":
                self.selected.text_color = self.theme_cls.opposite_text_color
                self.selected.secondary_text_color = self.theme_cls.opposite_secondary_text_color
                self.selected.ids.movie_icon.text_color = self.theme_cls.bg_darkest
                self.selected.ids.icon_id.text_color = self.theme_cls.bg_darkest

    def selection_mode(self, on):
        self.on_selection = on

        if on:
            for movie in self.root.ids.lista_filmes.children:
                movie.ids.icon_id.icon = "checkbox-blank-outline"

        else:
            for movie in self.root.ids.lista_filmes.children:
                movie.ids.icon_id.icon = "dots-vertical"
                movie.ids.icon_id.text_color = self.theme_cls.opposite_bg_darkest


    # BACKEND
    def find_in_db_obj(self, obj):
        movie = obj.get_data()
        movie_info = self.moviesdb.search_table(
            year=movie[0],
            title=movie[1]
            )

        return movie_info[1:], movie_info[0]

    def find_in_database(self, filme): # MELHORAR
        titulo = filme.text[7:].replace(" ", "_")

        for item in self.moviesdb.get_table():
            # procura na db
            if item[1] == titulo:
                return item
        else:
            return []

    def find_index_in_database(self, filme): # MELHORAR
        titulo = filme.text[7:].replace(" ", "_")

        for x, item in enumerate(self.moviesdb.get_table()):
            # trocar por moviesdb
            if item[1] == titulo:
                return x
        else:
            return -1

    def get_info(self, *args):
        return get_info(*args)


if __name__ == "__main__":
    CineFile().run()
