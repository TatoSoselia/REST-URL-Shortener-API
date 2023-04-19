from flask import  request, redirect
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta
import validators
import shortuuid
import datetime
from models import UrlModel
from db import db
U_R_L = "http://127.0.0.1:5000"


blp = Blueprint("urls", __name__, description="Operations on urls")



@blp.route("/url")
class URL_Shortener(MethodView):
    def post(self):
        url = request.get_json()

        if 'url' not in url:
            abort(400, message = "URL is required.")
        if not validators.url(url['url']):
            abort(400, message = "Invalid URL.")

        short_url = shortuuid.uuid()[:7]
        new_url = {'short_url': short_url, 'url': url['url'] ,'created': datetime.datetime.utcnow(), 'counter': 0}
        data = UrlModel(**new_url)

        try:
            db.session.add(data)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the url.")
        return {'short_url': f'{U_R_L}/{short_url}'}, 201

@blp.route("/url/<string:custom>")
class Premium_URL_Shortener(MethodView):
    def post(self, custom):
        url = request.get_json()

        if 'url' not in url:
            abort(400, message = "URL is required.")
        if not validators.url(url['url']):
            abort(400, message = "Invalid URL.")

        new_url = {'short_url': custom, 'url': url['url'] ,'created': datetime.datetime.utcnow(), 'counter': 0}
        data = UrlModel(**new_url)

        try:
            db.session.add(data)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="Custom name already in use.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the url.")

        return {'short_url': f'{U_R_L}/{custom}'}, 201


@blp.route("/<string:short_url>")
class get_url(MethodView):
    def get(self, short_url):
        url = UrlModel.query.get_or_404(short_url)
        url.counter += 1
        db.session.commit()
        return redirect(url.url)


@blp.route("/url/<string:short_url>")
class get_url_info(MethodView):
    def get(self, short_url):
        url = UrlModel.query.get_or_404(short_url)
        return {
            'url': url.url,
            'created': url.created.isoformat(),
            'counter': url.counter
        }


def delete_old_urls():
    threshold_date = datetime.utcnow() - timedelta(days=30)
    old_urls = UrlModel.query.filter(UrlModel.created < threshold_date).all()
    for url in old_urls:
        db.session.delete(url)
    db.session.commit()