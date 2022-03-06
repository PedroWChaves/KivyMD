# import requests

# class ImdbManager():
#     def __init__(self, key, language="pt-BR"):
#         self.key = key
#         self.baselink = f"https://imdb-api.com/{language}/API/"


#     def url(self, query, *args):
#         url = self.baselink + query + self.key

#         for arg in args:
#             url += arg + "/"
#         else:
#             url = url[:-1]

#         return url


#     def make_request(self, url):
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             return {"Error": e}

#         data = response.json()
#         if data["errorMessage"]:
#             return {"Error": data["errorMessage"]}

#         return data

        
#     def search_movie(self, title):
#         movies = self.make_request(self.url("SearchMovie/", title))

#         if "Error" in movies:
#             print(movies['Error'])
#             return

#         for result in movies["results"]:
#             for key in result.keys():
#                 print(f"{key}: {result[key]}\n")

#             print("__________________________________________")



#     def get_movie_info(self, movie_id, infos=("title", "year", "genres")):
#         movie_info = self.make_request(self.url("Title/", movie_id))

#         if "Error" in movie_info:
#             print(movie_info["Error"])
#             return

#         if infos:
#             for info in infos:
#                 print(f"{info}: {movie_info[info]}\n\n")

#         else:
#             for key in movie_info.keys():
#                 print(f"{key}: {movie_info[key]}\n\n")

#         return movie_info


#     def search_movie(self, title):
#         movies = self.make_request(self.url("SearchMovie/", title))

#         if "Error" in movies:
#             print(movies['Error'])
#             return

#         # for result in movies["results"]:
#         #     for key in result.keys():
#         #         print(f"{key}: {result[key]}\n")
#         #     print("----------------------------------------------------------------------")

#         return movies["results"]



# from database import *

# def fill_movie_info(start, num_movies, filename, tablename):
#     my_manager = ImdbManager("k_yhwr0i17/")


#     mydb = SQLdb(filename, tablename)

#     for x, item in enumerate(mydb.get_table(f"LIMIT {start+100}")[start:start+num_movies]):
#         print(item)

#         options = my_manager.search_movie(item[0])
#         for option in options:
#             for key in option.keys():
#                 print(f"{key}: {option[key]}\n")
#             print("----------------------------------------------------------------------")

#         which_movie = 0 #int(input("\n Qual é o filme desejado? ")) if len(options) > 1 else 0

#         try:
#             movie_id = options[which_movie]["id"]
#             movie_info = my_manager.get_movie_info(movie_id + "/")

#             mydb.update_entry(start+x+1, 
#                 f"imdbId = '{movie_id}', year = '{movie_info['year']}', genres = '{movie_info['genres']}'"
#                 )
#         except IndexError:
#             pass

#     for item in mydb.get_table(f"LIMIT {start+100}")[start:start+num_movies]:
#         print(item)
#     mydb.con.close()



# if __name__ == "__main__":
#     # fill_movie_info(53, 20, "cup_movies_data.db", "cup_minha_lista")
#     my_manager = ImdbManager("k_yhwr0i17/")

#     my_manager.get_movie_info("tt1375666/", ())

# # mydb = SQLdb("cup_movies_data.db", "cup_minha_lista")
# # for item in mydb.get_table_rowid("LIMIT 50"):
# #     print(item)
# # mydb.con.close()


# # my_manager = ImdbManager("k_t23pjq0u/")
# # my_manager.search_movie("inception")
# # my_manager.get_movie_info("tt1375666/", ())


from kivy.network.urlrequest import UrlRequest
import urllib


class ImdbManager():
    INFO_TYPE = {
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

    def __init__(self, key, language="pt-BR"):
        self.key = key
        self.baselink = f"imdb-api.com/{language}/API"
        self.result = None


    # basic function for making get requests to the API
    def make_request(self, url, sucess_func, *args):
        # print("https://" + urllib.parse.quote(url))
        req = UrlRequest(url="https://" + urllib.parse.quote(url), timeout=5,
            on_success=lambda x,y: sucess_func(x, y, *args),
            on_redirect=self.redirect,
            on_failure=self.failure,
            on_error=self.error)

        req.wait()
        return req.result


    # def got_json(self, req, result, sucess_func, *args):
    #     print("sucess!")

    #     if not result['errorMessage']:
    #         sucess_func(result, *args)
            
    #     else:
    #         print(result['errorMessage'])
    #         sucess_func({}, *args)


    # request returned wanted json
    def process_result(func):

        def wrapper(self, req, result, *args):
            print("sucess!")
            if result['errorMessage']:
                print(result['errorMessage'])
                return #alguma coisa

            return func(self, result, *args)

        return wrapper


    # returns processed value to use in the app
    @process_result
    def get_movies(self, results):
        for result in results['results']:
            print(result['title'])
            print(result['id'])
            print(result['image'])
            print(result['description'])
            print("")

        return results['results']


    # returns processed value to use in the app
    @process_result
    def get_movie_info(self, result, info_type):
        infos = self.INFO_TYPE[info_type] + self.INFO_TYPE["Aditional"]
        print(infos, '\n')

        for key, value in result.items():
            if value and key in infos:
                print(f"{key}: {value}")

        return result


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
    def error(self, *args):
        print("error")
        for arg in args:
            print(arg)


    def search_movie(self, title):
        url = "/".join((self.baselink, "SearchMovie", self.key, title))
        
        return self.make_request(url, self.get_movies)


    def search_movie_info(self, movie_id, info_type, *args):
        url = "/".join((self.baselink, "Title", self.key, movie_id, ",".join(args)))

        self.make_request(url, self.get_movie_info, info_type)


# design = """
# BoxLayout:
#     orientation: "vertical"
#     spacing: "5dp"

#     MDRaisedButton:
#         text: "Procurar titulo"
#         on_release: app.my_imdb.search_movie("deadpool_2")
#         size_hint: 1, 1

#     MDRaisedButton:
#         text: "Pegar informação"
#         on_release: app.my_imdb.search_movie_info("tt1375666", "Basic")
#         size_hint: 1, 1

#     MDRaisedButton:
#         text: ""
#         # on_release: app.search_movie()
#         size_hint: 1, 1

# """

# class MyApp(MDApp):

#     def build(self):
#         self.my_imdb = ImdbManager("k_t23pjq0u")

#         return Builder.load_string(design)


# if __name__ == '__main__':
#     MyApp().run()
