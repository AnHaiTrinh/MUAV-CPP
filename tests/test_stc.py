import os

from src.core.cell import CellType
from src.planner.cpp.single.planner import SingleCPPPlannerFactory
from src.core.uav import UAV
from src.core.utils import load_map_from_text_file

test_suite = [
    (
        os.path.join("resources", "stc_8x8_dense_test.txt"),
        [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 3),
            (2, 3),
            (3, 3),
            (4, 3),
            (4, 4),
            (4, 5),
            (4, 6),
            (3, 6),
            (2, 6),
            (1, 6),
            (0, 6),
            (0, 7),
            (1, 7),
            (2, 7),
            (3, 7),
            (4, 7),
            (5, 7),
            (6, 7),
            (7, 7),
            (7, 6),
            (6, 6),
            (5, 6),
            (5, 5),
            (5, 4),
            (5, 3),
            (5, 2),
            (5, 1),
            (5, 0),
            (4, 0),
            (4, 1),
            (4, 2),
            (3, 2),
            (2, 2),
            (1, 2),
            (1, 1),
            (1, 0),
        ],
    ),
    (
        os.path.join("resources", "stc_8x8_sparse_test.txt"),
        [
            (0, 0),
            (0, 1),
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 1),
            (4, 2),
            (3, 2),
            (2, 2),
            (1, 2),
            (0, 2),
            (0, 3),
            (1, 3),
            (2, 3),
            (3, 3),
            (4, 3),
            (5, 3),
            (6, 3),
            (6, 4),
            (5, 4),
            (4, 4),
            (4, 5),
            (4, 6),
            (3, 6),
            (2, 6),
            (1, 6),
            (0, 6),
            (0, 7),
            (1, 7),
            (2, 7),
            (3, 7),
            (4, 7),
            (5, 7),
            (6, 7),
            (7, 7),
            (7, 6),
            (6, 6),
            (5, 6),
            (5, 5),
            (6, 5),
            (7, 5),
            (7, 4),
            (7, 3),
            (7, 2),
            (6, 2),
            (5, 2),
            (5, 1),
            (5, 0),
            (4, 0),
            (3, 0),
            (2, 0),
            (1, 0),
        ],
    ),
]


# def _assert_trajectory(_uav: UAV, want: list[tuple[int, int]]) -> None:
#     assert _uav.trajectory is not None
#     got = [(_cell.r, _cell.c) for _cell in _uav.trajectory]
#     print(got)
#
#     def _assert_circular_shift(list1: list[tuple[int, int]], list2: list[tuple[int, int]]) -> bool:
#         for i in range(len(list1)):
#             if list1[i:] + list1[:i] == list2:
#                 return True
#         return False
#
#     if _assert_circular_shift(got, want) or _assert_circular_shift(got[::-1], want):
#         print("OK")
#     else:
#         print("FAIL")
#         print(f"Got:{got}\nWant:{want}")
#
#
# for test_map_path, want_trajectory in test_suite:
#     test_map = load_map_from_text_file(test_map_path)
#     uav = UAV(r=0, c=0)
#     for row in test_map.cells:
#         for cell in row:
#             if cell.cell_type == CellType.FREE:
#                 cell.assign = uav.name
#
#     stc = SingleCPPPlannerFactory.get_planner("STC", test_map, uav)
#     stc.plan()
#     _assert_trajectory(uav, want_trajectory)

test_map = load_map_from_text_file(
    os.path.join("resources", "stc_8x8_non_homogeneous_test.txt")
)
uav = UAV(r=0, c=0)
for row in test_map.cells:
    for cell in row:
        if cell.cell_type == CellType.FREE:
            cell.assign = uav.name

stc = SingleCPPPlannerFactory.get_planner("STC", test_map, uav)
# adj_list = stc._construct_mega_graph()
# print(adj_list)
# stc.plan()
