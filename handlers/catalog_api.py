from flask import Blueprint, render_template, jsonify

from database_setup import Base, User, Category, Item
from database_session import *

catalog_api = Blueprint('catalog_api', __name__)


@catalog_api.route('/catalog.json')
def catalogJSON():
    """
    Returns a json file with all info about the complete catalog.
    """
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


@catalog_api.route('/catalog/<string:category_name>/items/category.json')
def categoryJSON(category_name):
    """
    Returns a json file with details about all items in the selected category.
    """
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


@catalog_api.route('/catalog/<string:category_name>/<string:item_name>/item.json')
def itemJSON(category_name, item_name):
    """
    Returns a json file with the details about the selected catalog item.
    """
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name, category_id=category.id).one()
    return jsonify(Item=item.serialize)
