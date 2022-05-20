import os

from flask import Flask


def create_app(test_config=None):
    #instance_relative_config=True tells the app that configuration files are relative to the instance folder
    app = Flask(__name__, instance_relative_config=True)
    #app.config.from_mapping() sets some default configuration that the app will use:
    app.config.from_mapping(
 #SECRET_KEY is used by Flask and extensions to keep data safe. 
 # It’s set to 'dev' to provide a convenient value during development, but it should be overridden with a random value when deploying.
        SECRET_KEY='dev',
        #DATABASE is the path where the SQLite database file will be saved
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
#app.config.from_pyfile() overrides the default configuration with values taken from the config.py file in the instance folder if it exists.
#For example, when deploying, this can be used to set a real SECRET_KEY.
        app.config.from_pyfile('config.py', silent=True)
    else:
        #test_config can also be passed to the factory, and will be used instead of the instance configuration.
        app.config.from_mapping(test_config)

  #os.makedirs() ensures that app.instance_path exists. 
# Flask doesn’t create the instance folder automatically, but it needs to be created because your project will create the SQLite database file there.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

 #@app.route() creates a simple route so you can see the application 
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app