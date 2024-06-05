import argparse
import time

from misc.benchmark._utils import setup, get_logger
from src.planner.cpp.multi.planner import MultiCoveragePathPlannerFactory
from src.planner.cpp.utils import map_to_assignment_matrix, get_assign_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--planners",
        nargs="+",
        default=["Transfer", "DARP"],
        help="mCPP planner",
    )
    parser.add_argument("-o", "--output", default="multi.log", help="Output log file")
    parser.add_argument("-n", "--num-uavs", default=8, type=int, help="Number of UAVS")
    args = parser.parse_args()
    logger = get_logger(args.output)
    for planner in args.planners:
        for map_name, _map, _uavs in setup(
            args.num_uavs, init_assign=True, init_uav_pos=True
        ):
            multi_planner = MultiCoveragePathPlannerFactory.get_planner(
                planner, _uavs, _map
            )
            start = time.time()
            success = True
            try:
                multi_planner.plan()
            except Exception:
                success = False
            end = time.time()

            assigned = map_to_assignment_matrix(_map, _uavs)
            assign_count = get_assign_count(assigned, args.num_uavs)
            logger.info(
                "%s,%s,%s,%.4f,%s,%s",
                map_name,
                planner,
                success,
                end - start,
                "|".join([f"{uav.trajectory_length:.4f}" for uav in _uavs]),
                "|".join([str(count) for count in assign_count]),
            )
