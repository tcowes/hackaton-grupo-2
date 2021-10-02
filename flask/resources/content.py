from flask import Response, request
from flask_restful import Resource
from database.models import Content

class ContentsApi(Resource):
  def get(self):
    contents = Content.objects().to_json()
    return Response(contents, mimetype="application/json", status=200)