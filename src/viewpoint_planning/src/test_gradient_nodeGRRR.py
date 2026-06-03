#!/usr/bin/env python3

import os
import time
import math
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
import rospy
from scipy.spatial import KDTree

from viewpoint_planners.gradientnbv_planner import GradientNBVPlanner
from viewpoint_planners.viewpoint_sampler import ViewpointSampler
from abb_control.arm_control_client import ArmControlClient
from perception.perceiver import Perceiver
from utils.py_utils import numpy_to_pose
from utils.sdf_spawner import SDFSpawner
from metrics import compute_all_metrics, detect_occlusion_type, save_and_print

try:
    from plots.plot_reconstruction import plot_reconstruction_comparison
except Exception:
    plot_reconstruction_comparison = None

try:
    from plots.plot_coverage import plot_coverage_progression
except Exception:
    plot_coverage_progression = None

try:
    from plots.plot_trajectory_3d import plot_3d_trajectory
except Exception:
    plot_3d_trajectory = None


NUM_ITERS  = 12
PLOT_DIR   = os.path.join("results", "plots")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_mesh_coordinates():
    file_path = "/home/ayse/gradientnbv/src/simulation_environment/meshes/bunny.dae"
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns   = {"ns": "http://www.collada.org/2005/11/COLLADASchema"}
    arr  = root.find(".//ns:float_array[@id='bun_zipper-mesh-positions-array']", ns)
    if arr is None:
        raise ValueError("Mesh positions array not found.")
    verts  = np.array(list(map(float, arr.text.split()))).reshape(-1, 3)
    verts  = verts[:, [0, 2, 1]] * np.array([-1.2, 1.2, 1.2]) + np.array([0.5, -0.4, 0.952])
    return verts, KDTree(verts)


