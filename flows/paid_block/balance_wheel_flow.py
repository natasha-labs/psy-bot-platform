import math
import tempfile

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_wheel(data: dict) -> str:
    labels = list(data.keys())
    values = list(data.values())

    count = len(labels)
    if count == 0:
        raise ValueError("No data for balance wheel")

    angles = [n / float(count) * 2 * math.pi for n in range(count)]
    angles += angles[:1]
    values += values[:1]

    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], labels, fontsize=10)
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], fontsize=9)
    plt.ylim(0, 5)

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.15)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_path = temp_file.name
    temp_file.close()

    plt.tight_layout()
    plt.savefig(temp_path, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    return temp_path
