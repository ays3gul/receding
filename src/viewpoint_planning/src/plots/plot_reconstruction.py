"""
Reconstruction comparison plot.
Left : reconstructed TARGET voxels (blue) — bunny only, background removed.
Right: ground-truth mesh (red).

Why this version fixes the "floating blob + vertical line" artefact
-------------------------------------------------------------------
The grid stores background/occluder voxels too. Those must NOT appear in the
reconstruction figure. We remove them in TWO independent ways so the plot is
clean no matter what the caller passes:

  1. If the caller passes `voxel_class_ids`, we keep only class == 0 (the
     target/bunny). This is the correct, semantic filter.
  2. We ALSO clip to the mesh bounding box as a geometric safety net. The old
     version only did (2), and the stray vertical line happened to fall inside
     the bunny's x/y bounds, so it survived. Doing (1) first removes it.

If `target_voxels` is already filtered (class 0 only) — which is what the
fixed planners now store — step (1) is a no-op and everything still works.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   # noqa: F401  (needed for 3d proj)


def plot_reconstruction_comparison(
    target_voxels,
    mesh_coordinates,
    save_path=None,
    method_label='RH-NBV',
    voxel_class_ids=None,     # optional (N,) array of semantic class ids
    elev=20,
    azim=-60,
):
    """
    Side-by-side 3D scatter: reconstructed target voxels vs ground-truth mesh.

    Args:
        target_voxels    : (N, 3) reconstructed voxel positions
        mesh_coordinates : (M, 3) ground-truth mesh points
        save_path        : PNG output path (optional)
        method_label     : label shown in subplot title and figure title
        voxel_class_ids  : (N,) semantic class id per voxel; if given, only
                           class 0 (target) voxels are plotted
        elev, azim       : 3D view angle
    """
    # Guard: nothing to plot yet
    if (target_voxels is None
            or not isinstance(target_voxels, np.ndarray)
            or target_voxels.ndim < 2
            or len(target_voxels) == 0):
        print("Reconstruction plot skipped: no target voxels detected.")
        return None, None

    mesh_arr  = np.asarray(mesh_coordinates)
    voxel_arr = np.asarray(target_voxels)
    n_raw     = len(voxel_arr)

    # ── Filter 1: semantic class (keep only target class 0) ──────────
    if voxel_class_ids is not None:
        cls = np.asarray(voxel_class_ids)
        if len(cls) == len(voxel_arr):
            keep = (np.round(cls).astype(int) == 0)
            voxel_arr = voxel_arr[keep]

    # ── Filter 2: geometric clip to mesh bounding box (+ margin) ─────
    # Safety net for any background voxel that slipped through (or when no
    # class ids are available). Margin keeps legitimate surface voxels.
    margin = 0.03
    lo = mesh_arr.min(axis=0) - margin
    hi = mesh_arr.max(axis=0) + margin
    in_bounds = np.all((voxel_arr >= lo) & (voxel_arr <= hi), axis=1)
    voxel_filtered = voxel_arr[in_bounds]

    n_removed = n_raw - len(voxel_filtered)
    if n_removed > 0:
        print(f"[ReconPlot] Removed {n_removed} non-target/out-of-bounds voxels "
              f"({len(voxel_filtered):,} target voxels remain)")

    # ── Figure ───────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 6))
    fig.suptitle(f"{method_label} Reconstruction vs. Ground Truth",
                 fontsize=13, fontweight='bold', y=1.01)

    # Left: reconstructed voxels
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.view_init(elev=elev, azim=azim)
    if len(voxel_filtered) > 0:
        ax1.scatter(
            voxel_filtered[:, 0], voxel_filtered[:, 1], voxel_filtered[:, 2],
            c='blue', s=1, alpha=0.6, rasterized=True,
        )
    ax1.set_title(
        f"Target Voxels Point Cloud\n"
        f"({method_label}: {len(voxel_filtered):,} target voxels)",
        fontsize=11, fontweight='bold',
    )
    ax1.set_xlabel('X (m)', fontsize=9)
    ax1.set_ylabel('Y (m)', fontsize=9)
    ax1.set_zlabel('Z (m)', fontsize=9)

    # Right: ground-truth mesh
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.view_init(elev=elev, azim=azim)
    ax2.scatter(
        mesh_arr[:, 0], mesh_arr[:, 1], mesh_arr[:, 2],
        c='red', s=1, alpha=0.6, rasterized=True,
    )
    ax2.set_title(
        f"Mesh Coordinates Point Cloud\n(Ground truth: {len(mesh_arr):,} points)",
        fontsize=11, fontweight='bold',
    )
    ax2.set_xlabel('X (m)', fontsize=9)
    ax2.set_ylabel('Y (m)', fontsize=9)
    ax2.set_zlabel('Z (m)', fontsize=9)

    # Equal aspect on both axes using mesh bounds
    mid  = mesh_arr.mean(axis=0)
    span = max((mesh_arr.max(axis=0) - mesh_arr.min(axis=0)).max() / 2, 0.10)
    for ax in [ax1, ax2]:
        ax.set_xlim(mid[0] - span, mid[0] + span)
        ax.set_ylim(mid[1] - span, mid[1] + span)
        ax.set_zlim(mid[2] - span, mid[2] + span)
        ax.set_box_aspect([1, 1, 1])

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close(fig)

    return fig, (ax1, ax2)
