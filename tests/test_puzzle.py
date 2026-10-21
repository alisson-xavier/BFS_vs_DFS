import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from search_lib import BFS, DFS
from sliding_puzzle import MOVES, PuzzleState, SlidingPuzzle

class PuzzleTests(unittest.TestCase):
    def test_validation(self):
        # testa tabuleiros inválidos: peças repetidas, quantidade incompatível e tamanho não aceito
        for tiles, size in [((0,) * 9, 3), (tuple(range(9)), 4), (tuple(range(4)), 2)]:
            with self.assertRaises(ValueError):
                PuzzleState(tiles, size)

    def test_actions_are_legal_and_immutable(self):
        # confere se os movimentos partem da posição correta e não alteram o estado original
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            original = problem.goal.tiles
            self.assertEqual(len(problem.actions(problem.goal)), 2)
            self.assertIsNone(MOVES[1].apply(problem.goal))
            self.assertIsNone(MOVES[3].apply(problem.goal))
            for action in problem.actions(problem.goal):
                state, cost = action.apply(problem.goal)
                self.assertEqual(cost, 1)
                # um movimento troca apenas o espaço vazio e uma peça vizinha
                self.assertEqual(sum(a != b for a, b in zip(state.tiles, original)), 2)
                # deve existir um movimento de volta para a configuração inicial
                self.assertTrue(any(a.apply(state)[0] == problem.goal for a in problem.actions(state)))
            self.assertEqual(problem.goal.tiles, original)

    def test_random_walk_reproducibility_and_solvability(self):
        # verifica se a caminhada aleatória é reproduzível e sempre gera estados solucionáveis
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            self.assertEqual(problem.random_walk(0), problem.goal)
            for seed in range(10):
                state = problem.random_walk(30, seed)
                self.assertEqual(state, problem.random_walk(30, seed))
                self.assertTrue(problem.is_solvable(state))
            # trocar duas peças do objetivo deve criar um estado sem solução
            swapped = list(problem.goal.tiles)
            swapped[0], swapped[1] = swapped[1], swapped[0]
            self.assertFalse(problem.is_solvable(PuzzleState(tuple(swapped), size)))

    def test_bfs_known_minimum_and_path(self):
        # monta um estado a dois movimentos do objetivo e confere o menor caminho encontrado
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            initial, _ = MOVES[2].apply(problem.goal)
            initial, _ = MOVES[0].apply(initial)
            result = BFS(problem).search(initial)
            self.assertEqual(result.status, 'solved')
            self.assertEqual(result.solution_node.cost, 2)
            # aplica as ações da solução para confirmar que elas levam ao objetivo
            state = initial
            for action in result.solution_node.get_path():
                state, _ = action.apply(state)
            self.assertEqual(state, problem.goal)

    def test_dfs_valid_path(self):
        # verifica se a busca em profundidade também encontra um caminho válido até o objetivo
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            # leva o espaço vazio para o canto superior direito, de onde a busca segue até o objetivo
            state = problem.goal
            for _ in range(size - 1):
                state, _ = MOVES[0].apply(state)
            initial = state
            result = DFS(problem).search(initial)
            self.assertEqual(result.status, 'solved')
            for action in result.solution_node.get_path():
                state, _ = action.apply(state)
            self.assertEqual(state, problem.goal)

    def test_goal_and_resource_limits(self):
        # confere o caso em que o estado inicial já é o objetivo e os limites de busca
        problem = SlidingPuzzle()
        initial, _ = MOVES[0].apply(problem.goal)
        for algorithm in (BFS, DFS):
            goal = algorithm(problem, max_nodes=1).search(problem.goal)
            self.assertEqual(goal.solution_node.cost, 0)
            result = algorithm(problem, max_nodes=1).search(initial)
            self.assertEqual(result.status, 'node_limit')
            self.assertLessEqual(result.metrics.nodes_generated, 1)
            # simula o relógio para testar o limite de tempo sem esperar de verdade
            with patch('search_lib.algorithms.graph_search.time.perf_counter', side_effect=[0, 2, 2]):
                result = algorithm(problem, time_limit=1).search(initial)
            self.assertEqual(result.status, 'time_limit')

    def test_cycles_are_not_revisited(self):
        # cria um problema simples em que cada estado leva ao outro, formando um ciclo
        class Cycle:
            def is_goal(self, state):
                return False

            def actions(self, state):
                class Edge:
                    def apply(self, state):
                        return 1 - state, 1
                return [Edge()]

        # verifica se as buscas reconhecem que os estados já visitados não devem ser repetidos
        for algorithm in (BFS, DFS):
            result = algorithm(Cycle()).search(0)
            self.assertEqual(result.status, 'exhausted')
            self.assertEqual(result.metrics.nodes_generated, 2)
            self.assertEqual(result.metrics.nodes_expanded, 2)

    def test_benchmark_csv_pairs(self):
        # executa o benchmark e confere se os resultados são salvos nos arquivos esperados
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            output = Path(directory) / 'sample.csv'
            subprocess.run([sys.executable, '-B', 'main.py', 'benchmark', '--sizes', '3', '4',
                            '--depths', '0', '2', '--trials', '1', '--max-nodes', '100',
                            '--output', str(output)], check=True, capture_output=True)
            # lê as linhas geradas para comparar os estados iniciais de cada par de algoritmos
            with output.open(encoding='utf-8') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 8)
            for index in range(0, len(rows), 2):
                self.assertEqual(rows[index]['initial_state'], rows[index+1]['initial_state'])
            self.assertTrue(output.with_suffix('.md').exists())


if __name__ == '__main__':
    # permite executar os testes diretamente por este arquivo
    unittest.main()