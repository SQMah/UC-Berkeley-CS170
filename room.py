class Room:
    def __init__(self, rm_id, student=None):
        self.rm_id = rm_id
        if student is None:
            self.students = frozenset()
        else:
            self.students = frozenset([student])
        self.stress = 0
        self.happiness = 0

    def __hash__(self):
        return hash(self.students)

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
