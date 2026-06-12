#!/usr/bin/env python3
"""
test_baseline_node.py — PSO / Random baseline driver.

Runs the PSO or Random planner under EXACTLY the same conditions as
test_rh_node.py and test_gradient_node.py (same VoxelGrid grid/voxel size via
fair_comparison_config, same jittered start pose, same mesh GT, same F1 metric,
same occlusion scenarios, same per-iteration reconstruction snapshots, same
output layout) so RH-NBV, GradientNBV, PSO and Random are all directly
comparable.

Only the planning STRATEGY differs between planners; the environment and the
evaluation code (via PlannerEvalMixin) are identical.

Usage:
    PLANNER=pso    python3 test_baseline_node.py
    PLANNER=random python3 test_baseline_node.py
    EXPERIMENT=C PLANNER=pso python3 test_baseline_node.py   # 20 viewpoints
    NUM_TRIALS=4 PLANNER=random python3 test_baseline_node.py
"""
import os
import json
import math
import time
import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")

import rospy

from abb_control.arm_control_client import ArmControlClient
from perception.perceiver import Perceiver
from viewpoint_planners.viewpoint_sampler import ViewpointSampler
from utils.py_utils import numpy_to_pose
from utils.sdf_spawner import SDFSpawner

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pso_planner import PsoPlanner
    from random_planner import RandomPlanner
except ModuleNotFoundError:
    from viewpoint_planners.pso_planner import PsoPlanner
    from viewpoint_planners.random_planner import RandomPlanner

from metrics import compute_all_metrics, detect_occlusion_type, save_and_print

try:
    from fair_comparison_config import (
        GRID_SIZE as FC_GRID_SIZE,
        get_target_position as fc_get_target_position,
        jitter_start_pose as fc_jitter_start_pose,
        seed_for_trial as fc_seed_for_trial,
        BASE_SEED,
    )
except ModuleNotFoundError:
    from viewpoint_planners.fair_comparison_config import (
        GRID_SIZE as FC_GRID_SIZE,
        get_target_position as fc_get_target_position,
        jitter_start_pose as fc_jitter_start_pose,
        seed_for_trial as fc_seed_for_trial,
        BASE_SEED,
    )

from plots.plot_coverage import plot_coverage_progression
from plots.plot_trajectory_3d import plot_3d_trajectory
from plots.plot_reconstruction import (
    plot_reconstruction_comparison,
    plot_reconstruction_evolution_grid,
    plot_reconstruction_single_iter,
)

PLANNER    = os.environ.get("PLANNER", "pso").lower()   # 'pso' or 'random'
EXPERIMENT = os.environ.get("EXPERIMENT", "D").upper()
_default_iters = 20 if EXPERIMENT == "C" else 5
NUM_ITERS  = int(os.environ.get("NUM_ITERS", _default_iters))
NUM_TRIALS = int(os.environ.get("NUM_TRIALS", 1))

TARGET_POSITION = fc_get_target_position()

if PLANNER not in ("pso", "random"):
    raise SystemExit(f"PLANNER must be 'pso' or 'random', got '{PLANNER}'")
METHOD_NAME = {"pso": "PSO", "random": "Random"}[PLANNER]


def get_mesh_coordinates():
    """Identical mesh transform to viewpoint_planning.py (fair GT)."""
    import xml.etree.ElementTree as ET
    from scipy.spatial import KDTree
    file_path = "/home/ayse/Desktop/RecedingHorizon/src/simulation_environment/meshes/bunny.dae"
    tree = ET.parse(file_path); root = tree.getroot()
    ns = {"ns": "http://www.collada.org/2005/11/COLLADASchema"}
    arr = root.find(".//ns:float_array[@id='bun_zipper-mesh-positions-array']", ns)
    raw = list(map(float, arr.text.split()))
    vertices = np.array(raw).reshape(-1, 3)
    vertices_swapped = vertices[:, [0, 2, 1]]
    scale = np.array([-1.2, 1.2, 1.2])
    z_corr = float(os.environ.get("MESH_Z_CORR", 0.048))
    translation = np.array([0.5, -0.4, 1.0 - z_corr])
    coords = vertices_swapped * scale + translation
    return coords, KDTree(coords)


