import torch
import torch.nn as nn
import numpy as np
from typing import Tuple

from scene_representation.voxel_grid import VoxelGrid

from utils.rviz_visualizer import RvizVisualizer
from utils.py_utils import numpy_to_pose, numpy_to_pose_array
from utils.torch_utils import look_at_rotation, transform_from_rotation_translation


class GradientNBVPlanner(nn.Module):
    """
    Class to plan a locally optimal viewpoint using gradient-based optimization.
    (Burusa et al., ICRA 2024)
    """

    def __init__(
        self,
        start_pose: np.array,
        grid_size: np.array = np.array([0.3, 0.3, 0.3]),
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
        mesh_tree=None,
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

        # For F1 / Chamfer / Hausdorff — same interface as RHPlanner
        self.mesh_coordinates = mesh_coordinates
        self.mesh_tree = mesh_tree
        self.target_voxels = np.array(0)

        # Ray-tracing counter: GradientNBV calls compute_gain once per
        # gradient step. With num_samples=1 that is 1 call per iteration,
        # matching the Burusa paper's reported values.
        self.ray_trace_count = 0

    def optimization_params(
        self, start_pose: np.array, target_params: np.array
    ) -> None:
        self.camera_params = nn.Parameter(
            torch.tensor(
                [
                    start_pose[0],
                    start_pose[1],
                    start_pose[2],
                    target_params[0],
                    target_params[1],
                    target_params[2],
                ],
                dtype=torch.float32,
                device=self.device,
                requires_grad=True,
            )
        )
        self.target_params = torch.tensor(
            target_params,
            dtype=torch.float32,
            device=self.device,
        )
        self.camera_bounds = torch.tensor(
            [
                [
                    start_pose[0] - 0.2,
                    start_pose[1] - 0.1,
                    start_pose[2] - 0.15,
                    target_params[0] - 0.1,
                    target_params[1] - 0.1,
                    target_params[2] - 0.1,
                ],
                [
                    start_pose[0] + 0.2,
                    start_pose[1] + 0.1,
                    start_pose[2] + 0.15,
                    target_params[0] + 0.1,
                    target_params[1] + 0.1,
                    target_params[2] + 0.1,
                ],
            ],
            dtype=torch.float32,
            device=self.device,
        )
        self.optimizer = torch.optim.AdamW(self.parameters(), lr=0.03)

    def update_voxel_grid(
        self, depth_image: np.array, semantics: torch.tensor, viewpoint: np.array
    ):
        depth_image = torch.tensor(depth_image, dtype=torch.float32, device=self.device)
        position = torch.tensor(viewpoint[:3], dtype=torch.float32, device=self.device)
        orientation = torch.tensor(
            viewpoint[3:], dtype=torch.float32, device=self.device
        )
        transform = transform_from_rotation_translation(
            orientation[None, :], position[None, :]
        )
        coverage = self.voxel_grid.insert_depth_and_semantics(
            depth_image, semantics, transform
        )
        if coverage is not None:
            coverage = coverage.cpu().numpy()
        return coverage

    def loss(self, target_pos: np.array) -> torch.tensor:
        if target_pos is not None:
            self.target_params = torch.tensor(
                target_pos, dtype=torch.float32, device=self.device
            )
        else:
            self.target_params = self.camera_params[3:]
        loss, gain_image = self.voxel_grid.compute_gain(
            self.camera_params[:3], self.target_params
        )
        # Each compute_gain call = 1 ray-tracing call (Burusa et al.)
        self.ray_trace_count += 1
        return loss, gain_image

    def next_best_view(self, target_pos=None) -> Tuple[np.array, float, int]:
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

    def get_viewpoint(self) -> np.array:
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

    def calculate_F1(self):
        """Same interface as RHPlanner.calculate_F1().

        Filters to target-class voxels (class 0 = bunny) so the reconstruction
        plot and precision are not polluted by background/occluder voxels.
        """
        from scipy.spatial import KDTree
        voxel_points, _, sem_class_ids = self.get_occupied_points()

        if len(voxel_points) == 0:
            self.target_voxels = np.zeros((0, 3))
            return 0, 0, 0

        target_mask = (sem_class_ids == 0)
        target_voxels = voxel_points[target_mask]
        self.target_voxels = target_voxels

        if len(target_voxels) == 0:
            return 0, 0, 0

        mesh_tree = KDTree(self.mesh_coordinates)
        voxel_tree = KDTree(target_voxels)
        half = 0.002
        radius = half * np.sqrt(3)

        nr_correct = 0
        for voxel in target_voxels:
            for idx in mesh_tree.query_ball_point(voxel, r=radius):
                coord = self.mesh_coordinates[idx]
                if all(abs(voxel[d] - coord[d]) <= half for d in range(3)):
                    nr_correct += 1
                    break

        nr_recalled = 0
        for coord in self.mesh_coordinates:
            for idx in voxel_tree.query_ball_point(coord, r=radius):
                voxel = target_voxels[idx]
                if all(abs(voxel[d] - coord[d]) <= half for d in range(3)):
                    nr_recalled += 1
                    break

        precision = nr_correct / len(target_voxels)
        recall = nr_recalled / len(self.mesh_coordinates)
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall > 0 else 0
        )
        return f1, recall, precision

    def compute_sigma(self) -> float:
        if not isinstance(self.target_voxels, np.ndarray) or self.target_voxels.ndim < 2:
            return 0.0
        if len(self.target_voxels) == 0:
            return 0.0
        centroid = self.target_voxels.mean(axis=0)
        dists = np.linalg.norm(self.target_voxels - centroid, axis=1)
        return float(dists.mean())

    def visualize(self):
        voxel_points, sem_conf_scores, sem_class_ids = self.get_occupied_points()
        self.rviz_visualizer.visualize_voxels(
            voxel_points, sem_conf_scores, sem_class_ids
        )
        target = self.camera_params.detach().cpu().numpy()[3:]
        rois = np.array([[*target, 1.0, 0.0, 0.0, 0.0]])
        self.rviz_visualizer.visualize_rois(numpy_to_pose_array(rois))
        camera_bounds = self.camera_bounds.cpu().numpy()[:, :3]
        self.rviz_visualizer.visualize_camera_bounds(camera_bounds)
