"""Adaptação local: busca em grafo com limites e métricas da Equipe A."""
from collections import deque
from dataclasses import dataclass
import math
import time

from search_lib.core import SearchMetrics, SearchNode, SearchResult, SearchStrategy


@dataclass
class GraphResult(SearchResult):
    status: str = "exhausted"


class GraphSearch(SearchStrategy):
    breadth_first = True

    def __init__(self, problem, max_nodes=100_000, time_limit=5.0):
        super().__init__(problem)
        if max_nodes < 1 or not math.isfinite(time_limit) or time_limit <= 0:
            raise ValueError("Os limites de nós e tempo devem ser positivos e finitos.")
        self.max_nodes = max_nodes
        self.time_limit = time_limit

    def search(self, initial_state):
        start = time.perf_counter()
        metrics = SearchMetrics(nodes_generated=1, max_frontier_size=1)
        frontier = deque([SearchNode(initial_state)])
        visited = {initial_state}

        def finish(node, status):
            metrics.execution_time = time.perf_counter() - start
            return GraphResult(node, metrics, status)

        while frontier:
            if time.perf_counter() - start >= self.time_limit:
                return finish(None, "time_limit")
            node = frontier.popleft() if self.breadth_first else frontier.pop()
            if self.problem.is_goal(node.state):
                return finish(node, "solved")
            metrics.nodes_expanded += 1
            actions = list(self.problem.actions(node.state))
            # A pilha visita os sucessores na mesma ordem usada pela fila.
            if not self.breadth_first:
                actions.reverse()
            for action in actions:
                if time.perf_counter() - start >= self.time_limit:
                    return finish(None, "time_limit")
                result = action.apply(node.state)
                if result is None:
                    continue
                state, cost = result
                if state in visited:
                    continue
                if metrics.nodes_generated >= self.max_nodes:
                    return finish(None, "node_limit")
                visited.add(state)
                frontier.append(SearchNode(state, node, action, node.cost + cost))
                metrics.nodes_generated += 1
                metrics.max_frontier_size = max(metrics.max_frontier_size, len(frontier))
        return finish(None, "exhausted")