# Occlusion scenarios — IDENTICAL to viewpoint_planning.py / the other drivers.
def spawn_occlusion(sdf, occ):
    if occ == "none":
        pass
    elif occ == "frontal":
        sdf.spawn_sized_box(np.array([0.5, -0.25, 1.1]), 1, "medium")
    elif occ == "half_box":
        sdf.spawn_named_model(np.array([0.40, -0.40, 1.10]), 1, "panel_side")
        sdf.spawn_named_model(np.array([0.64, -0.40, 1.10]), 2, "panel_side")
        sdf.spawn_named_model(np.array([0.50, -0.51, 1.10]), 3, "panel_back")
    elif occ == "tunnel":
        sdf.spawn_named_model(np.array([0.43, -0.25, 1.10]), 1, "panel_tunnel")
        sdf.spawn_named_model(np.array([0.57, -0.25, 1.10]), 2, "panel_tunnel")
    elif occ == "well":
        sdf.spawn_named_model(np.array([0.40, -0.40, 1.08]), 1, "panel_side_low")
        sdf.spawn_named_model(np.array([0.64, -0.40, 1.08]), 2, "panel_side_low")
        sdf.spawn_named_model(np.array([0.52, -0.28, 1.08]), 3, "panel_front_low")
        sdf.spawn_named_model(np.array([0.52, -0.52, 1.08]), 4, "panel_front_low")


def make_run_dir(occ):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"run_{ts}_exp{EXPERIMENT}_{occ}_{METHOD_NAME}"
    d = os.path.join("results", name)
    os.makedirs(d, exist_ok=True)
    return d


def build_planner(start_pose, image_size, intrinsics, mesh_coords, mesh_tree):
    """Construct PSO or Random with the SAME environment params as the others.
    Each planner keeps its own strategy hyperparameters (PSO swarm constants /
    Random sampler) at their library defaults."""
    if PLANNER == "pso":
        return PsoPlanner(
            start_pose=start_pose,
            mesh_coordinates=mesh_coords,
            mesh_tree=mesh_tree,
            grid_size=np.array(FC_GRID_SIZE, dtype=float),
            grid_center=TARGET_POSITION,
            image_size=image_size,
            intrinsics=intrinsics,
            target_params=TARGET_POSITION,
        )
    else:  # random
        return RandomPlanner(
            start_pose=start_pose,
            mesh_coordinates=mesh_coords,
            mesh_tree=mesh_tree,
            grid_size=np.array(FC_GRID_SIZE, dtype=float),
            grid_center=TARGET_POSITION,
            image_size=image_size,
            intrinsics=intrinsics,
            target_params=TARGET_POSITION,
        )


def next_view(planner):
    """Adapter over the two planners' view methods.
    PSO:    pso_view()    -> (viewpoint, utility)
    Random: random_view() -> (viewpoint, 0.0, 1)
    Returns (viewpoint, loss_scalar)."""
    if PLANNER == "pso":
        vp, util = planner.pso_view()
        return vp, float(util)
    else:
        vp, loss, _ = planner.random_view()
        return vp, float(loss)


