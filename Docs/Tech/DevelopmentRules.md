# Regras de Desenvolvimento – Braziliation

- Branches:
  - `main`: produção estável
  - `develop`: integração
  - `feature/*`: novas features
  - `hotfix/*`: correções emergenciais
  - `chore/*`: manutenção técnica

- Commits:
  tipo(scope): descrição breve
  Ex: feature(player): adicionar salto duplo

- Merge apenas via Pull Request.
- CI deve estar verde antes do merge.
- Tag releases com semantic versioning: v0.1.0, v0.1.1, ...
