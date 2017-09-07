from flask import Blueprint, render_template

from database_setup import Base, User, Category, Item
from database_session import *

home = Blueprint('home', __name__)

@home.route('/')
@home.route('/catalog')
def showCatalog():
    # This is a catalog application"
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(8)
    return render_template('catalog.html', categories=categories, items=items)