"""Serviço para operações com músculos"""

from models import Musculo
from . import BaseService
import logging

logger = logging.getLogger(__name__)

class MusculoService(BaseService):
    """Gerencia operações relacionadas a músculos"""
    
    @staticmethod
    def get_all():
        """Retorna todos os músculos"""
        try:
            return Musculo.query.order_by(Musculo.nome_exibicao).all()
        except Exception as e:
            logger.error(f"Erro ao buscar músculos: {e}")
            return []
    
    @staticmethod
    def get_all_nomes():
        """Retorna lista com nomes de exibição dos músculos"""
        try:
            musculos = MusculoService.get_all()
            return [m.nome_exibicao for m in musculos]
        except Exception as e:
            logger.error(f"Erro ao buscar nomes dos músculos: {e}")
            return []
    
    @staticmethod
    def get_by_id(musculo_id):
        """Retorna músculo por ID"""
        try:
            return Musculo.query.get(musculo_id)
        except Exception as e:
            logger.error(f"Erro ao buscar músculo {musculo_id}: {e}")
            return None
    
    @staticmethod
    def get_by_nome_exibicao(nome_exibicao):
        """Retorna músculo pelo nome de exibição"""
        try:
            return Musculo.query.filter_by(nome_exibicao=nome_exibicao).first()
        except Exception as e:
            logger.error(f"Erro ao buscar músculo {nome_exibicao}: {e}")
            return None
    
    @staticmethod
    def get_by_nome(nome):
        """Retorna músculo pelo nome (lowercase)"""
        try:
            return Musculo.query.filter_by(nome=nome.lower()).first()
        except Exception as e:
            logger.error(f"Erro ao buscar músculo {nome}: {e}")
            return None