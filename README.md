# PyAFV — Active Finite Voronoi Cell Tissue Simulator

A Python simulation framework for 2D epithelial cell tissue mechanics using the **Active Finite Voronoi (AFV)** model. Cells are represented as Voronoi regions with tunable area and perimeter elasticity, driven by an external flow force past a circular obstacle — making it ideal for studying collective cell migration, galvanotaxis, and tissue rheology.

---

## What is the AFV Model?

Each cell is a polygon defined by its Voronoi region. The total energy of the tissue is:

```
E = KA·Σ(Aᵢ - A₀)² + KP·Σ(Pᵢ - P₀)² + Λ·Σ(non-contact edge lengths)
```

- **Area term** (`KA`, `A0`): penalises deviations from the preferred cell area
- **Perimeter term** (`KP`, `P0`): controls cell shape and cortical tension
- **Lambda term** (`Λ`): models differential tension between free and cell-cell contact edges

The dimensionless **shape index** `p0 = P0 / √A0` is the key control parameter:

| `p0` | Tissue state |
|------|-------------|
| < 3.72 | Solid-like (jammed) — cells resist deformation |
| ≈ 3.81 | Solid–fluid transition |
| > 3.81 | Fluid-like (unjammed) — cells flow freely |

---

## Initial State: Unrelaxed vs Relaxed

Before running active dynamics, cells are placed randomly and relaxed to mechanical equilibrium under elastic forces only (no driving). The difference is stark:

| Unrelaxed (random seeding) | Relaxed (500 steps, elastic only) |
|:-:|:-:|
| ![Unrelaxed initial state](initial_unrelaxed.png) | ![Relaxed initial state](initial_relaxed.png) |

> Both images are generated automatically when you run `Simulate_2d_flow.py`.

---

## Simulation in Action

The flow simulation drives ~750 cells left-to-right past a circular obstacle.  
Cells are coloured by their normalised area `A/A₀` (blue = compressed, red = stretched).

### Matplotlib / PNG output — `p0 = 5.0`, 800 cells

<video src="simulation_video_5.0_n800.mp4" controls width="100%"></video>

### ParaView / VTP output — full field data

<video src="paraview_sim_1.mp4" controls width="100%"></video>

---

## Setup

### Prerequisites

```bash
# Python 3.10+
pip install numpy matplotlib tqdm pyvista
```

For VTP output (ParaView visualization), `pyvista` is required.  
For the PNG-only path, `pyvista` is not needed.

### Install PyAFV

```bash
cd pyafv
pip install -e .
```

---

## Running the Simulation

There are two simulation scripts, both in the `pyafv/` directory. They model the same physics but differ in their output format.

### Option A — PNG Frames (lightweight, matplotlib)

**File:** [`pyafv/simulate_with_png_out.py`](pyafv/simulate_with_png_out.py)

```bash
cd pyafv
python simulate_with_png_out.py
```

**Outputs:**
- `png_frames/frame_0000.png` … `frame_NNNN.png` — one frame every 40 steps
- `trajectories.npy` — cell centre positions at each saved step
- `trajectories.png` — trajectory plot of all cell paths

Each frame is a matplotlib figure showing cells coloured by `A/A₀`.

---

### Option B — VTP Frames (full data, ParaView)

**File:** [`pyafv/Simulate_2d_flow.py`](pyafv/Simulate_2d_flow.py)

```bash
cd pyafv
python Simulate_2d_flow.py
```

**Outputs:**
- `initial_unrelaxed.vtp` — tissue state before relaxation
- `initial_relaxed.vtp` — tissue state after 500-step relaxation
- `vtk_frames/frame_0000.vtp` … — one frame every 40 steps
- `trajectories.npy` + `trajectories.png`

Each `.vtp` file carries per-cell fields: `area`, `perimeter`, `elastic_force`, `total_force`, `cell_center`.

---

## Visualization

### Make a Video from PNG Frames (FFmpeg)

After running **Option A**, assemble the frames into an MP4:

```bash
# Standard 30 fps video
ffmpeg -framerate 30 -i pyafv/png_frames/frame_%04d.png \
       -c:v libx264 -pix_fmt yuv420p simulation.mp4

# Slower playback (10 fps) for detailed inspection
ffmpeg -framerate 10 -i pyafv/png_frames/frame_%04d.png \
       -c:v libx264 -pix_fmt yuv420p simulation_slow.mp4

# High quality with scaling
ffmpeg -framerate 24 -i pyafv/png_frames/frame_%04d.png \
       -vf "scale=1920:-2" -c:v libx264 -crf 18 -pix_fmt yuv420p simulation_hq.mp4
```

