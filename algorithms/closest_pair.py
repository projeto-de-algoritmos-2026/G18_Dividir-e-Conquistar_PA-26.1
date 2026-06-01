"""
Implementação do algoritmo Par de Pontos Mais Próximos via Dividir e Conquistar.

Estratégia:
- Divide o conjunto de pontos ao meio por coordenada X (pré-ordenados).
- Resolve recursivamente cada metade.
- Combina os resultados verificando a faixa central (strip) com largura 2*delta.
- Complexidade esperada: O(n log n).

Contexto GPS:
- Cada ponto representa um carro ou entregador no mapa.
- O algoritmo encontra o par de carros mais próximos, ou pode ser adaptado
  para encontrar o carro mais próximo de um passageiro fixo.
"""
