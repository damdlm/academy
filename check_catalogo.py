import json
from pathlib import Path

BASE = Path("storage")
catalogo_path = BASE / "exercises-ptbr-full-translation.json"

print(f"Verificando arquivo: {catalogo_path}")
print(f"Arquivo existe: {catalogo_path.exists()}")

if catalogo_path.exists():
    print(f"Tamanho do arquivo: {catalogo_path.stat().st_size} bytes")
    
    try:
        with open(catalogo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            print(f"Primeiros 200 caracteres: {conteudo[:200]}")
            
            # Tenta carregar o JSON
            dados = json.loads(conteudo)
            print(f"JSON carregado com sucesso!")
            print(f"Tipo do dado: {type(dados)}")
            print(f"Quantidade de itens: {len(dados)}")
            
            if len(dados) > 0:
                print("\nPrimeiro exercício:")
                print(json.dumps(dados[0], indent=2, ensure_ascii=False))
                
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"Erro: {e}")
else:
    print("Arquivo não encontrado!")
    
    # Lista arquivos na pasta storage
    try:
        arquivos = list(BASE.glob("*"))
        print(f"\nArquivos em storage/:")
        for f in arquivos:
            print(f"  - {f.name}")
    except Exception as e:
        print(f"Erro ao listar: {e}")