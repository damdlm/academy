"""Serviço para operações com exercícios"""

from models import db, Exercicio, Musculo, HistoricoTreino, RegistroTreino
from sqlalchemy.orm import joinedload
from . import BaseService
import logging

logger = logging.getLogger(__name__)

class ExercicioService(BaseService):
    """Gerencia operações relacionadas a exercícios"""
    
    @staticmethod
    def get_all(user_id=None, load_relations=False):
        """Retorna todos os exercícios do usuário"""
        try:
            query = Exercicio.query
            query = BaseService.filter_by_user(query, user_id)
            
            if load_relations:
                query = query.options(
                    joinedload(Exercicio.musculo_ref),
                    joinedload(Exercicio.treino_ref)
                )
            
            return query.order_by(Exercicio.nome).all()
        except Exception as e:
            BaseService.handle_error(e, "Erro ao buscar exercícios")
            return []
    
    @staticmethod
    def get_by_id(exercicio_id, user_id=None, load_relations=False):
        """Retorna exercício por ID"""
        try:
            query = Exercicio.query.filter_by(id=exercicio_id)
            query = BaseService.filter_by_user(query, user_id)
            
            if load_relations:
                query = query.options(
                    joinedload(Exercicio.musculo_ref),
                    joinedload(Exercicio.treino_ref)
                )
            
            return query.first()
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao buscar exercício {exercicio_id}")
            return None
    
    @staticmethod
    def get_by_treino(treino_id, user_id=None):
        """Retorna exercícios de um treino"""
        try:
            query = Exercicio.query.filter_by(treino_id=treino_id)
            query = BaseService.filter_by_user(query, user_id)
            return query.all()
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao buscar exercícios do treino {treino_id}")
            return []
    
    @staticmethod
    def get_musculo_id(nome_musculo):
        """Retorna ID do músculo pelo nome"""
        try:
            musculo = Musculo.query.filter_by(nome_exibicao=nome_musculo).first()
            return musculo.id if musculo else None
        except Exception as e:
            logger.error(f"Erro ao buscar ID do músculo {nome_musculo}: {e}")
            return None
    
    @staticmethod
    def create(nome, musculo_nome, treino_id=None, descricao='', user_id=None):
        """Cria novo exercício"""
        try:
            if user_id is None:
                user_id = BaseService.get_current_user_id()
            if not user_id:
                logger.warning("Tentativa de criar exercício sem usuário logado")
                return None
            
            musculo_id = ExercicioService.get_musculo_id(musculo_nome)
            
            exercicio = Exercicio(
                nome=nome,
                descricao=descricao,
                musculo_id=musculo_id,
                treino_id=treino_id,
                user_id=user_id
            )
            db.session.add(exercicio)
            db.session.commit()
            logger.info(f"Exercício '{nome}' criado para usuário {user_id}")
            return exercicio
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao criar exercício '{nome}'")
            return None
    
    @staticmethod
    def update(exercicio_id, nome=None, musculo_nome=None, treino_id=None, 
               descricao=None, user_id=None):
        """Atualiza exercício"""
        try:
            exercicio = ExercicioService.get_by_id(exercicio_id, user_id)
            if not exercicio:
                logger.warning(f"Exercício {exercicio_id} não encontrado")
                return None
            
            if nome:
                exercicio.nome = nome
            if descricao is not None:
                exercicio.descricao = descricao
            if treino_id is not None:
                exercicio.treino_id = treino_id
            if musculo_nome:
                musculo_id = ExercicioService.get_musculo_id(musculo_nome)
                if musculo_id:
                    exercicio.musculo_id = musculo_id
            
            db.session.commit()
            logger.info(f"Exercício {exercicio_id} atualizado")
            return exercicio
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao atualizar exercício {exercicio_id}")
            return None
    
    @staticmethod
    def delete(exercicio_id, user_id=None):
        """Exclui exercício"""
        try:
            exercicio = ExercicioService.get_by_id(exercicio_id, user_id)
            if not exercicio:
                logger.warning(f"Exercício {exercicio_id} não encontrado")
                return False
            
            db.session.delete(exercicio)
            db.session.commit()
            logger.info(f"Exercício {exercicio_id} excluído")
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao excluir exercício {exercicio_id}")
            return False
    
    @staticmethod
    def get_ultima_carga(exercicio_id, user_id=None):
        """Retorna última carga do exercício"""
        try:
            query = RegistroTreino.query.filter_by(exercicio_id=exercicio_id)
            query = BaseService.filter_by_user(query, user_id)
            registro = query.order_by(RegistroTreino.data_registro.desc()).first()
            
            if registro and registro.series:
                primeira_serie = registro.series[0]
                return float(primeira_serie.carga)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar última carga do exercício {exercicio_id}: {e}")
            return None
    
    @staticmethod
    def get_ultimas_series(exercicio_id, versao_id=None, limite=1, user_id=None):
        """Retorna as últimas séries de um exercício"""
        try:
            query = HistoricoTreino.query\
                .join(RegistroTreino)\
                .filter(RegistroTreino.exercicio_id == exercicio_id)
            
            query = BaseService.filter_by_user(query, user_id)
            
            if versao_id:
                query = query.filter(RegistroTreino.versao_id == versao_id)
            
            series = query.order_by(RegistroTreino.data_registro.desc())\
                .limit(limite).all()
            
            resultado = []
            for serie in series:
                resultado.append({
                    'carga': float(serie.carga),
                    'repeticoes': serie.repeticoes
                })
            
            return resultado
        except Exception as e:
            logger.error(f"Erro ao buscar últimas séries: {e}")
            return []