#!/usr/bin/env python3
"""
test_rh_node_tomato.py — RH-NBV driver for tomato06 scenario.

test_rh_node.py'nin birebir kopyası; tek fark:
  - MESH_TARGET=tomato  → viewpoint_planning.py tomato6.dae yükler
  - TARGET_POS override → tomato centroid [0.5, -0.4, 1.13]

Orijinal test_rh_node.py'ye dokunma.

Gereksinim:
  1. Gazebo'da tomato06_bunnypos.world açık olmalı
     (roslaunch abb_l515_bringup abb_l515_bringup.launch model:=tomato06_bunnypos)
  2. viewpoint_planning.py güncel versiyonu src/viewpoint_planners/ altında olmalı
     (MESH_TARGET env var desteği eklenmiş hali)

Usage:
    python3 test_rh_node_tomato.py               # 5 viewpoint (Exp D)
    EXPERIMENT=C python3 test_rh_node_tomato.py  # 20 viewpoint (Exp C)
    NUM_ITERS=20 NUM_TRIALS=3 python3 test_rh_node_tomato.py
"""
import os

# ── Tomato env overrides — viewpoint_planning.py bunları okur ────────────────
os.environ.setdefault("MESH_TARGET", "tomato")
os.environ.setdefault("TARGET_POS",  "0.5,-0.4,1.06")   # fruit centroid
os.environ.setdefault("GRID_SIZE",    "0.25,0.25,0.25")  # fruit bbox + margin
# ─────────────────────────────────────────────────────────────────────────────

import json
import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")

import rospy

from viewpoint_planners.viewpoint_planning import ViewpointPlanning
from metrics import compute_all_metrics, detect_occlusion_type, save_and_print
from plots.plot_coverage import plot_coverage_progression
from plots.plot_trajectory_3d import plot_3d_trajectory
from plots.plot_candidate_sequences import (
    plot_candidate_sequences,
    plot_candidate_sequences_grid,
)
from plots.plot_reconstruction import (
    plot_reconstruction_comparison,
    plot_reconstruction_evolution_grid,
    plot_reconstruction_single_iter,
)
from viewpoint_planners.fair_comparison_config import BASE_SEED as FC_BASE_SEED


EXPERIMENT = os.environ.get("EXPERIMENT", "D").upper()
_default_iters = 20 if EXPERIMENT == "C" else 5
NUM_ITERS  = int(os.environ.get("NUM_ITERS", _default_iters))
NUM_TRIALS = int(os.environ.get("NUM_TRIALS", 1))
BASE_SEED  = FC_BASE_SEED

RH_PARAMS = {
    "horizon":              int(os.environ.get("RH_H", 3)),
    "num_candidates":       int(os.environ.get("RH_K", 10)),
    "lambda_cost":        float(os.environ.get("RH_LAMBDA", 2.0)),
    "discount":           float(os.environ.get("RH_GAMMA", 0.85)),
    "step_size":          float(os.environ.get("RH_STEP", 0.065)),
    "use_spherical_bounds": os.environ.get("RH_SHELL", "0") != "0",
    "occlusion_bonus":    float(os.environ.get("OCC_BONUS", 0.0)),
}
K = RH_PARAMS["num_candidates"]
H = RH_PARAMS["horizon"]


