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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--output', type=Path, default=Path('results/figures'))
    args = parser.parse_args()
    with args.csv.open(encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        parser.error('CSV sem resultados.')
    sizes = sorted({int(r['size']) for r in rows})
    depths = sorted({int(r['walk_depth']) for r in rows})
    args.output.mkdir(parents=True, exist_ok=True)
    metrics = [('execution_time_s', 'Tempo de busca (s)', 'tempo'),
               ('nodes_generated', 'Nós gerados', 'nos_gerados'),
               ('max_frontier_size', 'Tamanho máximo da fronteira', 'fronteira'),
               ('success', 'Buscas resolvidas (%)', 'sucesso')]
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    for metric, label, filename in metrics:
        fig, axes = plt.subplots(1, len(sizes), figsize=(11, 4.3), squeeze=False)
        for ax, size in zip(axes[0], sizes):
            for algorithm, color, marker in [('BFS', '#0072B2', 'o'), ('DFS', '#D55E00', 's')]:
                averages, lows, highs = [], [], []
                for depth in depths:
                    group = [r for r in rows if int(r['size']) == size
                             and int(r['walk_depth']) == depth and r['algorithm'] == algorithm]
                    values = [100 * (r['status'] == 'solved') if metric == 'success'
                              else float(r[metric]) for r in group]
                    if not values:
                        raise ValueError(f'Configuração ausente: {size}, {depth}, {algorithm}')
                    averages.append(statistics.mean(values))
                    q = statistics.quantiles(values, n=4, method='inclusive') if len(values) > 1 else values * 3
                    lows.append(q[0])
                    highs.append(q[2])
                ax.plot(depths, averages, marker=marker, color=color, label=algorithm, linewidth=2)
                if metric != 'success':
                    ax.fill_between(depths, lows, highs, color=color, alpha=0.13)
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
        caption = ('Média de todas as execuções; faixa: percentis 25–75. Eixo y logarítmico.'
                   if metric != 'success' else 'Percentual de soluções encontradas dentro dos limites comuns de recursos.')
        fig.suptitle(label, fontweight='bold')
        fig.text(0.5, 0.015, caption, ha='center', fontsize=10)
        fig.tight_layout(rect=(0, 0.055, 1, 0.95))
        fig.savefig(args.output / f'{filename}.png', dpi=160)
        fig.savefig(args.output / f'{filename}.svg')
        plt.close(fig)
    summary = {}
    for size in sizes:
        for algorithm in ('BFS', 'DFS'):
            group = [r for r in rows if int(r['size']) == size and r['algorithm'] == algorithm]
            summary[f'{size}x{size}_{algorithm}'] = {
                'runs': len(group), 'status': dict(Counter(r['status'] for r in group)),
                **{m: statistics.mean(float(r[m]) for r in group) for m, _, _ in metrics if m != 'success'},
                'peak_memory_mib': statistics.mean(float(r['peak_memory_mib']) for r in group)}
    (args.output.parent / 'statistics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
