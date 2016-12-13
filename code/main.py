"""
This program finds an optimal (not THE optimal) seating arrangement for a class of students.

Author: Spencer Tryba
2016-12-03
"""

# kivy.require('1.9.1')
from random import randint
from math import sqrt
import csv

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.properties import NumericProperty

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox


class SeatingChartApp(App):
    def build(self):
        return MainScreen()


class MainScreen(BoxLayout):
    pass


class CustomScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(CustomScreenManager, self).__init__(**kwargs)    # Call the superclass __init__()
        self.students = {}  # Start a dictionary for all of the students

    def save_student(self):
        name = self.ids.student_screen.ids.student_name.text
        board = self.ids.student_screen.ids.close_to_board
        reading_value = self.ids.student_screen.ids.reading.value
        writing_value = self.ids.student_screen.ids.writing.value
        math_value = self.ids.student_screen.ids.math.value
        science_value = self.ids.student_screen.ids.science.value
        chattiness_value = self.ids.student_screen.ids.chattiness.value
        focus_value = self.ids.student_screen.ids.focus.value
        safety_value = self.ids.student_screen.ids.safety.value

        if name in self.students:
            # Fix and update this section to use the get_att() and set_att() functions with a list
            self.students[name].close_to_board = board
            self.students[name].reading = reading_value
            self.students[name].writing = writing_value
            self.students[name].math = math_value
            self.students[name].science = science_value
            self.students[name].chattiness = chattiness_value
            self.students[name].focus = focus_value
            self.students[name].safety = safety_value

        else:
            # Fix and update this section to use the get_att() and set_att() functions with a list
            student = Student1()
            student.name = name
            student.close_to_board = board
            student.reading = reading_value
            student.writing = writing_value
            student.math = math_value
            student.science = science_value
            student.chattiness = chattiness_value
            student.focus = focus_value
            student.safety = safety_value

            self.add_widget(student)    # Add the student screen to the screen manager
            self.students[student.name] = student   # Add the student screen to the dictionary of students


class SeatingChartScreen(Screen):
    """
    This class is a sub-class of the BoxLayout class. The first box is for buttons and the second
    box is for the FloatLayout that holds all of the desk objects.
    """

    def __init__(self, **kwargs):
        self.max_mutations = 3000  # The max number of mutations
        super(SeatingChartScreen, self).__init__(**kwargs)    # Call the superclass __init__()

        self.energy = 0.0           # Initial energy of the seating chart, lower is better
        self.students = {}          # Empty dictionary to hold the student label objects
        self.desks = []             # Empty list to hold the desk scatter objects
        self.mutation = 0           # The current mutation number, used for animating the name label swapping

        # self.drop_down = DropDown()
        # btn = Button(text="New Student", size_hint_y=None, height=40)
        # btn.bind(on_release=lambda btn: self.drop_down.select(btn.text))
        # self.drop_down.add_widget(btn)
        # self.ids.student_button.bind(on_release=self.drop_down.open)
        # self.drop_down.bind(on_select=lambda instance, x: setattr(self.ids.student_button, 'text', x))

        with open('student_data.csv', 'r') as file:
            reader = csv.reader(file)
            student_data = list(reader)

        for i in range(len(student_data) - 1):  # For each student...
            # make a student object and add it to the list of student Labels
            student = Student(*student_data[i + 1]) # The [i + 1] drops the headers in the data file
            student.id = student.name   # Assign the student an ID
            student.text = student.name + "\n" # Assign the student some text to display

            self.students[student.name] = student   # Add the student object to the dictionary

            desk = Desk()                       # Make a desk object (a Scatter)
            desk.id = str(i)                    # Add an ID to the desk
            desk.student = student              # Assign the student to the desk

            desk.add_widget(student)            # Add the student label to the desk
            self.desks.append(desk)             # Add the desk to the list of desks

            self.add_widget(desk)  # Add the desk widget to the seating chart widget

    def swap_students(self, desk_1, desk_2):  # Swap the positions of the two students
        # Swap the students
        desk_1.student, desk_2.student = desk_2.student, desk_1.student

        desk_1.remove_widget(desk_2.student)   # Remove the old student's name from the desk
        desk_2.remove_widget(desk_1.student)   # Remove the old student's name from the desk

        desk_1.add_widget(self.students[desk_1.student.name]),   # Add the new student's name to the desk
        desk_2.add_widget(self.students[desk_2.student.name]),   # Add the new student's name to the desk

    def shuffle_students(self):  # Shuffle the students between desks
        for i in range(1000):   # Make 1000 random seating changes
            index_1 = randint(0, len(self.desks) - 1)  # The first random student
            while True:
                index_2 = randint(0, len(self.desks) - 1)  # The second random student
                if index_1 != index_2:  # Make sure we didn't select the same student twice
                    break

            self.swap_students(self.desks[index_1], self.desks[index_2])  # Swap the students' positions

    def measure_energy(self):  # Measure the 'energy' in the seating chart. Lower energy is better.
        self.energy = 0.0
        for i, desk in enumerate(self.desks):   # Look at each desk in the seating chart
            student = self.students[desk.student.name]    # Make a reference to the student at the current desk
            if student.close_to_teacher:  # If the student need to be close to the teacher...
                try:
                    self.energy += -3.0 / (self.ids["seating_chart"].top - desk.y) ** 2  # Add to the seating chart energy
                except ZeroDivisionError:
                    self.energy += 0

            for j, class_mate_desk in enumerate(self.desks):  # For each classmate...
                class_mate = self.students[class_mate_desk.student.name]   # Make a reference to the student at the current desk
                if j <= i:  # If we have already measured this student-classmate interaction...
                    continue  # Skip this interaction

                for attribute in student.att_list:
                    # Use a inverse square law to measure the interaction between the student and classmate
                    # And add the interaction to the total energy level
                    try:
                        self.energy += (getattr(student, attribute) * getattr(class_mate, attribute)) \
                                       / distance(desk, class_mate_desk) ** 2
                        # Add the interaction to the total energy level
                    except ZeroDivisionError:
                        self.energy += 0

                if class_mate.name in student.distractors:
                    try:
                        # If the classmate is a known distractor for the student...
                        # add to the interaction
                        self.energy += 1.5 / distance(desk, class_mate_desk) ** 2
                    except ZeroDivisionError:
                        self.energy += 0

                if class_mate.name in student.conflicts:
                    try:
                        # If the classmate is a known conflict for the student...
                        # add to the interaction
                        self.energy += 3.0 / distance(desk, class_mate_desk) ** 2
                    except ZeroDivisionError:
                        self.energy += 0

        return self.energy

    def mutate(self, *args):
        current_energy = self.measure_energy()

        index_1 = randint(0, len(self.desks) - 1)  # The first random student
        while True:
            index_2 = randint(0, len(self.desks) - 1)  # The second random student
            if index_1 != index_2:  # Make sure we didn't select the same student twice
                break

        self.swap_students(self.desks[index_1], self.desks[index_2])  # Swap the students' positions

        next_energy = self.measure_energy()  # Find the energy of the next generation

        if next_energy > current_energy:  # If the new generation has higher energy...
            self.swap_students(self.desks[index_1], self.desks[index_2])  # Swap the students' positions
            self.energy = current_energy

        self.mutation += 1  # Increment the number of mutations
        self.ids["progress"].value = self.mutation  # Update the progress bar

        if self.mutation >= self.max_mutations:  # Mutate for 3000 generations
            self.stop_mutation()

    def stop_mutation(self):
        self.mutation = 0
        Clock.unschedule(self.mutate)  # Stop mutating
        self.ids["optimize_button"].state = "normal"  # Set the toggle button back to normal
        self.ids["progress"].value = 0  # Set the progress bar back to 0

    def optimize(self):
        self.shuffle_students() # Shuffle the students
        Clock.schedule_interval(self.mutate, 1/100.)    # Start mutating


