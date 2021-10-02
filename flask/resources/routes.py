from .content import ContentsApi

def initialize_routes(api):
    api.add_resource(ContentsApi, '/api/content/all')