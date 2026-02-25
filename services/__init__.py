"""Camada de serviços da aplicação"""

from flask_login import current_user
from models import db
import logging

logger = logging.getLogger(__name__)

class BaseService:
    """Classe base para todos os serviços"""
    
    @staticmethod
    def get_current_user_id():
        """Retorna ID do usuário atual"""
        return current_user.id if current_user and current_user.is_authenticated else None
    
    @staticmethod
    def filter_by_user(query, user_id=None):
        """Aplica filtro de usuário à query"""
        if user_id is None:
            user_id = BaseService.get_current_user_id()
        if user_id:
            return query.filter_by(user_id=user_id)
        return query
    
    @staticmethod
    def handle_error(e, message="Erro na operação"):
        """Tratamento padronizado de erros"""
        logger.error(f"{message}: {str(e)}", exc_info=True)
        db.session.rollback()
        return None

# Importar serviços para facilitar acesso
from .treino_service import TreinoService
from .exercicio_service import ExercicioService
from .musculo_service import MusculoService
from .versao_service import VersaoService
from .registro_service import RegistroService
from .estatistica_service import EstatisticaService

__all__ = [
    'BaseService',
    'TreinoService',
    'ExercicioService',
    'MusculoService',
    'VersaoService',
    'RegistroService',
    'EstatisticaService'
]