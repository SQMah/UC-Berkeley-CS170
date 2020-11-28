import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
import sys
import heapq
from functools import partial
from typing import Dict


class PriorityQueue:
    """
	  Implements a priority queue data structure. Each inserted item
	  has a priority associated with it and the client is usually interested
	  in quick retrieval of the lowest-priority item in the queue. This
	  data structure allows O(1) access to the lowest-priority item.
	"""

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)


class PriorityQueueWithFunction(PriorityQueue):
    """
	Implements a priority queue with the same push/pop signature of the
	Queue and the Stack classes. This is designed for drop-in replacement for
	those two classes. The caller has to provide a priority function, which
	extracts each item's priority.
	"""

    def __init__(self, priorityFunction):
        """priorityFunction (item) -> priority"""
        self.priorityFunction = priorityFunction  # store the priority function
        PriorityQueue.__init__(self)  # super-class initializer

    def push(self, item):
        """Adds an item to the queue with priority from the priority function"""
        PriorityQueue.push(self, item, self.priorityFunction(item))


class Room:
    def __init__(self, rm_id, student=None):
        self.rm_id = rm_id
        if student is None:
            self.students = frozenset()
        else:
            self.students = frozenset([student])
        self.stress = 0
        self.happiness = 0

    def copy(self):
        new_room = Room(self.rm_id)
        new_room.students = self.students
        new_room.stress = self.stress
        new_room.happiness = self.happiness
        return new_room

    def copy_and_add_student(self, new_student, happiness, stress):
        """Returns a new copy of room."""
        new_room = Room(self.rm_id)
        new_room.students = frozenset(list(self.students) + [new_student])
        new_room.stress = self.stress + stress
        new_room.happiness = self.happiness + happiness
        return new_room

    def get_rm_id(self):
        return self.rm_id

    def get_happiness(self):
        return self.happiness

    def get_stress(self):
        return self.stress

    def calculate_test_happiness_and_stress(self, test_student, G):
        total_happiness = self.happiness
        total_stress = self.stress
        for student in self.students:
            data = G.get_edge_data(student, test_student)
            total_happiness += data["happiness"]
            total_stress += data["stress"]
        return total_happiness, total_stress

    def get_dict(self):
        return {self.rm_id: list(self.students)}

    def __repr__(self):
        return str(self.students)


def get_priority_for_student(G, s: float, ra: dict, can_add_room: bool, student: int):
    """
	:param G:
		Graph
	:param s:
		Stress budget
	:param student:
		Student id
	:param can_add_room:
		Whether or not to populate non_permissible list, don't need to check if rooms can't be added.
	:param ra:
		Dict of room assigments
	:return list[tuple]:
		[(-happiness, happiness, stress, room, student_ID)]
		Need -happiness in the front so priority queue gets highest permissible happiness first.

		Non permissible items have the order
		[(-stress, happiness, stress, room, student_ID)]
		Because we want to take the student with the highest pairwise stress and put them in their own room.
	"""

    permissible = []
    non_permissible = []
    k = len(ra)
    if k != 0:
        for room_num in ra:
            room = ra[room_num]
            happiness, stress = room.calculate_test_happiness_and_stress(student, G)
            if stress <= (s / k):
                permissible.append((-happiness, happiness, stress, room_num, student))
            if can_add_room:
                non_permissible.append((-stress, happiness, stress, room_num, student))
    else:
        total_data_students = {}
        for studentA in G.nodes:
            for studentB in G.nodes:
                if studentA != studentB:
                    data = G.get_edge_data(studentA, studentB)
                    happiness, stress = data["happiness"], data["stress"]
                    if studentA not in total_data_students:
                        total_data_students[studentA] = [0, 0]
                    total_data_students[studentA][0] += happiness
                    total_data_students[studentA][1] += stress
        for student in total_data_students:
            happiness, stress = total_data_students[student]
            non_permissible.append((-stress, happiness, stress, 0, student))
    return permissible, non_permissible


