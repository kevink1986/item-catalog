from flask import Blueprint, render_template, redirect, url_for

from database_setup import Base, User, Category, Item
from database_session import *

category = Blueprint('category', __name__)


@category.route('/catalog/<string:category_name>/')
@category.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    """
    Renders the category page for the selected category. The user is redirected
    to the home page if the category doesn't exists.
    """
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