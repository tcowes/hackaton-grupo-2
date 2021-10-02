from datetime import datetime
from utils.replace import _replace


class Payload:
    def __init__(self, platform_name=None,
                 platform_country=None,
                 section=None,
                 id_=None,
                 title=None,
                 year=None,
                 duration=None,
                 deeplink_web=None,
                 synopsis=None,
                 image=None,
                 rating=None,
                 genres=None,
                 cast=None,  # ver
                 directors=None,  # ver
                 is_original=None,
                 episodes=None,
                 parent_id=None,
                 parent_title=None,
                 episode=None,
                 season=None,
                 seasons=None,
                 number=None,
                 crew=None):  # ver
        self._platformName = platform_name
        self._platformCountry = platform_country
        self._section = section
        self._id = id_
        self._title = title
        self._year = year
        self._duration = duration
        self._deeplink_web = deeplink_web
        self._synopsis = synopsis
        self._image = image
        self._rating = rating
        self._genres = genres
        self._cast = cast
        self._directors = directors
        self._is_original = is_original
        self._timestamp = datetime.now().isoformat()
        self._episodes = episodes
        self._parent_id = parent_id
        self._parent_title = parent_title
        self._episode = episode
        self._season = season
        self._seasons = seasons
        self._number = number
        self._crew = crew

    @property
    def section(self):
        return self._section

    @section.setter
    def section(self, section):
        self._section = section

    @property
    def platform_name(self):
        return self._platformName

    @platform_name.setter
    def platform_name(self, name):
        self._platformName = name

    @property
    def platform_country(self):
        return self._platform

    @platform_country.setter
    def platform_country(self, country):
        self._platformCountry = country

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, new_title):
        self.clean_title = _replace(new_title)
        self._title = new_title

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, new_year):
        self._year = new_year

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration):
        self._duration = new_duration

    @property
    def deeplink_web(self):
        return self._deeplink_web

    @deeplink_web.setter
    def deeplink_web(self, new_deeplink_web):
        self._deeplink_web = new_deeplink_web

    @property
    def synopsis(self):
        return self._synopsis

    @synopsis.setter
    def synopsis(self, new_synopsis):
        self._synopsis = new_synopsis

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, new_rating):
        self._rating = new_rating

    @property
    def genres(self):
        return self._genres

    @genres.setter
    def genres(self, new_genres):
        self._genres = new_genres

    @property
    def cast(self):
        return self._cast

    @cast.setter
    def cast(self, new_cast):
        self._cast = new_cast

    @property
    def directors(self):
        return self._directors

    @directors.setter
    def directors(self, new_directors):
        self._directors = new_directors

    @property
    def crew(self):
        return self._crew

    @crew.setter
    def crew(self, new_crew):
        self._crew = new_crew

    @property
    def is_original(self):
        return self._is_original

    @is_original.setter
    def is_original(self, new_is_original):
        self._is_original = new_is_original

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, new_parent_id):
        self._parent_id = new_parent_id

    @property
    def parent_title(self):
        return self._parent_title

    @parent_title.setter
    def parent_title(self, new_parent_title):
        self._parent_title = new_parent_title

    @property
    def episode(self):
        return self._episode

    @episode.setter
    def episode(self, new_episode):
        self._episode = new_episode

    # Numero de temporada.
    # ---------------------------------- #
    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, new_season):
        self._season = new_season
    # ---------------------------------- #

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, new_number):
        self._number = new_number

    # Cantidad de temporadas.
    # ---------------------------------- #
    @property
    def seasons(self):
        return self._seasons

    @seasons.setter
    def seasons(self, new_season):
        self._seasons = new_season
    # ---------------------------------- #

    @property
    def episodes(self):
        return self._episodes

    @episodes.setter
    def episodes(self, new_episodes):
        self._episodes = new_episodes

    def payload_Content(self):
        return {
            'PlatformName': self._platformName,
            'PlatformCountry': self._platformCountry,
            'Section': self._section,
            'Id': self._id,
            'Title': self._title,
            'Type': 'Content',
            'Year': self._year,
            'Duration': self._duration,
            'Deeplink': self._deeplink_web,
            'Synopsis': self._synopsis,
            'Image': self._image,
            'Rating': self._rating,
            'Genres': self._genres,
            'Cast': self._cast,
            'Directors': self._directors,
            'Crew': self._crew,
            'IsOriginal': self._is_original,
        }

    def payload_serie(self):
        return {
            'PlatformName': self._platformName,
            'PlatformCountry': self._platformCountry,
            'Section': self._section,
            'Id': self._id,
            'Title': self._title,
            'Type': 'serie',
            'Year': self._year,
            'Seasons': self._seasons,
            'Deeplink': self._deeplink_web,
            'Synopsis': self._synopsis,
            'Image': self._image,
            'Rating': self._rating,
            'Genres': self._genres,
            'Cast': self._cast,
            'Directors': self._directors,
            'Crew': self._crew,
            'IsOriginal': self._is_original,
        }

    def payload_season(self):
        return {
            'Id': self._id,
            'Title': self._title,
            'Deeplink': self._deeplink_web,
            'Number': self._number,
            'Episodes': self._episodes,
            'Year': self._year
        }

    def payload_episode(self):
        return {
            'ParentId': self._parent_id,
            'ParentTitle': self._parent_title,
            'Id': self.id,
            'Title': self.title,
            'Episode': self.episode,
            'Season': self.season,
            'Year': self.year,
            'Image': self._image,
            'Duration': self.duration,
            'Deeplink': self.deeplink_web,
            'Synopsis': self.synopsis,
            'Rating': self.rating,
            'Genres': self.genres,
            'Cast': self.cast,
            'Directors': self.directors,
            'Crew': self.crew,
            'IsOriginal': self._is_original,
        }
