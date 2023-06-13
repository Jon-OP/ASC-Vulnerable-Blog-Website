from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from apu_blog.auth import login_required
from apu_blog.db import get_database

blueprint = Blueprint('blog', __name__)

# [Not Important] Redirect Users to Home Page; Displays all Posts by all Users
@blueprint.route('/')
def index():
    database = get_database()
    posts = database.execute(
        'SELECT p.id, title, body, created, author_id, username, profile_picture'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# [Not Important] Allow User to create their own Posts
@blueprint.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            database = get_database()
            database.execute(
                'INSERT INTO post (title, body, author_id, author_profile_picture)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], g.user['profile_picture'])
            )
            database.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

# [Not Important] Retrieve specific Post by ID and User from the Database
def get_post(id, check_author = True):
    post = get_database().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (id,)
    ).fetchone()

    if post is None:
        abort(404, f'Post ID {id} doesn\'t exist.')
        
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

# [Not Important] Allow Users to Update their own post
@blueprint.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    id = request.args.get('id')
    post = get_post(id)
    if request.method == 'POST':
        title = request.args.get("title")
        print(title)
        title = request.form['title']
        body = request.form['body']
        print(request.args.get('name'))
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            database = get_database()
            database.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?', (title, body, id)
            )
            database.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

# [Not Important] Allow Users to Delete their own Post
@blueprint.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    database = get_database()
    database.execute('DELETE FROM post WHERE id = ?', (id,))
    database.commit()
    return redirect(url_for('blog.index'))