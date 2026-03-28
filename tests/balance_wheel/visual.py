import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import tempfile


def generate_wheel(data: dict):
    labels = list(data.keys())
    values = list(data.values())

    if not labels:
        return None

    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    values = values + values[:1]
    angles = list(angles) + [angles[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_ylim(0, 5)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp.name)
    plt.close()

    return tmp.name
