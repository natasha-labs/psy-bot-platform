import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import tempfile


def generate_wheel(data: dict):
    labels = list(data.keys())
    values = list(data.values())

    if not labels or not values:
        return None

    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)

    ax.set_ylim(0, 5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_file.name, bbox_inches="tight")
    plt.close(fig)

    return tmp_file.name
