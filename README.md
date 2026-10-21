# BFS vs DFS: Sliding Puzzle Benchmark

Este repositório contém a implementação e a análise comparativa entre dois algoritmos de busca não informada (**BFS** e **DFS**) aplicados ao problema do **Sliding Puzzle** (Quebra-Cabeça de Deslizar).

O projeto utiliza a biblioteca de busca fornecida pela **Equipe A** para conduzir os experimentos e avaliar o desempenho de ambos os algoritmos.

---

## Sobre o Projeto

O objetivo principal deste estudo é comparar o comportamento, a eficiência e o consumo de recursos computacionais dos algoritmos:
* **BFS** (Breadth-First Search / Busca em Largura)
* **DFS** (Depth-First Search / Busca em Profundidade)

### Problema Abordado
O problema escolhido é o **Sliding Puzzle** nos seguintes tamanhos:
* **3x3** (8-puzzle)
* **4x4** (15-puzzle)

Para garantir a imparcialidade e a aleatoriedade dos testes, os **estados iniciais** do puzzle serão gerados através de um algoritmo de **Random Walk** (caminho aleatório) a partir do estado objetivo, garantindo que as instâncias sejam solucionáveis e apresentem diferentes níveis de dificuldade.

---

## Requisitos e Dependências

* **Linguagem:** Python 3.10 ou superior; execução das buscas apenas com biblioteca padrão. Para gerar gráficos, instale `requirements-plots.txt`.
* **Biblioteca de Busca:** Biblioteca fornecida pela **Equipe A**
* **[Repositório base da equipe parceira](https://github.com/GustavoFelipeM/search_lib/tree/main/search_lib)**

---

## Execução

Execute os comandos na raiz do projeto.

Resolver um 8-puzzle gerado por Random Walk e mostrar o caminho completo:

```bash
python main.py solve --size 3 --depth 10 --seed 42 --algorithm BFS --show-path
```

Resolver um 15-puzzle com DFS (zero representa o espaço vazio):

```bash
python main.py solve --size 4 --algorithm DFS --board 1 2 3 0 5 6 7 4 9 10 11 8 13 14 15 12 --show-path
```

Comparar os dois algoritmos variando tamanho e profundidade do Random Walk:

```bash
python main.py benchmark --sizes 3 4 --depths 5 10 20 --trials 3 --seed 42 --max-nodes 100000 --time-limit 5 --output results/benchmark.csv
```

Cada execução exporta um CSV com resultados individuais e um resumo Markdown com o mesmo nome. Os limites valem por algoritmo e por instância. O comando `solve` retorna código 1 quando não encontra uma solução ou recebe um estado insolúvel; argumentos inválidos retornam código 2.

Executar os testes:

```bash
python -B -m unittest discover -s tests -v
```

Arquivos principais: `sliding_puzzle.py` representa estados e movimentos; `main.py` oferece solução e benchmark; `search_lib/` contém a biblioteca adaptada da Equipe A; `tests/` contém as validações automatizadas.

---

## Metodologia de Testes e Comparações

### Entrega D.1

Pergunta: **Como BFS e DFS, com controle de estados repetidos, diferem em tempo, nós gerados e tamanho máximo da fronteira ao resolver Sliding Puzzles 3×3 e 4×4?**

O relatório completo está em [RELATORIO_D1.md](RELATORIO_D1.md), com figuras em `results/figures/`, dados individuais em `results/d1.csv` e ambiente/protocolo em `results/d1_metadata.json`.

Reproduzir o protocolo da entrega (480 buscas; pode levar vários minutos):

```bash
python main.py benchmark --sizes 3 4 --depths 5 10 15 20 30 40 --trials 20 --seed 42 --max-nodes 30000 --time-limit 2 --output results/d1.csv
python -m pip install -r requirements-plots.txt
python plot_results.py results/d1.csv --output results/figures
```

O primeiro comando regenera os dados e o resumo automático; o segundo instala somente as dependências dos gráficos; o terceiro regenera figuras e estatísticas. O relatório interpretativo e os metadados documentam a execução entregue e devem ser revisados se os experimentos forem repetidos.

Os testes são realizados variando os seguintes parâmetros:
* **Dimensão do Tabuleiro:** 3x3 e 4x4.
* **Profundidade do Random Walk:** Geração de estados iniciais variados.

Ao final da execução, os algoritmos são comparados com base em métricas como:
* Número de nós gerados e expandidos.
* Tempo de execução.
* Uso de memória.
* Custo do caminho encontrado.

### Protocolo e interpretação

O objetivo é a sequência de 1 a 8 ou 15, com o vazio no canto inferior direito. Cada movimento desloca o vazio por uma casa ortogonal e custa 1. A ordem dos sucessores é cima, baixo, esquerda, direita; a inserção na pilha do DFS é invertida para respeitar essa ordem de visita.

O Random Walk parte do objetivo e executa exatamente a quantidade de movimentos solicitada, escolhendo uniformemente entre os movimentos legais. Retornos imediatos e ciclos são permitidos: sua profundidade **não corresponde necessariamente à distância mínima da solução**, nem garante dificuldade crescente. Sementes fixas tornam os estados reproduzíveis. Na rodada `i` (iniciando em zero), a semente é `seed + i`; BFS e DFS recebem o mesmo estado. A ordem dos algoritmos alterna entre rodadas. Estados repetidos ou já resolvidos são mantidos e registrados no CSV.

A biblioteca original usava busca em árvore. A adaptação local mantém as interfaces e classes da Equipe A, acrescentando um conjunto de estados descobertos para impedir ciclos e limites de recursos. Os arquivos `bfs_tree.py` e `dfs_tree.py` preservam os caminhos de importação, mas agora executam **busca em grafo**. A origem e as alterações estão registradas em `SEARCH_LIB_SOURCE.txt`.

Definições das métricas:

* `nodes_generated`: estados distintos admitidos na fronteira, incluindo a raiz; sucessores repetidos não contam.
* `nodes_expanded`: nós cujos sucessores começaram a ser examinados; o objetivo não é expandido. Uma interrupção pode ocorrer durante a última expansão.
* `max_frontier_size`: maior número de nós aguardando exploração.
* `execution_time_s`: tempo de busca via `perf_counter`, com a instrumentação de memória ativa; exclui geração da instância, impressão e exportação.
* `peak_memory_mib`: pico das alocações Python durante cada busca, medido por `tracemalloc`; não é a memória total do processo. A instrumentação adiciona custo de execução a ambos os algoritmos.
* `cost` e `solution_length`: custo e número de movimentos; ficam vazios quando não há solução encontrada.
* `status`: `solved`, `node_limit`, `time_limit` ou `exhausted`. Atingir um limite não significa que a instância é insolúvel.

O limite de nós restringe estados admitidos, com interrupção ao tentar admitir o próximo estado; não é um limite em bytes. O limite de tempo é verificado entre expansões e sucessores. BFS garante caminho mínimo para estes custos unitários quando encontra a solução. DFS pode produzir caminhos muito maiores. O espaço de estados do 15-puzzle é muito grande: os limites evitam buscas sem controle, mas instâncias difíceis podem terminar sem solução encontrada.

O resumo inclui médias de tempo e memória de todas as execuções e custo médio apenas das resolvidas. Taxas de sucesso diferentes podem enviesar a comparação de custos; use o CSV para comparar pares resolvidos por ambos. Os resultados de exemplo em `results/sample.csv` e `results/sample.md` são uma amostra limitada, não uma conclusão geral sobre desempenho.

---

## Autoria do projeto
Trabalho desenvolvido para fins acadêmicos/técnicos de avaliação de algoritmos de busca em Inteligência Artificial.