def make_run_dir(occ):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shell = "shell" if RH_PARAMS["use_spherical_bounds"] else "box"
    name = f"run_{ts}_exp{EXPERIMENT}_{occ}_K{K}_H{H}_{shell}_tomato_fruit"
    run_dir = os.path.join("results", name)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def save_plots(vp, occ, out_dir, recon_snapshots=None):
    rh = vp.rh_planner

    def _try(fn, label):
        try:
            fn()
        except Exception as e:
            print(f"  [plot] {label} failed: {e}")

    _try(lambda: plot_coverage_progression(
        coverages={"RH-NBV-Tomato": vp.coverages_rh},
        save_path=os.path.join(out_dir, f"coverage_rh_tomato_{occ}.png"),
        title=f"RH-NBV Tomato Coverage (Occlusion: {occ}, K={K}, H={H})",
    ), "coverage")

    _try(lambda: plot_3d_trajectory(
        trail=vp.trail_rh,
        mesh_coordinates=rh.mesh_coordinates,
        occlusion_type=occ,
        save_path=os.path.join(out_dir, f"trajectory_3d_rh_tomato_{occ}.png"),
        title=f"RH-NBV Tomato 3D Trajectory (Occlusion: {occ})",
        method_label="RH-NBV-Tomato",
    ), "trajectory")

    if hasattr(rh, "candidate_history") and len(rh.candidate_history) > 0:
        _try(lambda: plot_candidate_sequences(
            candidate_history=rh.candidate_history,
            mesh_coordinates=rh.mesh_coordinates,
            occlusion_type=occ,
            iteration_to_plot=min(2, len(rh.candidate_history) - 1),
            save_path=os.path.join(out_dir, f"candidates_iter2_tomato_{occ}.png"),
        ), "candidates_single")

        _try(lambda: plot_candidate_sequences_grid(
            candidate_history=rh.candidate_history,
            mesh_coordinates=rh.mesh_coordinates,
            occlusion_type=occ,
            iterations_to_plot=[i for i in [0, 1, 2, 3] if i < len(rh.candidate_history)],
            save_path=os.path.join(out_dir, f"candidates_grid_tomato_{occ}.png"),
        ), "candidates_grid")

    _try(lambda: plot_reconstruction_comparison(
        target_voxels=(rh.all_target_voxels
                       if getattr(rh, "all_target_voxels", None) is not None
                       and len(rh.all_target_voxels) > 0
                       else rh.target_voxels),
        mesh_coordinates=rh.mesh_coordinates,
        save_path=os.path.join(out_dir, f"reconstruction_rh_tomato_{occ}.png"),
        method_label="RH-NBV-Tomato",
    ), "reconstruction")

    if recon_snapshots:
        _try(lambda: plot_reconstruction_evolution_grid(
            voxel_snapshots=recon_snapshots,
            mesh_coordinates=rh.mesh_coordinates,
            save_path=os.path.join(out_dir,
                                   f"reconstruction_evolution_rh_tomato_{occ}.png"),
            method_label="RH-NBV-Tomato",
        ), "reconstruction_evolution")

        iter_dir = os.path.join(out_dir, "reconstruction_per_iter")
        os.makedirs(iter_dir, exist_ok=True)
        for i, snap in enumerate(recon_snapshots):
            _try(lambda snap=snap, i=i: plot_reconstruction_single_iter(
                target_voxels=snap,
                mesh_coordinates=rh.mesh_coordinates,
                iteration=i + 1,
                save_path=os.path.join(iter_dir,
                                       f"reconstruction_rh_tomato_{occ}_view{i+1:02d}.png"),
                method_label="RH-NBV-Tomato",
            ), f"reconstruction_view{i+1}")


