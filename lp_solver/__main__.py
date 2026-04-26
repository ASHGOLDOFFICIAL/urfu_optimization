import time

import argparse
import dataclasses
import enum
import highspy
import logging
import pathlib


def _setup_logging() -> None:
    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.DEBUG,
    )


class Solver(enum.StrEnum):
    SIMPLEX_PRIMAL = 'primal'
    SIMPLEX_DUAL = 'dual'
    INTERIOR_POINT = 'ip'


@dataclasses.dataclass(frozen=True)
class Arguments:
    input: pathlib.Path
    solver: Solver
    verbose: bool


def _read_args() -> Arguments:
    """
    Reads command line arguments.
    :rtype: argparse.Namespace CLI arguments.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-i", "--input",
        type=pathlib.Path,
        required=True,
        help="Input file"
    )
    ap.add_argument(
        "-s", "--solver",
        type=Solver,
        required=True,
        help="Solver to use"
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        required=False,
        help="Enable verbose output"
    )
    args = ap.parse_args()
    return Arguments(
        input=args.input,
        solver=args.solver,
        verbose=args.verbose,
    )


@dataclasses.dataclass(frozen=True)
class Solution:
    objective_value: float
    runtime: float
    status: str


def _solve(input: pathlib.Path, solver: Solver) -> Solution:
    """
    Solves the problem given in input file.
    :rtype: result of solving this problem.
    """
    filename = str(input)
    highs = highspy.Highs()
    highs.setOptionValue("output_flag", False)

    status = highs.readModel(filename)
    logging.debug(f'Reading model file {filename} returns a status of {status}')

    # https://ergo-code.github.io/HiGHS/dev/options/definitions/
    match solver:
        case Solver.SIMPLEX_PRIMAL:
            highs.setOptionValue("solver", 'simplex')
            highs.setOptionValue("simplex_strategy", 4)
        case Solver.SIMPLEX_DUAL:
            highs.setOptionValue("solver", 'simplex')
            highs.setOptionValue("simplex_strategy", 1)
        case Solver.INTERIOR_POINT:
            highs.setOptionValue('solver', 'ipm')

    start_time = time.process_time()
    highs.run()
    end_time = time.process_time()

    return Solution(
        objective_value=highs.getInfo().objective_function_value,
        runtime=end_time - start_time,
        status=highs.modelStatusToString(highs.getModelStatus()),
    )


def _format_result(r: Solution) -> str:
    return (
        "=== Result ===\n"
        f"Status         : {r.status}\n"
        f"Objective      : {r.objective_value}\n"
        f"Runtime (sec)  : {r.runtime}\n"
        "==============="
    )


def _main():
    args = _read_args()
    if args.verbose:
        _setup_logging()
    result = _solve(args.input, args.solver)
    print(_format_result(result))


if __name__ == "__main__":
    _main()
