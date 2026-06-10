from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import database
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=BASE_DIR)
app.secret_key = 'python-tutorial-secret-key-change-in-production'

database.init_db()


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        error = None
        if not username or not email or not password:
            error = 'Все поля обязательны для заполнения.'
        elif len(username) < 3:
            error = 'Имя пользователя должно содержать минимум 3 символа.'
        elif len(password) < 6:
            error = 'Пароль должен содержать минимум 6 символов.'
        elif password != confirm:
            error = 'Пароли не совпадают.'
        else:
            db = database.get_db()
            existing = db.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()
            db.close()
            if existing:
                error = 'Пользователь с таким именем или email уже существует.'

        if error:
            flash(error, 'error')
            return render_template('register.html', username=username, email=email)

        db = database.get_db()
        db.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, generate_password_hash(password))
        )
        db.commit()
        db.close()
        flash('Регистрация прошла успешно! Войдите в систему.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', username='', email='')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('admin') if session.get('role') == 'admin' else url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        db = database.get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        db.close()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Неверное имя пользователя или пароль.', 'error')
            return render_template('login.html', username=username)

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        flash(f'Добро пожаловать, {user["username"]}!', 'success')
        if user['role'] == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('index'))

    return render_template('login.html', username='')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('Доступ запрещён. Требуются права администратора.', 'error')
        return redirect(url_for('login'))

    db = database.get_db()
    users = db.execute(
        'SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    total = len(users)
    admins = sum(1 for u in users if u['role'] == 'admin')
    students = total - admins
    db.close()

    return render_template('admin.html', users=users, total=total, admins=admins, students=students)


@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if user_id == session.get('user_id'):
        flash('Нельзя удалить собственный аккаунт.', 'error')
        return redirect(url_for('admin'))

    db = database.get_db()
    user = db.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    if user and user['role'] == 'admin':
        flash('Нельзя удалить другого администратора.', 'error')
        db.close()
        return redirect(url_for('admin'))

    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    flash('Пользователь удалён.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/role/<int:user_id>', methods=['POST'])
def change_role(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if user_id == session.get('user_id'):
        flash('Нельзя изменить собственную роль.', 'error')
        return redirect(url_for('admin'))

    new_role = request.form.get('role', 'student')
    if new_role not in ('student', 'admin'):
        new_role = 'student'

    db = database.get_db()
    db.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    db.commit()
    db.close()
    flash('Роль пользователя обновлена.', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = database.get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user is None:
        flash('Пользователь не найден.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_role = request.form.get('role', 'student')

        error = None
        if not new_username or not new_email or not new_role:
            error = 'Все поля обязательны для заполнения.'
        elif len(new_username) < 3:
            error = 'Имя пользователя должно содержать минимум 3 символа.'
        elif new_role not in ('student', 'admin'):
            error = 'Недопустимая роль.'
        elif user_id == session.get('user_id') and new_role != 'admin':
            error = 'Нельзя изменить собственную роль.'
        else:
            existing = db.execute(
                'SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?',
                (new_username, new_email, user_id)
            ).fetchone()
            if existing:
                error = 'Пользователь с таким именем или email уже существует.'

        if error:
            flash(error, 'error')
        else:
            db.execute(
                'UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?',
                (new_username, new_email, new_role, user_id)
            )
            db.commit()
            flash('Пользователь обновлён.', 'success')
            if user_id == session.get('user_id'):
                session['username'] = new_username
                session['role'] = new_role
        
        db.close()
        return redirect(url_for('admin'))

    db.close()
    return render_template('admin_edit.html', user=user)


@app.route('/api/me')
def api_me():
    return jsonify({
        'logged_in': bool(session.get('user_id')),
        'username': session.get('username', ''),
        'role': session.get('role', ''),
    })


@app.route('/api/submit-code', methods=['POST'])
def submit_code():
    if not session.get('user_id'):
        return jsonify({'ok': False, 'error': 'Необходимо войти в систему.'}), 401

    data = request.get_json(silent=True) or {}
    lesson = data.get('lesson', '').strip()
    task_title = data.get('task_title', '').strip()
    student_code = data.get('student_code', '').strip()

    if not lesson or not student_code:
        return jsonify({'ok': False, 'error': 'Пустой код или не указан урок.'}), 400

    db = database.get_db()
    db.execute(
        'INSERT INTO quiz_submissions (user_id, username, lesson, task_title, student_code) VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], session['username'], lesson, task_title, student_code)
    )
    db.commit()
    db.close()
    return jsonify({'ok': True, 'message': 'Код отправлен на проверку!'})


@app.route('/admin/submissions')
def admin_submissions():
    if session.get('role') != 'admin':
        flash('Доступ запрещён.', 'error')
        return redirect(url_for('login'))

    db = database.get_db()
    submissions = db.execute(
        'SELECT * FROM quiz_submissions ORDER BY created_at DESC'
    ).fetchall()
    db.close()
    return render_template('admin_submissions.html', submissions=submissions)


@app.route('/api/submission/<int:sub_id>')
def get_submission(sub_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'forbidden'}), 403
    db = database.get_db()
    sub = db.execute('SELECT student_code FROM quiz_submissions WHERE id = ?', (sub_id,)).fetchone()
    db.close()
    if not sub:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'code': sub['student_code']})


@app.route('/admin/submissions/<int:sub_id>/status', methods=['POST'])
def update_submission_status(sub_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    status = request.form.get('status', 'pending')
    note = request.form.get('admin_note', '').strip()
    if status not in ('approved', 'rejected', 'pending'):
        status = 'pending'

    db = database.get_db()
    db.execute(
        'UPDATE quiz_submissions SET status = ?, admin_note = ? WHERE id = ?',
        (status, note, sub_id)
    )
    db.commit()
    db.close()
    flash('Статус обновлён.', 'success')
    return redirect(url_for('admin_submissions'))


# Защита страниц уроков — требует авторизации
@app.before_request
def require_login_for_lessons():
    path = request.path.lstrip('/')
    is_lesson = (
        path == 'lessons.html'
        or path.startswith('lesson-')
        or path == 'playground.html'
    )
    if is_lesson and not session.get('user_id'):
        flash('Для доступа к урокам необходимо войти в систему.', 'error')
        return redirect(url_for('login'))


# Serve all other static files (existing HTML pages, CSS, JS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


if __name__ == '__main__':
    print('Запуск сервера...')
    print('Откройте браузер: http://localhost:5000')
    print('Администратор: login=admin, password=admin123')
    app.run(debug=True, port=5000)