def step_dist(trail):
    p1, p2 = trail[-2], trail[-1]
    return math.sqrt(sum((p2[i] - p1[i])**2 for i in range(3)))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    rospy.init_node("gradient_test")
    os.makedirs("results", exist_ok=True)
    os.makedirs(PLOT_DIR,   exist_ok=True)

    # ---- scene setup -------------------------------------------------------
    target_position = np.array([0.5, -0.4, 1.1])
    sdf_spawner     = SDFSpawner()
    arm_control     = ArmControlClient()
    perceiver       = Perceiver()
    viewpoint_sampler = ViewpointSampler()

    # Choose occlusion — must match what you used for RH-NBV
    sdf_spawner.spawn_box(np.array([0.65, -0.3, 1.1]), 1)   # easy
    # sdf_spawner.spawn_box(np.array([0.6, -0.25, 1.1]), 1)  # hard
    # sdf_spawner.spawn_box(np.array([0.6, -0.3, 1.1]), 1)   # extreme box1
    # sdf_spawner.spawn_box(np.array([0.6, -0.3, 1.2]), 2)   # extreme box2

    occ = detect_occlusion_type()
    print(f"\n{'='*60}")
    print(f"  GradientNBV | Occlusion: {occ} | {NUM_ITERS} iterations")
    print(f"{'='*60}\n")

    camera_pose = viewpoint_sampler.predefine_start_pose(target_position)
    arm_control.move_arm_to_pose(numpy_to_pose(camera_pose))

    camera_info = perceiver.get_camera_info()
    image_size  = np.array([camera_info.width, camera_info.height])
    intrinsics  = np.array(camera_info.K).reshape(3, 3)

    mesh_coordinates, mesh_tree = get_mesh_coordinates()

    # ---- planner -----------------------------------------------------------
    t0 = time.time()
    planner = GradientNBVPlanner(
        start_pose=camera_pose,
        grid_size=np.array([0.3, 0.6, 0.3]),
        grid_center=target_position,
        image_size=image_size,
        intrinsics=intrinsics,
        num_samples=1,
        target_params=target_position,
        mesh_coordinates=mesh_coordinates,
        mesh_tree=mesh_tree,
    )
    init_time = time.time() - t0

    # ---- metric arrays -----------------------------------------------------
    coverages       = np.array([0.0])
    recalls         = np.array([0.0])
    precisions      = np.array([0.0])
    f1s             = np.array([0.0])
    trajectory_dist = np.array([0.0])
    cumulative_time = np.array([init_time])
    ray_calls       = np.array([0])
    sigma_series    = np.array([0.0])
    trail           = [camera_pose[:3].copy()]

    print(f"{'it':>2} | {'cov%':>8} | {'F1':>7} | {'recall':>7} | "
          f"{'prec':>7} | {'dist(m)':>8} | {'time(s)':>8} | {'rays':>5}")
    print("-" * 72)

    # ---- main loop ---------------------------------------------------------
    for i in range(NUM_ITERS):
        t_iter = time.time()

        viewpoint, loss, _ = planner.next_best_view(target_pos=target_position)
        camera_pose = viewpoint
        trail.append(camera_pose[:3].copy())

        is_success = arm_control.move_arm_to_pose(numpy_to_pose(camera_pose))
        rospy.sleep(1.0)

        if is_success:
            depth_image, _, semantics = perceiver.run()
            coverage  = planner.update_voxel_grid(depth_image, semantics, camera_pose)
            dist_step = step_dist(trail)
        else:
            coverage  = coverages[-1]
            dist_step = 0.0

        coverage = float(coverage) if coverage is not None else float(coverages[-1])
        coverages       = np.append(coverages, coverage)
        trajectory_dist = np.append(trajectory_dist, trajectory_dist[-1] + dist_step)
        cumulative_time = np.append(cumulative_time, cumulative_time[-1] + (time.time() - t_iter))

        f1, recall, precision = planner.calculate_F1()
        f1s        = np.append(f1s,        f1)
        recalls    = np.append(recalls,    recall)
        precisions = np.append(precisions, precision)
        ray_calls  = np.append(ray_calls,  planner.ray_trace_count)
        sigma_series = np.append(sigma_series, planner.compute_sigma())

        print(f"{i+1:>2} | {coverage:>8.3f} | {f1:>7.4f} | {recall:>7.4f} | "
              f"{precision:>7.4f} | {trajectory_dist[-1]:>8.3f} | "
              f"{cumulative_time[-1]:>8.1f} | {planner.ray_trace_count:>5}")

    print("-" * 72)

    # ---- DIAGNOSTIC: what is actually in the grid? -------------------------
    # This tells us (a) whether the filtered planner code is running, and
    # (b) which semantic class the bunny voxels actually have.
    vp_all, _, cls_all = planner.get_occupied_points()
    import collections
    print("\n[DEBUG] occupied voxels total:", len(vp_all))
    print("[DEBUG] class id distribution:",
          dict(collections.Counter(np.round(cls_all).astype(int).tolist())))
    print("[DEBUG] planner.target_voxels shape:",
          np.asarray(planner.target_voxels).shape)
    print("-" * 72)

    # ---- metrics & JSON ----------------------------------------------------
    target_voxels = planner.target_voxels
    if isinstance(target_voxels, np.ndarray) and target_voxels.ndim < 2:
        target_voxels = None

    results = compute_all_metrics(
        coverages=coverages.tolist(),
        recalls=recalls.tolist(),
        precisions=precisions.tolist(),
        distances=trajectory_dist.tolist(),
        times=cumulative_time.tolist(),
        ray_calls=ray_calls.tolist(),
        method_name="GradientNBV",
        occlusion_type=occ,
        params={"lr": 0.03, "num_samples": 1},
        target_voxels=target_voxels,
        mesh_coordinates=mesh_coordinates,
    )
    results["sigma_series"] = sigma_series.tolist()
    save_and_print(results, prefix="results/results")

    # ---- plots -------------------------------------------------------------
    # 1. Reconstruction
    if plot_reconstruction_comparison is not None:
        try:
            path = os.path.join(PLOT_DIR, f"reconstruction_gradientnbv_{occ}.png")
            plot_reconstruction_comparison(
                target_voxels=planner.target_voxels,
                mesh_coordinates=mesh_coordinates,
                save_path=path,
                method_label="GradientNBV",
            )
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Reconstruction plot failed: {e}")

    # 2. Coverage
    if plot_coverage_progression is not None:
        try:
            path = os.path.join(PLOT_DIR, f"coverage_gradientnbv_{occ}.png")
            plot_coverage_progression(
                coverages={"GradientNBV": coverages},
                save_path=path,
                title=f"GradientNBV Coverage (Occlusion: {occ})",
            )
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Coverage plot failed: {e}")

    # 3. 3D Trajectory
    if plot_3d_trajectory is not None:
        try:
            path = os.path.join(PLOT_DIR, f"trajectory_3d_gradientnbv_{occ}.png")
            plot_3d_trajectory(
                trail=np.array(trail),
                mesh_coordinates=mesh_coordinates,
                occlusion_type=occ,
                save_path=path,
                title=f"GradientNBV 3D Trajectory (Occlusion: {occ})",
                method_label="GradientNBV",
            )
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Trajectory plot failed: {e}")

    print("\nDone.")