> On Windows, use the [FFmpeg Windows build](https://ffmpeg.org/download.html) and run from PowerShell.

---

### Load VTP Frames in ParaView

After running **Option B**:

1. Open **ParaView** (5.x or later)
2. **File → Open** → navigate to `pyafv/vtk_frames/`
3. Select `frame_0000.vtp` — ParaView will auto-detect the series as `frame_..vtp`
4. Click **Apply** in the Properties panel
5. In the toolbar dropdown (defaults to "Solid Color"), select a cell field:
   - `area` — cell area (compare to `A0 = π·r²`)
   - `perimeter` — cell perimeter
   - `elastic_force` — vector field of elastic restoring forces
   - `total_force` — elastic + driving + obstacle repulsion

**Playing the animation:**
- Press the **Play** button or use **View → Animation View** for fine control
- Adjust speed with the frame rate spinner
- **File → Save Animation** to export an MP4 directly from ParaView

**Useful ParaView filters for this data:**
- **Glyph** on `total_force` → visualise force vectors as arrows
- **Threshold** on `area` → isolate compressed or stretched cells
- **Plot Over Line** → measure field profiles across the obstacle wake

> To load the pre-run `initial_unrelaxed.vtp` / `initial_relaxed.vtp` snapshots, open them individually the same way and use the Spreadsheet View to inspect per-cell values.

---

## Parameter Reference

All tissue physics live in `afv.PhysicalParams`. Simulation geometry is set in the script header.

### Tissue Parameters (`PhysicalParams`)

| Parameter | Default | What it controls | Effect of increasing |
|-----------|---------|-----------------|----------------------|
| `r` | `1.0` | Maximum cell radius (sets length scale) | Larger cells; rescales everything |
| `A0` | `π·r²` | Preferred cell area | Cells swell to reach `A0`; set via `A0 = π·r²` |
| `P0` | `p0·√A0` | Preferred perimeter | Higher `P0` → more fluid-like tissue |
| `KA` | `1.0` | Area elasticity stiffness | Stiffer resistance to area changes |
| `KP` | `1.0` | Perimeter elasticity stiffness | Stiffer resistance to shape changes |
| `Lambda` | `0.1` | Free-edge line tension | Higher → cells prefer fewer free edges (cluster) |

#### The shape index `p0`

This is the most important control parameter. Set it via:

```python
target_p0 = 3.84            # change this value
P0 = target_p0 * np.sqrt(A0)
```

| `p0` value | Expected behaviour |
|------------|-------------------|
| `3.72` | Fully jammed solid — minimal cell rearrangement |
| `3.80–3.84` | Near the fluid transition — some rearrangement |
| `3.84` | Default — moderately fluid |
| `4.0+` | Highly fluid — rapid cell mixing |

---

### Simulation Geometry

| Parameter | Default | What it controls |
|-----------|---------|-----------------|
| `Lx` | `120.0` | Domain width (flow direction) |
| `Ly` | `60.0` | Domain height (periodic in Y) |
| `radius` | `1.0` | Cell radius (also sets `r` in `PhysicalParams`) |
| `mu` | `1.0` | Cell mobility (scales force → velocity) |
| `dt` | `0.005` | Integration time step |
| `steps` | `12000` | Total simulation steps |
| `save_interval` | `40` | Steps between saved frames |

---

### Obstacle Parameters

| Parameter | Default | What it controls |
|-----------|---------|-----------------|
| `obs_center` | `[50, Ly/2]` | Obstacle position (x, y) |
| `obs_radius` | `5.0` | Obstacle size |
| `obs_stiffness` | `50.0` | Repulsion spring constant |

---

### Driving Force

| Parameter | Default | What it controls |
|-----------|---------|-----------------|
| `flow_force` | `1.5` | Uniform x-direction force on all cells |

```python
driving[:, 0] = flow_force   # applied every step as a body force in +x
```

---

### Tweaking Guide

**To make cells more fluid (easier rearrangement):**
```python
target_p0 = 4.0   # increase from 3.84
```

**To slow down the flow:**
```python
flow_force = 0.5   # reduce from 1.5
dt = 0.01          # can also increase dt slightly
```

**To make a larger obstacle and observe a bigger wake:**
```python
obs_radius = 10.0
obs_center = np.array([40.0, Ly / 2])   # move upstream
```

**To change cell density:**
```python
# In simulate_with_png_out.py, line ~99:
N = round(1000 * (Lx / 30.0))   # increase multiplier for denser packing
```

**To run fewer steps for a quick test:**
```python
steps = 2000
save_interval = 20
```

---

## Project Structure

```
PyAFV/
├── pyafv/                        # Simulation scripts
│   ├── simulate_with_png_out.py  # PNG output simulation
│   ├── Simulate_2d_flow.py       # VTP output simulation
│   ├── pyafv/                    # AFV library package
│   │   ├── physical_params.py    # PhysicalParams dataclass
│   │   ├── finite_voronoi.py     # Single-process simulator
│   │   ├── parallel_voronoi.py   # Multi-process simulator
│   │   └── _plotutils.py         # Matplotlib helpers
│   ├── examples/                 # Minimal usage examples
│   │   ├── active_FV.py          # Basic active dynamics
│   │   └── relaxation.py         # Relaxation-only demo
│   └── timesteps/                # Pre-run VTK frame snapshots
├── initial_unrelaxed.png         # Generated: tissue before relaxation
├── initial_relaxed.png           # Generated: tissue after relaxation
└── requirements.txt
```

---

## Simulation Outputs (Google Drive)

Videos, trajectory plots, and initial state images are stored on Google Drive:

**[PyAFV_Galvanotaxis — Google Drive](https://drive.google.com/drive/folders/1scMuUVJCb3zcT6cVbU9k7Rh70m8bXO-a)**

```
PyAFV_Galvanotaxis/
├── videos/          — MP4 simulations (matplotlib & ParaView)
├── trajectories/    — Cell trajectory plots per p0 value
└── initial_states/  — Unrelaxed and relaxed tissue snapshots
```

> Upload the contents of the local `Drive_Upload/` folder into the matching subfolders above.

---

## Credits

Built on the [PyAFV](https://pyafv.readthedocs.io) library by Wei Wang (2025).  
Simulation scripts and galvanotaxis study by Bijay Behera.
