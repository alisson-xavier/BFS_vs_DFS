"""CLI para solucionar instâncias e comparar BFS/DFS."""
import argparse
import csv
import gc
import json
from pathlib import Path
import statistics
import tracemalloc

from search_lib import BFS, DFS
from sliding_puzzle import PuzzleState, SlidingPuzzle
benchmark --sizes 3 4 --depths 5 10 15 20 30 40 --trials 20 --seed 42 --max-nodes 30000 --time-limit 2 --output results/d1.csv
def run_search(problem, initial, algorithm, max_nodes, time_limit):
    # limpa objetos antigos e começa a medir o pico de memória desta busca
    gc.collect()
    tracemalloc.start()
    try:
        # seleciona o algoritmo pedido e executa a busca com os limites definidos
        result = {"BFS": BFS, "DFS": DFS}[algorithm](
            problem, max_nodes=max_nodes, time_limit=time_limit).search(initial)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        # encerra a medição mesmo se a busca gerar algum erro
        tracemalloc.stop()
    node = result.solution_node
    # reúne o resultado e as métricas em um formato fácil de exibir ou salvar
    row = {
        "algorithm": algorithm, "status": result.status,
        "nodes_generated": result.metrics.nodes_generated,
        "nodes_expanded": result.metrics.nodes_expanded,
        "max_frontier_size": result.metrics.max_frontier_size,
        "execution_time_s": result.metrics.execution_time,
        "peak_memory_mib": peak / (1024 ** 2),
        "cost": node.cost if node else None,
        "solution_length": node.depth if node else None,
    }
    return result, row

def positive(value):
    # valida argumentos que precisam ser inteiros maiores que zero
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Use um inteiro positivo.")
    return number

def nonnegative(value):
    # valida argumentos que aceitam zero, mas não valores negativos
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Use um inteiro não negativo.")
    return number

def positive_float(value):
    import math
    # exige um número finito maior que zero para o limite de tempo
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Use um número positivo e finito.")
    return number

def build_parser():
    # monta os comandos e as opções disponíveis na linha de comando
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    solve = commands.add_parser("solve", help="Resolve uma instância")
    solve.add_argument("--size", type=int, choices=[3, 4], default=3)
    solve.add_argument("--depth", type=nonnegative, default=10)
    solve.add_argument("--seed", type=int, default=42)
    solve.add_argument("--algorithm", choices=["BFS", "DFS"], default="BFS")
    solve.add_argument("--board", type=int, nargs="+", help="Peças em ordem de linhas; 0 = vazio")
    solve.add_argument("--show-path", action="store_true", help="Mostra todos os tabuleiros do caminho")
    bench = commands.add_parser("benchmark", help="Compara os algoritmos em instâncias idênticas")
    bench.add_argument("--sizes", type=int, choices=[3, 4], nargs="+", default=[3, 4])
    bench.add_argument("--depths", type=nonnegative, nargs="+", default=[5, 10, 20])
    bench.add_argument("--trials", type=positive, default=3)
    bench.add_argument("--seed", type=int, default=42)
    bench.add_argument("--output", type=Path, default=Path("results/benchmark.csv"))
    # aplica os mesmos limites de busca aos dois comandos
    for command in (solve, bench):
        command.add_argument("--max-nodes", type=positive, default=100_000)
        command.add_argument("--time-limit", type=positive_float, default=5.0)
    return parser

def solve(args, parser):
    # cria o problema e usa o tabuleiro informado ou gera um passeio aleatório
    problem = SlidingPuzzle(args.size)
    try:
        initial = (PuzzleState(tuple(args.board), args.size) if args.board is not None
                   else problem.random_walk(args.depth, args.seed))
    except ValueError as exc:
        # transforma erros de validação em uma mensagem de uso da CLI
        parser.error(str(exc))
    print(f"Estado inicial:\n{initial}\n")
    # evita gastar tempo de busca quando a paridade já indica que não há solução
    if not problem.is_solvable(initial):
        print("Estado insolúvel: paridade incompatível com o objetivo.")
        return 1
    result, row = run_search(problem, initial, args.algorithm, args.max_nodes, args.time_limit)
    print(json.dumps(row, ensure_ascii=False, indent=2))
    if result.solution_node is None:
        print("Busca encerrada sem solução encontrada; consulte status e limites.")
        return 1
    # recupera e exibe a sequência de movimentos encontrada
    actions = result.solution_node.get_path()
    print("Movimentos do vazio:", " -> ".join(a.name for a in actions) or "já resolvido")
    if args.show_path:
        # mostra cada configuração, começando pelo tabuleiro inicial
        state = initial
        print(f"\nPasso 0:\n{state}")
        for index, action in enumerate(actions, 1):
            state, _ = action.apply(state)
            print(f"\nPasso {index} ({action.name}):\n{state}")
    return 0

