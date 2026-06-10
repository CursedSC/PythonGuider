import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password_hash TEXT  NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'student',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS quiz_submissions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            username     TEXT    NOT NULL,
            lesson       TEXT    NOT NULL,
            task_title   TEXT    NOT NULL,
            student_code TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'pending',
            admin_note   TEXT    DEFAULT '',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

    # Создать администратора по умолчанию (если ещё не существует)
    admin = db.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin:
        db.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@python-tutorial.ru', generate_password_hash('admin123'), 'admin')
        )
        db.commit()
        print('Администратор создан: login=admin, password=admin123')

    db.close()
