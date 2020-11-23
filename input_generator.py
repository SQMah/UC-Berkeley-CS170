import random
import math
import os

N = 10


def round_decimals_down(number: float, decimals: int = 2):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor


def random_round(number):
    """Takes an input number and randomly rounds it to 0-3 decimal places."""
    dp = random.randrange(0, 4, 1)
    return round_decimals_down(number, dp)


def get_stress_level():
    """Get a random legal value for stress level."""
    stress = 0
    # Handle the case where stress can't be 0
    while stress == 0:
        stress = random.uniform(0, 100)
    return stress


def generate_random_input(n):
    """Generates valid lines for input, and writes to a file of name n.in"""
    with open(f"{n}.in", "w") as f:
        f.write(f"{n}\n")
        f.write(f"{random_round(get_stress_level())}\n")
        for i in range(n):
            for j in range(i + 1, n):
                f.write(f"{i} {j} {random_round(random.uniform(0, 100))}" \
                        + f" {random_round(random.uniform(0, 100))}\n")


def generate_output(n):
    student_dict = {}  # Maps student to room ID
    k = random.randrange(1, n, 1)
    for i in range(0, n):
        student_dict[i] = random.randrange(0, k, 1)
    # Check that room numbers are in increasing order
    rooms = sorted(list(set([val for val in student_dict.values()])))
    room_dex = {val: i for i, val in enumerate(rooms)}
    for student in student_dict:
        student_dict[student] = room_dex[student_dict[student]]
    with open(os.path.join("samples", f"{n}.out"), "w") as f:
        for student, room in student_dict.items():
            f.write(f"{student} {room}\n")
    return student_dict, k, n


def generate_input(student_dict, k, n):
    input_dict = {}  # Map a pair tuple, to a (happiness, stress) tuple
    s_max = random_round(get_stress_level())
    MAX_STRESS = s_max / k

    room_dict = {}
    for student, room in student_dict.items():
        if room not in room_dict:
            room_dict[room] = set()
        room_dict[room].add(student)

    room_stats = {}  # Map a room ID to a (min_happiness, max_stress) tuple
    """
    The condition is that any other student in other rooms can't
    have a happiness higher than min_happiness, and a stress lower than max_stress
    """
    global_max_stress = float("-inf")
    global_min_happiness = float("inf")
    for room, students in room_dict.items():
        curr_stress = 0
        min_happiness = float("inf")
        max_stress = float("-inf")
        for i in students:
            for j in students:
                if i != j and (min(i, j), max(i, j)) not in input_dict:
                    happiness = random_round(random.uniform(10, 100))
                    min_happiness = min(happiness, min_happiness)
                    stress = random_round(random.uniform(0, MAX_STRESS - curr_stress))
                    max_stress = max(stress, max_stress)
                    curr_stress += stress
                    input_dict[(min(i, j), max(i, j))] = (happiness, stress)
        room_stats[room] = (min_happiness, max_stress)
        global_max_stress = max(max_stress, global_max_stress)
        global_min_happiness = min(min_happiness, global_min_happiness)

    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in input_dict:
                i_room = student_dict[i]
                j_room = student_dict[j]
                happiness_i, stress_i = room_stats[i_room]
                happiness_j, stress_j = room_stats[j_room]
                if len(room_dict[student_dict[i]]) == 1 or len(room_dict[student_dict[j]]) == 1:
                    # Both of the students are alone
                    happiness_max = global_min_happiness
                    stress_min = global_max_stress
                else:
                    happiness_max = min(happiness_i, happiness_j)
                    stress_min = max(stress_i, stress_j)
                happiness = random_round(random.uniform(0, happiness_max))
                stress = random_round(random.uniform(stress_min, MAX_STRESS))
                input_dict[(i, j)] = (happiness, stress)

    with open(os.path.join("samples", f"{n}.in"), "w") as f:
        f.write(f"{n}\n")
        f.write(f"{s_max}\n")
        for pair in input_dict:
            i, j = pair
            happiness, stress = input_dict[pair]
            f.write(f"{i} {j} {happiness} {stress}\n")


if __name__ == "__main__":
    generate_input(*generate_output(N))
