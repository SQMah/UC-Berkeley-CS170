# Replace this solver with whatever solver you're trying to test
from greedy_solver import solve
from utils import is_valid_solution, calculate_happiness
from parse import read_input_file, read_output_file, write_output_file
import sys
import os

if __name__ == "__main__":
    assert len(sys.argv) == 2
    folder = sys.argv[1]
    ratio_results = []
    dir_list = os.listdir(folder)
    for file in dir_list:
        if os.path.splitext(file)[1] == ".in" and file == "10.in":
            print(f"Processing {file}")
            path = os.path.join(folder, file)
            sol_f_name = file.replace(".in", ".out")
            sol_f_path = os.path.join(folder, sol_f_name)
            G, s = read_input_file(path)
            D, k = solve(G, s)
            assert is_valid_solution(D, G, s, k)
            print("SOLVER: Total Happiness: {}".format(calculate_happiness(D, G)))
            D_sol = read_output_file(sol_f_path, G, s)
            print("SOLUTION: Total Happiness: {}".format(calculate_happiness(D_sol, G)))
            print("="*50)
            write_output_file(D, f'out/{sol_f_name}')