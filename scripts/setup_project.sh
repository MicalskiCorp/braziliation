#!/usr/bin/env bash
set -e
REPO_NAME="Braziliation"
echo "Criando estrutura local para $REPO_NAME"
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"

mkdir -p Assets/Art Assets/Audio Assets/Sprites Assets/UI Assets/Tilemaps
mkdir -p Docs/Design Docs/ArtStyle Docs/Tech Docs/Roadmap
mkdir -p Scripts/Player Scripts/Enemies Scripts/Managers Scripts/UI
mkdir -p Tests/Unit

cat > README.md <<'EOF'
# Braziliation
Jogo plataforma 2D em pixel art (C#) — ambientação dieselpunk pós-apocalíptica brasileira.
EOF

cat > LICENSE <<'EOF'
MIT License
Copyright (c) 2025 Braziliation
EOF

curl -s https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore -o .gitignore || touch .gitignore

git init
git lfs install || true
git add .
git commit -m "Initial project skeleton for Braziliation"
echo "Estrutura criada. Agora adicione o remote e faça push para o repositório remoto."
