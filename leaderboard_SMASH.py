from gurobi_solver import solve
from utils import is_valid_solution, calculate_happiness
from parser import read_input_file, read_output_file, write_output_file
import os
import argparse
import json
from git import Repo

current_progress_f_path = None
repo = Repo(os.path.join(os.getcwd(), ".git"))
origin = repo.remote(name='origin')

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Test a solver on a folder of inputs, and write the outputs")
        parser.add_argument("-i", "--input", help="Folder of .in files.")
        parser.add_argument("-o", "--output", default=None, help="Folder of .out files.")
        args = parser.parse_args()
        folder = args.input
        assert os.path.isdir(args.input)
        assert os.path.isdir(args.output)
        with open('leaderboard.json', 'r') as f:
            leaderboard = json.load(f)
        dir_list = os.listdir(folder)
        for file in dir_list:
            if os.path.splitext(file)[1] == ".in":
                origin.pull()
                print("=" * 50)
                input_f_path = os.path.join(args.input, file)
                output_f_name = file.replace(".in", ".out")
                output_f_path = os.path.join(args.output, output_f_name)
                partial_f_path = output_f_path.replace(".out", ".inprogress")
                partial_f_name = os.path.basename(partial_f_path)
                G, s = read_input_file(input_f_path)
                if os.path.isfile(partial_f_path):
                    print(f"Skipping processing {file}, partial output found")
                    continue
                if os.path.isfile(output_f_path):
                    D_out = read_output_file(output_f_path, G, s)
                    output_happiness = calculate_happiness(D_out, G)
                    if output_happiness >= leaderboard[file]:
                        print(f"Skipping processing {file}, output happiness: {output_happiness}, "
                              f"leaderboard happiness: {leaderboard[file]}")
                        continue
                    else:
                        print(f"Processing {file}, output happiness: {output_happiness} "
                              f"lower than leaderboard happiness: {leaderboard[file]}")
                else:
                    print(f"Processing {file}, because output not found.")
                with open(partial_f_path, 'w') as f:
                    f.write('b r u h\n')
                repo.git.add(partial_f_path)
                repo.index.commit(f"Add {partial_f_name}")
                origin.push()
                current_progress_f_path = current_progress_f_path
                print(f"[PUSH] {partial_f_name} in progress to repo.")
                D, k = solve(G, s, early_terminate=True, obj=leaderboard[file])
                assert is_valid_solution(D, G, s, k)
                os.remove(partial_f_path)
                write_output_file(D, output_f_path)
                repo.index.commit(f"Found solution for {file}")
                origin.push()
    except KeyboardInterrupt:
        if current_progress_f_path is not None and os.path.isfile(current_progress_f_path):
            print("Exiting...")
            os.remove(current_progress_f_path)
            print(f"Removing in progress file at {current_progress_f_path}")
            repo.commit(f"Remove progress file {os.path.basename(current_progress_f_path)}")
            origin.push()
            print(f"[PUSH] Removed {os.path.basename(current_progress_f_path)} in progress to repo.")
