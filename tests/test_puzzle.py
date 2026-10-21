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
        for tiles, size in [((0,) * 9, 3), (tuple(range(9)), 4), (tuple(range(4)), 2)]:
            with self.assertRaises(ValueError):
                PuzzleState(tiles, size)

    def test_actions_are_legal_and_immutable(self):
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            original = problem.goal.tiles
            self.assertEqual(len(problem.actions(problem.goal)), 2)
            self.assertIsNone(MOVES[1].apply(problem.goal))
            self.assertIsNone(MOVES[3].apply(problem.goal))
            for action in problem.actions(problem.goal):
                state, cost = action.apply(problem.goal)
                self.assertEqual(cost, 1)
                self.assertEqual(sum(a != b for a, b in zip(state.tiles, original)), 2)
                self.assertTrue(any(a.apply(state)[0] == problem.goal for a in problem.actions(state)))
            self.assertEqual(problem.goal.tiles, original)

    def test_random_walk_reproducibility_and_solvability(self):
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            self.assertEqual(problem.random_walk(0), problem.goal)
            for seed in range(10):
                state = problem.random_walk(30, seed)
                self.assertEqual(state, problem.random_walk(30, seed))
                self.assertTrue(problem.is_solvable(state))
            swapped = list(problem.goal.tiles)
            swapped[0], swapped[1] = swapped[1], swapped[0]
            self.assertFalse(problem.is_solvable(PuzzleState(tuple(swapped), size)))

    def test_bfs_known_minimum_and_path(self):
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            initial, _ = MOVES[2].apply(problem.goal)
            initial, _ = MOVES[0].apply(initial)
            result = BFS(problem).search(initial)
            self.assertEqual(result.status, 'solved')
            self.assertEqual(result.solution_node.cost, 2)
            state = initial
            for action in result.solution_node.get_path():
                state, _ = action.apply(state)
            self.assertEqual(state, problem.goal)

    def test_dfs_valid_path(self):
        for size in (3, 4):
            problem = SlidingPuzzle(size)
            # Vazio no canto superior direito: DFS segue baixo até o objetivo.
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
        problem = SlidingPuzzle()
        initial, _ = MOVES[0].apply(problem.goal)
        for algorithm in (BFS, DFS):
            goal = algorithm(problem, max_nodes=1).search(problem.goal)
            self.assertEqual(goal.solution_node.cost, 0)
            result = algorithm(problem, max_nodes=1).search(initial)
            self.assertEqual(result.status, 'node_limit')
            self.assertLessEqual(result.metrics.nodes_generated, 1)
            with patch('search_lib.algorithms.graph_search.time.perf_counter', side_effect=[0, 2, 2]):
                result = algorithm(problem, time_limit=1).search(initial)
            self.assertEqual(result.status, 'time_limit')

    def test_cycles_are_not_revisited(self):
        class Cycle:
            def is_goal(self, state):
                return False

            def actions(self, state):
                class Edge:
                    def apply(self, state):
                        return 1 - state, 1
                return [Edge()]
        for algorithm in (BFS, DFS):
            result = algorithm(Cycle()).search(0)
            self.assertEqual(result.status, 'exhausted')
            self.assertEqual(result.metrics.nodes_generated, 2)
            self.assertEqual(result.metrics.nodes_expanded, 2)

    def test_benchmark_csv_pairs(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            output = Path(directory) / 'sample.csv'
            subprocess.run([sys.executable, '-B', 'main.py', 'benchmark', '--sizes', '3', '4',
                            '--depths', '0', '2', '--trials', '1', '--max-nodes', '100',
                            '--output', str(output)], check=True, capture_output=True)
            with output.open(encoding='utf-8') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 8)
            for index in range(0, len(rows), 2):
                self.assertEqual(rows[index]['initial_state'], rows[index+1]['initial_state'])
            self.assertTrue(output.with_suffix('.md').exists())


if __name__ == '__main__':
    unittest.main()