def run_single_trial(trial_idx, occ, run_dir):
    trial_seed = BASE_SEED + trial_idx
    trial_dir = os.path.join(run_dir, f"trial_{trial_idx:02d}")
    os.makedirs(trial_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  RH-NBV TOMATO TRIAL {trial_idx+1}/{NUM_TRIALS}  |  seed={trial_seed}")
    print(f"  K={K}, H={H}, gamma={RH_PARAMS['discount']}, "
          f"lambda={RH_PARAMS['lambda_cost']} | Occlusion: {occ}")
    print(f"{'='*60}\n")

    seed_for_start = None if trial_idx == 0 else trial_seed
    vp = ViewpointPlanning(lr=0, trial_seed=seed_for_start, rh_params=RH_PARAMS)

    recon_snapshots = []

    for i in range(NUM_ITERS):
        print(f"--- RH-Tomato Iteration {i+1}/{NUM_ITERS} ---")
        vp._diagnose_f1 = (EXPERIMENT == "D" and i == NUM_ITERS - 1)
        vp.run_rh()
        rh = vp.rh_planner
        snap = (rh.all_target_voxels
                if getattr(rh, "all_target_voxels", None) is not None
                and len(rh.all_target_voxels) > 0
                else rh.target_voxels)
        snap = (snap.copy() if isinstance(snap, np.ndarray) and snap.ndim == 2
                else np.zeros((0, 3)))
        recon_snapshots.append(snap)

    target_voxels = vp.rh_planner.target_voxels
    mesh_coords   = vp.rh_planner.mesh_coordinates
    if isinstance(target_voxels, np.ndarray) and target_voxels.ndim < 2:
        target_voxels = None

    results = compute_all_metrics(
        coverages=vp.coverages_rh.tolist(),
        recalls=vp.recall_rh.tolist(),
        precisions=vp.precision_rh.tolist(),
        distances=vp.trajectory_distance_rh.tolist(),
        times=vp.cumulative_time_rh.tolist(),
        ray_calls=vp.ray_calls_rh.tolist(),
        method_name="RH-NBV-Tomato",
        occlusion_type=occ,
        params={**RH_PARAMS, "trial": trial_idx, "seed": trial_seed,
                "target": "tomato"},
        target_voxels=target_voxels,
        mesh_coordinates=mesh_coords,
    )
    results["sigma_series"]           = vp.sigma_rh.tolist()
    results["occluded_recall_series"] = vp.occluded_recall_rh.tolist()
    results["tp_series"]              = vp.tp_rh.tolist()
    results["fp_series"]              = vp.fp_rh.tolist()
    results["fn_series"]              = vp.fn_rh.tolist()

    save_and_print(results, prefix=os.path.join(trial_dir, "metrics"),
                   experiment=EXPERIMENT)
    save_plots(vp, occ, trial_dir, recon_snapshots=recon_snapshots)
    return results


def summarize(all_results, occ, run_dir):
    summary = {
        "occlusion":  occ,
        "target":     "tomato",
        "num_trials": len(all_results),
        "num_iters":  NUM_ITERS,
        "rh_params":  RH_PARAMS,
        "per_trial": [
            {"trial": i,
             "final_coverage":  r["final_coverage"],
             "final_f1":        r["final_f1"],
             "final_distance":  r["final_distance"],
             "total_ray_calls": r["total_ray_calls"],
             "coverage_auc":    r["coverage_auc"]}
            for i, r in enumerate(all_results)
        ],
        "mean": {}, "std": {},
    }
    for key in ["final_coverage", "final_f1", "final_distance",
                "total_ray_calls", "coverage_auc"]:
        vals = np.array([r[key] for r in all_results], dtype=float)
        summary["mean"][key] = round(float(vals.mean()), 4)
        summary["std"][key]  = round(float(vals.std()),  4)

    path = os.path.join(run_dir, "summary.json")
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'#'*60}")
    print(f"  SUMMARY — RH-NBV Tomato | {len(all_results)} trial(s) | {occ}")
    print(f"{'#'*60}")
    print(f"  Final coverage : {summary['mean']['final_coverage']:.2f} "
          f"+/- {summary['std']['final_coverage']:.2f} %")
    print(f"  Final F1       : {summary['mean']['final_f1']*100:.2f} "
          f"+/- {summary['std']['final_f1']*100:.2f} %")
    print(f"  Trajectory dist: {summary['mean']['final_distance']:.3f} "
          f"+/- {summary['std']['final_distance']:.3f} m")
    print(f"  Coverage AUC   : {summary['mean']['coverage_auc']:.2f}")
    print(f"  Saved -> {path}\n")
    return summary


if __name__ == "__main__":
    rospy.init_node("rh_test_tomato")

    occ = detect_occlusion_type()
    run_dir = make_run_dir(occ)

    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump({
            "experiment":      EXPERIMENT,
            "target":          "tomato_fruit",  # Fruit1-4 only, dal/yaprak doğal occluder
            "mesh_target_env": os.environ.get("MESH_TARGET"),
            "target_pos_env":  os.environ.get("TARGET_POS"),
            "num_iters":       NUM_ITERS,
            "num_trials":      NUM_TRIALS,
            "base_seed":       BASE_SEED,
            "rh_params":       RH_PARAMS,
            "occlusion":       occ,
            "timestamp":       datetime.datetime.now().isoformat(),
        }, f, indent=2)

    print(f"\nRun directory : {run_dir}")
    print(f"Target        : tomato06_bunnypos (MESH_TARGET=tomato, TARGET_POS=0.5,-0.4,1.13)")
    print(f"RH-NBV Tomato | {NUM_ITERS} viewpoints | {NUM_TRIALS} trial(s)\n")

    all_results = [run_single_trial(t, occ, run_dir) for t in range(NUM_TRIALS)]
    summarize(all_results, occ, run_dir)
    print("\nRH-NBV Tomato complete.")
