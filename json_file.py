import json
import os

    # self.theme_cls.primary_palette = "Red"
    # self.theme_cls.primary_hue = "700"
    # self.theme_cls.primary_light_hue = "400"
    # self.theme_cls.primary_dark_hue = "900"
    # self.theme_cls.accent_palette = "Yellow"
    # self.theme_cls.accent_light_hue = "200"
    # self.theme_cls.accent_dark_hue = "800"
    # self.theme_cls.theme_style = "Dark"

def default_data():
    return {
        "profile": {
        "nickname": "Meu Perfil",
        "acccountname": "user",
        "email": "pedrodlmchaves@gmail.com",
        "password": "0108",
        "api_key": "None",
        "profile_icon": "account-circle"
        },
        "color": "Red",
        "color_hue": "700",
        "accent": "Yellow",
        "accent_hue": "400",
        "theme": "Dark",
        "time_format": "%d/%m - %Hh%M",
        "current_order": "ORDER BY title ASC, year DESC",
        "selected": "",
    }


def load_json(path, file):
    error = False
    try:
        with open(path + file, "r") as f:
            data = json.load(f)

    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        data = default_data()
        error = e

    return (data, error)

def save_json(data, path, file):
    with open(path + file, "w") as f:
        json.dump(data, f, indent=4)

    #print("json salvo!") # ABRIR DIALOGO OU SNACKBAR PARA AVISAR QUE FOI SALVO COM SUCESSO
                          # OU RETORNAR VERDADEIRO

def reset_json(path, file):
    save_json(default_data(), path, file)

def delete_json(path, file):
    if not os.path.exists(path + file):
      return

    os.remove(path + file)

def rename_json(path, old_name, new_name): # TESTAR
    if not os.path.exists(path + old_name):
        return

    if os.path.exists(path + new_name):
        for n in range(1, len([name for name in os.listdir(path)])):
            try_name = f"{path}{new_name.split('.')[0]} ({n}).json"

            if not os.path.exists(try_name):
                os.rename(path + new_name, try_name)
                break

    os.rename(path + old_name, path + new_name)