class StudentScreen(Screen):
    def __init__(self, **kwargs):
        super(StudentScreen, self).__init__(**kwargs)    # Call the superclass __init__()

        # A list of the attributes we will compare
        self.att_list = ["reading_pro", "math_pro", "chattiness", "focus", "safety"]


class DistractionsScreen(Screen):
    pass


class ConflictsScreen(Screen):
    pass


class Student1(Screen):
    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)    # Call the superclass __init__()
        self.name = ""  # Student's name
        self.close_to_board = False  # Does the student need to be close to the teacher?

        self.distractions = []  # A list of other students that distract this student
        self.conflicts = [] # A list of other students that are in conflict with this student

        # The following attributes are rated on a -1 to 1 scale.
        # -1: Significantly bellow standard
        #  0: Bellow standard
        #  1: At or above standard
        self.reading = 0        # Reading proficiency
        self.math = 0           # Math proficiency
        self.chattiness = 0     # Student's chattiness
        self.focus = 0          # Student's ability to ignore unexpected behavior and focus on their work
        self.safety = 0         # Student's safety with others and self


class StudentStacks(BoxLayout):
    pass


class Attribute(BoxLayout):
    attribute = StringProperty("")
    value = NumericProperty(None)


class Desk(Scatter):
    pass


class Student(Label):
    def __init__(self, student_name, close_to_teacher="False", distractors="", conflicts="",
                 reading_pro=0.0, math_pro=0.0, chattiness=0.0, focus=0.0, safety=0.0, **kwargs):
        super(Student, self).__init__(**kwargs)    # Call the superclass __init__()
        self.name = student_name  # Student's name
        self.close_to_teacher = bool(close_to_teacher)    # Does the student need to be close to the teacher?

        self.distractors = distractors.split()  # A list of other students that distract this student
        self.conflicts = conflicts.split()      # A list of other students that are in conflict with this student

        # The following attributes are rated on a -1 to 1 scale.
        # -1: Significantly bellow standard
        #  0: Bellow standard
        #  1: At or above standard
        self.reading_pro = float(reading_pro)  # Reading proficiency
        self.math_pro = float(math_pro)        # Math proficiency
        self.chattiness = float(chattiness)    # Student's chattiness
        self.focus = float(focus)              # Student's ability to ignore unexpected behavior and focus on their work
        self.safety = float(safety)            # Student's safety with others and self

        # A list of the attributes we will compare
        self.att_list = ["reading_pro", "math_pro", "chattiness", "focus", "safety"]


def distance(point_1, point_2):
    return sqrt((point_2.x - point_1.x) ** 2 + (point_2.y - point_1.y) ** 2)

if __name__ == '__main__':
    SeatingChartApp().run()
