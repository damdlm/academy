import re
from datetime import datetime

# Mapeamento de meses para números
MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}

def converter_periodo_para_data(periodo_str):
    """
    Converte strings de período como "Janeiro/2024", "Março-26" ou "Fevereiro 2024"
    em uma data no formato YYYY-MM-DD (primeiro dia do mês)
    """
    if not periodo_str:
        return datetime.now().strftime("%Y-%m-%d")
    
    periodo_limpo = periodo_str.strip().lower()
    
    # Padrão 1: "Mês/Ano" ou "Mês-Ano" ou "Mês Ano"
    padrao1 = re.match(r'([a-zA-Zçãõáéíóú]+)[/\-\s]+(\d{2,4})', periodo_limpo)
    if padrao1:
        mes_nome = padrao1.group(1).lower()
        ano = padrao1.group(2)
        
        # Converter ano para 4 dígitos
        if len(ano) == 2:
            ano = f"20{ano}" if int(ano) <= 50 else f"19{ano}"
        
        # Obter número do mês
        mes_num = MESES.get(mes_nome)
        if mes_num:
            return f"{ano}-{mes_num:02d}-01"
    
    # Padrão 2: Apenas o mês (assume ano atual)
    padrao2 = re.match(r'([a-zA-Zçãõáéíóú]+)', periodo_limpo)
    if padrao2:
        mes_nome = padrao2.group(1).lower()
        mes_num = MESES.get(mes_nome)
        if mes_num:
            ano_atual = datetime.now().year
            return f"{ano_atual}-{mes_num:02d}-01"
    
    # Fallback
    print(f"Aviso: Não foi possível converter período '{periodo_str}'. Usando data atual.")
    return datetime.now().strftime("%Y-%m-%d")

def ordenar_periodos(periodos):
    """Ordena lista de períodos (ex: ['Janeiro/2024', 'Fevereiro/2024'])"""
    def chave_ordenacao(periodo):
        partes = periodo.split('/')
        if len(partes) != 2:
            return (9999, 0)
        
        mes_nome = partes[0].lower()
        ano = int(partes[1])
        mes_num = MESES.get(mes_nome, 0)
        return (ano, mes_num)
    
    return sorted(periodos, key=chave_ordenacao, reverse=True)