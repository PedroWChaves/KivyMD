from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout

from main import CineFile as MyApp

def delete_dialog(*args):
    MyApp.get_running_app().dialog = None


# CLASSES
class CancelButton(MDFlatButton):
    pass

class OkayButton(MDRaisedButton):
    pass

class BaseDialog(MDDialog):
    def get_info(self, dismiss, *args):
        if dismiss: self.dismiss()

        content = self.ids.spacer_top_box.children[0]
        return content.get_info(*args)       


class BaseContent(BoxLayout):
    def get_info(self, *args):
        values = [self.ids[arg].text for arg in args]

        if not values:
            values = [self.ids[key].text for key in self.ids.keys()]

        return values

# editar infos perfil
class EditProfileContent(BaseContent):
    nickname = StringProperty()
    accountname = StringProperty()
    api_key = StringProperty()
    profile_icon = StringProperty()

# adicionar e editar filme
class AddMovieContent(BaseContent):
    title = StringProperty()
    imdbId = StringProperty()
    year = StringProperty()
    genres = StringProperty()
    priority = StringProperty()

# detalhes do filme
class MovieDetailContent(BaseContent):
    title = StringProperty()
    imdbId = StringProperty()
    year = StringProperty()
    genres = StringProperty()
    priority = StringProperty()

# resultados ao procurar titulo do filme no imdb
# class SearchMovieResultsContent(BaseContent):
#     pass

# ordenar lista
class ListOrderContent(BaseContent):
    order = ListProperty()
    sort = ListProperty()

    option_dict = {
        "Lançamento": "year",
        "Título": "title",
        "Categoria 1": "genres",
        "Categoria 2": "genres", # genres[1]
        "Prioridade": "priority",
        "Adicionado": "rowid",
        "Aleatório": "RANDOM()"
    }

    def get_info(self, **kwargs):
        return self.order, self.sort

    def add_to_order(self, obj):
        self.order.append(self.option_dict[obj.text])
        self.sort.append(obj.ids.sort.icon[-10:])

        obj.lefticon = f"numeric-{len(self.order)}-circle"

    def remove_in_order(self, obj):
        self.sort.pop(self.order.index(self.option_dict[obj.text]))
        self.order.remove(self.option_dict[obj.text])

        for child in self.children[1:-1]:
            try:
                num = int(child.lefticon[8])
                if num > int(obj.lefticon[8]):
                    child.lefticon = f"numeric-{num-1}-circle"
            except ValueError:
                pass

        obj.lefticon = "circle-outline"

    def update_sort(self, obj, sort):
        self.sort[self.order.index(self.option_dict[obj.text])] = sort[-10:]


class OrderItem(BoxLayout):
    text = StringProperty()
    lefticon = StringProperty("circle-outline")
    righticon = StringProperty("sort-alphabetical-ascending")

    def update_order(self):
        if self.lefticon == "circle-outline":
            self.parent.add_to_order(self)
        elif "numeric-" in self.lefticon:
            self.parent.remove_in_order(self)

    def update_sort(self):
        # change_icon
        if "asc" in self.righticon:
            self.righticon = self.righticon.replace("asc", "desc")
        elif "desc" in self.righticon:
            self.righticon = self.righticon.replace("desc", "asc")

        if "numeric-" in self.lefticon:
            self.parent.update_sort(self, self.righticon)

# config prioridade
class PrioridadeContent(BaseContent):
    pass

# config categoria
class CategoriaContent(BaseContent):
    pass

# config lançamento
class LancamentoContent(BaseContent):
    pass

class WhichMovieInfoContent(BaseContent):
    def get_info(self, *args):
        infos_dict = {
            "Básicas": "Basic",
            "Completas": "Complete",
            "Todas": "All"    
        }

        for child in self.children[8:]:
            if child.children[0].active:
                info = infos_dict[child.text]

        aditional = []
        for child in self.children[:7]:
            if child.children[0].active:
                aditional.append(child.text)

        return info, aditional


# FUNÇÕES
# adicionar filme
def message_dialog(app, title, message):
    dialog = BaseDialog(
        title=title,
        text=message,
    )

    return dialog

