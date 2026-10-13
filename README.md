# IDA* vs RBFS: Sliding Puzzle Benchmark

Este repositório contém a implementação e a análise comparativa entre dois algoritmos de busca informada (**IDA\*** e **RBFS**) aplicados ao problema do **Sliding Puzzle** (Quebra-Cabeça de Deslizar). 

O projeto utiliza a biblioteca de busca fornecida pela **Equipe A** para conduzir os experimentos e avaliar o desempenho de ambos os algoritmos.

---

## Sobre o Projeto

O objetivo principal deste estudo é comparar o comportamento, a eficiência e o consumo de recursos computacionais dos algoritmos:
* **IDA\*** (Iterative Deepening A*)
* **RBFS** (Recursive Best-First Search)

### Problema Abordado
O problema escolhido é o **Sliding Puzzle** nos seguintes tamanhos:
* **3x3** (8-puzzle)
* **4x4** (15-puzzle)

Para garantir a imparcialidade e a aleatoriedade dos testes, os **estados iniciais** do puzzle são gerados através de um algoritmo de **Random Walk** (caminho aleatório) a partir do estado objetivo, garantindo que as instâncias sejam solucionáveis e apresentem diferentes níveis de dificuldade.

---

## Requisitos e Dependências

* **Linguagem:** Python
* **Biblioteca de Busca:** Biblioteca fornecida pela **Equipe A**
* **[Repositório base da equipe parceira](https://github.com/GustavoFelipeM/search_lib/tree/main/search_lib)**

---

## Execução

*Em construção*

---

## Metodologia de Testes e Comparações

Os testes são realizados variando os seguintes parâmetros:
* **Dimensão do Tabuleiro:** 3x3 e 4x4.
* **Profundidade do Random Walk:** Geração de estados iniciais variados.

Ao final da execução, os algoritmos são comparados com base em métricas como:
* Número de nós gerados e expandidos.
* Tempo de execução.
* Uso de memória.
* Custo do caminho encontrado.

---

## Autoria do projeto
Trabalho desenvolvido para fins acadêmicos/técnicos de avaliação de algoritmos de busca em Inteligência Artificial.
