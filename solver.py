import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
import sys
from queue import PriorityQueue
from multiprocessing import Pool, cpu_count
from functools import partialmethod

class Room:
	def __init__(self, rm_id):
		self.rm_id = rm_id
		self.students = set()
		self.stress = 0
		self.happiness = 0

	def get_rm_id(self):
		return self.rm_id

	def add_student(self, new_student, happiness, stress):
		self.students.add(new_student)
		self.happiness = happiness
		self.stress = stress

	'''def calculate_happiness_and_stress(self, G):
		total_happiness = 0
		total_stress = 0
		for studentA in students:
			for studentB in students:
				if studentA != studentB:
					data = G.get_edge_data(studentA, studentB)
					total_happiness += data[0]
					total_stress += data[1]
		return total_happiness, total_stress;
	'''

	def get_happiness(self):
		return self.happiness

	def get_stress(self):
		return self.stress

	def calculate_test_happiness_and_stress(self, test_student, G):
		total_happiness = self.happiness
		total_stress = self.stress
		for student in self.students:
			data = G.get_edge_data(student, test_student)
			total_happiness += data[0]
			total_stress += data[1]
		return total_happiness, total_stress

	def get_dict(self):
		return {self.rm_id: list(self.students)}

def solver_helper(G, s: float, rs: set, ra: dict):
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
	k = len(ra)
	q = PriorityQueue()
	with Pool(cpu_count()) as p:
		res = p.map([])
	max_happiness = float("-inf")
	room_stress = None
	best_student = None  # student, test happiness, test stress
	best_room = None
	for student in rs:
		for room_num in ra:
			room = ra[room_num]
			happiness, stress = room.calculate_test_happiness_and_stress(student, G)
			if stress <= (s / k) and (
					happiness > max_happiness or (happiness == max_happiness and stress < room_stress)):
				max_happiness = happiness
				room_stress = stress
				best_student = student
				best_room = room_num
	if best_student is not None:
		ra[best_room].add_student(best_student, max_happiness, room_stress)
		result = solver_helper(G, s, rs.copy(), ra.copy())

# continue calling algorithm
# else backtrack


def solve(G, s):
	"""
	Args:
		G: networkx.Graph
		s: stress_budget
	Returns:
		D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
		k: Number of breakout rooms
	"""
	rooms = {}
	# Put student in best breakout room that maximizes happiness
	remaining_students = set(G.nodes)
	total_data_students = {}
	for studentA in G.nodes:
		for studentB in G.nodes:
			if studentA != studentB:
				data = G.get_edge_data(studentA, studentB)
				happiness, stress = data[0], data[1]
				if studentA not in total_data_students:
					total_data_students[studentA] = [0, 0]
				total_data_students[studentA][0] += happiness
				total_data_students[studentA][1] += stress
	min_stress_student = min(total_data_students, key=lambda x: total_data_students[x][1])
	rooms[0] = Room(0)
	rooms[0].add_student(min_stress_student, 0, 0)
	remaining_students.remove(min_stress_student)
	return solver_helper(G, s, remaining_students, rooms)


if __name__ == "__main__":
	assert len(sys.argv) == 2
	path = sys.argv[1]
	G, s = read_input_file(path)

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G, s = read_input_file(path)
#     D, k = solve(G, s)
#     assert is_valid_solution(D, G, s, k)
#     print("Total Happiness: {}".format(calculate_happiness(D, G)))
#     write_output_file(D, 'out/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('file_path/inputs/*')
#     for input_path in inputs:
#         output_path = 'file_path/outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G, s = read_input_file(input_path, 100)
#         D, k = solve(G, s)
#         assert is_valid_solution(D, G, s, k)
#         cost_t = calculate_happiness(T)
#         write_output_file(D, output_path)
