from datetime import datetime

def formatar_data(data_str):
    """
    Converte data do formato YYYY-MM-DD para DD/MM/AAAA
    Se a data for inválida ou None, retorna string vazia
    """
    if not data_str:
        return ""
    
    try:
        # Tenta converter do formato ISO (YYYY-MM-DD)
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        # Se não conseguir converter, retorna o original
        return data_str

def formatar_data_para_input(data_str):
    """
    Converte data do formato DD/MM/AAAA para YYYY-MM-DD para uso em inputs date
    """
    if not data_str:
        return ""
    
    try:
        # Tenta converter do formato brasileiro
        data = datetime.strptime(data_str, "%d/%m/%Y")
        return data.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        # Se não conseguir converter, retorna o original
        return data_str

def data_atual_formatada():
    """Retorna a data atual no formato DD/MM/AAAA"""
    return datetime.now().strftime("%d/%m/%Y")

def data_atual_iso():
    """Retorna a data atual no formato YYYY-MM-DD para inputs"""
    return datetime.now().strftime("%Y-%m-%d")