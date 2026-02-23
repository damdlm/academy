"""
Pacote de utilitários da aplicação FitLog
"""

from .file_utils import load_json, save_json, clear_cache, get_periodos_existentes
from .date_utils import converter_periodo_para_data, MESES
from .exercise_utils import (
    buscar_musculo_no_catalogo, get_series_from_registro,
    calcular_media_series, calcular_volume_total, remover_acentos
)
from .stats_utils import calcular_estatisticas_musculo, calcular_estatisticas_treino
from .version_utils import (
    # Versões
    get_versoes_globais, get_versao_ativa,
    get_treinos_da_versao, get_exercicios_do_treino, get_todos_exercicios_da_versao,
    # Gerenciamento de treinos dentro das versões
    adicionar_treino_na_versao, editar_treino_na_versao, remover_treino_da_versao,
    # Gerenciamento de exercícios dentro dos treinos
    adicionar_exercicio_ao_treino, remover_exercicio_do_treino, reordenar_exercicios_do_treino,
    # Verificação de versão ativa
    verificar_versao_ativa,
    # Verificação de onde um exercício é usado
    verificar_exercicio_em_versoes,
    # Migração
    migrar_versoes_para_novo_formato,
    # Compatibilidade (mantidas para não quebrar)
    get_versoes_treino_antigo, get_versao_ativa_antiga, get_exercicios_por_versao_antiga,
    get_versoes_treino, get_exercicios_por_versao,
    get_ultimas_series
)
from .format_utils import (
    formatar_data, formatar_data_para_input, data_atual_formatada, data_atual_iso
)

__all__ = [
    'load_json', 'save_json', 'clear_cache', 'get_periodos_existentes',
    'converter_periodo_para_data', 'MESES',
    'buscar_musculo_no_catalogo', 'get_series_from_registro',
    'calcular_media_series', 'calcular_volume_total', 'remover_acentos',
    'calcular_estatisticas_musculo', 'calcular_estatisticas_treino',
    'get_versoes_globais', 'get_versao_ativa',
    'get_treinos_da_versao', 'get_exercicios_do_treino', 'get_todos_exercicios_da_versao',
    'adicionar_treino_na_versao', 'editar_treino_na_versao', 'remover_treino_da_versao',
    'adicionar_exercicio_ao_treino', 'remover_exercicio_do_treino', 'reordenar_exercicios_do_treino',
    'verificar_versao_ativa',
    'verificar_exercicio_em_versoes',
    'migrar_versoes_para_novo_formato',
    'get_versoes_treino_antigo', 'get_versao_ativa_antiga', 'get_exercicios_por_versao_antiga',
    'get_versoes_treino', 'get_exercicios_por_versao',
    'get_ultimas_series',
    'formatar_data', 'formatar_data_para_input', 'data_atual_formatada', 'data_atual_iso'
]