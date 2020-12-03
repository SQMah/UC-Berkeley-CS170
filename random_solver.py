import networkx as nx
from parser import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
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
	for i in range(1, len(G.nodes)):
		D, k = random_solve(G, s, i)
		calculate_happiness(D, G)

def random_solve(G, s, k):
	N = len(G.nodes)
	rooms = {}
	D = {}
	#initializes all rooms
	for i in range(k):
		rooms[i] = Room(i)
	#randomly assigns a student to a room such that student doesn't exceed s / k
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
	print(D)
	#calculates ratios {studentA: {studentB: studentB's ratio}}
	ratios = calculate_ratios(G)
	#swaps based on ratios
	for student in G.nodes: 
		student_ratios = ratios[student]
		sorted_ratios = sorted(student_ratios.items(), key=lambda item: item[1])
		best_student = sorted_ratios[len(sorted_ratios) - 1][0]
		students_in_room = rooms[D[student]].students
		print("student", student)
		print("student_ratios", student_ratios)
		print("D", D)
		print("students_in_room", students_in_room)
		print("room id", rooms[D[student]].rm_id)
		students_in_room.remove(student)
		student_by_ratio = sorted(students_in_room, key = lambda student: student_ratios[student])
		students_in_room.add(student)
		if student_by_ratio:
			worst_student = student_by_ratio[0]
			#swap
			roomA = rooms[D[worst_student]]
			roomB = rooms[D[best_student]]
			print(roomA.students)
			print(roomB.students)
			test_swap(D, rooms, worst_student, best_student, s, k, G)
	return D
		#swap based on ratio = happiness / stress

def test_swap(D, rooms, A, B, s, k, G):
	roomA_id = D[A]
	roomB_id = D[B]
	roomA = rooms[D[A]]
	roomB = rooms[D[B]]
	beforeAH, beforeAS = roomA.happiness, roomA.stress
	beforeBH, beforeBS = roomB.happiness, roomB.stress
	roomA.remove(A)
	roomB.remove(B)
	afterAH, afterAS = roomA.calculate_test_happiness_and_stress(B, G)
	afterBH, afterBS = roomB.calculate_test_happiness_and_stress(A, G)
	#make the swap
	if afterAH + afterBH > beforeAH + beforeBH:
		if afterBS < s / k and afterAS < s / k:
			roomA.add_student(B, afterAH, afterAS)
			roomB.add_student(A, afterBH, afterBS)
			D[A] = roomB_id
			D[B] = roomA_id
	#don't make the swap
	else:
		roomA.add(A)
		roomB.add(B)
def calculate_ratios(G):
	ratios = {}
	for studentA in G.nodes:
		studentA_ratios = {}
		for studentB in G.nodes:
			if studentA != studentB:
				data = G.get_edge_data(studentA, studentB)
				happiness, stress = data['happiness'], data['stress']
				if stress == 0:
					ratio = float("inf")
				else:
					ratio = happiness / stress
				studentA_ratios[studentB] = ratio
		ratios[studentA] = studentA_ratios;
	return ratios
# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
	assert len(sys.argv) == 2
	path = sys.argv[1]
	G, s = read_input_file(path)
	D, k = solve(G, s)
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
