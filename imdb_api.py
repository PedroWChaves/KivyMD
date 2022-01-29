import requests

class ImdbManager():
    def __init__(self, key, language="pt-BR"):
        self.key = key

        self.baselink = f"https://imdb-api.com/{language}/API/"


    def url(self, query, *args):
        url = self.baselink + query + self.key

        for arg in args:
            url += arg + "/"
        else:
            url = url[:-1]

        return url


    def make_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"Error": e}

        data = response.json()
        if data["errorMessage"]:
            return {"Error": data["errorMessage"]}

        return data

        
    def search_movie(self, title):
        movies = self.make_request(self.url("SearchMovie/", title))

        if "Error" in movies:
            print(movies['Error'])
            return

        for result in movies["results"]:
            for key in result.keys():
                print(f"{key}: {result[key]}\n")

            print("__________________________________________")



    def get_movie_info(self, movie_id, infos=("title", "year", "genres")):
        movie_info = self.make_request(self.url("Title/", movie_id))

        if "Error" in movie_info:
            print(movie_info["Error"])
            return

        if infos:
            for info in infos:
                print(f"{info}: {movie_info[info]}\n\n")

        else:
            for key in movie_info.keys():
                print(f"{key}: {movie_info[key]}\n\n")

        return movie_info


    def search_movie(self, title):
        movies = self.make_request(self.url("SearchMovie/", title))

        if "Error" in movies:
            print(movies['Error'])
            return

        # for result in movies["results"]:
        #     for key in result.keys():
        #         print(f"{key}: {result[key]}\n")
        #     print("----------------------------------------------------------------------")

        return movies["results"]



from database import *

def fill_movie_info(start, num_movies, filename, tablename):
    my_manager = ImdbManager("k_yhwr0i17/")


    mydb = SQLdb(filename, tablename)

    for x, item in enumerate(mydb.get_table(f"LIMIT {start+100}")[start:start+num_movies]):
        print(item)

        options = my_manager.search_movie(item[0])
        for option in options:
            for key in option.keys():
                print(f"{key}: {option[key]}\n")
            print("----------------------------------------------------------------------")

        which_movie = 0 #int(input("\n Qual é o filme desejado? ")) if len(options) > 1 else 0

        try:
            movie_id = options[which_movie]["id"]
            movie_info = my_manager.get_movie_info(movie_id + "/")

            mydb.update_entry(start+x+1, 
                f"imdbId = '{movie_id}', year = '{movie_info['year']}', genres = '{movie_info['genres']}'"
                )
        except IndexError:
            pass

    for item in mydb.get_table(f"LIMIT {start+100}")[start:start+num_movies]:
        print(item)
    mydb.con.close()



if __name__ == "__main__":
    # fill_movie_info(53, 20, "cup_movies_data.db", "cup_minha_lista")
    my_manager = ImdbManager("k_yhwr0i17/")

    my_manager.get_movie_info("tt1375666/", ())

# mydb = SQLdb("cup_movies_data.db", "cup_minha_lista")
# for item in mydb.get_table_rowid("LIMIT 50"):
#     print(item)
# mydb.con.close()


# my_manager = ImdbManager("k_t23pjq0u/")
# my_manager.search_movie("inception")
# my_manager.get_movie_info("tt1375666/", ())


'''
FullActor,FullCast,Posters,Images,Trailer,Ratings,Wikipedia,


title, originalTitle
type
year, releaseDate
image
runtime, runtimeStr
plot, plotLocal
directors, directorList
writers, writerList
stars, starList
genres, genreList
contentRating
imDbRating
posters
images
trailer
keywords, keywordList
similars



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