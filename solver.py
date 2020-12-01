import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, convert_dictionary
import sys
import glob
from os.path import basename, normpath

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
		total_happiness = "happiness"
		total_stress = "happiness"
		for studentA in students:
			for studentB in students:
				if studentA != studentB:
					data = G.get_edge_data(studentA, studentB)
					total_happiness += data["happiness"]
					total_stress += data["stress"]
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
			total_happiness += data["happiness"]
			total_stress += data["stress"]
		return total_happiness, total_stress

	def get_dict(self):
		return {self.rm_id: list(self.students)}


def solve(G, s):
	"""
	Args:
		G: networkx.Graph
		s: stress_budget
	Returns:
		D: Dictionary mapping for student to breakout room r e.g. {"happiness":2, "stress":0, 2:1, 3:2}
		k: Number of breakout rooms
	"""

	# TODO: your code here!
	N = len(G.nodes)
	edges = G.edges
	#Put student in best breakout room that maximizes happiness
	total_data_students = {}
	for studentA in G.nodes:
		for studentB in G.nodes:
			if studentA != studentB:
				data = G.get_edge_data(studentA, studentB);
				happiness, stress = data["happiness"], data["stress"]
				if studentA not in total_data_students:
					total_data_students[studentA] = {"happiness": 0, "stress": 0}
				total_data_students[studentA]["happiness"] += happiness
				total_data_students[studentA]["stress"] += stress
	total_data_students = dict(sorted(total_data_students.items(), key = lambda x: x[1]["stress"]))
	best_D = {i : i for i in range(N)}
	best_D_happiness = 0
	best_k = N
	for k in range(1, N):
		b = s / k
		rooms = {}
		no_valid_solution = False
		remaining_students = set(G.nodes)
		min_stress = iter(total_data_students)
		for i in range(k):
			min_stress_student = next(min_stress)
			rooms[i] = Room(i)
			rooms[i].add_student(min_stress_student, 0, 0)
			remaining_students.remove(min_stress_student)
		for student in remaining_students:
			max_happiness = float("-inf")
			room_stress = None
			best_room = None
			for room_num in rooms:
				room = rooms[room_num]
				happiness, stress = room.calculate_test_happiness_and_stress(student, G)
				if stress <= (s / k) and (happiness > max_happiness or (happiness == max_happiness and stress < room_stress)): 
					max_happiness = happiness;
					room_stress = stress 
					best_room = room_num
			if best_room != None:
				rooms[best_room].add_student(student, max_happiness, room_stress)
			else:
				no_valid_solution = True;
				break;
		if not no_valid_solution:
			final_rooms = {}
			for room in rooms:
				final_rooms[room] = rooms[room].students
			D = convert_dictionary(final_rooms)
			happiness = calculate_happiness(D, G) 
			if happiness > best_D_happiness:
				best_D_happiness = happiness
				best_D = D
				best_k = k
	return best_D, best_k
	#continue calling algorithm
	#else backtrack

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#	  assert len(sys.argv) == 2
#	  path = sys.argv["stress"]
#	  G, s = read_input_file(path)
#	  D, k = solve(G, s)
#	  assert is_valid_solution(D, G, s, k)
#	  print("Total Happiness: {}".format(calculate_happiness(D, G)))
#	  write_output_file(D, 'out/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
if __name__ == '__main__':
	path = sys.argv[1]
	inputs = glob.glob(path + "/*")
	for input_path in inputs:
		output_path = path + "/" + basename(normpath(input_path))[:-3] + '.out'
		G, s = read_input_file(input_path)
		D, k = solve(G, s)
		assert is_valid_solution(D, G, s, k)
		cost_t = calculate_happiness(D, G)
		write_output_file(D, output_path)
