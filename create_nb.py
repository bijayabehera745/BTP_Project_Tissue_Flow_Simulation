import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Phase 1: 2D Tissue Patch (Fluid State)\n",
                "This notebook simulates a tissue patch in the unjammed fluid state and visualizes the results."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import tqdm\n",
                "import pyafv as afv\n",
                "\n",
                "# Parameters\n",
                "N = 100                      # Number of cells\n",
                "radius = 1.0                 # Maximal cell radius\n",
                "mu = 1.0                     # Mobility\n",
                "dt = 0.005                   # Time step\n",
                "noise_strength = 3.0         # Thermal noise to drive unjammed motion\n",
                "steps = 1500                 # Total simulation steps\n",
                "\n",
                "# Target shape index p0 > 3.81 for fluid state (Bi et al., 2015)\n",
                "# p0 = P0 / sqrt(A0). If A0 = pi, sqrt(A0) ~ 1.772.\n",
                "# P0 = 3.85 * sqrt(pi) * radius ~ 6.82 * radius\n",
                "phys = afv.PhysicalParams(\n",
                "    r=radius,\n",
                "    A0=np.pi*(radius**2),\n",
                "    P0=6.82*radius, \n",
                "    KA=1.0,\n",
                "    KP=1.0,\n",
                "    Lambda=0.1\n",
                ")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Initialize cells in a square block\n",
                "pts = np.random.rand(N, 2) * 15.0\n",
                "sim = afv.FiniteVoronoiSimulator(pts, phys)\n",
                "\n",
                "# Plot 1: Initial Voronoi Model\n",
                "fig1, ax1 = plt.subplots(figsize=(6, 6))\n",
                "sim.plot_2d(ax=ax1)\n",
                "ax1.set_title(\"1. Initial Voronoi Model (Step 0)\")\n",
                "ax1.set_xlim(-2, 17)\n",
                "ax1.set_ylim(-2, 17)\n",
                "ax1.set_aspect('equal')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"Running overdamped Langevin dynamics with active noise...\")\n",
                "# Track trajectories to visualize unjammed flow/rearrangements\n",
                "trajectories = np.zeros((steps, N, 2))\n",
                "\n",
                "for step in tqdm.tqdm(range(steps), desc=\"Fluid simulation\"):\n",
                "    diag = sim.build()\n",
                "    forces = diag[\"forces\"]\n",
                "    \n",
                "    # Add random active noise to simulate temperature / active motility\n",
                "    active_forces = np.random.randn(N, 2) * noise_strength\n",
                "    \n",
                "    total_forces = forces + active_forces\n",
                "    \n",
                "    pts += mu * total_forces * dt\n",
                "    sim.update_positions(pts)\n",
                "    \n",
                "    trajectories[step] = pts.copy()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Plot 2: Fluid Motion Plot (Trajectories + Final Voronoi)\n",
                "fig2, ax2 = plt.subplots(figsize=(8, 8))\n",
                "for i in range(N):\n",
                "    ax2.plot(trajectories[:, i, 0], trajectories[:, i, 1], alpha=0.3, linewidth=1.0)\n",
                "sim.plot_2d(ax=ax2)\n",
                "ax2.set_title(r\"2. Fluid State Unjammed Motion ($p_0 > 3.81$)\")\n",
                "ax2.set_xlim(-2, 17)\n",
                "ax2.set_ylim(-2, 17)\n",
                "ax2.set_aspect('equal')\n",
                "plt.show()\n",
                "\n",
                "# Plot 3: Only the trajectory lines\n",
                "fig3, ax3 = plt.subplots(figsize=(8, 8))\n",
                "for i in range(N):\n",
                "    ax3.plot(trajectories[:, i, 0], trajectories[:, i, 1], alpha=0.3, linewidth=1.0)\n",
                "ax3.set_title(\"3. Cell Trajectories Only\")\n",
                "ax3.set_xlim(-2, 17)\n",
                "ax3.set_ylim(-2, 17)\n",
                "ax3.set_aspect('equal')\n",
                "plt.show()"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(os.path.join("pyafv", "simulate.ipynb"), "w") as f:
    json.dump(notebook, f, indent=2)

print("Notebook generated successfully.")
