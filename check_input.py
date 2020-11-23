from input_generator import generate_input, generate_output
from parse import read_output_file, validate_file, read_input_file
from utils import calculate_stress_for_room, calculate_happiness_for_room, calculate_happiness, room_to_student

if __name__ == "__main__":
    N = 50
    generate_input(*generate_output(N))
    IN_FILE = f"{N}.in"
    OUT_FILE = f"{N}.out"
    if not validate_file(IN_FILE):
        raise ValueError("Invalid input file!")
    G, stress_budget = read_input_file(IN_FILE)
    # Read output file already checks if it is valid
    D = read_output_file(OUT_FILE, G, stress_budget)
    print(f"TOTAL HAPPINESS: {calculate_happiness(D, G)}")
    print(f"STRESS BUDGET: {stress_budget}")
    print(D)
    room_map = room_to_student(D)
    print(room_map)
    for room in room_map:
        students = room_map[room]
        print(f"ROOM: {room}, students: {students}, happiness: {calculate_happiness_for_room(students, G)}, "
              f"stress: {calculate_stress_for_room(students, G)}")


