#!/usr/bin/env python3
"""
test_gradient_node_tomato.py — GradientNBV baseline driver for tomato06.

Tamamen test_gradient_node.py'nin kopyası; SADECE şu 3 şey değişti:
  1. get_mesh_coordinates() → tomato6.dae yükler (bunny yerine)
  2. TARGET_POSITION       → fruit centroid [0.5, -0.4, 1.06]
  3. GRID_SIZE              → fruit bbox [0.25, 0.25, 0.25] (dal/yaprak doğal occluder)
  3. spawn_occlusion()     → tomato için pass (bunny'e özel koordinatlar)

Orijinal test_gradient_node.py'ye hiç dokunma — bu dosya onu override etmez.

Usage:
    python3 test_gradient_node_tomato.py
    NUM_ITERS=10 python3 test_gradient_node_tomato.py

Gereksinim:
    tomato6.dae dosyasının yolu DAE_PATH değişkeninde tanımlı.
    Kendi setup'ına göre düzenle (aşağıda DAE_PATH satırı).
"""
import os
import json
import math
import time
import datetime
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib
matplotlib.use("Agg")

import rospy
from scipy.spatial import KDTree

from abb_control.arm_control_client import ArmControlClient
from perception.perceiver import Perceiver
from viewpoint_planners.viewpoint_sampler import ViewpointSampler
from utils.py_utils import numpy_to_pose
from utils.sdf_spawner import SDFSpawner

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from gradient_nbv_planner import GradientNBVPlanner
except ModuleNotFoundError:
    from viewpoint_planners.gradient_nbv_planner import GradientNBVPlanner

from metrics import compute_all_metrics, detect_occlusion_type, save_and_print

try:
    from fair_comparison_config import (
        GRID_SIZE as FC_GRID_SIZE,
        jitter_start_pose as fc_jitter_start_pose,
        seed_for_trial as fc_seed_for_trial,
    )
except ModuleNotFoundError:
    from viewpoint_planners.fair_comparison_config import (
        GRID_SIZE as FC_GRID_SIZE,
        jitter_start_pose as fc_jitter_start_pose,
        seed_for_trial as fc_seed_for_trial,
    )

from plots.plot_coverage import plot_coverage_progression
from plots.plot_trajectory_3d import plot_3d_trajectory
from plots.plot_reconstruction import (
    plot_reconstruction_comparison,
    plot_reconstruction_evolution_grid,
    plot_reconstruction_single_iter,
)

# ─── Ayarlar ──────────────────────────────────────────────────────────────────

EXPERIMENT = os.environ.get("EXPERIMENT", "D").upper()
_default_iters = 20 if EXPERIMENT == "C" else 5
NUM_ITERS  = int(os.environ.get("NUM_ITERS", _default_iters))
NUM_TRIALS = int(os.environ.get("NUM_TRIALS", 1))
BASE_SEED  = int(os.environ.get("BASE_SEED", 42))

# tomato06.world: <pose>1.0 0 0.8 0 0 0</pose>
# Mesh Z_UP, scale=0.4 → gerçek centroid ≈ [1.0, 0.0, 1.13]
# Bunu kendin ölçmek istersen: python3 -c "..." (yukarıdaki bbox scriptini çalıştır)
# Fruit centroid (Fruit1-4 combined bbox centroid from tomato6.dae)
TARGET_POSITION = np.array([0.5, -0.4, 1.06])
# Fruit-only grid — smaller than full-tree grid, dal/yaprak doğal occluder
FRUIT_GRID_SIZE = [0.25, 0.25, 0.25]

# ── Tomato6 DAE yolu ──────────────────────────────────────────────────────────
# Kendi workspace'indeki yola göre düzenle:
DAE_PATH = os.environ.get(
    "TOMATO_DAE_PATH",
    # greenhouse_usecase zip'ini bu klasöre çıkardıysan:
    os.path.expanduser(
        "~/Desktop/RecedingHorizon/src/simulation_environment/"
        "meshes/tomato6.dae"
    )
)
# Alternatif — greenhouse_usecase paketi src'de kuruluysa:
# DAE_PATH = os.path.expanduser(
#     "~/Desktop/RecedingHorizon/src/greenhouse_usecase/"
#     "greenhouse_gazebo/meshes/tomato/simple_meshes/tomato6.dae"
# )

