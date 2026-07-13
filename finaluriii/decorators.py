from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ამ გვერდისთვის საჭიროა ავტორიზაცია!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                flash('თქვენ არ გაქვთ ამ მოქმედების უფლება!', 'error')
                return redirect(url_for('properties.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator