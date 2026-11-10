"""Maintainer-style one-factor plots: matrix dimension on the X axis.

Run: python lab1/size_curves.py --output results/size_curves --matrix-count 3 --repeats 2
The basic three-class study in results/ is retained unchanged.
"""
import argparse
import csv
import json
from pathlib import Path

from experiments import BASELINE, SWEEPS, run_study, summarize

# Each integer dimension is measured, not an interpolated data point.
DIMENSIONS = {
    "small": tuple(range(3, 6)),
    "medium": tuple(range(6, 13)),
    "large": tuple(range(13, 25)),
}
# These plateau thresholds MUST trigger early stopping to reveal sensitivity.
LEVELS = dict(SWEEPS)
LEVELS["plateau_limit"] = (3, 5, 10, 20)
LEVELS["plateau_diff"] = (0.005, 0.02, 0.05, 0.1)

DISPLAY = {
    "population_size": ("Размер популяции", "особей"),
    "mutation_probability": ("Вероятность мутации", "p"),
    "mutation_percent": ("Максимальная доля инверсии", "%"),
    "elitist_percent": ("Доля элитизма", "%"),
    "plateau_limit": ("Длина окна плато", "поколений"),
    "plateau_diff": ("Относительный порог плато", "порог"),
    "max_iterations": ("Лимит поколений", "поколений"),
}


def baseline_for(parameter):
    baseline = dict(BASELINE)
    if parameter in ("plateau_limit", "plateau_diff"):
        baseline["plateau_diff"] = 0.05
    return baseline


def rows_for_parameter(parameter, count=3, repeats=2, seed=20261021,
                       dimensions=None):
    if parameter not in LEVELS:
        raise ValueError("unknown parameter")
    dimensions = DIMENSIONS if dimensions is None else dimensions
    return run_study(matrix_count=count, repeats=repeats, seed=seed,
                     classes=dimensions, sweeps={parameter: LEVELS[parameter]},
                     baseline=baseline_for(parameter))


def running_mean(values, width=3):
    """Visual-only smoothing: every plotted value derives from real measurements."""
    k = width // 2
    return [sum(values[max(0,i-k):min(len(values),i+k+1)]) /
            len(values[max(0,i-k):min(len(values),i+k+1)])
            for i in range(len(values))]


def plot_parameter(parameter, summaries, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11, "axes.titlesize": 14,
        "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#ffffff",
    })
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    title, unit = DISPLAY[parameter]
    levels = LEVELS[parameter]
    nums = list(range(3, 25))
    index = {(str(r["value"]), int(r["size"])): r for r in summaries
             if r["parameter"] == parameter and r["size"] != "all"}
    fig, ax = plt.subplots(figsize=(10.2, 5.4), dpi=130)
    ax.axvspan(3, 5.5, alpha=.10, color="#17a398")
    ax.axvspan(5.5, 12.5, alpha=.08, color="#1b649b")
    ax.axvspan(12.5, 24, alpha=.055, color="#d14e45")
    colors = ["#0b4b8b", "#00a7a0", "#d9742d", "#953f84"]
    for j, value in enumerate(levels):
        measured = [100 * float(index[(str(value), n)]["mean_gap"]) for n in nums]
        # Plot all 22 actual x coordinates, with a visual 3-point mean to reduce
        # stochastic jitter. Original per-size values remain in summary.csv.
        line, = ax.plot(nums, running_mean(measured), linewidth=2.25,
                        color=colors[j], label=str(value), zorder=3)
        ax.scatter(nums, measured, s=10, color=line.get_color(), alpha=.14, zorder=2)
    ax.set_xlim(3,24)
    ax.set_ylim(bottom=0)
    ax.set_xticks([3,5,7,9,11,13,15,17,19,21,23,24])
    ax.set_xlabel("Размерность матрицы n × n", labelpad=9)
    ax.set_ylabel("Отклонение от точного оптимума, %", labelpad=8)
    ax.set_title(f"{title}: зависимость качества от размерности", pad=15)
    ax.grid(axis="y", alpha=.22)
    ax.spines[["right","top"]].set_visible(False)
    ax.legend(title=f"Значение: {unit}", loc="upper left", framealpha=.95,
              edgecolor="#c7d6e4", fontsize=10, ncol=2)
    ax.text(4, -0.075, "малые", color="#168272", ha="center",
            transform=ax.get_xaxis_transform(), fontsize=10)
    ax.text(9, -0.075, "средние", color="#0b4b8b", ha="center",
            transform=ax.get_xaxis_transform(), fontsize=10)
    ax.text(18, -0.075, "большие", color="#c05e4b", ha="center",
            transform=ax.get_xaxis_transform(), fontsize=10)
    fig.subplots_adjust(left=.105,right=.97,top=.87,bottom=.21)
    fig.savefig(output / f"{parameter}_mean_gap.png", dpi=180)
    plt.close(fig)


def save_curves(output="results/size_curves", matrix_count=3, repeats=2,
                seed=20261021, dimensions=None, levels=None):
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    dims = DIMENSIONS if dimensions is None else dimensions
    levels = LEVELS if levels is None else levels
    raw_all=[]; summary_all=[]
    for param, level_values in levels.items():
        raw = run_study(matrix_count=matrix_count, repeats=repeats, seed=seed,
                        classes=dims, sweeps={param: level_values},
                        baseline=baseline_for(param))
        summary = [s for s in summarize(raw) if s["size"] != "all"]
        raw_all.extend(raw); summary_all.extend(summary)
        # Plot full-size studies (tests may provide reduced dimension grids).
        if tuple(x for group in dims.values() for x in group) == tuple(range(3,25)):
            plot_parameter(param,summary,output/"plots")
    with (output/"raw_results.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(raw_all[0].keys()))
        writer.writeheader();writer.writerows(raw_all)
    with (output/"summary.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(summary_all[0].keys()))
        writer.writeheader();writer.writerows(summary_all)
    (output/"metadata.json").write_text(json.dumps({
        "x_axis":"integer dimension n from 3 to 24",
        "seed":seed,"matrix_count_per_n":matrix_count,"repeats":repeats,
        "size_classes":dims,"levels":levels,"baseline":BASELINE,
        "plateau_baseline_for_plateau_parameters":0.05,
        "y_axis":"mean relative cost gap to exact optimum (percent)",
        "visual_smoothing":"centered 3-point moving average over measured sizes",
        "scatter":"raw mean at each size (semi-transparent)",
        "trials":len(raw_all)
    },ensure_ascii=False,indent=2),encoding="utf-8")
    return raw_all,summary_all


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="results/size_curves")
    p.add_argument("--matrix-count",type=int,default=3)
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--seed",type=int,default=20261021)
    args=p.parse_args()
    rows,summary=save_curves(args.output,args.matrix_count,args.repeats,args.seed)
    print(f"Size curves: {len(rows)} trials, {len(summary)} per-size rows")


if __name__=="__main__":
    main()
