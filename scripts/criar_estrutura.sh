#!/bin/bash

echo "🚀 Criando estrutura de diretórios do FitLog..."

# Diretórios principais
mkdir -p logs
mkdir -p static/css
mkdir -p static/js/modules
mkdir -p static/js/vendor
mkdir -p static/images
mkdir -p static/fonts

# Templates
mkdir -p templates/auth
mkdir -p templates/admin/partials
mkdir -p templates/register
mkdir -p templates/stats
mkdir -p templates/version/partials

# Código fonte
mkdir -p routes
mkdir -p services
mkdir -p repositories
mkdir -p utils
mkdir -p middleware
mkdir -p schemas

# Testes
mkdir -p tests/unit/test_services
mkdir -p tests/unit/test_utils
mkdir -p tests/integration/test_routes
mkdir -p tests/integration/test_api
mkdir -p tests/fixtures

# Documentação
mkdir -p docs
mkdir -p scripts
mkdir -p migrations/versions

# Criar arquivos __init__.py
touch routes/__init__.py
touch services/__init__.py
touch repositories/__init__.py
touch utils/__init__.py
touch middleware/__init__.py
touch schemas/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/test_services/__init__.py
touch tests/unit/test_utils/__init__.py
touch tests/integration/__init__.py
touch tests/integration/test_routes/__init__.py
touch tests/integration/test_api/__init__.py

# Arquivos principais
touch app.py
touch config.py
touch models.py
touch requirements.txt
touch .env
touch .gitignore

echo "✅ Estrutura criada com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Copiar o conteúdo dos arquivos fornecidos"
echo "2. Instalar dependências: pip install -r requirements.txt"
echo "3. Configurar banco de dados no arquivo .env"
echo "4. Executar: python app.py"