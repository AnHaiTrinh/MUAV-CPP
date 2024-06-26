import argparse

from misc.benchmark._utils import setup, get_logger, time_func
from src.planner.cpp.single.planner import SingleCoveragePathPlannerFactory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--algos",
        nargs="+",
        default=["kruskal", "dfs"],
        help="MST Algorithm",
    )
    parser.add_argument("-o", "--output", default="single.log", help="Output log file")
    args = parser.parse_args()
    logger = get_logger(args.output)
    test_cases = setup(1, init_assign=True, init_uav_pos=True)
    for algo in args.algos:
        for map_name, _map, _uavs in test_cases:
            uav = _uavs[0]
            planner = SingleCoveragePathPlannerFactory.get_planner(
                "STC", _map, uav, mst_algo=algo
            )
            coverage_time, success = time_func(planner.plan)

            logger.info(
                "%s,%s,%s,%.4f,%.4f",
                map_name,
                algo,
                success,
                coverage_time,
                uav.trajectory_length,
            )
