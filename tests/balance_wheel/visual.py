import matplotlib.pyplot as plt
import numpy as np
import tempfile


def generate_wheel(data: dict):
    labels = list(data.keys())
    values = list(data.values())

    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_ylim(0, 5)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp.name)
    plt.close()

    return temp.name