def run_single_trial(trial_idx, occ, run_dir, mesh_coords, mesh_tree,
                     arm, perceiver, sampler):
    trial_dir = os.path.join(run_dir, f"trial_{trial_idx:02d}")
    os.makedirs(trial_dir, exist_ok=True)
    print(f"\n{'='*60}\n  {METHOD_NAME} TRIAL {trial_idx+1}/{NUM_TRIALS} | "
          f"Occlusion: {occ}\n{'='*60}\n")

    # Same jittered start pose as RH / GradientNBV (paired across planners).
    start_pose = sampler.predefine_start_pose(TARGET_POSITION)
    start_pose = fc_jitter_start_pose(start_pose, trial_idx)
    arm.move_arm_to_pose(numpy_to_pose(start_pose))

    cam_info = perceiver.get_camera_info()
    image_size = np.array([cam_info.width, cam_info.height])
    intrinsics = np.array(cam_info.K).reshape(3, 3)

    planner = build_planner(start_pose, image_size, intrinsics,
                            mesh_coords, mesh_tree)

    coverages = [0.0]; recalls = [0.0]; precisions = [0.0]
    distances = [0.0]; times = [0.0]
    tp = [0]; fp = [0]; fn = [0]
    sigmas = [0.0]; occ_recalls = [0.0]
    recon_snapshots = []
    trail = [start_pose[:3].copy()]

    for i in range(NUM_ITERS):
        print(f"--- {METHOD_NAME} Iteration {i+1}/{NUM_ITERS} ---")
        t0 = time.time()
        viewpoint, loss = next_view(planner)
        ok = arm.move_arm_to_pose(numpy_to_pose(viewpoint))
        rospy.sleep(1.0)
        if ok:
            depth, _, sem = perceiver.run()
            cov = planner.update_voxel_grid(depth, sem, viewpoint)
            cov = float(cov) if cov is not None else coverages[-1]
            d = math.sqrt(sum((viewpoint[k]-trail[-1][k])**2 for k in range(3)))
            trail.append(viewpoint[:3].copy())
            distances.append(distances[-1] + d)
            if planner.occluded_mesh_points is None:
                planner.set_occluded_mesh_points()
        else:
            cov = coverages[-1]
            distances.append(distances[-1])
        coverages.append(cov)
        times.append(times[-1] + (time.time() - t0))

        diag = (EXPERIMENT == "D" and i == NUM_ITERS - 1)
        # Same tunnel-panel voxel masking the other planners use.
        occ_positions = None
        if occ == "tunnel":
            occ_positions = [
                (np.array([0.43, -0.25, 1.10]), np.array([0.012, 0.052, 0.102])),
                (np.array([0.57, -0.25, 1.10]), np.array([0.012, 0.052, 0.102])),
            ]
        f1, rec, prec = planner.calculate_F1(
            occluder_positions=occ_positions, diagnose=diag)
        recalls.append(rec); precisions.append(prec)
        tp.append(planner.last_tp); fp.append(planner.last_fp); fn.append(planner.last_fn)
        sigmas.append(planner.compute_sigma())
        occ_recalls.append(planner.compute_occluded_recall())

        snap = (planner.all_target_voxels
                if getattr(planner, "all_target_voxels", None) is not None
                and len(planner.all_target_voxels) > 0
                else planner.target_voxels)
        recon_snapshots.append(
            snap.copy() if isinstance(snap, np.ndarray) and snap.ndim == 2
            else np.zeros((0, 3)))

        print(f"[{METHOD_NAME}] coverage={cov:.4f} | loss={loss:.4f} | "
              f"F1={f1:.4f} | recall={rec:.4f} | precision={prec:.4f} | "
              f"occ_recall={occ_recalls[-1]:.4f}")

    # Random/PSO have no ray-tracing-call accounting comparable to RH/Gradient;
    # report zeros so the column exists but isn't misleadingly attributed.
    ray_calls = [0] * len(coverages)

    results = compute_all_metrics(
        coverages=coverages, recalls=recalls, precisions=precisions,
        distances=distances, times=times, ray_calls=ray_calls,
        method_name=METHOD_NAME, occlusion_type=occ,
        params={"planner": METHOD_NAME, "trial": trial_idx,
                "seed": fc_seed_for_trial(trial_idx)},
        target_voxels=planner.target_voxels, mesh_coordinates=mesh_coords,
    )
    results["tp_series"] = tp; results["fp_series"] = fp; results["fn_series"] = fn
    results["sigma_series"]           = sigmas
    results["occluded_recall_series"] = occ_recalls
    save_and_print(results, prefix=os.path.join(trial_dir, "metrics"),
                   experiment=EXPERIMENT)

    # --- Plots (same helpers as the other planners) ---
    def _try(fn, label):
        try:
            fn()
        except Exception as e:
            print(f"  [plot] {label} failed: {e}")

    _try(lambda: plot_coverage_progression(
        coverages={METHOD_NAME: coverages},
        save_path=os.path.join(trial_dir, f"coverage_{PLANNER}_{occ}.png"),
        title=f"{METHOD_NAME} Coverage (Occlusion: {occ})",
    ), "coverage")

    _try(lambda: plot_3d_trajectory(
        trail=trail,
        mesh_coordinates=mesh_coords,
        occlusion_type=occ,
        save_path=os.path.join(trial_dir, f"trajectory_3d_{PLANNER}_{occ}.png"),
        title=f"{METHOD_NAME} 3D Trajectory (Occlusion: {occ})",
        method_label=METHOD_NAME,
    ), "trajectory")

    _try(lambda: plot_reconstruction_comparison(
        target_voxels=(planner.all_target_voxels
                       if getattr(planner, "all_target_voxels", None) is not None
                       and len(planner.all_target_voxels) > 0
                       else planner.target_voxels),
        mesh_coordinates=mesh_coords,
        save_path=os.path.join(trial_dir, f"reconstruction_{PLANNER}_{occ}.png"),
        method_label=METHOD_NAME,
    ), "reconstruction")

    if recon_snapshots:
        _try(lambda: plot_reconstruction_evolution_grid(
            voxel_snapshots=recon_snapshots,
            mesh_coordinates=mesh_coords,
            save_path=os.path.join(trial_dir,
                                   f"reconstruction_evolution_{PLANNER}_{occ}.png"),
            method_label=METHOD_NAME,
        ), "reconstruction_evolution")

        iter_dir = os.path.join(trial_dir, "reconstruction_per_iter")
        os.makedirs(iter_dir, exist_ok=True)
        for i, snap in enumerate(recon_snapshots):
            _try(lambda snap=snap, i=i: plot_reconstruction_single_iter(
                target_voxels=snap,
                mesh_coordinates=mesh_coords,
                iteration=i + 1,
                save_path=os.path.join(iter_dir,
                                       f"reconstruction_{PLANNER}_{occ}_view{i+1:02d}.png"),
                method_label=METHOD_NAME,
            ), f"reconstruction_view{i+1}")

    return results


