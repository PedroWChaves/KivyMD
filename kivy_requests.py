from kivy.network.urlrequest import UrlRequest
from kivy.lang import Builder

from kivymd.app import MDApp

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
        self.baselink = f"https://imdb-api.com/{language}/API"


    def make_request(self, url, sucess_func, *args):
        req = UrlRequest(url=url, timeout=5,
            on_success=lambda x,y: self.got_json(x, y, sucess_func, *args),
            on_redirect=self.redirect,
            on_failure=self.failure,
            on_error=self.error)


    def got_json(self, req, result, sucess_func, *args):
        print("sucess!")

        if not result['errorMessage']:
            sucess_func(result, *args)
            
        else:
            print(result['errorMessage'])
            sucess_func({}, *args)


    def redirect(self, *args):
        print("redirect")
        for arg in args:
            print(arg)


    def failure(self, *args):
        print("failure")
        for arg in args:
            print(arg)


    def error(self, *args):
        print("error")
        for arg in args:
            print(arg)


    def search_movie(self, title, sucess_func):
        url = "/".join((self.baselink, "SearchMovie", self.key, title))
        
        self.make_request(url, sucess_func)


    def search_movie_info(self, movie_id, sucess_func, info_type, *args):
        url = "/".join((self.baselink, "Title", self.key, movie_id, ",".join(args)))

        self.make_request(url, sucess_func, info_type)


design = """
BoxLayout:
    orientation: "vertical"
    spacing: "5dp"

    MDRaisedButton:
        text: "Procurar titulo"
        on_release: app.search_movie()
        size_hint: 1, 1

    MDRaisedButton:
        text: "Pegar informação"
        on_release: app.search_movie_info("tt1375666", "None", 'FullActor', 'FullCast', 'Posters', 'Images', 'Trailer', 'Ratings', 'Wikipedia')
        size_hint: 1, 1

    MDRaisedButton:
        text: ""
        # on_release: app.search_movie()
        size_hint: 1, 1

"""

class MyApp(MDApp):
    result = None

    def build(self):
        self.my_imdb = ImdbManager("k_t23pjq0u")

        return Builder.load_string(design)


    def search_movie(self, title="deadpool_2"):
        self.my_imdb.search_movie(title, self.print_movies)


    def search_movie_info(self, movie_id, info_type, *args):
        self.my_imdb.search_movie_info(movie_id, self.print_movie_info, info_type, *args)


    def print_movies(self, results):
        if not results:
            return

        for result in results['results']:
            print(result['title'])
            print(result['id'])
            print(result['image'])
            print(result['description'])
            print("")

    def print_movie_info(self, result, info_type):
        if not result:
            print("sem informacao, irmao")
            return

        infos = self.my_imdb.INFO_TYPE[info_type] + self.my_imdb.INFO_TYPE["Aditional"]
        print(infos, '\n')

        for key, value in result.items():
            if value and key in infos:
                print(key)
                # print(f"{key}: {value}")


MyApp().run()

'''
basic movie info:
    title, year, id(?), image, genres, runtimeStr

complete movie info: (1 API call)
    title, originalTitle
    type
    year
    image
    runtimeStr
    plot, plotLocal
    directors, directorList
    writers, writerList
    stars, starList
    actorList
    genres, genreList
    contentRating
    imDbRating
    imDbRatingVotes
    posters
    images
    trailer
    keywords, keywordList
    similars

aditional movie info: (1 API call each)
    FullActor,FullCast,Posters,Images,Trailer,Ratings,Wikipedia 

all possible movie info:
    id
    title
    originalTitle
    fullTitle
    type
    year
    image
    releaseDate
    runtimeMins
    runtimeStr
    plot
    plotLocal
    plotLocalIsRtl
    awards
    directors
    directorList
    writers
    writerList
    stars
    starList
    actorList
    fullCast
    genres
    genreList
    companies
    companyList
    countries
    countryList
    languages
    languageList
    contentRating
    imDbRating
    imDbRatingVotes
    metacriticRating
    ratings
    wikipedia
    posters
    images
    trailer
    boxOffice
    tagline
    keywords
    keywordList
    similars
    tvSeriesInfo
    tvEpisodeInfo
    errorMessage

'''