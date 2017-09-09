from flask import Blueprint, render_template, redirect, url_for, flash, request

from database_setup import Base, User, Category, Item
from database_session import *

from flask import session as login_session
from functools import wraps


item = Blueprint('item', __name__)


def login_required(func):
    """Wraper function that checks if users are logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper


def item_exists(func):
    """Wraper function that checks if an item exists in the database."""
    @wraps(func)
    def wrapper(category_name, item_name):
        item = session.query(Item).filter_by(name=item_name).one_or_none()
        if not item:
            return redirect(url_for('home.showCatalog'))
        else:
            return func(category_name, item_name)
    return wrapper


def category_exists(func):
    """Wraper function that checks if a category exists in the database."""
    @wraps(func)
    def wrapper(category_name, item_name):
        category = session.query(Category).filter_by(
            name=category_name).one_or_none()
        if not category:
            return redirect(url_for('home.showCatalog'))
        else:
            return func(category_name, item_name)
    return wrapper


def user_authorized(func):
    """
    Wraper function that checks if users are allowed to edit/delete items.
    """
    @wraps(func)
    def wrapper(category_name, item_name):
        item = session.query(Item).filter_by(name=item_name).one()
        if item.user_id != login_session['user_id']:
            flash('You can only edit or delete items you created yourself.')
            return redirect(
                url_for(
                    'item.showItem',
                    category_name=category_name,
                    item_name=item_name))
        else:
            return func(category_name, item_name)
    return wrapper


@item.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def addItem():
    """
    Renders the add item page for users that are logged in and creates a new
    Item in the database if a POST request comes in.
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category']
        if session.query(Item).filter_by(
                name=name,
                category_id=category_id).one_or_none():
            return render_template('additem.html',
                                   error='Item already excists!')
        item = Item(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(item)
        session.commit()
        return redirect(url_for('home.showCatalog'))
    else:
        return render_template('additem.html', categories=categories)


@item.route('/catalog/<string:category_name>/<string:item_name>/')
@item_exists
@category_exists
def showItem(category_name, item_name):
    """Renders the item pag."""
    category = session.query(Category).filter_by(
        name=category_name).one_or_none()
    item = session.query(Item).filter_by(
        name=item_name, category_id=category.id).one_or_none()
    return render_template('item.html', item=item, category=category)


@item.route(
    '/catalog/<string:category_name>/<string:item_name>/edit',
    methods=[
        'GET',
        'POST'])
@item_exists
@category_exists
@login_required
@user_authorized
def editItem(category_name, item_name):
    """
    Renders the edit item page for users that are logged in and edits the
    selected item if a POST request comes in.
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    item = session.query(Item).filter_by(name=item_name).one()

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['price']:
            item.price = request.form['price']
        if request.form['category']:
            item.category_id = request.form['category']
        session.add(item)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(
            url_for(
                'category.showCategory',
                category_name=category_name))
    else:
        return render_template(
            'edititem.html',
            item=item,
            categories=categories)


@item.route(
    '/catalog/<string:category_name>/<string:item_name>/delete',
    methods=[
        'GET',
        'POST'])
@login_required
@user_authorized
def deleteItem(category_name, item_name):
    """
    Renders the delete item page for users that are logged in and deletes the
    selected item if a POST request comes in.
    """
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(
            url_for(
                'category.showCategory',
                category_name=category_name))
    else:
        return render_template('deleteitem.html', item=item)
