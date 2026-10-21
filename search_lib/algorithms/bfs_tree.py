from search_lib.algorithms.graph_search import GraphSearch


class BFS(GraphSearch):
    """Busca em largura com controle de estados repetidos."""
    breadth_first = True
