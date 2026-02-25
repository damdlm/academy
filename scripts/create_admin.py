#!/usr/bin/env python3
"""
Script para criar usuário admin manualmente
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db, User

def create_admin(username, email, password):
    """Cria um novo usuário admin"""
    app = create_app()
    
    with app.app_context():
        # Verificar se já existe
        if User.query.filter_by(username=username).first():
            print(f"❌ Usuário {username} já existe!")
            return False
        
        user = User(
            username=username,
            email=email,
            is_admin=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Usuário admin {username} criado com sucesso!")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    create_admin(sys.argv[1], sys.argv[2], sys.argv[3])