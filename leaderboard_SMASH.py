from gurobi_solver import solve
from utils import calculate_happiness
from parser import read_input_file, read_output_file, write_output_file
import os
import argparse
import json
from git import Repo
from threading import Event


CONTINUE_ON_INTERRUPT = False
TIMEOUT_S = float("inf")
EPSILON = 10e-4



current_progress_f_path = None


def repo_add(file_path):
    repo = Repo(os.path.join(os.getcwd(), ".git"))
    repo.git.add(file_path)
    print(f"[GIT] add {file_path}")


def repo_rm(file_path):
    repo = Repo(os.path.join(os.getcwd(), ".git"))
    repo.git.rm(file_path)
    print(f"[GIT] rm {file_path}")


def repo_pull():
    repo = Repo(os.path.join(os.getcwd(), ".git"))
    origin = repo.remote(name='origin')
    origin.pull()
    print(f"[GIT] pull")


def repo_commit(msg):
    repo = Repo(os.path.join(os.getcwd(), ".git"))
    repo.index.commit(msg)
    print(f"[GIT] {msg}")


def repo_push():
    repo = Repo(os.path.join(os.getcwd(), ".git"))
    origin = repo.remote(name='origin')
    origin.push()
    print("[GIT] Pushed to repo.")


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
        interrupt_event = Event()
        for file in dir_list:
            if os.path.splitext(file)[1] == ".in" and "large-107" in file:
                print("=" * 50)
                input_f_path = os.path.join(args.input, file)
                output_f_name = file.replace(".in", ".out")
                output_f_path = os.path.join(args.output, output_f_name)
                partial_f_path = output_f_path.replace(".out", ".inprogress")
                partial_f_name = os.path.basename(partial_f_path)
                output_happiness = float("-inf")
                G, s = read_input_file(input_f_path)
                if os.path.isfile(output_f_path):
                    D_out = read_output_file(output_f_path, G, s)
                    output_happiness = max(output_happiness, calculate_happiness(D_out, G))
                    diff = leaderboard[file] - output_happiness
                    if diff <= EPSILON:
                        print(f"Skipping processing {file}, output happiness: {output_happiness}, "
                              f"leaderboard happiness: {leaderboard[file]}")
                        continue
                    else:
                        repo_pull()
                        D_out = read_output_file(output_f_path, G, s)
                        output_happiness = max(output_happiness, calculate_happiness(D_out, G))
                        diff = abs(output_happiness - leaderboard[file])
                        if diff <= EPSILON:
                            print(f"Skipping processing {file}, output happiness: {output_happiness}, "
                                  f"leaderboard happiness: {leaderboard[file]}")
                            continue
                        else:
                            print(f"Processing {file}, output happiness: {output_happiness} "
                                  f"lower than leaderboard happiness: {leaderboard[file]}")
                else:
                    repo_pull()
                    if os.path.isfile(output_f_path):
                        D_out = read_output_file(output_f_path, G, s)
                        output_happiness = max(output_happiness, calculate_happiness(D_out, G))
                        diff = abs(output_happiness - leaderboard[file])
                        if diff <= EPSILON:
                            print(f"Skipping processing {file}, output happiness: {output_happiness}, "
                                  f"leaderboard happiness: {leaderboard[file]}")
                            continue
                        else:
                            print(f"Processing {file}, output happiness: {output_happiness} "
                                  f"lower than leaderboard happiness: {leaderboard[file]}")
                    else:
                        print(f"Processing {file}, because output not found.")
                repo_pull()
                if os.path.isfile(partial_f_path):
                    print(f"Skipping processing {file}, partial output found")
                    continue

                with open(partial_f_path, 'w') as f:
                    f.write('b r u h\n')
                repo_add(partial_f_path)
                repo_commit(f"{file} in progress")
                repo_push()
                current_progress_f_path = current_progress_f_path
                bare_filename = file.replace(".in", "")
                D, k = solve(G, s, early_terminate=True, obj=leaderboard[file], did_interrupt=interrupt_event,
                             prev=output_happiness, filename=bare_filename, output_dir=args.output, epsilon=EPSILON)
                did_improve = False
                if D is not None and k is not None:
                    solver_happiness = calculate_happiness(D, G)
                    print("SOLVER: Total Happiness: {}".format(solver_happiness))
                    write_output_file(D, output_f_path)
                    repo_add(output_f_path)
                    model_sol_path = os.path.join(args.output, bare_filename + ".sol")
                    if os.path.isfile(model_sol_path):
                        repo_add(model_sol_path)
                os.remove(partial_f_path)
                repo_rm(partial_f_path)
                if D is not None and k is not None:
                    repo_commit(f"Found better solution for {file}")
                else:
                    repo_commit(f"Remove .inprogress for {file}")
                repo_push()
                if interrupt_event.isSet():
                    interrupt_event.clear()
                    if not CONTINUE_ON_INTERRUPT:
                        break
    except KeyboardInterrupt:
        if current_progress_f_path is not None and os.path.isfile(current_progress_f_path):
            print("Exiting...")
            os.remove(current_progress_f_path)
            repo_rm(current_progress_f_path)
            repo_commit(f"Remove progress file {os.path.basename(current_progress_f_path)}")
            repo_push()
