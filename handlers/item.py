from flask import Blueprint, render_template, redirect, url_for, flash, request

from database_setup import Base, User, Category, Item
from database_session import *

from flask import session as login_session

item = Blueprint('item', __name__)

# Add a catalog item
@item.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
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
            category_id=category_id)
        session.add(item)
        session.commit()
        return redirect(url_for('home.showCatalog'))
    else:
        return render_template('additem.html', categories=categories)


# Show a catalog item
@item.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    category = session.query(Category).filter_by(
        name=category_name).one_or_none()
    if not category:
        return redirect(url_for('showCatalog'))
    item = session.query(Item).filter_by(
        name=item_name, category_id=category.id).one_or_none()
    if not item:
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('item.html', item=item, category=category)


# Edit a catalog item
@item.route(
    '/catalog/<string:category_name>/<string:item_name>/edit',
    methods=[
        'GET',
        'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
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
        return redirect(url_for('category.showCategory', category_name=category_name))
    else:
        return render_template(
            'edititem.html',
            item=item,
            categories=categories)


# Delete a catalog item
@item.route(
    '/catalog/<string:category_name>/<string:item_name>/delete',
    methods=[
        'GET',
        'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('category.showCategory', category_name=category_name))
    else:
        return render_template('deleteitem.html', item=item)
