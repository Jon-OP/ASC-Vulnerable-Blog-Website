import os
from flask import Flask, render_template, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler

def create_app(test_config = None):
    from . import db, auth, blog
    app = Flask(__name__, instance_relative_config=True)

    # STATIC FOLDER TO STORE USER'S PROFILE PICTURE + SPECIFY ALLOWED FILE FORMAT - Unrestricted File Upload
    PROFILE_PICTURE_FOLDER = os.path.join(app.root_path, 'static', 'profile_picture')
    ALLOWED_PROFILE_PICTURE_FORMAT = {'png', 'jpg', 'jpeg'}

    app.config['PROFILE_PICTURE_FOLDER'] = PROFILE_PICTURE_FOLDER
    app.config['ALLOWED_PROFILE_PICTURE_FORMAT'] = ALLOWED_PROFILE_PICTURE_FORMAT
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'apu_blog.sqlite')
    )
    app.config['SCHEDULER'] = BackgroundScheduler()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Connect Database to App and Register Blueprints
    db.init_app(app)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(blog.blueprint)

    # Configure Scheduler to reset Auth_Attempt on User Account every 20 minutes - Login Page Vulnerability (Anti-Bruteforce Mechanism)
    app.config['SCHEDULER'].add_job(
        lambda: db.reset_auth_count(app), trigger='interval', minutes=20
    )
    app.config['SCHEDULER'].start()

    @app.route('/hello')
    def hello():
        return 'Hello Universe'

    # # Old Vulnerable Command - SSTI/XSS Vulnerability
    # @app.errorhandler(404)
    # def page_not_found(error):
    #     error_message = "ERROR {}".format(error)
    #     print(error_message)
    #     return render_template_string(error_message)

    # Sanitized Command
    @app.errorhandler(404)
    def page_not_found(error):
        error_message = "ERROR {}".format(error)
        return render_template('error_404.html', error_message=error_message)

    return app