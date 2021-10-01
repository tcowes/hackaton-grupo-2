import re
import time
import requests
import datetime
from common import config
from utils.mongo import mongo
from utils.payload import Payload
from utils.replace import _replace
from utils.season_helper import SeasonHelper
from utils.datamanager import Datamanager, RequestsUtils


class HBOMax():
    """
    TODO:

    - DATOS IMPORTANTES:
        - Versión Final: TODO:
        - VPN: TODO:
        - ¿Usa Selenium?: TODO:
        - ¿Usa Playwright?: TODO:
        - ¿Tiene API?: TODO:
        - ¿Usa BS4?: TODO:
        - ¿Se relaciona con scripts TP? TODO:
        - ¿Instancia otro archivo de la carpeta "platforms"?: TODO:
        - Última revisión: TODO:
        - ¿Cuanto demoró la ultima vez? TODO:
        - ¿Cuantos contenidos trajo la ultima vez? TODO:

    - OTROS COMENTARIOS:
        TODO:
    """
    def __init__(self, ott_site_uid, ott_site_country, type):
        self._config = config()['ott_sites'][ott_site_uid]
        # urls:
        self.deeplink = self._config['urls']['deeplink']
        self.section_api = self._config['urls']['section_api']
        self.content_api = self._config['urls']['content_api']
        # generic:
        self._platform_code = self._config['countries'][ott_site_country]
        self._created_at = time.strftime("%Y-%m-%d")
        self.country_code = ott_site_country
        self.mongo = mongo()
        self.sesion = requests.session()
        # bbdd:
        self.collections = config()['mongo']['collections']
        self.database = self.collections['top_ten_hackaton']
        # data lists:
        self.prepayloads = []
        self.payloads = []
        self.payloads_epi = []
        self.scraped = []
        self.scraped_epi = []
        self.ids_originals = []
        self.skippedTitles = 0
        self.skippedEpis = 0
        self.res = RequestsUtils()

        if type == 'scraping':
            self._scraping()

    def _scraping(self):

        sections_ids = (
            'urn:hbo:tray:Ih5zk_5MKc9dbHP-IyOjO',  # Movies
            'urn:hbo:tray:fYZFVXDBbYrKbaf_ZAlsF',  # Series
            'urn:hbo:tray:wBNZilMZVN3CW82FRYp2A'  # Kids
        )

        self.get_originals()

        for section in sections_ids:
            url = self.section_api.format(
                section=section,
                country=self.country_code
            )
            data = Datamanager._getJSON(self, url)

            for content in data[-1]['body']['references']['items']:
                content_url = self.build_url(content)
                content_data = Datamanager._getJSON(self, content_url)
                _type = 'movie' if ':feature:' in content_url else 'serie'
                if content_data[0]['statusCode'] != 200:
                    # Si el contenido figura en la API de las secciones
                    # pero está caido se saltea.
                    continue
                if _type == 'serie':
                    prepayload = self.prescraping_serie(content_data)
                else:
                    prepayload = self.prescraping_movie(content_data)
                self.prepayloads.append(prepayload)

        for item in self.prepayloads:
            payload = self.build_payload(item)
            if item['Type'] == 'movie':
                payload = payload.payload_movie()
            else:
                # Compilo datos de los episodios para una serie
                compiled_data = self.scraping_episodes(
                    payload, item['Episodes'])
                epi_payloads = [episode.payload_episode() for episode in compiled_data]
                seasons = SeasonHelper().get_seasons_complete(epi_payloads)
                self.complete_serie(payload, compiled_data, seasons)
                payload = payload.payload_serie()

        Datamanager._insertIntoDB(self, self.payloads, self.database)

        self.sesion.close()

    def build_url(self, content_id, season=False):
        """En base a un id de contenido, construye la
        url que sirve para hacer la request y traer
        sus datos.
        """
        if season:
            # Caso temporadas
            url = self.content_api.format(
                content_id=content_id, country=self.country_code)
        else:
            serie = re.search(
                'urn:hbo:tile:(.+?):type:(series|franchise)', content_id)
            episode = re.search('urn:hbo:tile:(.+?):type:episode', content_id)
            if serie:
                # Caso series
                clean_id = serie.group(1)
                id_for_url = f'urn:hbo:page:{clean_id}:type:series'
            elif episode:
                # Caso episodios
                clean_id = episode.group(1)
                id_for_url = f'urn:hbo:page:{clean_id}:type:episode'
            else:
                # Caso peliculas
                clean_id = re.search(
                    'urn:hbo:tile:(.+?):type:feature', content_id).group(1)
                id_for_url = f'urn:hbo:feature:{clean_id}'
            url = self.content_api.format(
                content_id=id_for_url, country=self.country_code)
        return url

    def prescraping_serie(self, serie_data):
        """Este método se encarga de prescrapear las
        temporadas y sus respectivos episodios, también
        va a crear un prepayload con datos pertinentes
        de la serie.

        - Args:
            - serie_data (dict): json de la serie
        - Return: dict - prepayload de la serie
        """
        content_body = serie_data[0]['body']
        title = content_body['details']['title']
        id_ = content_body['myListId']

        # Buscar ids de temporadas:
        season_ids = []
        for tile in serie_data:
            label = tile['body'].get('label')
            if label == 'Seasons':
                season_ids.extend(tile['body']['references']['tabs'])

        episodes_data = []
        if not season_ids:
            # Solo tiene una temporada y los episodios están sueltos:
            for tile in serie_data:
                header = tile['body'].get('header')
                if not header:
                    continue
                label = tile['body']['header'].get('label')
                if label == 'Episodes':
                    episodes_ids = tile['body']['references']['items']
                    self.get_episodes_data(episodes_ids, episodes_data)
        else:
            # Hacer una request por id:
            urls_seasons = [self.build_url(
                id_, season=True) for id_ in season_ids]
            seasons_responses = self.res.async_requests(
                urls_seasons, max_workers=4)
            # Traer los datos de los episodios de cada temporada:
            for season in seasons_responses:
                season_data = season.json()
                if season_data[0]['statusCode'] != 200:
                    continue
                # Busco los episodios:
                episodes_ids = season_data[0]['body']['references']['items']
                self.get_episodes_data(episodes_ids, episodes_data)
        if not episodes_data:
            # Si no se trajo datos de los episodios se saltea la serie.
            return None

        prepayload = self.build_prepayload(
            title, id_, 'serie', serie_data[0], episodes_data
        )
        return prepayload

    def get_episodes_data(self, id_list, data_list):
        """Este método hace peticiones asíncronas
        para obtener los episodios de una temporada.
        Cuando obtiene esos episodios los agrega a la
        lista de episodios que recibe como segundo
        parámetro.

        - Args:
            - id_list ([str]): lista de ids de episodios
            - data_list ([dict]): lista de datos de episodios ya obtenidos
        """
        print(f'Trayendo datos de {len(id_list)} episodios...')
        urls_episodes = [self.build_url(id_) for id_ in id_list]
        episodes_responses = self.res.async_requests(urls_episodes, max_workers=4)
        for episode in episodes_responses:
            episode_data = episode.json()
            if episode_data[0]['statusCode'] != 200:
                continue
            data_list.append(episode_data)

    def scraping_episodes(self, serie_data, episodes_list):
        """En base a una lista de episodios, se scrapea
        uno por uno mientras que se van recopilando sus datos
        para luego atribuirselos a la serie.

        - Args:
            - serie_data (Payload): datos de la serie
            - episodes_list ([[dict]]): datos de los episodios de una serie
        - Return: [Payload] - lista de payloads de los episodios
        """
        episodes_data = []
        for episode in episodes_list:
            # Se arma este dict para localizar los campos
            # en el json y que sea mas facil procesarlos mas adelante
            epi_details = episode[0]['body']['details']
            epi_dict = {
                'ParentId': serie_data.id,
                'ParentTitle': serie_data.clean_title,
                'Id': episode[0]['id'],
                'Title': epi_details['title'],
                'Type': 'episode',
                'JSON': { 
                    'Synopsis': epi_details['description'],
                    'Metadata': epi_details['metadata'].replace('\xa0', ''), # de aca saco duracion y year
                    'Rating': epi_details['localizedRating']['value'],
                    'Image': epi_details, # se revisan los campos mas adelante
                    'Groups': episode[1]['body']['groups'], # de aca cast, directors y crew
                    'SeasonAndNumber': episode[2]['body']['metadata'],
                    'isFree': episode[0]['body']['isFree']
                }
            }
            payload_epi = self.build_payload(epi_dict)
            # Si la serie es original sus episodios también
            payload_epi.is_original = serie_data.is_original
            # Y también comparten provider
            payload_epi.provider = serie_data.provider
            episodes_data.append(payload_epi)
            payload_epi = payload_epi.payload_episode()
            Datamanager._checkDBandAppend(
                self, payload_epi, self.scraped_epi, self.payloads_epi,
                isEpi=True
            )
        return episodes_data

    def build_prepayload(self, title, id_, type_, json, episodes=None):
        """En base a algunos parámetros, devuelve
        un dict que comprende un prepayload de un contenido

        - Args:
            - title (str): titulo del contenido
            - id_ (str): id del contenido
            - type_ (str): tipo del contenido
            - json (dict): json del contenido
            - episodes (list): opcional, lista de episodios, defaults to None
        - Return: dict - prepayload del contenido
        """
        prepayload = {
            'PlatformCode': self._platform_code,
            'Title': title,
            'Id': id_,
            'Type': type_,
            'JSON': json,
            'CreatedAt': self._created_at,
            'Episodes': episodes
        }
        return prepayload

    def prescraping_movie(self, movie_data):
        """Este método se encarga de crear un 
        prepayload con datos pertinentes de la 
        pelicula.

        - Args:
            - movie_data (dict): json de la pelicula
        - Return: dict - prepayload de la pelicula
        """
        for tile in movie_data:
            body = tile['body']
            if body.get('titles'):
                title = body['titles']['full']
                id_ = tile['id']

        prepayload = self.build_prepayload(
            title, id_, 'movie', movie_data
        )
        return prepayload

    def build_payload(self, content):
        """Este método construye un payload en base
        a los datos recibidos por parámetro.

        - Args:
            - content (dict): prepayload de un contenido
        - Return: Payload
        """
        payload = Payload()
        payload.title = content['Title']
        payload.clean_title = _replace(payload.title)
        payload.id = self.get_clean_id(content['Id'])
        payload.is_original = payload.id in self.ids_originals

        type_ = content['Type']
        json = content['JSON']
        payload.duration = self.get_duration(json, type_)
        payload.year = self.get_year(json, type_)
        payload.genres = self.get_genres(json, type_)
        payload.rating = self.get_rating(json, type_)
        payload.images = self.get_images(json, type_)
        payload.synopsis = self.get_synopsis(json, type_)
        payload.packages = self.get_packages(json, type_)
        payload.cast = self.get_cast(json, type_)
        payload.directors = self.get_directors(json, type_)
        payload.crew = self.get_crew(json, type_)
        payload.availability = self.get_availability(json, type_)
        payload.deeplink_web = self.get_deeplink(payload.id, type_)
        payload.providers = self.get_providers(json, type_)
        payload.is_branded = self.get_is_branded(json, type_)

        if content['Type'] == 'episode':
            payload.parent_id = content['ParentId']
            payload.parent_title = content['ParentTitle']
            payload.episode = self.get_episode(json)
            payload.season = self.get_season(json, payload.title)
        return payload

    def get_originals(self):
        """Hace una request a una API que trae todos los ids
        de los títulos originales de HBO Max
        """
        url = self.section_api.format(
            section='urn:hbo:page:originals', country=self.country_code)
        data = Datamanager._getJSON(self, url)

        for tile in data:
            body = tile['body']
            if body.get('header'):
                label = body['header'].get('label')
                if label == 'A-Z Max Originals':
                    originals = [self.get_clean_id(id_) for id_ in body['references']['items']]
                    self.ids_originals.extend(originals)
                    break
                else:
                    continue

    def get_duration(self, json, type_):
        if type_ == 'movie':
            return json[0]['body']['duration'] // 60
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            metadata = json['Metadata']
            if 'HR' in metadata and 'MIN' in metadata:
                hours = int(re.findall(r'\d+', metadata)[0])
                minutes = int(re.findall(r'\d+', metadata)[1])
                duration = (hours * 60) + minutes
            elif 'MIN' in metadata:
                minutes = int(re.findall(r'\d+', metadata)[0])
                duration = minutes
            elif 'HR' in metadata:
                hours = int(re.findall(r'\d+', metadata)[0])
                duration = hours * 60
            else:
                duration = None
            return duration

    def get_year(self, json, type_):
        if type_ == 'movie':
            return json[-1]['body'].get('releaseYear')
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            metadata = json['Metadata']
            numbers = re.findall(r'\d+', metadata)
            year = None
            for number in numbers:
                if int(number) in range(1870, datetime.now().year+1):
                    year = int(number)
            return year

    def get_genres(self, json, type_):
        if type_ == 'movie':
            return json[0]['body']['genres']
        else:
            # Series y episodios no traen generos en esta plataforma.
            return None

    def get_rating(self, json, type_):
        if type_ == 'movie':
            rating = json[-1]['body']['ratingCode']
            return rating if rating != 'UNKNOWN' else None
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            return json['Rating'] if json['Rating'] != 'UNKNOWN' else None   

    def get_images(self, json, type_):
        images = []
        if type_ == 'movie':
            image_list_location = json[-1]['body']['images']
            for image in image_list_location:
                # Las demás imagenes son repetidas
                if image == 'tileburnedin' or image == 'tilezoom':
                    formatted_image = self.format_image(image_list_location[image])
                    images.append(formatted_image)
        elif type_ == 'serie':
            image = json['body']['details'].get('image')
            if image:
                formatted_image = self.format_image(image['uri'])
                images.append(formatted_image)
        elif type_ == 'episode':
            image = json['Image'].get('image')
            if image:
                formatted_image = self.format_image(image['uri'])
                images.append(formatted_image)
        return images if images else None

    def get_synopsis(self, json, type_):
        synopsis = None
        if type_ == 'movie':
            synopsis = json[-1]['body']['summaries']['full']
        elif type_ == 'serie':
            synopsis = json['body']['details']['description']
        elif type_ == 'episode':
            synopsis = json['Synopsis']
        return synopsis.replace('\n', '')

    def get_packages(self, json, type_):
        is_free = False
        if type_ == 'movie':
            is_free = json[-1]['body']['isFree']
        elif type_ == 'serie':
            is_free = False  # se valida de otra forma!
        elif type_ == 'episode':
            is_free = json['isFree']  
        return [{'Type': 'free-vod'}] if is_free else [{'Type': 'subscription-vod'}]

    def get_cast(self, json, type_):
        cast = []
        if type_ == 'movie':
            credits_ = json[-1]['body']['credits']
            if credits_.get('cast'):
                for actor in credits_['cast']:
                    if actor['person'] not in cast:
                        cast.append(actor['person'])
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            for group in json['Groups']:
                if 'Cast' in group['label']:
                    for person in group['items']:
                        if person['value'] not in cast:
                            cast.append(person['value'])
        return cast if cast else None

    def get_directors(self, json, type_):
        directors = []
        if type_ == 'movie':
            credits_ = json[-1]['body']['credits']
            if credits_.get('directors'):
                for director in credits_['directors']:
                    if director['person'] not in credits_['directors']:
                        directors.append(director['person'])
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            for group in json['Groups']:
                if 'Directors' in group['label']:
                    for person in group['items']:
                        if person['value'] not in directors:
                            directors.append(person['value'])
        return directors if directors else None

    def get_availability(self, json, type_):
        if type_ == 'movie':
            endtime = json[-1]['body']['endDate'] // 1000
            return str(datetime.date.fromtimestamp(endtime))
        else:
            # Series y episodios no traen availability en esta plataforma.
            return None

    def get_deeplink(self, clean_id, type_):
        if type_ == 'movie':
            slug = f'urn:hbo:page:{clean_id}:type:feature'
        elif type_ == 'serie':
            slug = f'urn:hbo:page:{clean_id}:type:series'
        elif type_ == 'episode':
            slug = f'urn:hbo:page:{clean_id}:type:episode'
        return self.deeplink + slug

    def get_crew(self, json, type_):
        crew = []
        if type_ == 'movie':
            credits_ = json[-1]['body']['credits']
            for credit in credits_:
                if credit == 'cast' or credit == 'directors':
                    continue
                for person in credits_[credit]:
                    crew.append({'Role': person['role'], 'Name': person['person']})
        elif type_ == 'serie':
            return None
        elif type_ == 'episode':
            for group in json['Groups']:
                if group['label'] in ('Directors', 'Cast & Crew', 'Rating Information'):
                    continue
                for person in group['items']:
                    crew.append({'Role': person['label'], 'Name': person['value']})
        return crew if crew else None

    def get_providers(self, json, type_):
        if type_ == 'movie':
            provider = json[-1]['body']['displayBrand']
            return [provider] if provider != '' else None
        elif type_ == 'serie':
            provider = json['body']['details'].get('attributionIcon')
            return [provider['alternateText']] if provider else None

    def get_is_branded(self, json, type_):
        brand = logo = None
        if type_ == 'movie':
            logo = json[-1]['body'].get('attributionIcon')
        elif type_ == 'serie':
            logo = json['body']['details'].get('attributionIcon')
        if logo:
            brand = logo['alternateText']
        return brand == 'Max Originals'

    def get_episode(self, json):
        return json['SeasonAndNumber']['hadron-legacy-telemetry']['episodeNumber']

    def get_season(self, json, title):
        season_title = json['SeasonAndNumber']['hadron-legacy-telemetry'].get('seasonTitle')
        number_in_season = re.findall(r'\d+', season_title) if season_title else None
        number_in_title = re.search(r'S(\d+)', title)
        if number_in_season:
            return int(number_in_season[0])
        elif number_in_title:
            return int(number_in_title.group(1))
        else:
            return None

    def get_clean_id(self, id_):
        """Procesa un id para devolverlo limpio

        Pueden venir en este formato:
        - 'urn:hbo:feature:GVU3k2gEncoNJjhsJAY0_'
        - 'urn:hbo:tile:GXuu7ygQ61cI9DgEAAAAY:type:series'
        - 'urn:hbo:tile:GX7_dBQJHuaipuAEAAAAE:type:feature'

        Solo interesa el que es una combinación de letras, nros y símbolos.
        """
        clean_id = re.search('urn:hbo:(.+?):(.+?)(:|$)', id_).group(2)
        return clean_id

    def format_image(self, image_url):
        """Este método se encarga de darle formato
        a las urls de las imagenes que vienen por api
        para un contenido.
        """
        raw_image = image_url.replace('{{', '{')
        raw_image = raw_image.replace('}}', '}')
        if 'scaleDownToFit' in raw_image:
            formatted_image = raw_image.format(
                size='1000x1000',
                compression='low',
                protection='false',
                scaleDownToFit='false'
            )
        else:
            formatted_image = raw_image.format(
                size='1000x1000',
                compression='low',
                protection='false'
            )
        # Campo que no siempre viene:
        return formatted_image
