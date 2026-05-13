import os
from app import app, db, bcrypt
from flask import render_template, send_from_directory, request, redirect, url_for, flash, abort
from app.db_classes import User
from flask_login import login_user, logout_user
from app.forms import LoginForm
from app.notes_utils import scan_notes_tree, get_note_content, search_notes, get_folder_children, NOTES_DIR

#region login

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect('/')
        flash('Login invalid', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#endregion login

#region notes

@app.route('/')
def index():
    tree = scan_notes_tree()
    return render_template('index.html', tree=tree)

@app.route('/notes/<path:note_path>')
def view_note(note_path):
    notes_real = os.path.realpath(NOTES_DIR)
    requested = os.path.realpath(os.path.join(NOTES_DIR, note_path))
    if not requested.startswith(notes_real + os.sep):
        abort(404)
    if not os.path.isfile(requested):
        abort(404)
    tree = scan_notes_tree()
    title, content = get_note_content(requested, note_path)
    return render_template('note.html', title=title, content=content, tree=tree, current_path=note_path)

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = search_notes(q) if q else []
    tree = scan_notes_tree()
    return render_template('search.html', results=results, query=q, tree=tree)

@app.route('/browse/<path:folder_path>')
def browse_folder(folder_path):
    notes_real = os.path.realpath(NOTES_DIR)
    folder_abs = os.path.realpath(os.path.join(NOTES_DIR, folder_path))
    if not folder_abs.startswith(notes_real + os.sep):
        abort(404)
    if not os.path.isdir(folder_abs):
        abort(404)
    title, folder_note_path, children = get_folder_children(folder_path)
    parts = folder_path.replace("\\", "/").split("/")
    breadcrumbs = [{"title": p, "path": "/".join(parts[:i + 1])} for i, p in enumerate(parts)]
    tree = scan_notes_tree()
    return render_template('folder.html', title=title, folder_note_path=folder_note_path,
                           children=children, breadcrumbs=breadcrumbs, tree=tree)

@app.route('/notes-files/<path:filename>')
def notes_files(filename):
    return send_from_directory(NOTES_DIR, filename)

#endregion notes
