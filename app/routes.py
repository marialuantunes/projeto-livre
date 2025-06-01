
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from package.models import User, Post, Like
from package.utils import allowed_file
from app import db, login_manager

main = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all() if current_user.is_authenticated else []
    return render_template('index.html', posts=posts)

@main.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username e senha são obrigatórios', 'error')
        return redirect(url_for('routes.index'))

    if User.query.filter_by(username=username).first():
        flash('Username já existe', 'error')
        return redirect(url_for('routes.index'))

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash('Cadastro realizado com sucesso! Faça login', 'success')
    return redirect(url_for('routes.index'))

@main.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        flash('Username ou senhas inválidos', 'error')
        return redirect(url_for('routes.index'))

    login_user(user)
    flash('Login realizado com sucesso', 'success')
    return redirect(url_for('routes.index'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Deslogado com sucesso', 'success')
    return redirect(url_for('routes.index'))

@main.route('/posts/create', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    body = request.form.get('body')
    caption = request.form.get('caption')

    if not title or not body:
        flash('Título e conteúdo são obrigatóros', 'error')
        return redirect(url_for('routes.index'))


    image = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image = filename

    post = Post(
        title=title,
        body=body,
        image=image,
        caption=caption,
        author=current_user
    )
    db.session.add(post)
    db.session.commit()

    flash('Post criado com sucesso', 'success')
    return redirect(url_for('routes.index'))

@main.route('/posts/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author.id != current_user.id:
        flash('Você pode deletar apenas o seu post', 'error')
        return redirect(url_for('routes.index'))


    if post.image:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image))
        except OSError:
            pass

    db.session.delete(post)
    db.session.commit()

    flash('Post deletado com sucesso', 'success')
    return redirect(url_for('routes.index'))

@main.route('/posts/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)

    like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    if like:
        db.session.delete(like)
        action = 'removed'
    else:
        like = Like(
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(like)
        action = 'added'

    db.session.commit()

    flash(f'Like {action} successfully', 'success')
    return redirect(url_for('routes.index'))
