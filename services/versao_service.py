"""Serviço para operações com versões de treino"""

from models import db, VersaoGlobal, TreinoVersao, VersaoExercicio, Treino, Exercicio, Musculo
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from . import BaseService
from .treino_service import TreinoService
from .exercicio_service import ExercicioService
from utils.date_utils import converter_periodo_para_data
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VersaoService(BaseService):
    """Gerencia operações relacionadas a versões"""
    
    @staticmethod
    def get_all(user_id=None):
        """Retorna todas as versões do usuário"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                return []
            
            return VersaoGlobal.query.filter_by(user_id=user_id)\
                .order_by(VersaoGlobal.numero_versao.desc()).all()
        except Exception as e:
            BaseService.handle_error(e, "Erro ao buscar versões")
            return []
    
    @staticmethod
    def get_by_id(versao_id, user_id=None, load_relations=False):
        """Retorna versão por ID"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                return None
            
            query = VersaoGlobal.query.filter_by(id=versao_id, user_id=user_id)
            
            if load_relations:
                query = query.options(
                    joinedload(VersaoGlobal.treinos)
                    .joinedload(TreinoVersao.exercicios)
                )
            
            return query.first()
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao buscar versão {versao_id}")
            return None
    
    @staticmethod
    def get_ativa(periodo=None, user_id=None):
        """Retorna versão ativa para um período"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                return None
            
            if periodo:
                data_periodo = converter_periodo_para_data(periodo)
                return VersaoGlobal.query.filter(
                    VersaoGlobal.user_id == user_id,
                    VersaoGlobal.data_inicio <= data_periodo,
                    (VersaoGlobal.data_fim.is_(None) | (VersaoGlobal.data_fim >= data_periodo))
                ).order_by(VersaoGlobal.data_inicio.desc()).first()
            else:
                return VersaoGlobal.query.filter_by(user_id=user_id, data_fim=None).first()
        except Exception as e:
            BaseService.handle_error(e, "Erro ao buscar versão ativa")
            return None
    
    @staticmethod
    def create(descricao, data_inicio, divisao='ABC', data_fim=None, user_id=None):
        """Cria nova versão com divisão específica"""
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                logger.warning("Tentativa de criar versão sem usuário logado")
                return None
            
            # Validar divisão
            divisoes_validas = ['ABC', 'ABCD', 'ABCDE']
            if divisao not in divisoes_validas:
                logger.warning(f"Divisão inválida: {divisao}. Usando ABC.")
                divisao = 'ABC'
            
            # Finalizar versão atual se existir
            versao_atual = VersaoService.get_ativa(user_id=user_id)
            if versao_atual and not data_fim:
                versao_atual.data_fim = data_inicio
            
            ultima_versao = db.session.query(func.max(VersaoGlobal.numero_versao))\
                .filter_by(user_id=user_id).scalar() or 0
            
            nova_versao = VersaoGlobal(
                numero_versao=ultima_versao + 1,
                descricao=descricao,
                divisao=divisao,  # 👈 NOVO CAMPO
                data_inicio=data_inicio,
                data_fim=data_fim,
                user_id=user_id
            )
            db.session.add(nova_versao)
            db.session.commit()
            logger.info(f"Versão {nova_versao.numero_versao} criada com divisão {divisao}")
            return nova_versao
        except Exception as e:
            BaseService.handle_error(e, "Erro ao criar versão")
            return None
    
    @staticmethod
    def update(versao_id, descricao=None, divisao=None, data_inicio=None, data_fim=None, user_id=None):
        """Atualiza uma versão existente"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                logger.warning(f"Versão {versao_id} não encontrada")
                return None
            
            if descricao is not None:
                versao.descricao = descricao
            if divisao is not None:
                # Validar divisão
                divisoes_validas = ['ABC', 'ABCD', 'ABCDE']
                if divisao in divisoes_validas:
                    versao.divisao = divisao
                else:
                    logger.warning(f"Divisão inválida: {divisao}")
            if data_inicio is not None:
                versao.data_inicio = data_inicio
            if data_fim is not None:
                versao.data_fim = data_fim
            
            db.session.commit()
            logger.info(f"Versão {versao_id} atualizada")
            return versao
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao atualizar versão {versao_id}")
            return None
    
    @staticmethod
    def clone(versao_id, user_id=None):
        """Clona uma versão existente"""
        try:
            versao_origem = VersaoService.get_by_id(versao_id, user_id, load_relations=True)
            if not versao_origem:
                logger.warning(f"Versão {versao_id} não encontrada para clonagem")
                return False
            
            data_atual = datetime.now().date()
            
            # Verificar se já existe versão ativa
            versao_ativa = VersaoService.get_ativa(user_id=user_id)
            if versao_ativa:
                logger.warning("Tentativa de clonar com versão ativa existente")
                return False
            
            # Criar nova versão
            ultima_versao = db.session.query(func.max(VersaoGlobal.numero_versao))\
                .filter_by(user_id=user_id).scalar() or 0
            
            nova_versao = VersaoGlobal(
                numero_versao=ultima_versao + 1,
                descricao=f"Cópia de {versao_origem.descricao}",
                divisao=versao_origem.divisao,  # 👈 MANTER A MESMA DIVISÃO
                data_inicio=data_atual,
                data_fim=None,
                user_id=user_id
            )
            db.session.add(nova_versao)
            db.session.flush()
            
            # Clonar treinos
            for tv in versao_origem.treinos:
                exercicios_ids = [ve.exercicio_id for ve in tv.exercicios]
                VersaoService.adicionar_treino(
                    nova_versao.id,
                    tv.treino_ref.codigo if tv.treino_ref else str(tv.treino_id),
                    tv.nome_treino,
                    tv.descricao_treino,
                    exercicios_ids,
                    user_id
                )
            
            db.session.commit()
            logger.info(f"Versão {versao_id} clonada como versão {nova_versao.numero_versao}")
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao clonar versão {versao_id}")
            return False

    @staticmethod
    def _get_or_create_musculo(nome_exibicao):
        """Método auxiliar para obter ou criar músculo"""
        try:
            musculo = Musculo.query.filter_by(nome_exibicao=nome_exibicao).first()
            if not musculo:
                musculo = Musculo(
                    nome=nome_exibicao.lower(),
                    nome_exibicao=nome_exibicao
                )
                db.session.add(musculo)
                db.session.flush()
                logger.info(f"Músculo criado: {nome_exibicao}")
            return musculo
        except Exception as e:
            logger.error(f"Erro ao criar/obter músculo {nome_exibicao}: {e}")
            raise
    
    # ===== MÉTODO PRINCIPAL CORRIGIDO =====
    @staticmethod
    def create_with_split(descricao, data_inicio, split_type, data_fim=None, user_id=None):
        """
        Cria uma nova versão com todos os treinos de uma divisão pré-definida
        
        Args:
            descricao: Descrição da versão
            data_inicio: Data de início
            split_type: Tipo de divisão ("3x", "4x" ou "5x")
            data_fim: Data de fim (opcional)
            user_id: ID do usuário
        
        Returns:
            VersaoGlobal: Versão criada ou None em caso de erro
        """
        try:
            from data.workout_splits import ALL_SPLITS, MUSCLE_MAPPING
            
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                logger.warning("Tentativa de criar versão sem usuário logado")
                return None
            
            logger.info(f"Iniciando criação de versão para usuário {user_id} com split {split_type}")
            
            # Validar split_type
            if split_type not in ALL_SPLITS:
                logger.error(f"Tipo de divisão inválido: {split_type}")
                return None
            
            split_data = ALL_SPLITS[split_type]
            logger.info(f"Dados do split carregados: {split_data['nome']}")
            
            # Finalizar versão atual se existir
            versao_atual = VersaoService.get_ativa(user_id=user_id)
            if versao_atual and not data_fim:
                versao_atual.data_fim = data_inicio
                logger.info(f"Versão atual {versao_atual.id} finalizada em {data_inicio}")
            
            # Criar nova versão
            ultima_versao = db.session.query(func.max(VersaoGlobal.numero_versao))\
                .filter_by(user_id=user_id).scalar() or 0
            
            # ===== CORREÇÃO: Não concatenar o nome da divisão na descrição =====
            nova_versao = VersaoGlobal(
                numero_versao=ultima_versao + 1,
                descricao=descricao,  # Usar apenas a descrição fornecida pelo usuário
                data_inicio=data_inicio,
                data_fim=data_fim,
                user_id=user_id
            )
            db.session.add(nova_versao)
            db.session.flush()
            logger.info(f"Nova versão criada: ID {nova_versao.id}, número {nova_versao.numero_versao}")
            
            # Para cada treino na divisão, criar na versão
            for codigo, treino_data in split_data["treinos"].items():
                logger.info(f"Processando treino {codigo}: {treino_data['nome']}")
                
                # Verificar se o treino base já existe
                treino_base = Treino.query.filter_by(
                    user_id=user_id,
                    codigo=codigo
                ).first()
                
                if not treino_base:
                    # Criar treino base
                    treino_base = Treino(
                        codigo=codigo,
                        nome=treino_data["nome"],
                        descricao=treino_data.get("descricao", f"Treino {codigo}"),
                        user_id=user_id
                    )
                    db.session.add(treino_base)
                    db.session.flush()
                    logger.info(f"Treino base {codigo} criado (ID: {treino_base.id})")
                else:
                    logger.info(f"Treino base {codigo} já existe (ID: {treino_base.id})")
                
                # Criar associação do treino com a versão
                treino_versao = TreinoVersao(
                    versao_id=nova_versao.id,
                    treino_id=treino_base.id,
                    nome_treino=treino_data["nome"],
                    descricao_treino=treino_data.get("descricao", f"Treino {codigo} na versão"),
                    ordem=len(nova_versao.treinos)
                )
                db.session.add(treino_versao)
                db.session.flush()
                logger.info(f"Treino {codigo} associado à versão (ID: {treino_versao.id})")
                
                # Criar exercícios para este treino
                for ordem, ex_data in enumerate(treino_data["exercicios"]):
                    # Garantir que o músculo existe
                    musculo_nome = MUSCLE_MAPPING.get(ex_data["musculo"], ex_data["musculo"])
                    musculo = VersaoService._get_or_create_musculo(musculo_nome)
                    
                    # Verificar se exercício já existe
                    exercicio = Exercicio.query.filter_by(
                        user_id=user_id,
                        nome=ex_data["nome"]
                    ).first()
                    
                    if not exercicio:
                        exercicio = Exercicio(
                            nome=ex_data["nome"],
                            descricao=f"Exercício para {treino_data['nome']}",
                            musculo_id=musculo.id,
                            treino_id=treino_base.id,
                            user_id=user_id
                        )
                        db.session.add(exercicio)
                        db.session.flush()
                        logger.debug(f"Exercício criado: {ex_data['nome']} (ID: {exercicio.id})")
                    
                    # Associar exercício à versão
                    ve = VersaoExercicio(
                        treino_versao_id=treino_versao.id,
                        exercicio_id=exercicio.id,
                        ordem=ordem
                    )
                    db.session.add(ve)
            
            db.session.commit()
            logger.info(f"Versão {nova_versao.numero_versao} criada com divisão {split_type}")
            return nova_versao
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar versão com divisão {split_type}: {str(e)}", exc_info=True)
            BaseService.handle_error(e, f"Erro ao criar versão com divisão {split_type}")
            return None


    @staticmethod
    def delete(versao_id, user_id=None):
        """
        Exclui uma versão e todos os seus relacionamentos (cascade)
        
        Args:
            versao_id: ID da versão a ser excluída
            user_id: ID do usuário (opcional)
        
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        try:
            user_id = user_id or BaseService.get_current_user_id()
            if not user_id:
                logger.warning("Tentativa de excluir versão sem usuário logado")
                return False
            
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                logger.warning(f"Versão {versao_id} não encontrada para exclusão")
                return False
            
            # Verificar se existem registros de treino usando esta versão
            from models import RegistroTreino
            registros = RegistroTreino.query.filter_by(
                versao_id=versao_id,
                user_id=user_id
            ).first()
            
            if registros:
                logger.warning(f"Não é possível excluir versão {versao_id} pois existem registros vinculados")
                return False
            
            # Usar transação para garantir atomicidade
            db.session.begin_nested()
            
            # Excluir a versão (os relacionamentos serão excluídos em cascata)
            db.session.delete(versao)
            db.session.commit()
            
            logger.info(f"Versão {versao_id} excluída com sucesso")
            return True
            
        except Exception as e:
            db.session.rollback()
            BaseService.handle_error(e, f"Erro ao excluir versão {versao_id}")
            return False

    @staticmethod
    def finalizar(versao_id, data_fim, user_id=None):
        """Finaliza uma versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                logger.warning(f"Versão {versao_id} não encontrada")
                return False
            
            versao.data_fim = data_fim
            db.session.commit()
            logger.info(f"Versão {versao_id} finalizada")
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao finalizar versão {versao_id}")
            return False
    
    @staticmethod
    def get_treinos(versao_id, user_id=None):
        """Retorna treinos de uma versão (formato para template) com ordenação"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id, load_relations=True)
            if not versao:
                return {}
            
            resultado = {}
            for tv in versao.treinos:
                treino = TreinoService.get_by_id(tv.treino_id, user_id)
                if treino:
                    resultado[treino.codigo] = {
                        "id": tv.treino_id,
                        "codigo": treino.codigo,
                        "nome": tv.nome_treino,
                        "descricao": tv.descricao_treino,
                        "exercicios": [ve.exercicio_id for ve in tv.exercicios],
                        "ordem": tv.ordem if hasattr(tv, 'ordem') else 0
                    }
            
            # Ordenar por ordem
            resultado = dict(sorted(resultado.items(), key=lambda item: item[1].get('ordem', 0)))
            return resultado
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao buscar treinos da versão {versao_id}")
            return {}

    
    @staticmethod
    def get_exercicios(versao_id, treino_codigo=None, user_id=None):
        """Retorna exercícios de uma versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                return []
            
            query = db.session.query(Exercicio)\
                .join(VersaoExercicio, VersaoExercicio.exercicio_id == Exercicio.id)\
                .join(TreinoVersao, TreinoVersao.id == VersaoExercicio.treino_versao_id)\
                .filter(TreinoVersao.versao_id == versao_id)
            
            if treino_codigo:
                treino = TreinoService.get_by_codigo(treino_codigo, user_id)
                if treino:
                    query = query.filter(TreinoVersao.treino_id == treino.id)
            
            return query.order_by(TreinoVersao.treino_id, VersaoExercicio.ordem).all()
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao buscar exercícios da versão {versao_id}")
            return []
    
    @staticmethod
    def adicionar_treino(versao_id, treino_codigo, nome_treino, descricao_treino, 
                         exercicios_ids, user_id=None):
        """Adiciona treino a uma versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                logger.warning(f"Versão {versao_id} não encontrada")
                return False
            
            treino = TreinoService.get_by_codigo(treino_codigo, user_id)
            if not treino:
                logger.warning(f"Treino {treino_codigo} não encontrado")
                return False
            
            # Verificar se já existe
            if any(tv.treino_id == treino.id for tv in versao.treinos):
                logger.warning(f"Treino {treino_codigo} já existe na versão")
                return False
            
            treino_versao = TreinoVersao(
                versao_id=versao_id,
                treino_id=treino.id,
                nome_treino=nome_treino,
                descricao_treino=descricao_treino,
                ordem=len(versao.treinos)
            )
            db.session.add(treino_versao)
            db.session.flush()
            
            for ordem, ex_id in enumerate(exercicios_ids):
                ve = VersaoExercicio(
                    treino_versao_id=treino_versao.id,
                    exercicio_id=ex_id,
                    ordem=ordem
                )
                db.session.add(ve)
            
            db.session.commit()
            logger.info(f"Treino {treino_codigo} adicionado à versão {versao_id}")
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao adicionar treino à versão {versao_id}")
            return False
    
    @staticmethod
    def remover_treino(versao_id, treino_codigo, user_id=None):
        """Remove treino de uma versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                return False
            
            treino = TreinoService.get_by_codigo(treino_codigo, user_id)
            if not treino:
                return False
            
            # Encontrar o treino na versão
            treino_versao = None
            for tv in versao.treinos:
                if tv.treino_id == treino.id:
                    treino_versao = tv
                    break
            
            if not treino_versao:
                return False
            
            db.session.delete(treino_versao)
            db.session.commit()
            logger.info(f"Treino {treino_codigo} removido da versão {versao_id}")
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao remover treino da versão {versao_id}")
            return False
    
    @staticmethod
    def adicionar_exercicio(versao_id, treino_codigo, exercicio_id, user_id=None):
        """Adiciona exercício a um treino na versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                return False
            
            treino = TreinoService.get_by_codigo(treino_codigo, user_id)
            if not treino:
                return False
            
            # Encontrar o treino na versão
            treino_versao = None
            for tv in versao.treinos:
                if tv.treino_id == treino.id:
                    treino_versao = tv
                    break
            
            if not treino_versao:
                return False
            
            # Verificar se exercício já existe
            for ve in treino_versao.exercicios:
                if ve.exercicio_id == exercicio_id:
                    return True  # Já existe
            
            # Adicionar no final
            nova_ordem = len(treino_versao.exercicios)
            ve = VersaoExercicio(
                treino_versao_id=treino_versao.id,
                exercicio_id=exercicio_id,
                ordem=nova_ordem
            )
            db.session.add(ve)
            db.session.commit()
            
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao adicionar exercício à versão")
            return False
    
    @staticmethod
    def remover_exercicio(versao_id, treino_codigo, exercicio_id, user_id=None):
        """Remove exercício de um treino na versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                return False
            
            treino = TreinoService.get_by_codigo(treino_codigo, user_id)
            if not treino:
                return False
            
            # Encontrar o treino na versão
            treino_versao = None
            for tv in versao.treinos:
                if tv.treino_id == treino.id:
                    treino_versao = tv
                    break
            
            if not treino_versao:
                return False
            
            # Encontrar e remover o exercício
            for ve in treino_versao.exercicios:
                if ve.exercicio_id == exercicio_id:
                    db.session.delete(ve)
                    db.session.commit()
                    return True
            
            return False
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao remover exercício da versão")
            return False
    
    @staticmethod
    def reordenar_exercicios(versao_id, treino_codigo, nova_ordem, user_id=None):
        """Reordena exercícios de um treino na versão"""
        try:
            versao = VersaoService.get_by_id(versao_id, user_id)
            if not versao:
                return False
            
            treino = TreinoService.get_by_codigo(treino_codigo, user_id)
            if not treino:
                return False
            
            # Encontrar o treino na versão
            treino_versao = None
            for tv in versao.treinos:
                if tv.treino_id == treino.id:
                    treino_versao = tv
                    break
            
            if not treino_versao:
                return False
            
            # Atualizar ordem
            for ordem, ex_id in enumerate(nova_ordem):
                for ve in treino_versao.exercicios:
                    if ve.exercicio_id == ex_id:
                        ve.ordem = ordem
                        break
            
            db.session.commit()
            return True
        except Exception as e:
            BaseService.handle_error(e, f"Erro ao reordenar exercícios")
            return False