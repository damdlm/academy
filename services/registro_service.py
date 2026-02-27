"""Serviço para operações com registros de treino"""

from models import db, RegistroTreino, HistoricoTreino
from sqlalchemy.orm import joinedload
from datetime import datetime
from . import BaseService
import logging

logger = logging.getLogger(__name__)

class RegistroService(BaseService):
    """Gerencia operações relacionadas a registros de treino"""
    
    @staticmethod
    def get_all(filtros=None, user_id=None, load_series=False):
        """Retorna registros com filtros opcionais"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                return []
            
            query = RegistroTreino.query.filter_by(user_id=user_id)
            
            if load_series:
                query = query.options(joinedload(RegistroTreino.series))
            
            if filtros:
                if 'treino_id' in filtros and filtros['treino_id']:
                    query = query.filter_by(treino_id=filtros['treino_id'])
                if 'periodo' in filtros and filtros['periodo']:
                    query = query.filter_by(periodo=filtros['periodo'])
                if 'semana' in filtros and filtros['semana'] is not None:
                    query = query.filter_by(semana=filtros['semana'])
                if 'exercicio_id' in filtros and filtros['exercicio_id']:
                    query = query.filter_by(exercicio_id=filtros['exercicio_id'])
                if 'versao_id' in filtros and filtros['versao_id']:
                    query = query.filter_by(versao_id=filtros['versao_id'])
            
            return query.order_by(RegistroTreino.data_registro.desc()).all()
        except Exception as e:
            BaseService.handle_error(e, "Erro ao buscar registros")
            return []
    
    @staticmethod
    def salvar_registros(treino_id, versao_id, periodo, semana, dados_exercicios, user_id=None):
        """Salva múltiplos registros de uma sessão de treino"""
        try:
            if user_id is None:
                user_id = BaseService.get_current_user_id()
            if not user_id:
                logger.warning("Tentativa de salvar registros sem usuário logado")
                return False
            
            # Remover registros antigos da mesma sessão
            RegistroTreino.query.filter_by(
                treino_id=treino_id,
                periodo=periodo,
                semana=semana,
                versao_id=versao_id,
                user_id=user_id
            ).delete()
            
            # Criar novos registros
            for ex_id, dados in dados_exercicios.items():
                if dados['carga'] and dados['repeticoes']:
                    registro = RegistroTreino(
                        treino_id=treino_id,
                        versao_id=versao_id,
                        periodo=periodo,
                        semana=semana,
                        exercicio_id=ex_id,
                        data_registro=dados.get('data_registro', datetime.now()),
                        user_id=user_id
                    )
                    db.session.add(registro)
                    db.session.flush()
                    
                    # Criar séries
                    for i in range(dados['num_series']):
                        serie = HistoricoTreino(
                            registro_id=registro.id,
                            carga=dados['carga'],
                            repeticoes=dados['repeticoes'],
                            ordem=i+1
                        )
                        db.session.add(serie)
            
            db.session.commit()
            logger.info(f"Registros salvos para treino {treino_id}, semana {semana}")
            return True
        except Exception as e:
            BaseService.handle_error(e, "Erro ao salvar registros")
            return False
    
    @staticmethod
    def get_periodos_existentes(user_id=None):
        """Retorna lista de períodos com registros"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                return []
            
            registros = RegistroTreino.query\
                .filter_by(user_id=user_id)\
                .with_entities(RegistroTreino.periodo)\
                .distinct().all()
            
            return sorted([r[0] for r in registros], reverse=True)
        except Exception as e:
            BaseService.handle_error(e, "Erro ao buscar períodos")
            return []
    
    @staticmethod
    def get_semanas_por_periodo(user_id=None):
        """Retorna dicionário com semanas agrupadas por período"""
        try:
            registros = RegistroService.get_all(user_id=user_id)
            
            semanas_set = set()
            for r in registros:
                semanas_set.add((r.periodo, r.semana, f"{r.periodo}_{r.semana}"))
            
            periodos_dict = {}
            for periodo, semana, key in semanas_set:
                if periodo not in periodos_dict:
                    periodos_dict[periodo] = []
                periodos_dict[periodo].append({
                    "semana": semana,
                    "key": key
                })
            
            return periodos_dict
        except Exception as e:
            BaseService.handle_error(e, "Erro ao agrupar semanas")
            return {}
    
    @staticmethod
    def get_volume_total_por_semana(registros):
        """Calcula volume total por semana"""
        try:
            volume_por_semana = {}
            for r in registros:
                key = f"{r.periodo}_{r.semana}"
                if key not in volume_por_semana:
                    volume_por_semana[key] = 0
                
                for serie in r.series:
                    volume_por_semana[key] += float(serie.carga) * serie.repeticoes
            
            return volume_por_semana
        except Exception as e:
            logger.error(f"Erro ao calcular volume por semana: {e}")
            return {}