def write_summary(rows, output):
    # prepara o cabeçalho e explica como interpretar as médias do relatório
    lines = ["# Comparação BFS × DFS", "",
             "Médias de tempo/memória incluem buscas interrompidas; custo médio considera apenas soluções.",
             "Compare o custo somente entre instâncias resolvidas por ambos; as taxas de sucesso podem diferir.", "",
             "| Tamanho | Walk | Algoritmo | Resolvidas | Tempo médio (s) | Pico médio (MiB) | Custo médio |",
             "|---|---|---|---|---|---|---|"]
    # agrupa os resultados por tamanho, profundidade do passeio e algoritmo
    for size, depth, algorithm in sorted({(r['size'], r['walk_depth'], r['algorithm']) for r in rows}):
        group = [r for r in rows if (r['size'], r['walk_depth'], r['algorithm']) == (size, depth, algorithm)]
        solved = [r for r in group if r['status'] == 'solved']
        cost = f"{statistics.mean(r['cost'] for r in solved):.2f}" if solved else "—"
        lines.append(f"| {size}x{size} | {depth} | {algorithm} | {len(solved)}/{len(group)} | "
                     f"{statistics.mean(r['execution_time_s'] for r in group):.6f} | "
                     f"{statistics.mean(r['peak_memory_mib'] for r in group):.3f} | {cost} |")
    # registra observações sobre os algoritmos, o passeio aleatório e as métricas
    lines += ["", "BFS encontra caminhos mínimos com custo unitário quando conclui. DFS não garante custo mínimo.",
              "A profundidade do Random Walk não é a distância ótima: retornos e ciclos são permitidos.",
              "Limites atingidos não demonstram que o tabuleiro é insolúvel.",
              "Memória: pico de alocações Python via tracemalloc, não o RSS total do processo."]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

def benchmark(args):
    # prepara o arquivo CSV e executa as buscas nas instâncias de cada configuração
    rows = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = None
        for size in args.sizes:
            problem = SlidingPuzzle(size)
            for depth in args.depths:
                for trial in range(args.trials):
                    seed = args.seed + trial
                    # reutiliza o mesmo estado inicial para comparar os algoritmos
                    initial = problem.random_walk(depth, seed)
                    # alterna a ordem de execução para reduzir efeito da ordem no tempo
                    algorithms = ("BFS", "DFS") if trial % 2 == 0 else ("DFS", "BFS")
                    for algorithm in algorithms:
                        result, metrics = run_search(problem, initial, algorithm, args.max_nodes, args.time_limit)
                        row = dict(size=size, walk_depth=depth, trial=trial+1, seed=seed,
                                   initial_state=" ".join(map(str, initial.tiles)),
                                   max_nodes=args.max_nodes, time_limit_s=args.time_limit, **metrics)
                        # cria o cabeçalho a partir dos campos da primeira linha
                        if writer is None:
                            writer = csv.DictWriter(stream, fieldnames=list(row))
                            writer.writeheader()
                        writer.writerow(row)
                        # grava cada resultado imediatamente para preservar o progresso do benchmark
                        stream.flush()
                        rows.append(row)
                        print(f"{size}x{size} walk={depth} rodada={trial+1} {algorithm}: "
                              f"{row['status']} custo={row['cost']} tempo={row['execution_time_s']:.3f}s", flush=True)
                        del result
    # salva um resumo em Markdown ao lado do CSV
    summary = args.output.with_suffix(".md")
    write_summary(rows, summary)
    print(f"\nCSV: {args.output}\nResumo: {summary}")
    return 0

def main():
    # interpreta os argumentos e encaminha para o comando escolhido
    parser = build_parser()
    args = parser.parse_args()
    return solve(args, parser) if args.command == "solve" else benchmark(args)

if __name__ == "__main__":
    # permite executar a CLI diretamente e repassar o código de saída ao sistema
    raise SystemExit(main())