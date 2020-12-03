"""
Replace this solver with whatever solver you're trying to test
"""
from gurobi_solver import solve

from utils import is_valid_solution, calculate_happiness
from parser import read_input_file, read_output_file, write_output_file
import os
import argparse

if __name__ == "__main__":
    """
    First argument is folder of .in files to test on.
    Second argument is folder to write .out files to,
        files will have the same filename as the input file (minus the '.in').
    Third (optional) argument is a folder of .out files to compare the solver results against.
    """
    parser = argparse.ArgumentParser(description="Test a solver on a folder of inputs, and write the outputs")
    parser.add_argument("-i", "--input", help="Folder of .in files to test on")
    parser.add_argument("-o", "--output", default=None, help="Folder to write .out files to, files will "
                                                             "have the same filename as the input file "
                                                             "(minus the '.in').")
    parser.add_argument("-r", "--result", default=None,
                        help="Folder of .out files to compare the solver results against, "
                             "must have same filenames as the input file (minus the '.in').")
    args = parser.parse_args()
    ratio_results = []
    folder = args.input
    dir_list = os.listdir(folder)
    if args.output is not None and not os.path.isdir(args.output):
        os.mkdir(args.output)
    for file in dir_list:
        if os.path.splitext(file)[1] == ".in":
            print(f"Processing {file}")
            path = os.path.join(folder, file)
            sol_f_name = file.replace(".in", ".out")
            G, s = read_input_file(path)
            D, k = solve(G, s)
            assert is_valid_solution(D, G, s, k)
            solver_happiness = calculate_happiness(D, G)
            print("SOLVER: Total Happiness: {}".format(solver_happiness))
            if args.result is not None:
                sol_f_path = os.path.join(args.result, sol_f_name)
                if os.path.isfile(sol_f_path):
                    D_sol = read_output_file(sol_f_path, G, s)
                    sol_happiness = calculate_happiness(D_sol, G)
                    print("SOLUTION: Total Happiness: {}".format(sol_happiness))
                    ratio_results.append(solver_happiness / sol_happiness)
            print("=" * 50)
            if args.output is not None:
                write_output_file(D, os.path.join(args.output, sol_f_name))
    if ratio_results:
        print(f"SOLVER / SOLUTION optimality ratio: {sum(ratio_results) / len(ratio_results)}")
