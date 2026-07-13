from flask import render_template, redirect, url_for, request, flash, session
from . import auth_bp
from models import db, User

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'Visitor')
        phone = request.form.get('phone')

        if not username or not email or not password:
            flash('შეავსეთ სავალდებულო ველები!', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('მომხმარებელი ამ სახელით ან მეილით უკვე არსებობს!', 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, role=role, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('რეგისტრაცია წარმატებით დასრულდა!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('წარმატებული ავტორიზაცია!', 'success')
            return redirect(url_for('properties.index'))
        
        flash('არასწორი მონაცემები!', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('თქვენ გამოხვედით სისტემიდან.', 'success')
    return redirect(url_for('auth.login'))