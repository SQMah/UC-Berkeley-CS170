import gurobipy.gurobipy as gp
from gurobipy.gurobipy import GRB
import numba
import numpy as np


@numba.njit
def index_generator(n):
    vals = []
    for i in range(n):
        for j in range(i + 1, n):
            vals.append((i, j))
    return vals


def softterm(model, where):
    if where == GRB.Callback.MIP:
        runtime = model.cbGet(GRB.Callback.RUNTIME)
        objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
        objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
        print(objbst)


def solve(G, s, early_terminate=True):
    """
    Iterates through every possible k, from 1 to len(G.nodes) and takes the maximum.
    Results calculated using gurobi.
    :param G: networkX graph
    :param s: float
        stress budget
    :param early_terminate: bool
        if true, will terminate the optimization when objective found is >= than what is currently on the leaderboard
    :return: tuple
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """
    n = len(G.nodes)
    indices = index_generator(n)
    m = gp.Model(f"Maximum happiness")
    # student_indicator[i][j] == 1, student i is in room j
    student_indicator = m.addVars(n, n, vtype=GRB.BINARY, name="student_indicator")
    # room[i] == 1 means room at index i exists.
    room_indicator = m.addVars(n, vtype=GRB.BINARY, name="room_indicator")
    room_stress = m.addVars(n, vtype=GRB.CONTINUOUS, name="room_stress")
    # Constrain that each student can only be in one room, and has to be in one room
    m.addConstrs(student_indicator.sum(i, '*') == 1 for i in range(n))
    m.addConstrs(room_stress[r] == gp.quicksum(
        G.get_edge_data(*index)["stress"] * student_indicator[index[0], r] * student_indicator[index[1], r]
        for index in indices) for r in range(n))
    # Constrain that if a room does not exist, then students can't be assigned to that room.
    for k in range(0, n):
        m.addGenConstrIndicator(room_indicator[k], False, student_indicator.sum('*', k) == 0)
    m.addConstrs((room_stress[r] * room_indicator.sum() <= s for r in range(n)), name="s_max")
    m.setObjective(
        sum(gp.quicksum(
            G.get_edge_data(*index)["happiness"] * student_indicator[index[0], r] * student_indicator[index[1], r]
            for index in indices) for r in range(n)),
        GRB.MAXIMIZE)
    if early_terminate:
        m.optimize(softterm) # noqa
    else:
        m.optimize()

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
    return allocation, k
