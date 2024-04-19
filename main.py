import os
from flask import Flask
from application.config import LocalDevConfig
from application.config import ProdConfig, desired_config
from application.database import db

app = None

def create_app():
    app = Flask(__name__)
    print(app)
    if desired_config == 'production':
        print("starting production development")
        app.config.from_object(ProdConfig)
    elif desired_config == 'development' :
        print("starting local development")
        app.config.from_object(LocalDevConfig)
    db.init_app(app)
    app.app_context().push()
    return app
app = create_app()

from application.controllers import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080)
