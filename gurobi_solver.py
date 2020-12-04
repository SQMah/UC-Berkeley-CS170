import gurobipy.gurobipy as gp
from gurobipy.gurobipy import GRB
import numba
import numpy as np
from utils import is_valid_solution, calculate_happiness
from threading import Event
import os

val = None
did_early_terminate = False
ep = None


@numba.njit
def index_generator(n):
    values = []
    for i in range(n):
        for j in range(i + 1, n):
            values.append((i, j))
    return values


def soft_term(model, where):
    global did_early_terminate
    if where == GRB.Callback.MIP:
        best_obj = model.cbGet(GRB.Callback.MIP_OBJBST)
        if ep is not None:
            diff = abs(best_obj-val)
            if diff <= ep:
                print(f"EARLY TERMINATION. Found happiness: {best_obj}, leaderboard happiness: {val}")
                did_early_terminate = True
                model.terminate()
        if best_obj >= val:
            print(f"EARLY TERMINATION. Found happiness: {best_obj}, leaderboard happiness: {val}")
            did_early_terminate = True
            model.terminate()


def solve(G, s, early_terminate=False, obj=None, did_interrupt: Event = None, prev: float = None,
          filename: str = None, output_dir: str = None, epsilon: float = None):
    """
    Iterates through every possible k, from 1 to len(G.nodes) and takes the maximum.
    Results calculated using gurobi.
    :param G: networkX graph
    :param s: float
        stress budget
    :param early_terminate: bool
        if true, will terminate the optimization when objective found is >= than what is currently on the leaderboard
    :param obj: float
        Value to terminate when exceeded.
    :param did_interrupt: Event
        Event to signify if interrupted.
    :param prev: float
        The previous happiness for an output, if one exists.
    :param filename: str
        Filename of input file without the .in
    :param output_dir: str
        Path to output directory to look for model files.
    :param epsilon: float
        When a solution the optimal +- epsilon, can terminate.
    :return: tuple
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """
    global val
    global ep
    ep = epsilon
    val = obj
    n = len(G.nodes)
    indices = index_generator(n)
    m = gp.Model(f"Maximum happiness")
    # student_indicator[i][j] == 1, student i is in room j
    student_indicator = m.addVars(n, n, vtype=GRB.BINARY, name="student_indicator")
    # room[i] == 1 means room at index i exists.
    room_indicator = m.addVars(n, vtype=GRB.BINARY, name="room_indicator")
    room_stress = m.addVars(n, vtype=GRB.CONTINUOUS, name="room_stress")
    total_happiness = m.addVar(vtype=GRB.CONTINUOUS, name="total_happiness", lb=0.0, obj=1.0) # noqa
    if obj is not None:
        total_happiness.setAttr(GRB.Attr.VarHintVal, obj)
    # Constrain that each student can only be in one room, and has to be in one room
    m.addConstrs(student_indicator.sum(i, '*') == 1 for i in range(n))
    m.addConstrs(room_stress[r] == gp.quicksum(
        G.get_edge_data(*index)["stress"] * student_indicator[index[0], r] * student_indicator[index[1], r]
        for index in indices) for r in range(n))
    # Constrain that if a room does not exist, then students can't be assigned to that room.
    m.addConstr(sum(gp.quicksum(
            G.get_edge_data(*index)["happiness"] * student_indicator[index[0], r] * student_indicator[index[1], r]
            for index in indices) for r in range(n)) == total_happiness, name="happiness_constraint")
    for k in range(0, n):
        m.addGenConstrIndicator(room_indicator[k], False, student_indicator.sum('*', k) == 0)  # noqa
    m.addConstrs((room_stress[r] * room_indicator.sum() <= s for r in range(n)), name="s_max")
    m.setObjective(total_happiness, GRB.MAXIMIZE)
    f_path = None
    file_exts = {".sol"}
    if filename is not None and output_dir is not None:
        f_path = os.path.join(output_dir, filename)
        for ext in file_exts:
            f_path_ext = f_path + ext
            if os.path.isfile(f_path_ext):
                m.update()
                print(f"Found previous model {ext} at {f_path_ext}")
                m.read(f_path_ext)
    if early_terminate:
        m.optimize(soft_term)  # noqa
    else:
        m.optimize()
    if did_interrupt is not None and m.Status == GRB.INTERRUPTED and not did_early_terminate:
        did_interrupt.set()
    try:
        # Compute results
        allocation = {}
        # Map room number to 0, 1, 2 in order
        rooms = dict()
        for s_id in range(n):
            r = np.argmax([student_indicator[(s_id, r)].X for r in range(n)])
            if r not in rooms:
                rooms[r] = len(rooms)
            allocation[s_id] = rooms[r]
        k = len(set([r for r in allocation.values()]))
        assert is_valid_solution(allocation, G, s, k)
        happiness = calculate_happiness(allocation, G)
        if prev is None or happiness >= prev:
            # Got better solution than the output, save current solution.
            if f_path is not None:
                print(f"Current solution {happiness} is better or as good as previous solution {prev}.")
                print(f"Writing model solutions.")
                for ext in file_exts:
                    f_path_ext = f_path + ext
                    m.write(f_path_ext)
            return allocation, k
        else:
            print("Did not improve on previous solution, not saving.")
        return None, None
    except AttributeError:
        print("[ERROR] Did not find a solution.")
        return None, None
    except AssertionError:
        print("[ERROR] Did not find a feasible solution.")
        return None, None