# ─── Mesh yükleyici ───────────────────────────────────────────────────────────

def get_mesh_coordinates():
    """
    tomato6.dae'yi yükler, Gazebo'nun uyguladığı transform'u uygular:
      - DAE koordinat sistemi: Z_UP
      - Gazebo scale : 0.4 0.4 0.4  (tomato06.world'den)
      - Gazebo pose  : 1.0  0  0.8  (tomato06.world'den)
    """
    if not os.path.isfile(DAE_PATH):
        raise FileNotFoundError(
            f"tomato6.dae bulunamadı: {DAE_PATH}\n"
            "DAE_PATH env variable'ını veya dosyadaki DAE_PATH satırını düzenle."
        )

    tree = ET.parse(DAE_PATH)
    root = tree.getroot()
    ns = {"ns": "http://www.collada.org/2005/11/COLLADASchema"}

    # Sadece Fruit node'larının geometry ID'lerini topla
    # Dal ve yapraklar doğal occluder — ground truth'a dahil edilmiyor
    FRUIT_NODES = {"Fruit1", "Fruit2", "Fruit3", "Fruit4"}
    fruit_arr_ids = set()
    for node in root.findall(".//ns:visual_scene//ns:node", ns):
        name = node.get("name", "")
        if name in FRUIT_NODES:
            for inst in node.findall(".//ns:instance_geometry", ns):
                url = inst.get("url", "").lstrip("#")
                fruit_arr_ids.add(url.replace("-mesh", "") + "-mesh-positions-array")

    arrays = root.findall(".//ns:float_array", ns)
    pos_arrays = [
        a for a in arrays
        if (a.get("id") or "") in fruit_arr_ids
    ]
    if not pos_arrays:
        raise RuntimeError("Fruit positions arrays tomato6.dae içinde bulunamadı.")

    all_verts = []
    for a in pos_arrays:
        raw = list(map(float, a.text.split()))
        verts = np.array(raw).reshape(-1, 3)
        all_verts.append(verts)
    coords = np.vstack(all_verts)

    # Z_UP DAE → Gazebo/ROS dünya koordinatları:
    # DAE (x, y, z)  →  Gazebo (x, -z, y)
    coords_gz = np.column_stack([
        coords[:, 0],
        -coords[:, 2],
        coords[:, 1],
    ])

    # tomato06_bunnypos.world: pose=0.5 -0.4 0.8, scale=0.4
    scale       = np.array([0.4, 0.4, 0.4])
    translation = np.array([0.5, -0.4, 0.8])
    coords_world = coords_gz * scale + translation

    print(f"[tomato fruit mesh] {len(coords_world)} vertex yüklendi (Fruit1-4 only)")
    print(f"[tomato fruit mesh] bbox min: {coords_world.min(axis=0).round(3)}")
    print(f"[tomato fruit mesh] bbox max: {coords_world.max(axis=0).round(3)}")
    print(f"[tomato fruit mesh] centroid: {coords_world.mean(axis=0).round(3)}")

    return coords_world, KDTree(coords_world)


# ─── Occlusion (tomato için devre dışı) ───────────────────────────────────────

def spawn_occlusion(sdf, occ):
    # Bunny'e özel koordinatlar — tomato senaryosunda kullanılmıyor.
    # İleride tomato için occlusion senaryosu eklemek istersen buraya yaz.
    if occ != "none":
        print(f"[UYARI] Occlusion '{occ}' tomato senaryosunda desteklenmiyor, atlanıyor.")


# ─── Yardımcılar ──────────────────────────────────────────────────────────────

def make_run_dir(occ):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"run_{ts}_exp{EXPERIMENT}_{occ}_GradientNBV_tomato_fruit"
    d = os.path.join("results", name)
    os.makedirs(d, exist_ok=True)
    return d


# ─── Tek trial ────────────────────────────────────────────────────────────────

