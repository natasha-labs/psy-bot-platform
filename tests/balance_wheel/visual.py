import math
import tempfile

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_wheel(data: dict) -> str:
    labels = list(data.keys())
    values = list(data.values())

    if not labels:
        raise ValueError("No data for balance wheel")

    count = len(labels)

    angles = [2 * math.pi * i / count for i in range(count)]
    angles_closed = angles + [angles[0]]
    values_closed = values + [values[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10)

    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=9)

    ax.plot(angles_closed, values_closed, linewidth=2)
    ax.fill(angles_closed, values_closed, alpha=0.15)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_path = temp_file.name
    temp_file.close()

    fig.savefig(temp_path, format="png", dpi=200)
    plt.close(fig)

    return temp_path
