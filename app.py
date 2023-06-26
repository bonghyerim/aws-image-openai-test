from flask import Flask
from flask_restful import Api

from resources.photo import PhotoResource, PhotoReviewResource
from resources.search import NewsSearchResource

app = Flask(__name__)

api = Api(app)

api.add_resource( PhotoResource ,  '/photo')
api.add_resource( PhotoReviewResource  , '/review')
api.add_resource( NewsSearchResource  , '/search/news')

if __name__ == '__main__':
    app.run()



