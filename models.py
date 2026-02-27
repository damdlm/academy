from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# =====================================================
# MODELO DE USUÁRIO
# =====================================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    treinos = db.relationship('Treino', backref='usuario', lazy=True, cascade='all, delete-orphan')
    exercicios = db.relationship('Exercicio', backref='usuario', lazy=True, cascade='all, delete-orphan')
    versoes = db.relationship('VersaoGlobal', backref='usuario', lazy=True, cascade='all, delete-orphan')
    registros = db.relationship('RegistroTreino', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# =====================================================
# MODELOS DE DADOS
# =====================================================

class Treino(db.Model):
    __tablename__ = 'treinos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(1), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    exercicios = db.relationship('Exercicio', backref='treino_ref', lazy=True, cascade='all, delete-orphan')
    versoes = db.relationship('TreinoVersao', backref='treino_ref', lazy=True, cascade='all, delete-orphan')
    registros = db.relationship('RegistroTreino', backref='treino_ref', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'codigo', name='unique_treino_por_usuario'),
        db.Index('idx_treino_user', 'user_id'),
        db.Index('idx_treino_codigo', 'codigo'),
    )

class Musculo(db.Model):
    __tablename__ = 'musculos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    nome_exibicao = db.Column(db.String(50), nullable=False)
    
    exercicios = db.relationship('Exercicio', backref='musculo_ref', lazy=True)

class Exercicio(db.Model):
    __tablename__ = 'exercicios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, default='')
    musculo_id = db.Column(db.Integer, db.ForeignKey('musculos.id'))
    treino_id = db.Column(db.Integer, db.ForeignKey('treinos.id', ondelete='SET NULL'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    versoes = db.relationship('VersaoExercicio', backref='exercicio_ref', lazy=True, cascade='all, delete-orphan')
    registros = db.relationship('RegistroTreino', backref='exercicio_ref', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_exercicio_user', 'user_id'),
        db.Index('idx_exercicio_treino', 'treino_id'),
        db.Index('idx_exercicio_musculo', 'musculo_id'),  # NOVO ÍNDICE
    )

class VersaoGlobal(db.Model):
    __tablename__ = 'versoes_globais'
    id = db.Column(db.Integer, primary_key=True)
    numero_versao = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    divisao = db.Column(db.String(10), nullable=False, default='ABC')  # 👈 NOVO CAMPO
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    treinos = db.relationship('TreinoVersao', backref='versao_ref', lazy=True, cascade='all, delete-orphan')
    registros = db.relationship('RegistroTreino', backref='versao_ref', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'numero_versao', name='unique_versao_por_usuario'),
        db.Index('idx_versao_user_data', 'user_id', 'data_inicio', 'data_fim'),
    )

class TreinoVersao(db.Model):
    __tablename__ = 'treinos_versao'
    id = db.Column(db.Integer, primary_key=True)
    versao_id = db.Column(db.Integer, db.ForeignKey('versoes_globais.id', ondelete='CASCADE'), nullable=False)
    treino_id = db.Column(db.Integer, db.ForeignKey('treinos.id', ondelete='CASCADE'), nullable=False)
    nome_treino = db.Column(db.String(100), nullable=False)
    descricao_treino = db.Column(db.String(200))
    ordem = db.Column(db.Integer, default=0)
    
    exercicios = db.relationship('VersaoExercicio', backref='treino_versao_ref', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('versao_id', 'treino_id', name='unique_treino_na_versao'),
        db.Index('idx_treino_versao_versao', 'versao_id'),  # NOVO ÍNDICE
        db.Index('idx_treino_versao_treino', 'treino_id'),  # NOVO ÍNDICE
    )

class VersaoExercicio(db.Model):
    __tablename__ = 'versao_exercicios'
    id = db.Column(db.Integer, primary_key=True)
    treino_versao_id = db.Column(db.Integer, db.ForeignKey('treinos_versao.id', ondelete='CASCADE'), nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicios.id', ondelete='CASCADE'), nullable=False)
    ordem = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('treino_versao_id', 'exercicio_id', name='unique_exercicio_na_versao'),
        db.Index('idx_versao_exercicio_treino', 'treino_versao_id'),  # NOVO ÍNDICE
        db.Index('idx_versao_exercicio_exercicio', 'exercicio_id'),  # NOVO ÍNDICE
    )

class RegistroTreino(db.Model):
    __tablename__ = 'registros_treino'
    id = db.Column(db.Integer, primary_key=True)
    treino_id = db.Column(db.Integer, db.ForeignKey('treinos.id'), nullable=False)
    versao_id = db.Column(db.Integer, db.ForeignKey('versoes_globais.id'), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)
    semana = db.Column(db.Integer, nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicios.id'), nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    series = db.relationship('HistoricoTreino', backref='registro_ref', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_registro_user_data', 'user_id', 'data_registro'),
        db.Index('idx_registro_busca', 'user_id', 'treino_id', 'periodo', 'semana'),
        db.Index('idx_registro_exercicio', 'exercicio_id'),
        db.Index('idx_registro_versao', 'versao_id'),  # NOVO ÍNDICE
        db.Index('idx_registro_periodo_semana', 'periodo', 'semana'),  # NOVO ÍNDICE
    )

class HistoricoTreino(db.Model):
    __tablename__ = 'historico_treino'
    id = db.Column(db.Integer, primary_key=True)
    registro_id = db.Column(db.Integer, db.ForeignKey('registros_treino.id', ondelete='CASCADE'), nullable=False)
    carga = db.Column(db.Numeric(5,1), nullable=False)
    repeticoes = db.Column(db.Integer, nullable=False)
    ordem = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.Index('idx_historico_registro', 'registro_id'),
        db.Index('idx_historico_carga', 'carga'),  # NOVO ÍNDICE
    )