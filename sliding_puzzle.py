"""Sliding Puzzle 3x3/4x4 compatível com a biblioteca da Equipe A."""
from dataclasses import dataclass
import random
from search_lib import Action, Problem, State

@dataclass(frozen=True)
class PuzzleState(State):
    tiles: tuple[int, ...]
    size: int

    def __post_init__(self):
        # confere se o tabuleiro tem um tamanho aceito antes de validar as peças
        if self.size not in (3, 4):
            raise ValueError("O tamanho deve ser 3 ou 4.")
        # a tupla impede que o estado seja alterado depois de criado
        if not isinstance(self.tiles, tuple):
            raise ValueError("As peças devem ser fornecidas como tupla.")
        # garante que cada número apareça uma única vez, incluindo o espaço vazio (0)
        if (any(type(tile) is not int for tile in self.tiles)
                or sorted(self.tiles) != list(range(self.size ** 2))):
            raise ValueError("Use cada peça de 0 a size²-1 exatamente uma vez.")

    def __str__(self):
        # organiza as peças em linhas para facilitar a leitura do tabuleiro
        return "\n".join(
            " ".join(f"{tile:2}" if tile else " _" for tile in self.tiles[i:i+self.size])
            for i in range(0, len(self.tiles), self.size)
        )

@dataclass(frozen=True)
class Move(Action):
    name: str
    dr: int
    dc: int

    def apply(self, state):
        # encontra o espaço vazio e converte sua posição em linha e coluna
        blank = state.tiles.index(0)
        row, col = divmod(blank, state.size)
        # calcula onde o espaço vazio ficaria depois deste movimento
        row, col = row + self.dr, col + self.dc
        # se a nova posição sair do tabuleiro, o movimento não pode ser aplicado
        if not (0 <= row < state.size and 0 <= col < state.size):
            return None
        target = row * state.size + col
        # troca o espaço vazio com a peça vizinha e cria um novo estado
        tiles = list(state.tiles)
        tiles[blank], tiles[target] = tiles[target], tiles[blank]
        return PuzzleState(tuple(tiles), state.size), 1.0

# cada movimento indica o deslocamento do espaço vazio em linhas e colunas
MOVES = (Move("cima", -1, 0), Move("baixo", 1, 0),
         Move("esquerda", 0, -1), Move("direita", 0, 1))

class SlidingPuzzle(Problem):
    def __init__(self, size=3):
        # define o objetivo com as peças em ordem e o espaço vazio no final
        self.goal = PuzzleState(tuple(range(1, size * size)) + (0,), size)

    def actions(self, state):
        # libera somente movimentos que mantêm o espaço vazio dentro do tabuleiro
        row, col = divmod(state.tiles.index(0), state.size)
        return [move for move in MOVES
                if 0 <= row + move.dr < state.size and 0 <= col + move.dc < state.size]

    def is_goal(self, state):
        # compara o estado atual com a configuração final definida para o quebra-cabeça
        return state == self.goal

    def random_walk(self, steps, seed=42):
        """Executa exatamente steps movimentos legais, incluindo possíveis retornos."""
        if steps < 0:
            raise ValueError("A profundidade do Random Walk deve ser não negativa.")
        # usa uma semente para que o mesmo passeio aleatório possa ser reproduzido
        rng = random.Random(seed)
        state = self.goal
        # parte do objetivo e aplica um movimento legal a cada etapa
        for _ in range(steps):
            state, _ = rng.choice(self.actions(state)).apply(state)
        return state

    def is_solvable(self, state):
        # estados de outro tamanho não pertencem a este problema
        if state.size != self.goal.size:
            return False
        # conta as inversões, isto é, pares de peças fora da ordem esperada
        values = [tile for tile in state.tiles if tile]
        inversions = sum(a > b for i, a in enumerate(values) for b in values[i+1:])
        # em tabuleiros ímpares, a solução depende da paridade das inversões
        if state.size % 2:
            return inversions % 2 == 0
        # em tabuleiros pares, também importa a linha do espaço vazio, contada de baixo
        row_from_bottom = state.size - state.tiles.index(0) // state.size
        return (inversions + row_from_bottom) % 2 == 1