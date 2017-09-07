from flask import Blueprint, render_template, jsonify

from database_setup import Base, User, Category, Item
from database_session import *

catalog_api = Blueprint('catalog_api', __name__)


@catalog_api.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    output = []
    for c in categories:
        category = c.serialize
        item_list = []
        for i in items:
            if c.id == i.category_id:
                item_list.append(i.serialize)
        category['item'] = item_list
        output.append(category)
    return jsonify(Category=output)
