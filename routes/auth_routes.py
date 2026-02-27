from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from services.seed_service import SeedService
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

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
            logger.warning(f"Tentativa de login inválida para usuário: {username}")
            flash('Usuário ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        # Atualizar último login
        user.last_login = datetime.now()
        db.session.commit()
        
        login_user(user, remember=remember)
        logger.info(f"Usuário {username} logado com sucesso")
        flash(f'Bem-vindo, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
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
        
        if len(username) < 3:
            flash('Usuário deve ter pelo menos 3 caracteres', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Senha deve ter pelo menos 6 caracteres', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado', 'danger')
            return redirect(url_for('auth.register'))
        
        # Criar usuário
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Primeiro usuário é admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.flush()  # Para obter o ID do usuário
        
        # ===== NOVO: Criar apenas treinos mínimos (sem exercícios) =====
        logger.info(f"Criando treinos mínimos para novo usuário {username}")
        treinos_criados = SeedService.create_minimal_workouts(user.id)
        
        if treinos_criados:
            flash(f'Conta criada com {len(treinos_criados)} treinos básicos! Agora configure sua primeira versão.', 'success')
            logger.info(f"{len(treinos_criados)} treinos criados para {username}")
        else:
            flash('Conta criada, mas houve um erro ao configurar os treinos básicos.', 'warning')
            logger.error(f"Falha ao criar treinos para {username}")
        
        db.session.commit()
        
        logger.info(f"Novo usuário registrado: {username}")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logger.info(f"Usuário {current_user.username} fez logout")
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Página de perfil"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Alterar senha"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Todos os campos são obrigatórios', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('As senhas não coincidem', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('Nova senha deve ter pelo menos 6 caracteres', 'danger')
        return redirect(url_for('auth.profile'))
    
    if not current_user.check_password(current_password):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    logger.info(f"Senha alterada para usuário {current_user.username}")
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('auth.profile'))