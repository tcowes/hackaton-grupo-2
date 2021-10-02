class SeasonHelper():
    @staticmethod
    def get_season_payload():
        return {
                "Id": None,
                "Synopsis": None,
                "Title": None,
                "Deeplink":  None,
                "Number": None,
                "Year": None,
                "Image": None,
                "Directors": None,
                "Cast": None,
                "Episodes": None,
                "IsOriginal": None
            }

    def get_seasons_complete(self, episodes, forced=False):
        seasons = []
        seasons_numb = self.get_seasons_number(episodes)
        for season_n in seasons_numb:
            episodes_season = self.get_episodes_season(episodes, season_n)
            if not episodes_season:
                continue
            seasons.append({
                      "Id": self.get_id(episodes_season),
                      "Synopsis": self.get_synopsis(
                          episodes_season, forced=forced),
                      "Title": self.get_title(episodes_season, season_n),
                      "Deeplink":  self.get_deeplink(episodes_season),
                      "Number": season_n,
                      "Year": self.get_year(episodes_season, forced=forced),
                      "Image": self.get_images(episodes_season),
                      "Directors": self.get_directors(episodes_season),
                      "Cast": self.get_cast(episodes_season),
                      "Episodes": self.get_cant_ep(episodes_season)
                      })
        return seasons if seasons else None

    def get_functions_fields(self):
        return {
            "Id": self.get_id,
            "Synopsis": self.get_synopsis,
            "Title": self.get_title,
            "Deeplink":  self.get_deeplink,
            "Year": self.get_year,
            "Image": self.get_images,
            "Directors": self.get_directors,
            "Cast": self.get_cast,
            "Episodes": self.get_cant_ep,
            "IsOriginal": self.is_original
        }

    def complete_fields_seasons(self, episodes, seasons, *args, forced=False):
        functions = self.get_functions_fields()
        for season in seasons:
            episodes_season = self.get_episodes_season(
                episodes, season['Number'])
            if not episodes_season:
                continue
            for arg in args:
                if (forced) and ((arg == 'Image') or (arg == 'Synopsis')):
                    season[arg] = functions[arg](episodes_season, forced)
                else:
                    season[arg] = functions[arg](episodes_season)
        return seasons if seasons else None

    @staticmethod
    def get_cant_ep(episodes):
        return len(episodes)

    @staticmethod
    def get_list(episodes, field):
        _list = list()
        for episode in episodes:
            if episode[field]:
                _list = episode[field]
        return list(set(_list)) if _list else None

    def get_cast(self, episodes):
        return self.get_list(episodes, 'Cast')

    def get_directors(self, episodes):
        return self.get_list(episodes, 'Directors')

    def get_images(self, episodes):
        return self.get_list(episodes, 'Image')

    @staticmethod
    def get_year(episodes, forced=False):
        if (forced):
            for episode in episodes:
                if episode['Year']:
                    return episode['Year']

        return episodes[0]['Year']

    @staticmethod
    def get_deeplink(episodes):
        return episodes[0]['Deeplink']

    @staticmethod
    def get_id(episodes):
        return episodes[0]['Id']

    @staticmethod
    def get_synopsis(episodes, forced=False):
        if (forced):
            for episode in episodes:
                if episode['Synopsis']:
                    return episode['Synopsis']
        return episodes[0]['Synopsis']

    @staticmethod
    def get_title(episodes, season_n):
        return "{}: Season {}".format(episodes[0]['ParentTitle'], season_n)

    @staticmethod
    def get_episodes_season(episodes, season_number):
        episodes_s = list(filter(
            lambda x: x['Season'] == season_number, episodes))
        episodes_s = list(filter(
            lambda x: type(x['Episode']) == type(1), episodes_s))
        try:
            episodes_season = sorted(episodes_s, key=lambda k: k['Episode'])
        except Exception:
            episodes_season = episodes_s

        return episodes_season

    @staticmethod
    def get_seasons_number(episodes):
        seasons = list(set([ep['Season'] for ep in episodes]))
        return list(sorted(filter(lambda x: type(x) == type(1), seasons)))