def can_add_extra_room(ra: Dict[int, Room], s: float) -> bool:
    """Returns if the current room assignment supports extra rooms.
	:param ra:
		Dictionary of room assigments ID to Room object
	:param s:
		Stress budget
	:return bool:
		Whether or not the current room assigments support adding an extra room.
	"""
    if not ra:
        return True
    k = len(ra)
    return all([ra[room_num].get_stress() <= s / (k + 1) for room_num in ra])


def solver_helper(G, s: float, rs: set, ra: dict, visited):
    """
	Solver helper for recursive calls
	Args:
		G: networkX graph
		s: stress_budget
		rs: set of remaining students
		ra: room assignments
	Returns:
		???
	"""
    # print(ra)
    ra_to_set = frozenset(map(lambda x: x.students, list(ra.values())))
    visited.add(ra_to_set)
    if not rs:
        # If no remaining students, we've reached the optimal assigment
        return ra
    permissible_q = PriorityQueueWithFunction(lambda x: x[0])
    non_permissible_q = PriorityQueueWithFunction(lambda x: x[0])
    can_add_room = can_add_extra_room(ra, s)
    partial_get_priority_for_student = partial(get_priority_for_student, G, s, ra, can_add_room)
    results = list(map(partial_get_priority_for_student, rs))
    for res in results:
        permissible, non_permissible = res
        for item in permissible:
            permissible_q.push(item)
        for item in non_permissible:
            non_permissible_q.push(item)
    while not permissible_q.isEmpty():
        # There is some valid assignment
        _, happiness, stress, room_num, student = permissible_q.pop()
        new_rs = rs.copy()
        new_rs.remove(student)
        new_ra: Dict[int, Room] = {num: ra[num].copy() for num in ra if num != room_num}
        new_ra[room_num] = ra[room_num].copy_and_add_student(student, happiness, stress)
        new_ra_to_set = frozenset(map(lambda x: x.students, list(new_ra.values())))
        if new_ra_to_set not in visited:
            res = solver_helper(G, s, new_rs, new_ra, visited)
            if res is not None:
                return res
    while not non_permissible_q.isEmpty():
        # Create new room
        _, happiness, stress, room_num, student = non_permissible_q.pop()
        new_rs = rs.copy()
        new_rs.remove(student)
        new_ra: Dict[int, Room] = {num: ra[num].copy() for num in ra}
        new_ra[len(ra)] = Room(len(ra), student)
        new_ra_to_set = frozenset(map(lambda x: x.students, list(new_ra.values())))
        if new_ra_to_set not in visited:
            res = solver_helper(G, s, new_rs, new_ra, visited)
            if res is not None:
                return res
    # Signals caller to try next option, or backtrack
    return None


# continue calling algorithm
# else backtrack


def solve(G, s):
    """
		G: networkx.Graph
		s: stress_budget
	Returns:
		D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
		k: Number of breakout rooms
	"""
    rooms = {}
    visited = set()
    # Put student in best breakout room that maximizes happiness
    remaining_students = set(G.nodes)
    res = solver_helper(G, s, remaining_students, rooms, visited)
    D = {}
    for room_num in res:
        for student in res[room_num].students:
            D[student] = room_num
    print(res)
    return D, len(res)


if __name__ == "__main__":
    assert len(sys.argv) == 2
    path = sys.argv[1]
    G, s = read_input_file(path)
    D, k = solve(G, s)
    assert is_valid_solution(D, G, s, k)
    print("Total Happiness: {}".format(calculate_happiness(D, G)))
    write_output_file(D, 'out/test.out')

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#	 inputs = glob.glob('file_path/inputs/*')
#	 for input_path in inputs:
#		 output_path = 'file_path/outputs/' + basename(normpath(input_path))[:-3] + '.out'
#		 G, s = read_input_file(input_path, 100)
#		 D, k = solve(G, s)
#		 assert is_valid_solution(D, G, s, k)
#		 cost_t = calculate_happiness(T)
#		 write_output_file(D, output_path)
