from search_lib.algorithms.graph_search import GraphSearch


class DFS(GraphSearch):
    """Busca em profundidade com controle de estados repetidos."""
    breadth_first = False
