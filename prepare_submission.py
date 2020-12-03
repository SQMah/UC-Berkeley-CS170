import sys
import os
import json
from parser import validate_file

if __name__ == '__main__':
    outputs_dir = sys.argv[1]
    submission_name = sys.argv[2]
    submission = {}
    dirs_in_input_path = []
    for input_path in os.listdir("inputs"):
        folder_path = os.path.join(os.path.join("inputs", input_path))
        if os.path.isdir(folder_path):
            for inputs in os.listdir(folder_path):
                graph_name = inputs.split('.')[0]
                output_file = f'{outputs_dir}/{graph_name}.out'
                if os.path.exists(output_file) and validate_file(output_file):
                    output = open(f'{outputs_dir}/{graph_name}.out').read()
                    submission[inputs] = output
    with open(submission_name, 'w') as f:
        f.write(json.dumps(submission))
