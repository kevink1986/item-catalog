from flask import Flask

from handlers import home, auth, category, item, catalog_api


app = Flask(__name__)
app.register_blueprint(home.home)
app.register_blueprint(auth.auth)
app.register_blueprint(category.category)
app.register_blueprint(item.item)
app.register_blueprint(catalog_api.catalog_api)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
