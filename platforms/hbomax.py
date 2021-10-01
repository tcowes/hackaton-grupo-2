import requests
import time
from common import config
from utils.mongo import mongo
from utils.datamanager import Datamanager
# from utils.payload import Payload


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
        self.top_ten_section = self._config['urls']['top_ten_section']
        # generic:
        self._platform_code = self._config['countries'][ott_site_country]
        self._created_at = time.strftime("%Y-%m-%d")
        self.country_code = ott_site_country
        self.mongo = mongo()
        self.sesion = requests.session()
        # bbdd:
        self.collections = config()['mongo']['collections']
        self.database = self.collections['top_ten_hackaton']
        self.database_epis = self.collections['top_ten_hackaton_epi']
        # data lists:
        self.payloads = []
        self.payloads_epi = []
        self.scraped = []
        self.scraped_epi = []
        self.skippedTitles = 0
        self.skippedEpis = 0

        if type == 'scraping':
            self._scraping()

    def _scraping(self, testing=False):

        sections_ids = (
            'urn:hbo:tray:Ih5zk_5MKc9dbHP-IyOjO',  # Movies
            'urn:hbo:tray:fYZFVXDBbYrKbaf_ZAlsF',  # Series
            'urn:hbo:tray:wBNZilMZVN3CW82FRYp2A'  # Kids
        )

        for section in sections_ids:
            url = self.top_ten_section.format(
                section_id=section,
                country_code=self.country_code
            )
            data = Datamanager._getJSON(self, url)
            for content in data:
                if content['body'].get('titles'):
                    print(content['body']['titles']['full'])

        # for item in prescraping_list:
        #     payload = self.build_payload(item)
        #     if not payload:
        #         # Si no se pudo obtener el payload se saltea
        #         continue
        #     Datamanager._checkDBandAppend(
        #       self, payload, self.scraped, self.payloads
        #     )

        Datamanager._insertIntoDB(self, self.payloads, self.titanScraping)
        Datamanager._insertIntoDB(
            self, self.payloads_epi, self.titanScrapingEpisodios)

        self.sesion.close()

        if not testing:
            deleted = self.mongo.delete(
                self.titanPreScraping, {'PlatformCode': self._platform_code})
            print(f'Se eliminaron {deleted} items de PreScraping')
