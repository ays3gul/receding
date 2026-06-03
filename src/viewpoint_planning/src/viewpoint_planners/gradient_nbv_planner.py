import os
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple
from scipy.spatial import KDTree

from scene_representation.voxel_grid import VoxelGrid
from utils.rviz_visualizer import RvizVisualizer
from utils.py_utils import numpy_to_pose, numpy_to_pose_array
from utils.torch_utils import look_at_rotation, transform_from_rotation_translation


class GradientNBVPlanner(nn.Module):
    """
    Burusa et al. (ICRA 2024) gradient-based local NBV planner.
    Adapted to share the same VoxelGrid, mesh ground-truth and F1 metric as the
    RH-NBV planner so the two are compared under identical conditions.

    Only additions vs. the original: mesh_coordinates / mesh_tree storage,
    a ray_trace_count for parity with RH metrics, and calculate_F1 / sigma /
    occluded-recall helpers copied verbatim from rh_planner so the evaluation
    is byte-for-byte identical between planners.
    """

    def __init__(
        self,
        start_pose: np.array,
        grid_size: np.array = np.array([0.3, 0.6, 0.3]),
        voxel_size: np.array = np.array([0.003]),
        grid_center: np.array = np.array([0.5, -0.4, 1.1]),
        image_size: np.array = np.array([600, 450]),
        intrinsics: np.array = np.array(
            [
                [685.5028076171875, 0.0, 485.35955810546875],
                [0.0, 685.6409912109375, 270.7330627441406],
                [0.0, 0.0, 1.0],
            ],
        ),
        num_pts_per_ray: int = 128,
        num_features: int = 4,
        num_samples: int = 1,
        target_params: np.array = np.array([0.5, -0.4, 1.1]),
        mesh_coordinates: np.array = None,
        mesh_tree: KDTree = None,
    ) -> None:
        super(GradientNBVPlanner, self).__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        grid_size = torch.tensor(grid_size, dtype=torch.float32, device=self.device)
        voxel_size = torch.tensor(voxel_size, dtype=torch.float32, device=self.device)
        grid_center = torch.tensor(grid_center, dtype=torch.float32, device=self.device)
        self.optimization_params(start_pose, target_params)
        self.voxel_grid = VoxelGrid(
            grid_size=grid_size,
            voxel_size=voxel_size,
            grid_center=grid_center,
            width=image_size[0],
            height=image_size[1],
            fx=intrinsics[0, 0],
            fy=intrinsics[1, 1],
            cx=intrinsics[0, 2],
            cy=intrinsics[1, 2],
            num_pts_per_ray=num_pts_per_ray,
            num_features=num_features,
            target_params=self.target_params,
            device=self.device,
        )
        self.num_samples = num_samples
        self.rviz_visualizer = RvizVisualizer()

        # Parity additions with RH planner
        self.mesh_coordinates = mesh_coordinates
        self.mesh_tree = mesh_tree
        self.target_voxels = np.array(0)
        self.ray_trace_count = 0
        self.occluded_mesh_points = None
        self.last_tp = 0
        self.last_fp = 0
        self.last_fn = 0

    def optimization_params(self, start_pose, target_params):
        self.camera_params = nn.Parameter(
            torch.tensor(
                [start_pose[0], start_pose[1], start_pose[2],
                 target_params[0], target_params[1], target_params[2]],
                dtype=torch.float32, device=self.device, requires_grad=True,
            )
        )
        self.target_params = torch.tensor(
            target_params, dtype=torch.float32, device=self.device,
        )
        self.camera_bounds = torch.tensor(
            [
                [start_pose[0] - 0.2, start_pose[1] - 0.1, start_pose[2] - 0.15,
                 target_params[0] - 0.1, target_params[1] - 0.1, target_params[2] - 0.1],
                [start_pose[0] + 0.2, start_pose[1] + 0.1, start_pose[2] + 0.15,
                 target_params[0] + 0.1, target_params[1] + 0.1, target_params[2] + 0.1],
            ],
            dtype=torch.float32, device=self.device,
        )
        self.optimizer = torch.optim.AdamW(self.parameters(), lr=0.03)

    def update_voxel_grid(self, depth_image, semantics, viewpoint):
        depth_image = torch.tensor(depth_image, dtype=torch.float32, device=self.device)
        position = torch.tensor(viewpoint[:3], dtype=torch.float32, device=self.device)
        orientation = torch.tensor(viewpoint[3:], dtype=torch.float32, device=self.device)
        transform = transform_from_rotation_translation(
            orientation[None, :], position[None, :]
        )
        coverage = self.voxel_grid.insert_depth_and_semantics(
            depth_image, semantics, transform
        )
        if coverage is not None:
            coverage = coverage.cpu().numpy()
        return coverage

    def loss(self, target_pos):
        if target_pos is not None:
            self.target_params = torch.tensor(
                target_pos, dtype=torch.float32, device=self.device
            )
        else:
            self.target_params = self.camera_params[3:]
        loss, gain_image = self.voxel_grid.compute_gain(
            self.camera_params[:3], self.target_params
        )
        self.ray_trace_count += 1
        return loss, gain_image

    def next_best_view(self, target_pos=None):
        for _ in range(self.num_samples):
            self.optimizer.zero_grad()
            loss, gain_image = self.loss(target_pos)
            loss.backward()
            self.optimizer.step()
            self.camera_params.data = torch.clamp(
                self.camera_params.data, self.camera_bounds[0], self.camera_bounds[1]
            )
        viewpoint = self.get_viewpoint()
        self.rviz_visualizer.visualize_viewpoint(numpy_to_pose(viewpoint))
        self.rviz_visualizer.visualize_gain_image(gain_image)
        loss = loss.detach().cpu().numpy()
        return viewpoint, loss, self.num_samples

    def get_viewpoint(self):
        quat = look_at_rotation(self.camera_params[:3], self.camera_params[3:])
        quat = quat.detach().cpu().numpy()
        viewpoint = np.zeros(7)
        viewpoint[:3] = self.camera_params.detach().cpu().numpy()[:3]
        viewpoint[3:] = quat
        return viewpoint

    def get_occupied_points(self):
        voxel_points, sem_conf_scores, sem_class_ids = (
            self.voxel_grid.get_occupied_points()
        )
        return (
            voxel_points.cpu().numpy(),
            sem_conf_scores.cpu().numpy(),
            sem_class_ids.cpu().numpy(),
        )

    # ---- Evaluation helpers: identical logic to RHPlanner for fair comparison ----
    def calculate_F1(self, occluder_positions=None, match_threshold=None, diagnose=False):
        voxel_points, _, sem_class = self.get_occupied_points()
        self.last_tp = self.last_fp = self.last_fn = 0
        if len(voxel_points) == 0:
            self.target_voxels = np.zeros((0, 3)); return 0, 0, 0
        sem_class = np.asarray(sem_class)
        if sem_class.shape[0] == voxel_points.shape[0]:
            voxel_points = voxel_points[sem_class == 0]
        if len(voxel_points) == 0:
            self.target_voxels = np.zeros((0, 3)); return 0, 0, 0
        if occluder_positions:
            keep = np.ones(len(voxel_points), dtype=bool)
            for center, half in occluder_positions:
                in_occ = np.all(np.abs(voxel_points - np.array(center)) <= np.array(half), axis=1)
                keep &= ~in_occ
            voxel_points = voxel_points[keep]
        if len(voxel_points) == 0:
            self.target_voxels = np.zeros((0, 3)); return 0, 0, 0
        target = self.target_params.detach().cpu().numpy()
        roi_half = float(os.environ.get("ROI_HALF", 0.075))
        voxel_points = voxel_points[np.all(np.abs(voxel_points - target) <= roi_half, axis=1)]
        roi_mesh = self.mesh_coordinates[np.all(np.abs(self.mesh_coordinates - target) <= roi_half, axis=1)]
        if len(voxel_points) == 0 or len(roi_mesh) == 0:
            self.target_voxels = np.zeros((0, 3)); return 0, 0, 0
        self.target_voxels = voxel_points
        mesh_tree = KDTree(roi_mesh); voxel_tree = KDTree(voxel_points)
        if match_threshold is None:
            vs = self.voxel_grid.voxel_size
            if hasattr(vs, "detach"):
                vs = vs.detach().cpu().numpy()
            vsize = float(np.asarray(vs).reshape(-1)[0])
            match_threshold = float(os.environ.get("F1_THRESH", vsize * 4.0))
        half = match_threshold; radius = half * np.sqrt(3)
        if diagnose:
            d, _ = mesh_tree.query(voxel_points)
            pct = np.percentile(d, [0,25,50,75,100]) * 1000
            print(f"  [F1 DIAG][GradNBV] voxel->mesh nearest (mm): min={pct[0]:.1f} "
                  f"med={pct[2]:.1f} max={pct[4]:.1f} | thr={half*1000:.1f}mm | "
                  f"within thr={float(np.mean(d<=half))*100:.1f}%")
        nr_correct = 0
        for v in voxel_points:
            for idx in mesh_tree.query_ball_point(v, r=radius):
                if all(abs(v[d_]-roi_mesh[idx][d_]) <= half for d_ in range(3)):
                    nr_correct += 1; break
        nr_recalled = 0
        for c in roi_mesh:
            for idx in voxel_tree.query_ball_point(c, r=radius):
                if all(abs(voxel_points[idx][d_]-c[d_]) <= half for d_ in range(3)):
                    nr_recalled += 1; break
        self.last_tp = nr_correct
        self.last_fp = len(voxel_points) - nr_correct
        self.last_fn = len(roi_mesh) - nr_recalled
        precision = nr_correct / len(voxel_points)
        recall = nr_recalled / len(roi_mesh)
        f1 = 2*precision*recall/(precision+recall) if precision+recall>0 else 0
        return f1, recall, precision

    def visualize(self):
        voxel_points, sem_conf_scores, sem_class_ids = self.get_occupied_points()
        self.rviz_visualizer.visualize_voxels(voxel_points, sem_conf_scores, sem_class_ids)
        target = self.camera_params.detach().cpu().numpy()[3:]
        rois = np.array([[*target, 1.0, 0.0, 0.0, 0.0]])
        self.rviz_visualizer.visualize_rois(numpy_to_pose_array(rois))
        camera_bounds = self.camera_bounds.cpu().numpy()[:, :3]
        self.rviz_visualizer.visualize_camera_bounds(camera_bounds)
