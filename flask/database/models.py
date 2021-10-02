from .db import db

class Content(db.Document):
    meta = {
        'collection': 'hackatonTopTen'
    }
