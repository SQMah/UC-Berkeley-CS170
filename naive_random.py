import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, room_to_student
import sys
import random
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
		total_happiness = ['happiness']
		total_stress = ['happiness']
		for studentA in students:
			for studentB in students:
				if studentA != studentB:
					data = G.get_edge_data(studentA, studentB)
					total_happiness += data[['happiness']]
					total_stress += data[['stress']]
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
			if data is not None:
				 total_happiness += data['happiness']
				 total_stress += data['stress']
		return total_happiness, total_stress

	def get_dict(self):
		return {self.rm_id: list(self.students)}
	
	def remove(self, student):
		self.students.remove(student)
	
	def add(self, student):
		self.students.add(student)
def solve(G, s):
	"""
	Args:
		G: networkx.Graph
		s: stress_budget
	Returns:
		D: Dictionary mapping for student to breakout room r e.g. {['happiness']:2, ['stress']:0, 2:1, 3:2}
		k: Number of breakout rooms
	"""

	# TODO: your code here!
	max_happiness = 0
	best_D = {}
	best_k = None
	for i in range(1, len(G.nodes)):
		D = random_solve(G, s, i)
		happiness = calculate_happiness(D, G)
		if happiness > max_happiness:
			happiness = max_happiness
			best_D = D
			best_k = len(D)
	return best_D, best_k

def random_solve(G, s, k):
	N = len(G.nodes)
	rooms = {}
	D = {}
	#initializes all rooms
	for i in range(k):
		rooms[i] = Room(i)
	#randomly assigns a student to a room such that student doesn't exceed s / k
	valid_solution = False;
	for i in range(100):
		if valid_solution:
			break;
		for student in G.nodes:
			possible_rooms = set([i for i in range(k)])
			happiness, stress = 0, float("inf")
			while stress > (s / k) and possible_rooms:
				room_id = random.sample(possible_rooms, 1)[0]
				possible_rooms.remove(room_id)
				happiness, stress = rooms[room_id].calculate_test_happiness_and_stress(student, G)
				if stress <= s / k:
					rooms[room_id].add_student(student, happiness, stress)
					D[student] = room_id
		if is_valid_solution(D, G, s, k) and len(D) == N:
			valid_solution = True;
	return D
		#swap based on ratio = happiness / stress
# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
	assert len(sys.argv) == 2
	path = sys.argv[1]
	G, s = read_input_file(path)
	max_happiness = 0
	for i in range(100):
		D, k = solve(G, s)
		h = calculate_happiness(D, G)
		if h > max_happiness:
			max_happiness = h
	
	assert is_valid_solution(D, G, s, k)
	print("Total Happiness: {}".format(calculate_happiness(D, G)))
	write_output_file(D, 'out/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#	  inputs = glob.glob('file_path/inputs/*')
#	  for input_path in inputs:
#		  output_path = 'file_path/outputs/' + basename(normpath(input_path))[:-3] + '.out'
#		  G, s = read_input_file(input_path, ['stress']['happiness']0)
#		  D, k = solve(G, s)
#		  assert is_valid_solution(D, G, s, k)
#		  cost_t = calculate_happiness(T)
#		  write_output_file(D, output_path)