def run_single_trial(trial_idx, occ, run_dir, mesh_coords, mesh_tree,
                     arm, perceiver, sampler):
    trial_dir = os.path.join(run_dir, f"trial_{trial_idx:02d}")
    os.makedirs(trial_dir, exist_ok=True)
    print(f"\n{'='*60}\n  GradientNBV-Tomato TRIAL {trial_idx+1}/{NUM_TRIALS} | Occlusion: {occ}\n{'='*60}\n")

    # Tomato06 için özel start pose:
    # - Robot base (0,0,0), tomato x=1.0 y=0.0 z~1.13
    # - ViewpointSampler bunny'e göre y=-0.4 civarı hesaplıyor → kol ulaşamıyor
    # - Tomato önünden yaklaşım: x=0.55, y=-0.3, z=1.1 (dist_to_base~1.27m, erişilebilir)
    start_pose = sampler.predefine_start_pose(TARGET_POSITION)
    start_pose = fc_jitter_start_pose(start_pose, trial_idx)
    start_pose = fc_jitter_start_pose(start_pose, trial_idx)
    arm.move_arm_to_pose(numpy_to_pose(start_pose))

    cam_info   = perceiver.get_camera_info()
    image_size = np.array([cam_info.width, cam_info.height])
    intrinsics = np.array(cam_info.K).reshape(3, 3)

    planner = GradientNBVPlanner(
        start_pose=start_pose,
        grid_size=np.array(FRUIT_GRID_SIZE, dtype=float),
        grid_center=TARGET_POSITION,
        image_size=image_size,
        intrinsics=intrinsics,
        target_params=TARGET_POSITION,
        mesh_coordinates=mesh_coords,
        mesh_tree=mesh_tree,
    )

    coverages  = [0.0]; recalls = [0.0]; precisions = [0.0]
    distances  = [0.0]; times   = [0.0]; ray_calls  = [0]
    tp = [0]; fp = [0]; fn = [0]
    sigmas = [0.0]; occ_recalls = [0.0]
    recon_snapshots = []
    trail = [start_pose[:3].copy()]

    for i in range(NUM_ITERS):
        print(f"--- GradientNBV-Tomato Iteration {i+1}/{NUM_ITERS} ---")
        t0 = time.time()
        viewpoint, loss, _ = planner.next_best_view(target_pos=TARGET_POSITION)
        ok = arm.move_arm_to_pose(numpy_to_pose(viewpoint))
        rospy.sleep(1.0)
        if ok:
            depth, _, sem = perceiver.run()
            cov = planner.update_voxel_grid(depth, sem, viewpoint)
            cov = float(cov) if cov is not None else coverages[-1]
            d   = math.sqrt(sum((viewpoint[k] - trail[-1][k])**2 for k in range(3)))
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
        f1, rec, prec = planner.calculate_F1(
            occluder_positions=None, diagnose=diag)
        recalls.append(rec); precisions.append(prec)
        ray_calls.append(planner.ray_trace_count)
        tp.append(planner.last_tp)
        fp.append(planner.last_fp)
        fn.append(planner.last_fn)
        sigmas.append(planner.compute_sigma())
        occ_recalls.append(planner.compute_occluded_recall())

        snap = (planner.all_target_voxels
                if getattr(planner, "all_target_voxels", None) is not None
                and len(planner.all_target_voxels) > 0
                else planner.target_voxels)
        recon_snapshots.append(
            snap.copy() if isinstance(snap, np.ndarray) and snap.ndim == 2
            else np.zeros((0, 3)))

        print(f"[GradNBV-Tomato] coverage={cov:.4f} | loss={float(loss):.4f} | "
              f"F1={f1:.4f} | recall={rec:.4f} | precision={prec:.4f} | "
              f"occ_recall={occ_recalls[-1]:.4f}")

    results = compute_all_metrics(
        coverages=coverages, recalls=recalls, precisions=precisions,
        distances=distances, times=times, ray_calls=ray_calls,
        method_name="GradientNBV_tomato", occlusion_type=occ,
        params={"planner": "GradientNBV_tomato", "lr": 0.03,
                "trial": trial_idx, "seed": fc_seed_for_trial(trial_idx)},
        target_voxels=planner.target_voxels, mesh_coordinates=mesh_coords,
    )
    results["tp_series"]              = tp
    results["fp_series"]              = fp
    results["fn_series"]              = fn
    results["sigma_series"]           = sigmas
    results["occluded_recall_series"] = occ_recalls
    save_and_print(results, prefix=os.path.join(trial_dir, "metrics"),
                   experiment=EXPERIMENT)

    def _try(fn, label):
        try:
            fn()
        except Exception as e:
            print(f"  [plot] {label} failed: {e}")

    _try(lambda: plot_coverage_progression(
        coverages={"GradientNBV_tomato": coverages},
        save_path=os.path.join(trial_dir, f"coverage_gradientnbv_tomato_{occ}.png"),
        title=f"GradientNBV-Tomato Coverage (Occlusion: {occ})",
    ), "coverage")

    _try(lambda: plot_3d_trajectory(
        trail=trail,
        mesh_coordinates=mesh_coords,
        occlusion_type=occ,
        save_path=os.path.join(trial_dir, f"trajectory_3d_gradientnbv_tomato_{occ}.png"),
        title=f"GradientNBV-Tomato 3D Trajectory (Occlusion: {occ})",
        method_label="GradientNBV_tomato",
    ), "trajectory")

    _try(lambda: plot_reconstruction_comparison(
        target_voxels=(planner.all_target_voxels
                       if getattr(planner, "all_target_voxels", None) is not None
                       and len(planner.all_target_voxels) > 0
                       else planner.target_voxels),
        mesh_coordinates=mesh_coords,
        save_path=os.path.join(trial_dir,
                               f"reconstruction_gradientnbv_tomato_{occ}.png"),
        method_label="GradientNBV_tomato",
    ), "reconstruction")

    if recon_snapshots:
        _try(lambda: plot_reconstruction_evolution_grid(
            voxel_snapshots=recon_snapshots,
            mesh_coordinates=mesh_coords,
            save_path=os.path.join(trial_dir,
                                   f"reconstruction_evolution_gradientnbv_tomato_{occ}.png"),
            method_label="GradientNBV_tomato",
        ), "reconstruction_evolution")

        iter_dir = os.path.join(trial_dir, "reconstruction_per_iter")
        os.makedirs(iter_dir, exist_ok=True)
        for i, snap in enumerate(recon_snapshots):
            _try(lambda snap=snap, i=i: plot_reconstruction_single_iter(
                target_voxels=snap,
                mesh_coordinates=mesh_coords,
                iteration=i + 1,
                save_path=os.path.join(iter_dir,
                                       f"reconstruction_gradientnbv_tomato_{occ}_view{i+1:02d}.png"),
                method_label="GradientNBV_tomato",
            ), f"reconstruction_view{i+1}")

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rospy.init_node("gradient_test_tomato")
    arm      = ArmControlClient()
    perceiver = Perceiver()
    sampler  = ViewpointSampler()
    sdf      = SDFSpawner()

    occ = detect_occlusion_type()
    spawn_occlusion(sdf, occ)

    mesh_coords, mesh_tree = get_mesh_coordinates()
    run_dir = make_run_dir(occ)

    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump({
            "experiment":  EXPERIMENT,
            "planner":     "GradientNBV_tomato",
            "target":      "tomato06",
            "num_iters":   NUM_ITERS,
            "num_trials":  NUM_TRIALS,
            "base_seed":   BASE_SEED,
            "grid_size":   FRUIT_GRID_SIZE,
            "target_position": TARGET_POSITION.tolist(),
            "dae_path":    DAE_PATH,
            "occlusion":   occ,
            "timestamp":   datetime.datetime.now().isoformat(),
        }, f, indent=2)

    print(f"\nRun directory  : {run_dir}")
    print(f"Target position: {TARGET_POSITION}")
    print(f"DAE path       : {DAE_PATH}")
    print(f"GradientNBV-Tomato | {NUM_ITERS} viewpoints | Occlusion: {occ}\n")

    all_results = [
        run_single_trial(t, occ, run_dir, mesh_coords, mesh_tree,
                         arm, perceiver, sampler)
        for t in range(NUM_TRIALS)
    ]
    print("\nGradientNBV-Tomato baseline complete.")