if __name__ == "__main__":
    rospy.init_node(f"{PLANNER}_test")
    arm = ArmControlClient()
    perceiver = Perceiver()
    sampler = ViewpointSampler()
    sdf = SDFSpawner()

    occ = detect_occlusion_type()
    spawn_occlusion(sdf, occ)

    mesh_coords, mesh_tree = get_mesh_coordinates()
    run_dir = make_run_dir(occ)
    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump({"experiment": EXPERIMENT, "planner": METHOD_NAME,
                   "num_iters": NUM_ITERS, "num_trials": NUM_TRIALS,
                   "base_seed": BASE_SEED,
                   "grid_size": [float(v) for v in FC_GRID_SIZE],
                   "occlusion": occ,
                   "timestamp": datetime.datetime.now().isoformat()}, f, indent=2)

    print(f"\nRun directory: {run_dir}")
    print(f"{METHOD_NAME} baseline | {NUM_ITERS} viewpoints | "
          f"{NUM_TRIALS} trial(s) | Occlusion: {occ}\n")

    all_results = [run_single_trial(t, occ, run_dir, mesh_coords, mesh_tree,
                                    arm, perceiver, sampler)
                   for t in range(NUM_TRIALS)]
    print(f"\n{METHOD_NAME} baseline complete.")
