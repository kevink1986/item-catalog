from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

from flask import session as login_session
import string
import random

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius:150px;
                -moz-border-radius-webkit-border-radius: 150px;
                -moz-border-radius: 150px;"> '''
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    json = []
    for c in categories:
        category = c.serialize
        item_list = []
        for i in items:
            if c.id == i.category_id:
                item_list.append(i.serialize)
        category['item'] = item_list
        json.append(category)
    return jsonify(Category=json)


@app.route('/')
@app.route('/catalog')
def showCatalog():
    # This is a catalog application"
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(8)
    return render_template('catalog.html', categories=categories, items=items)


# Add a catalog item
@app.route('/catalog/add', methods=['GET', 'POST'])
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
        return redirect(url_for('showCatalog'))
    else:
        return render_template('additem.html', categories=categories)


# Show a category of catalog items
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if not any(c.name == category_name for c in categories):
        return redirect(url_for('showCatalog'))
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


# Show a catalog item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
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
@app.route(
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
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template(
            'edititem.html',
            item=item,
            categories=categories)


# Delete a catalog item
@app.route(
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
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleteitem.html', item=item)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
