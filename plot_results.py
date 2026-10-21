"""Gera figuras e estatísticas do CSV sem executar novamente as buscas."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    # lê os caminhos de entrada e saída informados pela linha de comando
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--output', type=Path, default=Path('results/figures'))
    args = parser.parse_args()

    # carrega os resultados já registrados no CSV
    with args.csv.open(encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        parser.error('CSV sem resultados.')

    # identifica os tamanhos de tabuleiro e as profundidades disponíveis
    sizes = sorted({int(r['size']) for r in rows})
    depths = sorted({int(r['walk_depth']) for r in rows})
    args.output.mkdir(parents=True, exist_ok=True)

    # associa cada coluna do CSV ao título e ao nome do arquivo da figura
    metrics = [('execution_time_s', 'Tempo de busca (s)', 'tempo'),
               ('nodes_generated', 'Nós gerados', 'nos_gerados'),
               ('max_frontier_size', 'Tamanho máximo da fronteira', 'fronteira'),
               ('success', 'Buscas resolvidas (%)', 'sucesso')]

    # aplica um estilo visual comum a todos os gráficos
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    for metric, label, filename in metrics:
        # cria um painel por tamanho de tabuleiro
        fig, axes = plt.subplots(1, len(sizes), figsize=(11, 4.3), squeeze=False)
        for ax, size in zip(axes[0], sizes):
            # compara BFS e DFS com cores e marcadores distintos
            for algorithm, color, marker in [('BFS', '#0072B2', 'o'), ('DFS', '#D55E00', 's')]:
                averages, lows, highs = [], [], []
                for depth in depths:
                    # reúne as execuções que pertencem a esta configuração
                    group = [r for r in rows if int(r['size']) == size
                             and int(r['walk_depth']) == depth and r['algorithm'] == algorithm]
                    # converte os estados em valores numéricos e calcula a taxa de sucesso
                    values = [100 * (r['status'] == 'solved') if metric == 'success'
                              else float(r[metric]) for r in group]
                    if not values:
                        raise ValueError(f'Configuração ausente: {size}, {depth}, {algorithm}')
                    averages.append(statistics.mean(values))
                    # usa os quartis para mostrar a variação entre execuções
                    q = statistics.quantiles(values, n=4, method='inclusive') if len(values) > 1 else values * 3
                    lows.append(q[0])
                    highs.append(q[2])
                ax.plot(depths, averages, marker=marker, color=color, label=algorithm, linewidth=2)
                # exibe a faixa entre os percentis 25 e 75 nas métricas numéricas
                if metric != 'success':
                    ax.fill_between(depths, lows, highs, color=color, alpha=0.13)

            # ajusta títulos, eixos e legenda de cada painel
            ax.set_title(f'Sliding Puzzle {size}×{size}')
            ax.set_xlabel('Comprimento do Random Walk')
            ax.set_ylabel(label)
            ax.set_xticks(depths)
            ax.grid(alpha=0.22)
            ax.legend()
            if metric != 'success':
                ax.set_yscale('log')
            else:
                ax.set_ylim(-3, 103)

        # acrescenta uma legenda explicativa e salva cada gráfico em dois formatos
        caption = ('Média de todas as execuções; faixa: percentis 25–75. Eixo y logarítmico.'
                   if metric != 'success' else 'Percentual de soluções encontradas dentro dos limites comuns de recursos.')
        fig.suptitle(label, fontweight='bold')
        fig.text(0.5, 0.015, caption, ha='center', fontsize=10)
        fig.tight_layout(rect=(0, 0.055, 1, 0.95))
        fig.savefig(args.output / f'{filename}.png', dpi=160)
        fig.savefig(args.output / f'{filename}.svg')
        plt.close(fig)

    # resume quantidade, status e médias por tamanho de tabuleiro e algoritmo
    summary = {}
    for size in sizes:
        for algorithm in ('BFS', 'DFS'):
            group = [r for r in rows if int(r['size']) == size and r['algorithm'] == algorithm]
            summary[f'{size}x{size}_{algorithm}'] = {
                'runs': len(group), 'status': dict(Counter(r['status'] for r in group)),
                **{m: statistics.mean(float(r[m]) for r in group) for m, _, _ in metrics if m != 'success'},
                'peak_memory_mib': statistics.mean(float(r['peak_memory_mib']) for r in group)}
    # salva as estatísticas ao lado da pasta de figuras e também as mostra na tela
    (args.output.parent / 'statistics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    # executa o programa quando este arquivo é chamado diretamente
    main()