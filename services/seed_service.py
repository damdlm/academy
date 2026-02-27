"""
Serviço para popular dados iniciais para novos usuários
"""

from models import db, Treino, Exercicio, Musculo
from data.default_workouts import WORKOUTS_3X, WORKOUTS_4X, WORKOUTS_5X, MUSCLE_MAPPING
import logging

logger = logging.getLogger(__name__)

class SeedService:
    """Serviço para criar dados iniciais para novos usuários"""
    
    @staticmethod
    def get_or_create_musculo(nome_exibicao):
        """Retorna um músculo existente ou cria um novo"""
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
    
    @staticmethod
    def create_minimal_workouts(user_id):
        """
        Cria apenas os treinos básicos (A, B, C) sem exercícios
        para que o usuário possa configurar depois
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Dicionário com os treinos criados
        """
        try:
            logger.info(f"Criando treinos mínimos para usuário {user_id}")
            
            treinos_criados = {}
            
            # Definir treinos básicos
            treinos_base = {
                "A": {"nome": "Treino A", "descricao": "Peito/Ombro/Tríceps"},
                "B": {"nome": "Treino B", "descricao": "Costas/Bíceps"},
                "C": {"nome": "Treino C", "descricao": "Pernas"}
            }
            
            for codigo, dados in treinos_base.items():
                # Verificar se o treino já existe
                treino_existente = Treino.query.filter_by(
                    user_id=user_id, 
                    codigo=codigo
                ).first()
                
                if treino_existente:
                    logger.warning(f"Treino {codigo} já existe para usuário {user_id}")
                    treinos_criados[codigo] = treino_existente
                    continue
                
                # Criar o treino (SEM EXERCÍCIOS)
                treino = Treino(
                    codigo=codigo,
                    nome=dados["nome"],
                    descricao=dados["descricao"],
                    user_id=user_id
                )
                db.session.add(treino)
                db.session.flush()
                logger.info(f"Treino {codigo} criado: {dados['nome']}")
                
                treinos_criados[codigo] = treino
            
            db.session.commit()
            logger.info(f"Total de {len(treinos_criados)} treinos mínimos criados para usuário {user_id}")
            return treinos_criados
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar treinos mínimos: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def create_default_workouts(user_id, frequency="3x"):
        """
        Cria treinos completos com exercícios para um usuário
        
        Args:
            user_id: ID do usuário
            frequency: Frequência desejada ("3x", "4x" ou "5x")
        
        Returns:
            dict: Dicionário com os treinos criados
        """
        try:
            logger.info(f"Criando treinos completos para usuário {user_id} - Frequência {frequency}")
            
            # Selecionar o conjunto de treinos baseado na frequência
            if frequency == "4x":
                workouts = WORKOUTS_4X
            elif frequency == "5x":
                workouts = WORKOUTS_5X
            else:  # default 3x
                workouts = WORKOUTS_3X
            
            treinos_criados = {}
            
            for codigo, workout_data in workouts.items():
                # Verificar se o treino já existe
                treino_existente = Treino.query.filter_by(
                    user_id=user_id, 
                    codigo=codigo
                ).first()
                
                if treino_existente:
                    logger.warning(f"Treino {codigo} já existe para usuário {user_id}")
                    treinos_criados[codigo] = treino_existente
                    continue
                
                # Criar o treino
                treino = Treino(
                    codigo=codigo,
                    nome=workout_data["nome"],
                    descricao=workout_data["descricao"],
                    user_id=user_id
                )
                db.session.add(treino)
                db.session.flush()
                logger.info(f"Treino {codigo} criado: {workout_data['nome']}")
                
                # Criar exercícios para este treino
                exercicios_criados = []
                for ex_data in workout_data["exercicios"]:
                    # Garantir que o músculo existe
                    musculo_nome = MUSCLE_MAPPING.get(ex_data["musculo"], ex_data["musculo"])
                    musculo = SeedService.get_or_create_musculo(musculo_nome)
                    
                    # Verificar se exercício já existe (pelo nome e usuário)
                    exercicio_existente = Exercicio.query.filter_by(
                        user_id=user_id,
                        nome=ex_data["nome"]
                    ).first()
                    
                    if exercicio_existente:
                        logger.debug(f"Exercício já existe: {ex_data['nome']}")
                        exercicios_criados.append(exercicio_existente)
                        continue
                    
                    # Criar exercício
                    exercicio = Exercicio(
                        nome=ex_data["nome"],
                        descricao=f"Exercício para {workout_data['nome']}",
                        musculo_id=musculo.id,
                        treino_id=treino.id,
                        user_id=user_id
                    )
                    db.session.add(exercicio)
                    db.session.flush()
                    exercicios_criados.append(exercicio)
                    logger.debug(f"Exercício criado: {ex_data['nome']}")
                
                treinos_criados[codigo] = treino
            
            db.session.commit()
            logger.info(f"Total de {len(treinos_criados)} treinos completos criados para usuário {user_id}")
            return treinos_criados
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar treinos completos: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def create_all_frequencies(user_id):
        """
        Cria todas as frequências de treino para um usuário (útil para testes)
        """
        result = {}
        result["3x"] = SeedService.create_default_workouts(user_id, "3x")
        result["4x"] = SeedService.create_default_workouts(user_id, "4x")
        result["5x"] = SeedService.create_default_workouts(user_id, "5x")
        return result