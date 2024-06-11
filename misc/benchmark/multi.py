import argparse

from misc.benchmark._utils import setup, get_logger, time_func
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
    test_cases = setup(args.num_uavs)
    for planner in args.planners:
        for map_name, _map, _uavs in test_cases:
            multi_planner = MultiCoveragePathPlannerFactory.get_planner(
                planner, _uavs, _map
            )
            plan_time, success = time_func(multi_planner.plan)

            assigned = map_to_assignment_matrix(_map, _uavs)
            assign_count = get_assign_count(assigned, len(_uavs))
            logger.info(
                "%s,%s,%s,%.4f,%s,%s",
                map_name,
                planner,
                success,
                plan_time,
                "|".join([f"{uav.trajectory_length:.4f}" for uav in _uavs]),
                "|".join([str(count) for count in assign_count]),
            )
