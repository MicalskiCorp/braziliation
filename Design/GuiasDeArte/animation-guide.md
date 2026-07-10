# Guia de Animação

## Princípios

- Animação deve priorizar legibilidade, não quantidade de frames.
- O primeiro frame precisa ser bom como sprite parado.
- Ataques, dano e interação precisam ter antecipação, impacto e recuperação claros.
- Em pixel art, 1 ou 2 pixels de deslocamento já podem ser muito.

## Contagens Recomendadas

| Animação | Frames | Observação |
|----------|--------|------------|
| Idle simples | 2 a 4 | Respiração, vapor ou oscilação pequena |
| Run | 6 a 8 | Priorizar leitura dos pés e centro de massa |
| Jump/Fall | 1 a 3 cada | Poses fortes importam mais que fluidez |
| Attack básico | 4 a 6 | Antecipação curta, frame de impacto claro |
| Hit | 1 a 3 | Flash, recuo ou pose quebrada |
| Death | 4 a 8 | Pode variar por inimigo |
| VFX pequeno | 3 a 6 | Fumaça, faísca, impacto |

## Export

- Use spritesheets por personagem/inimigo quando possível.
- Use tags do Aseprite para separar `idle`, `run`, `jump`, `attack`, `hit` e `death`.
- Exporte com nomes previsíveis: `chr_player_run_sheet.png`, `enm_automato_attack_sheet.png`.
- Mantenha pivot e tamanho de canvas estáveis entre animações do mesmo personagem.
