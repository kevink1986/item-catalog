from flask import Blueprint, render_template, redirect, url_for

from database_setup import Base, User, Category, Item
from database_session import *

category = Blueprint('category', __name__)

# Show a category of catalog items
@category.route('/catalog/<string:category_name>/')
@category.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if not any(c.name == category_name for c in categories):
        return redirect(url_for('home.showCatalog'))
    else:
        category = session.query(Category).filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category.id).all()
        count = len(items)
        return render_template(
            'category.html',
            categories=categories,
            category=category,
            items=items,
            count=count)