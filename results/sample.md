# Comparação BFS × DFS

Médias de tempo/memória incluem buscas interrompidas; custo médio considera apenas soluções.
Compare o custo somente entre instâncias resolvidas por ambos; as taxas de sucesso podem diferir.

| Tamanho | Walk | Algoritmo | Resolvidas | Tempo médio (s) | Pico médio (MiB) | Custo médio |
|---|---|---|---|---|---|---|
| 3x3 | 5 | BFS | 2/2 | 0.000691 | 0.021 | 3.00 |
| 3x3 | 5 | DFS | 0/2 | 0.212250 | 4.091 | — |
| 3x3 | 10 | BFS | 2/2 | 0.000177 | 0.009 | 1.00 |
| 3x3 | 10 | DFS | 1/2 | 0.099975 | 2.046 | 0.00 |
| 3x3 | 20 | BFS | 2/2 | 0.000496 | 0.015 | 3.00 |
| 3x3 | 20 | DFS | 1/2 | 0.094424 | 2.048 | 2.00 |
| 4x4 | 5 | BFS | 2/2 | 0.001523 | 0.051 | 3.00 |
| 4x4 | 5 | DFS | 0/2 | 0.205845 | 4.645 | — |
| 4x4 | 10 | BFS | 2/2 | 0.004291 | 0.108 | 3.00 |
| 4x4 | 10 | DFS | 1/2 | 0.094429 | 2.322 | 0.00 |
| 4x4 | 20 | BFS | 1/2 | 0.089677 | 2.184 | 2.00 |
| 4x4 | 20 | DFS | 0/2 | 0.179162 | 4.646 | — |

BFS encontra caminhos mínimos com custo unitário quando conclui. DFS não garante custo mínimo.
A profundidade do Random Walk não é a distância ótima: retornos e ciclos são permitidos.
Limites atingidos não demonstram que o tabuleiro é insolúvel.
Memória: pico de alocações Python via tracemalloc, não o RSS total do processo.
