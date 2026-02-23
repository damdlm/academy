from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Usuário ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        flash(f'Bem-vindo, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de novo usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validações
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('As senhas não conferem', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verificar se usuário já existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Nome de usuário já existe', 'danger')
            return redirect(url_for('auth.register'))
        
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('E-mail já cadastrado', 'danger')
            return redirect(url_for('auth.register'))
        
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        
        # Primeiro usuário é admin
        if User.query.count() == 0:
            new_user.is_admin = True
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Alterar senha"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('As novas senhas não conferem', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('auth.profile'))