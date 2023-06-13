import sqlite3, click
from flask import current_app, g

def get_database():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def reset_auth_count(app):
    with app.app_context():
        database = get_database()
        database.execute(
            'UPDATE user SET auth_attempt = 0'
        )
        database.commit()
        print('Resetted All User\'s Authentication Retries.')

def close_database(e=None):
    database = g.pop('db', None)
    if database is not None:
        database.close()

def init_database():
    database = get_database()
    with current_app.open_resource('schema.sql') as f:
        database.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_database_command():
    init_database()
    click.echo('Initialized the Blog Database')

def init_app(app):
    app.teardown_appcontext(close_database)
    app.cli.add_command(init_database_command)
    app.cli.add_command(show_database)


@click.command('show-db')
def show_database():
    database = get_database()
    users = database.execute(
        'SELECT * FROM user'
    ).fetchall()
    print('Accounts\n--------------')
    for row in users:
        data_row = ""
        for key in row.keys():
            data_row += f" {row[key]}"
        print(data_row)
    print('Posts\n--------------')
    posts = database.execute(
        'SELECT * FROM post'
    )
    for post in posts:
        post_string = ""
        for key in post.keys():
            post_string += f" {post[key]}"
        print(post_string)