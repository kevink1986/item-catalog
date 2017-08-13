from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

from flask import session as login_session
import string, random

#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


#Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def showCatalog():
    #return "This is a catalog application"
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(8)
    return render_template('catalog.html', categories=categories, items=items)

#Show a category of catalog items
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if not any(c.name == category_name for c in categories):
        return redirect(url_for('showCatalog'))
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    count = len(items)
    return render_template('category.html', categories=categories, category=category, items=items, count=count)
    #return "This is a list of catalog items of category: %s" % category_name


#Add a catalog item
@app.route('/catalog/<string:category_name>/add')
def addItem(category_name, item_name):
    return "Add a new item to category %s" % category_name


#Show a catalog item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    category = session.query(Category).filter_by(name = category_name).one()
    item = session.query(Item).filter_by(name = item_name, category_id = category.id).one()
    return render_template('item.html', item=item)
    #return "Show catalog item %s from category %s" % (item_name, category_name)


#Edit a catalog item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def editItem(category_name, item_name):
    return "Edit catalog item %s from category %s" % (item_name, category_name)


#Delete a catalog item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete')
def deleteItem(category_name, item_name):
    return "Delete catalog item %s from category %s" % (item_name, category_name)



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)