def confirmation_dialog(app, text, confirm_action, *args):
    dialog = BaseDialog(
        title = "Cofirmação",
        text = text,
        type = "alert",
        buttons=[
            CancelButton(),
            OkayButton(on_release=lambda x: confirm_action(*args)),
        ]
    )

    return dialog

def edit_profile_dialog(app, *args):
    dialog = BaseDialog(
        title = "Editar Perfil",
        type = "custom",
        content_cls = EditProfileContent(
            nickname = app.data['profile']['nickname'],
            accountname = app.data['profile']['accountname'],
            api_key = app.data['profile']['api_key'],
            profile_icon = app.data['profile']['profile_icon']
            ),
        buttons=[
            CancelButton(),
            OkayButton(on_release=app.edit_account)
        ]
    )

    return dialog

def add_movie_dialog(app):
    dialog = BaseDialog(
        title = "Adicionar Filme:",
        type = "custom",
        content_cls = AddMovieContent(),
        buttons=[
            CancelButton(),
            OkayButton(on_release=app.add_movie_item),
        ]
    )

    return dialog

# editar filme
def edit_movie_dialog(app, obj):
    movie_info, rowid = app.find_in_db_obj(obj)

    dialog = BaseDialog(
        title = "Editar Filme:",
        type = "custom",
        content_cls = AddMovieContent(
            title = app.get_info(movie_info, "title"),
            imdbId = app.get_info(movie_info, "imdbId"),
            year = str(app.get_info(movie_info, "year")),
            genres = app.get_info(movie_info, "genres"),
            priority = str(app.get_info(movie_info, "priority")),
        ),
        buttons=[
            CancelButton(),
            OkayButton(on_release=lambda x: app.edit_movie_item(obj, rowid)),
        ]
    )

    return dialog

# detalhes do filme
def movie_detail_dialog(app, obj):
    movie_info, _ = app.find_in_db_obj(obj)

    dialog = BaseDialog(
        title = "Detalhes do Filme:",
        type = "custom",
        content_cls = MovieDetailContent(
            title = app.get_info(movie_info, "title"),
            imdbId = app.get_info(movie_info, "imdbId"),
            year = str(app.get_info(movie_info, "year")),
            genres = app.get_info(movie_info, "genres"),
            priority = str(app.get_info(movie_info, "priority")),
        ),
        buttons=[
            CancelButton(),
            OkayButton(
                text="EDITAR",
                on_release=lambda x: app.close_and_open_dialog(edit_movie_dialog, obj)
            ),
        ]
    )

    return dialog

# def movie_search_results_dialog(app):
#     dialog = BaseDialog(
#         title = "Resultados da busca:",
#         type = "custom",
#         content_cls=SearchMovieResultsContent(),
#         buttons=[
#             CancelButton(),
#             OkayButton(on_release = app.order_list),
#         ]
#     )

#     return dialog

# ordenar lista
def list_order_dialog(app):
    dialog = BaseDialog(
        title = "Ordenar Lista Por:",
        type = "custom",
        content_cls=ListOrderContent(),
        buttons=[
            CancelButton(),
            OkayButton(on_release = app.order_list),
        ]
    )

    return dialog

# config prioridade
def prioridade_dialog(app):
    dialog = BaseDialog(
        title = "Configurações:",
        type = "custom",
        content_cls=PrioridadeContent(),
        buttons=[
            CancelButton(),
            OkayButton(),
        ]
    )

    return dialog

# config categoria
def categoria_dialog(app):
    dialog = BaseDialog(
        title = "Configurações:",
        type = "custom",
        content_cls=CategoriaContent(),
        buttons=[
            CancelButton(),
            OkayButton(),
        ]
    )

    return dialog

# config lançamento
def lancamento_dialog(app):
    dialog = BaseDialog(
        title = "Configurações:",
        type = "custom",
        content_cls=LancamentoContent(),
        buttons=[
            CancelButton(),
            OkayButton(),
        ]
    )

    return dialog


def which_movie_info_dialog(app, movie_id):
    dialog = BaseDialog(
        title = "Quais Informações?",
        type = "custom",
        content_cls=WhichMovieInfoContent(),
        buttons=[
            CancelButton(),
            OkayButton(on_release = lambda x: app.display_movie_info(movie_id)),
        ]
    )

    return dialog