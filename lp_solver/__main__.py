import argparse
import dataclasses
import enum
import highspy
import logging
import pathlib
import timeit


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
    times: int
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
        "-n", "--times",
        type=int,
        default=1,
        help="Number of times to solve to average runtime"
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
        times=args.times,
        verbose=args.verbose,
    )


@dataclasses.dataclass(frozen=True)
class Solution:
    objective_value: float
    average_runtime: float
    status: str


def _solve(input: pathlib.Path, solver: Solver, n: int = 1) -> Solution:
    """
    Solves the problem given in input file.
    :rtype: result of solving this problem.
    """
    assert n > 0, "Number of times should be positive."
    
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

    def clear_run():
        highs.clearSolver()
        highs.run()

    total_runtime = timeit.timeit(clear_run, number=n)

    return Solution(
        objective_value=highs.getInfo().objective_function_value,
        average_runtime=total_runtime / n,
        status=highs.modelStatusToString(highs.getModelStatus()),
    )


def _format_result(r: Solution) -> str:
    return (
        "==== Result ====\n"
        f"Status                : {r.status}\n"
        f"Objective             : {r.objective_value:.10e}\n"
        f"Average Runtime (sec) : {r.average_runtime}\n"
        "================"
    )


def _main():
    args = _read_args()
    if args.verbose:
        _setup_logging()
    result = _solve(args.input, args.solver, n=args.times)
    print(_format_result(result))


if __name__ == "__main__":
    _main()
