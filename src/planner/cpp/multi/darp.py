"""
An implementation of DARP (Divide Areas Algorithm for Optimal Multi-Robot Coverage Path Planning)
Reference: https://github.com/alice-st/DARP
"""

import numpy as np
import cv2

from src.core.map import Map
from src.core.uav import UAV
from src.planner.cpp.multi.single import MultiAsSingleCoveragePathPlanner
from src.planner.cpp.utils import get_assign_count

np.random.seed(42069)
_EPSILON = 1e-6
_CC_VARIATION = 0.01
_RANDOM_LEVEL = 1e-4
_DIRS = ((0, 1), (0, -1), (1, 0), (-1, 0))


class DARP(MultiAsSingleCoveragePathPlanner):
    name = "DARP"

    def __init__(self, uavs: list[UAV], _map: Map, **kwargs):
        super().__init__(uavs, _map, **kwargs)

        occupied_cells = _map.occupied_cells
        self.occupied_indices = np.array(
            [(cell.r, cell.c) for cell in occupied_cells]
        ).T

        self.cost_matrix = np.stack(
            [
                _euclidean_distance((uav.r, uav.c), (_map.height, _map.width))  # type: ignore
                for uav in uavs
            ],
            dtype=np.float64,
        )

        self.connected = np.full(self.num_uavs, True, dtype=bool)

        self.thresh = 0 if self.free_cell_count % self.num_uavs == 0 else 1

        self.max_iter = kwargs.get("max_iter", 100 * 2**self.num_uavs)
        self.single_planner_name = kwargs.get("single_planner_name", "STC")

    def assign(self) -> np.ndarray:
        while self.max_iter:
            down_thresh = (self.free_cell_count - self.thresh * (self.num_uavs - 1)) / (
                self.num_uavs * self.free_cell_count
            )
            up_thresh = (self.free_cell_count + self.thresh) / (
                self.num_uavs * self.free_cell_count
            )

            success = False
            iteration = 0

            while iteration < self.max_iter:
                # print(f"Iteration: {iteration + 1}/{self.max_iter}")
                assignment_matrix = self.get_assignment()
                area_counts = get_assign_count(assignment_matrix, self.num_uavs)

                connected_multiplier = np.stack(
                    [
                        self.get_connected_multiplier(assignment_matrix, i)
                        for i in range(self.num_uavs)
                    ]
                )

                if np.all(self.connected) and np.all(
                    np.abs(area_counts - self.free_cell_count // self.num_uavs)
                    <= self.thresh
                ):
                    success = True
                    # print("Success")
                    break

                div_fair_errors = np.zeros(self.num_uavs, dtype=np.float64)
                plain_errors = area_counts.astype(np.float64) / self.free_cell_count
                for i in range(self.num_uavs):
                    if plain_errors[i] < down_thresh:
                        div_fair_errors[i] = down_thresh - plain_errors[i]
                    elif plain_errors[i] > up_thresh:
                        div_fair_errors[i] = up_thresh - plain_errors[i]

                total_neg_perc = -np.sum(div_fair_errors[div_fair_errors < 0])
                total_neg_plain_errors = np.sum(plain_errors[div_fair_errors < 0])

                correction_multiplier = np.ones(self.num_uavs, dtype=np.float64)
                for i in range(self.num_uavs):
                    if div_fair_errors[i] < 0:
                        if total_neg_plain_errors != 0:
                            if div_fair_errors[i] < 0:
                                correction_multiplier[i] = 1 + plain_errors[
                                    i
                                ] * total_neg_perc / (total_neg_plain_errors * 2)
                            else:
                                correction_multiplier[i] = 1 - plain_errors[
                                    i
                                ] * total_neg_perc / (total_neg_plain_errors * 2)

                self.cost_matrix = (
                    self.cost_matrix
                    * correction_multiplier[:, np.newaxis, np.newaxis]
                    * _random_matrix(self.cost_matrix.shape)
                    * connected_multiplier
                )

                iteration += 1

            if success:
                break
            self.max_iter >>= 1
            self.thresh += 1

        return self.get_assignment()

    def get_assignment(self) -> np.ndarray:
        assignment_mat = np.argmin(self.cost_matrix, axis=0)
        assignment_mat[*self.occupied_indices] = -1

        return assignment_mat

    def get_connected_multiplier(
        self, assignment_matrix: np.ndarray, uav_index: int
    ) -> np.ndarray:
        uav_mask = _get_uav_mask(assignment_matrix, uav_index)
        num_labels, labels_im = cv2.connectedComponents(uav_mask, connectivity=4)
        if num_labels == 2:
            self.connected[uav_index] = True
            return np.ones_like(uav_mask, dtype=np.float64)

        self.connected[uav_index] = False
        uav_start_cell = (self.uavs[uav_index].r, self.uavs[uav_index].c)
        label = labels_im[uav_start_cell]
        primary_component = np.copy(labels_im).astype(np.uint8)
        primary_component[labels_im != 0] = 0
        primary_component[labels_im == label] = 1
        other_components = np.copy(labels_im).astype(np.uint8)
        other_components[labels_im != 0] = 1
        other_components[labels_im == label] = 0

        dist1 = _normalized_euclidean_distance(primary_component, True)
        dist2 = _normalized_euclidean_distance(other_components, False)
        connected_multiplier = (dist1 - dist2).astype(np.float64)
        return (_normalize_matrix(connected_multiplier) * 2 - 1) * _CC_VARIATION + 1


def _euclidean_distance(start: tuple[int, int], shape: tuple[int, int]) -> np.ndarray:
    """
    Return Euclidean distance from start to all cells in matrix of `shape`
    """
    row, col = shape
    r, c = start
    rows = np.arange(row)
    cols = np.arange(col)
    rows, cols = np.meshgrid(rows, cols, indexing="ij")
    return np.sqrt((rows - r) ** 2 + (cols - c) ** 2)


def _normalized_euclidean_distance(matrix: np.ndarray, add_one: bool) -> np.ndarray:
    dist_robot = _normalize_matrix(
        cv2.distanceTransform(
            1 - matrix, distanceType=cv2.DIST_L2, maskSize=0, dstType=5
        )
    )
    if add_one:
        dist_robot += 1
    return dist_robot


def _normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    min_val = matrix.min()
    max_val = matrix.max()
    return (matrix - min_val) / (max_val - min_val + _EPSILON)


def _get_uav_mask(assignment_matrix: np.ndarray, label: int) -> np.ndarray:
    return (assignment_matrix == label).astype(np.uint8) * 255


def _random_matrix(shape: tuple[int, ...]) -> np.ndarray:
    return (2 * np.random.uniform(0, 1, size=shape) - 1) * _RANDOM_LEVEL + 1


if __name__ == "__main__":
    from src.core.utils import load_map_from_file

    my_map = load_map_from_file("../../../../images_filled/London_2.png")

    my_uavs = [UAV(name=f"UAV{i + 1}") for i in range(5)]

    darp = DARP(my_uavs, my_map)
    darp.plan()
