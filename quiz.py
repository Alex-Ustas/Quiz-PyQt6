# TODO:
#   - QuizWindow: scrollbar
#   - participants
#   - CreateChangeQuizWindow: delete answer
#   - CreateChangeQuizWindow: change question order
#   - CreateChangeQuizWindow: scrollbar

import sys, pygame
import loader
from random import shuffle
from copy import deepcopy
from widget_settings import *

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QButtonGroup, QMessageBox
from PyQt6.QtCore import Qt

QUIZ_DATA = 'data/quiz.json'
USER_DATA = 'data/user.json'
RESULT_SOUND = ['data/giggle-22.wav', 'data/joyful.wav']


class WelcomeWindow(Window):
    def __init__(self):
        super().__init__('Quiz')
        self.setUpWindow()

    def setUpWindow(self):
        button_run_quiz = Button('Пройти квиз')
        button_run_quiz.clicked.connect(self.open_select_quiz_window)
        button_control_quiz = Button('Управлять квизами')
        button_control_quiz.clicked.connect(self.open_control_quiz_window)
        button_users = Button('Участники')

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(button_run_quiz)
        main_v_layout.addWidget(button_control_quiz)
        main_v_layout.addWidget(button_users)
        self.setLayout(main_v_layout)

    def open_select_quiz_window(self):
        self.window = SelectQuizWindow()
        self.window.show()
        self.close()

    def open_control_quiz_window(self):
        self.window = ControlQuizWindow()
        self.window.show()
        self.close()


class SelectQuizWindow(Window):
    def __init__(self):
        super().__init__('Выбор квиза', 500, 380)
        self.quiz = loader.get_json_data(QUIZ_DATA)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        quiz_list = [q['id'] for q in self.quiz]
        quiz_list.insert(0, 'Выберите квиз')
        self.quiz_combo_box = ComboList()
        self.quiz_combo_box.addItems(quiz_list)
        self.quiz_combo_box.currentIndexChanged.connect(self.on_select_quiz)
        quiz_h_layout.addWidget(self.quiz_combo_box)

        self.user = loader.get_json_data(USER_DATA)
        user_list = [u['name'] for u in self.user]
        user_list.insert(0, 'Выберите участника')
        self.user_combo_box = ComboList()
        self.user_combo_box.addItems(user_list)
        self.user_combo_box.currentIndexChanged.connect(self.on_select_user)
        user_h_layout.addWidget(self.user_combo_box)

        self.quiz_name_label = SmallLabel('Название квиза:', color='blue')
        self.quiz_questions_label = SmallLabel('Всего вопросов:', color='blue')
        self.user_quizzes_label = SmallLabel('Пройдено квиз:')
        self.user_answers_label = SmallLabel('Правильных ответов:')
        self.user_attempts_label = SmallLabel('')

        info_v_box = QVBoxLayout()
        info_v_box.addWidget(self.quiz_name_label)
        info_v_box.addWidget(self.quiz_questions_label)
        info_v_box.addWidget(self.user_quizzes_label)
        info_v_box.addWidget(self.user_answers_label)
        info_v_box.addWidget(self.user_attempts_label)

        info_group = Group('Информация')
        info_group.setLayout(info_v_box)

        self.button_run_quiz = Button('Пройти квиз')
        self.can_run(0, 0)
        self.button_run_quiz.clicked.connect(self.open_quiz_window)

        button_back = Button('Главное окно')
        button_back.clicked.connect(self.open_main_window)

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(quiz_h_layout)
        main_v_layout.addLayout(user_h_layout)
        main_v_layout.addWidget(info_group)
        main_v_layout.addWidget(self.button_run_quiz)
        main_v_layout.addWidget(button_back)
        self.setLayout(main_v_layout)

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()

    def open_quiz_window(self):
        selected_quiz = get_filtered_data('id', self.quiz_combo_box.currentText(), self.quiz)
        selected_user = get_filtered_data('name', self.user_combo_box.currentText(), self.user)
        self.window = QuizWindow(selected_quiz, selected_user)
        self.window.show()
        self.close()

    def on_select_quiz(self, index: int):
        self.quiz_name_label.setText(f'Название квиза:')
        self.quiz_questions_label.setText(f'Всего вопросов:')
        if index:
            selected_quiz = get_filtered_data('id', self.quiz_combo_box.itemText(index), self.quiz)
            self.quiz_name_label.setText(f'Название квиза: {selected_quiz['name']}')
            self.quiz_questions_label.setText(f'Всего вопросов: {len(selected_quiz['questions'])}')
        if self.user_combo_box.currentIndex():
            self.on_select_user(self.user_combo_box.currentIndex())
        self.can_run(index, self.user_combo_box.currentIndex())

    def on_select_user(self, index: int):
        self.user_quizzes_label.setText('Участником пройдено квиз:')
        self.user_answers_label.setText('Правильных ответов:')
        self.user_attempts_label.setText('')
        color = 'green'
        if index:
            selected_user = get_filtered_data('name', self.user_combo_box.itemText(index), self.user)
            answered = sum([rank[0] for quiz in selected_user['results'].values() for rank in quiz])
            total = sum([rank[1] for quiz in selected_user['results'].values() for rank in quiz])
            percent = count_percent(answered, total)
            self.user_quizzes_label.setText(f'Участником пройдено квиз: {len(selected_user["results"])}')
            self.user_answers_label.setText(f'Правильных ответов {answered} из {total} ({percent:.2f}%)')
            if 90 <= percent < 100:
                color = 'orange'
            elif total > answered:
                color = 'red'
            if self.quiz_combo_box.currentIndex():
                quiz_id = self.quiz_combo_box.currentText()
                text = f'Квиз {quiz_id}: не пройдено'
                if quiz_id in selected_user['results']:
                    results = selected_user['results'][quiz_id]
                    best_result = [r for r in results if r[0] / r[1] == max([res[0] / res[1] for res in results])][0]
                    text = f'Квиз {quiz_id}: было попыток: {len(results)}, лучший результат {best_result[0]} из {best_result[1]}'
                self.user_attempts_label.setText(text)
        for widget in [self.user_quizzes_label, self.user_answers_label, self.user_attempts_label]:
            change_style(widget, 'color', color)
        self.can_run(index, self.quiz_combo_box.currentIndex())

    def can_run(self, quiz_index: int, user_index: int):
        self.button_run_quiz.setEnabled(bool(quiz_index * user_index))


class QuizWindow(Window):
    def __init__(self, quiz: dict, user: dict):
        self.quiz = quiz
        self.user = user
        self.question = 0  # question number
        self.answer_type = None  # answer type: 1 - radio, 2 - checkbox, 3 - editbox
        self.to_confirm = True  # switch for confirm button
        self.score = [0, 0, len(self.quiz['questions'])]  # result: correct answers, total answered, total questions
        self.correct_answers = []

        super().__init__(f'Quiz {quiz['id']} {quiz['name']}', 1000, 800)
        self.setUpWindow()

    def setUpWindow(self):
        self.question_label = LabelCode('Вопрос', fixed_height=0)
        self.question_label.setWordWrap(True)

        question_v_layout = QVBoxLayout()
        question_v_layout.addWidget(self.question_label)
        self.question_group = Group('Вопрос')
        self.question_group.setLayout(question_v_layout)
        self.question_group.setFixedHeight(255)

        self.answer_v_layout = QVBoxLayout()
        self.answer_group = Group('Выберите ответ')
        self.answer_group.setLayout(self.answer_v_layout)

        self.note_label = LabelNote('')
        self.note_label.setWordWrap(True)
        self.note_label.setHidden(True)

        self.confirm_button = Button('Подтвердить', fixed_width=200)
        self.confirm_button.clicked.connect(self.on_click_confirm)

        # Progress Bar
        self.progressbar = ProgressBar()

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(self.question_group)
        main_v_layout.addWidget(self.answer_group)
        main_v_layout.addWidget(self.note_label)
        main_v_layout.addWidget(self.confirm_button)
        main_v_layout.addWidget(self.progressbar)
        main_v_layout.setAlignment(self.confirm_button, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(main_v_layout)
        self.show_question()

    def show_question(self):
        q_data = self.quiz['questions'][self.question]
        self.answer_type = q_data['type']
        choices = q_data['choices']
        if self.answer_type == 3:  # editbox
            self.correct_answers = [q_data['A']]
        else:
            self.correct_answers = [choices[int(a)] for a in q_data['A'].split(';')]
        if q_data['shuffle']:
            shuffle(choices)

        self.question_label.setText(q_data['Q'])
        self.question_group.setTitle(f'Вопрос {self.question + 1} из {self.score[2]}')
        self.confirm_button.setEnabled(False)
        self.update_statusbar()

        if self.answer_type == 1:  # radio
            self.answer_group.setTitle('Выберите один ответ')
            self.radio_group = QButtonGroup(self)
            for case in choices:
                radio_button = RadioButton(case)
                self.radio_group.addButton(radio_button)
                self.answer_v_layout.addWidget(radio_button)
            self.radio_group.buttonToggled.connect(self.on_radio_button_select)  # type: ignore
            self.answer_v_layout.addStretch()  # чтобы не растягивались по всему layout
        elif self.answer_type == 2:  # checkbox
            self.answer_group.setTitle('Выберите один или несколько ответов')
            self.check_group = QButtonGroup(self)
            self.check_group.setExclusive(False)
            for case in choices:
                checkbox = CheckBox(case)
                self.check_group.addButton(checkbox)
                self.answer_v_layout.addWidget(checkbox)
            self.check_group.buttonToggled.connect(self.on_checkbox_select)  # type: ignore
            self.answer_v_layout.addStretch()  # чтобы не растягивались по всему layout
        elif self.answer_type == 3:  # editbox
            self.answer_group.setTitle('Напишите ответ')
            self.edit_result = EditBox()
            self.edit_result.setPlaceholderText('Введите ответ и нажмите ENTER для подтверждения')
            self.edit_result.textChanged.connect(self.on_editbox_change)
            self.edit_result.returnPressed.connect(self.on_editbox_press_enter)
            self.answer_v_layout.addWidget(self.edit_result)
            self.answer_v_layout.setAlignment(self.edit_result, Qt.AlignmentFlag.AlignTop)
        else:
            print(f'\033[1m\033[33mtype = {self.answer_type} not defined\033[0m')

    def on_click_confirm(self):
        self.confirm_button.setText('Продолжить' if self.to_confirm else 'Подтвердить')
        if self.to_confirm:  # check and show current result
            match = 0
            if self.answer_type == 1:  # radio
                if self.radio_group.checkedButton().text() == self.correct_answers[0]:
                    match = 1
                for radio in self.radio_group.buttons():
                    if radio.text() == self.correct_answers[0]:
                        change_style(radio, 'color', 'green')
                    elif radio.isChecked():
                        change_style(radio, 'color', 'red')
            elif self.answer_type == 2:  # checkbox
                match = 1
                for checkbox in self.check_group.buttons():
                    if checkbox.isChecked() and checkbox.text() in self.correct_answers:
                        change_style(checkbox, 'color', 'green')
                    elif checkbox.isChecked() or checkbox.text() in self.correct_answers:
                        change_style(checkbox, 'color', 'red')
                        match = 0
            elif self.answer_type == 3:  # editbox
                if self.edit_result.text() == self.correct_answers[0]:
                    match = 1
                    change_style(self.edit_result, 'color', 'green')
                else:
                    change_style(self.edit_result, 'color', 'red')
                if match == 0:
                    result_label = LabelCode(f'Правильный ответ: {self.correct_answers[0]}')
                    self.answer_v_layout.addWidget(result_label)
                    self.answer_v_layout.addStretch()

            # play sound
            if self.quiz['playsound']:
                pygame.mixer.init()
                pygame.init()
                sound = pygame.mixer.Sound(RESULT_SOUND[match])
                sound.play()

            # show note
            note = self.quiz['questions'][self.question]['note']
            if note:
                self.note_label.setText(note)
                self.note_label.setHidden(False)

            self.score[0] += match
            self.score[1] += 1
            self.update_statusbar()
        else:  # next question
            if self.question == self.score[2] - 1:  # open result window
                self.window = ResultWindow(self.quiz, self.user, self.score)
                self.window.show()
                self.close()
            else:  # remove current widgets and show next question
                self.question += 1
                self.delete_widgets(self.answer_v_layout)
                self.show_question()
            self.note_label.setHidden(True)
        self.to_confirm = not self.to_confirm

    def on_radio_button_select(self):
        self.confirm_button.setEnabled(True)

    def on_checkbox_select(self):
        if self.to_confirm:
            result = any(map(lambda b: b.isChecked(), self.check_group.buttons()))
            self.confirm_button.setEnabled(result)

    def on_editbox_change(self):
        if self.to_confirm:
            self.confirm_button.setEnabled(bool(self.edit_result.text()))

    def on_editbox_press_enter(self):
        if self.edit_result.text() or not self.to_confirm:
            self.on_click_confirm()

    def update_statusbar(self):
        status_text = f'{self.user['name']}: правильных ответов {self.score[0]} из {self.score[1]}'
        self.progressbar.set_values(self.score[0], self.score[1] - self.score[0], self.score[2], status_text)


class ResultWindow(Window):
    def __init__(self, quiz: dict, user: dict, score: list[int]):
        self.quiz = quiz
        self.user = user
        self.score = score
        self.max_score = score[0] == score[1]
        super().__init__('Результат', 400, 250)
        self.setUpWindow()

    def setUpWindow(self):
        user_label = Label(self.user['name'], fixed_height=0)
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setWordWrap(True)

        quiz_label = Label(self.quiz['id'] + ' ' + self.quiz['name'], fixed_height=0)
        quiz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quiz_label.setWordWrap(True)

        percent = count_percent(self.score[0], self.score[1])
        answer_label = Label(f'Правильных ответов {self.score[0]} из {self.score[1]} ({percent:.2f}%)', fixed_height=0)
        if self.max_score:
            change_style(answer_label, 'color', 'green')
        elif 90 <= percent < 100:
            change_style(answer_label, 'color', 'orange')
        elif percent < 90:
            change_style(answer_label, 'color', 'red')
        answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.quiz['id'] not in self.user['results']:
            attempt_text = 'Первая попытка'
            if self.max_score:
                attempt_text += '. Отличный результат!'
        else:
            attempt_text = f'Попытка {len(self.user['results'][self.quiz['id']]) + 1}'
            if (self.max_score or self.score[0] / self.score[1] >
                    max([s[0] / s[1] for s in self.user['results'][self.quiz['id']]])):
                attempt_text += '. Лучший результат!'
        attempt_label = Label(attempt_text, fixed_height=0)
        attempt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_style(attempt_label, 'color', 'green')

        answered = sum([rank[0] for quiz in self.user['results'].values() for rank in quiz]) + self.score[0]
        total = sum([rank[1] for quiz in self.user['results'].values() for rank in quiz]) + self.score[1]
        percent = count_percent(answered, total)
        total_score_label = Label(f'Общий счет: {answered} из {total} ({percent:.2f}%)', fixed_height=0)
        total_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if answered == total:
            change_style(total_score_label, 'color', 'green')
        elif 90 <= percent < 100:
            change_style(total_score_label, 'color', 'orange')
        elif percent < 90:
            change_style(total_score_label, 'color', 'red')

        button_back = Button('Главное окно')
        button_back.clicked.connect(self.open_main_window)

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(user_label)
        main_v_layout.addWidget(quiz_label)
        main_v_layout.addWidget(answer_label)
        main_v_layout.addWidget(attempt_label)
        main_v_layout.addWidget(total_score_label)
        main_v_layout.addStretch()
        main_v_layout.addWidget(button_back)
        self.setLayout(main_v_layout)

        loader.save_user_data(USER_DATA, self.user['name'], self.quiz['id'], self.score)

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()


class ControlQuizWindow(Window):
    def __init__(self):
        self.to_save = False  # switch for save/change
        self.quiz = loader.get_json_data(QUIZ_DATA)
        self.quiz_list = [q['id'] for q in self.quiz]
        super().__init__('Управление квизами', 570, 280)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        self.quiz_combo_box = ComboList(fixed_width=100)
        self.quiz_combo_box.addItems(self.quiz_list)
        self.quiz_combo_box.setEditable(True)
        self.quiz_combo_box.setCurrentText('')
        self.quiz_combo_box.currentTextChanged.connect(self.on_quiz_number_change)

        quiz_h_layout.addWidget(self.quiz_combo_box)
        quiz_h_layout.addStretch()

        quiz_name_label = Label('Название')
        quiz_name_h_layout = QHBoxLayout()
        quiz_name_h_layout.addWidget(quiz_name_label)

        self.name_editbox = EditBox()
        self.name_editbox.setPlaceholderText('Введите название квиза')
        self.name_editbox.textEdited.connect(self.on_data_change)
        quiz_name_h_layout.addWidget(self.name_editbox)

        self.sound_checkbox = CheckBox('Со звуком')
        self.sound_checkbox.setFixedWidth(150)
        self.sound_checkbox.setChecked(True)
        self.sound_checkbox.stateChanged.connect(self.on_data_change)

        self.create_button = Button('Создать')
        self.change_button = Button('Изменить')
        self.delete_button = Button('Удалить')
        self.create_button.setEnabled(False)
        self.change_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.create_button.clicked.connect(self.open_create_window)
        self.change_button.clicked.connect(self.on_change_button)
        self.delete_button.clicked.connect(self.on_delete_button)
        buttons_h_layout = QHBoxLayout()
        buttons_h_layout.addWidget(self.create_button)
        buttons_h_layout.addWidget(self.change_button)
        buttons_h_layout.addWidget(self.delete_button)

        button_back = Button('Главное окно')
        button_back.clicked.connect(self.open_main_window)

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(quiz_h_layout)
        main_v_layout.addLayout(quiz_name_h_layout)
        main_v_layout.addWidget(self.sound_checkbox)
        main_v_layout.addStretch()
        main_v_layout.addLayout(buttons_h_layout)
        main_v_layout.addWidget(button_back)
        self.setLayout(main_v_layout)

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()

    def open_create_window(self):
        data = (self.quiz_combo_box.currentText(), self.name_editbox.text(), self.sound_checkbox.isChecked())
        self.window = CreateChangeQuizWindow(data)
        self.window.show()
        self.close()

    def open_change_window(self):
        quiz_id = self.quiz_combo_box.currentText()
        data = (quiz_id, self.name_editbox.text(), self.sound_checkbox.isChecked())
        quiz = get_filtered_data('id', quiz_id, self.quiz)
        self.window = CreateChangeQuizWindow(data, quiz['questions'])
        self.window.show()
        self.close()

    def on_quiz_number_change(self, quiz_id: str):
        quiz_name = self.name_editbox.text()
        self.change_button.setText('Изменить')
        self.to_save = False
        self.create_button.setEnabled(bool(quiz_id and not quiz_id in self.quiz_list and quiz_name))
        self.change_button.setEnabled(bool(quiz_id and quiz_id in self.quiz_list and quiz_name))
        self.delete_button.setEnabled(bool(quiz_id and quiz_id in self.quiz_list))
        if quiz_id and quiz_id in self.quiz_list:
            quiz = get_filtered_data('id', self.quiz_combo_box.currentText(), self.quiz)
            self.name_editbox.setText(quiz['name'])
            self.sound_checkbox.setChecked(quiz['playsound'])
        else:
            self.name_editbox.setText('')
            self.sound_checkbox.setChecked(True)
        self.on_data_change()

    def on_data_change(self):
        quiz_id = self.quiz_combo_box.currentText()
        quiz_name = self.name_editbox.text()
        if quiz_name == '':
            self.change_button.setEnabled(False)
            self.create_button.setEnabled(False)
        elif quiz_name and not quiz_id in self.quiz_list:
            self.create_button.setEnabled(True)
        elif quiz_id in self.quiz_list:
            self.change_button.setEnabled(True)
            q_data = get_filtered_data('id', quiz_id, self.quiz)
            if self.sound_checkbox.isChecked() == q_data['playsound'] and quiz_name == q_data['name']:
                self.change_button.setText('Изменить')
                self.to_save = False
            else:
                self.change_button.setText('Сохранить')
                self.to_save = True

    def on_change_button(self):
        if self.to_save:
            self.quiz[self.quiz_combo_box.currentIndex()]['name'] = self.name_editbox.text()
            self.quiz[self.quiz_combo_box.currentIndex()]['playsound'] = self.sound_checkbox.isChecked()
            loader.save_data(QUIZ_DATA, self.quiz)
            self.change_button.setText('Изменить')
            self.to_save = False
        else:
            self.open_change_window()

    def on_delete_button(self):
        quiz_id = self.quiz_combo_box.currentText()
        reply = QMessageBox.question(self, 'Удаление квиза',
                                     f'Вы действительно хотите удалить квиз\n{quiz_id} {self.name_editbox.text()}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            index = list(filter(lambda q: q[1]['id'] == quiz_id, enumerate(self.quiz)))[0][0]
            del self.quiz[index]
            self.quiz_list = [q['id'] for q in self.quiz]
            self.name_editbox.setText('')
            self.sound_checkbox.setChecked(True)
            self.quiz_combo_box.clear()
            self.quiz_combo_box.addItems(self.quiz_list)
            self.quiz_combo_box.setCurrentText('')

            userdata = loader.get_json_data(USER_DATA)
            for user in userdata:
                user['results'].pop(quiz_id, None)
            loader.save_data(USER_DATA, userdata)
            loader.save_data(QUIZ_DATA, self.quiz)


class CreateChangeQuizWindow(Window):
    def __init__(self, quiz_data: tuple, questions=None):
        self.quiz_id, self.quiz_name, self.playsound = quiz_data
        self.new_question = self.is_new = bool(questions is None)
        self.questions = [] if self.is_new else questions  # data for all questions
        self.pages = [1, 1] if self.is_new else [1, len(self.questions)]  # current, total
        self.question = {}
        self.generate_q_data()
        title = f'Создание' if self.is_new else f'Изменение'
        super().__init__(f'{title} квиза {self.quiz_id} {self.quiz_name}', 800, 800)
        self.setUpWindow()

    def setUpWindow(self):
        # Question section
        question_v_layout = QVBoxLayout()
        self.question_group = Group('Вопрос 1 из 1', fixed_height=180)
        self.question_group.setLayout(question_v_layout)

        self.question_text = TextBox(fixed_height=115)
        self.question_text.setPlaceholderText('Введите текст вопроса')
        self.question_text.textChanged.connect(self.check_data_before_save)
        question_v_layout.addWidget(self.question_text)

        # Answer section
        answer_v_layout = QVBoxLayout()
        answer_group = Group('Ответ')
        answer_group.setLayout(answer_v_layout)

        answer_type_h_layout = QHBoxLayout()
        answer_type_label = Label('Тип ответа')
        self.answer_type_list = ComboList()
        self.answer_type_list.addItems(['Один ответ', 'Несколько ответов', 'Ввод ответа'])
        self.answer_type_list.currentTextChanged.connect(self.on_answer_text_changed)
        answer_type_h_layout.addWidget(answer_type_label)
        answer_type_h_layout.addWidget(self.answer_type_list)

        answer_h_layout = QHBoxLayout()
        answer_label = Label('Введите ответ')
        self.answer_textbox = TextBox(fixed_height=50)
        self.answer_textbox.textChanged.connect(self.on_answer_text_changed)
        self.add_answer_button = Button('+', fixed_width=50)
        self.add_answer_button.clicked.connect(self.on_add_answer_button)
        answer_h_layout.addWidget(answer_label)
        answer_h_layout.addWidget(self.answer_textbox)
        answer_h_layout.addWidget(self.add_answer_button)

        self.answer_choices_v_layout = QVBoxLayout()

        answer_v_layout.addLayout(answer_type_h_layout)
        answer_v_layout.addLayout(answer_h_layout)
        answer_v_layout.addLayout(self.answer_choices_v_layout)
        answer_v_layout.addStretch()

        # Settings section
        weight_label = Label('Баллы за ответ')
        self.weight_spinbox = EditSpin(fixed_width=50)

        weight_h_layout = QHBoxLayout()
        weight_h_layout.addWidget(weight_label)
        weight_h_layout.addWidget(self.weight_spinbox)

        self.shuffle_checkbox = CheckBox('Перемешивать ответы', fixed_width=230)
        self.show_result_checkbox = CheckBox('Показывать ответы', fixed_width=230)

        self.note_text = TextBox(fixed_height=94)
        self.note_text.setPlaceholderText('Укажите примечание к вопросу, будет показано после ответа')
        change_style(self.note_text, 'font-size', '12px')

        settings_v_layout = QVBoxLayout()
        settings_v_layout.addLayout(weight_h_layout)
        settings_v_layout.addWidget(self.shuffle_checkbox)
        settings_v_layout.addWidget(self.show_result_checkbox)

        settings_h_layout = QHBoxLayout()
        settings_h_layout.addLayout(settings_v_layout)
        settings_h_layout.addWidget(self.note_text)

        # Navigation section
        self.prev_button = Button('', fixed_width=50)
        self.prev_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.prev_button.clicked.connect(self.on_prev_button)
        self.delete_button = Button('Удалить вопрос', fixed_width=200)
        self.delete_button.clicked.connect(self.on_delete_button)
        self.next_button = Button('', fixed_width=50)
        self.next_button.clicked.connect(self.on_next_button)

        navigation_h_layout = QHBoxLayout()
        navigation_h_layout.addWidget(self.prev_button)
        navigation_h_layout.addStretch()
        navigation_h_layout.addWidget(self.delete_button)
        navigation_h_layout.addStretch()
        navigation_h_layout.addWidget(self.next_button)

        # Footer section
        self.save_button = Button('Сохранить', fixed_width=150)
        self.save_button.clicked.connect(self.save_quiz)
        self.save_button.setEnabled(False)
        cancel_button = Button('Отменить', fixed_width=150)
        cancel_button.clicked.connect(self.open_control_quiz_window)

        footer_buttons_h_layout = QHBoxLayout()
        footer_buttons_h_layout.addWidget(self.save_button)
        footer_buttons_h_layout.addStretch()
        footer_buttons_h_layout.addWidget(cancel_button)

        # Main layout
        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(self.question_group)
        main_v_layout.addWidget(answer_group)
        main_v_layout.addLayout(settings_h_layout)
        main_v_layout.addLayout(navigation_h_layout)
        main_v_layout.addLayout(footer_buttons_h_layout)
        self.setLayout(main_v_layout)

        self.show_question()

    def open_control_quiz_window(self):
        self.window = ControlQuizWindow()
        self.window.show()
        self.close()

    def generate_q_data(self) -> None:
        if self.new_question:  # default data for new question
            self.question = {'type': 1,
                             'Q': '',
                             'choices': [],
                             'A': '',
                             'weight': 1,
                             'shuffle': True,
                             'show_result': True,
                             'note': ''}
        else:
            self.question = deepcopy(self.questions[self.pages[0] - 1])

    def show_question(self):
        self.question_group.setTitle(f'Вопрос {self.pages[0]} из {self.pages[1]}')
        self.answer_type_list.setEnabled(self.new_question)
        self.question_text.setPlainText(self.question['Q'])
        self.answer_type_list.setCurrentIndex(self.question['type'] - 1)
        self.weight_spinbox.setValue(self.question['weight'])
        self.shuffle_checkbox.setChecked(self.question['shuffle'])
        self.show_result_checkbox.setChecked(self.question['show_result'])
        self.note_text.setPlainText(self.question['note'])

        self.show_answer()

        # navigation buttons
        if self.pages[0] == 1:  # first question
            self.prev_button.setText('')
            self.prev_button.setIcon(QIcon('images/zero-page.png'))
        else:
            self.prev_button.setText(f'{self.pages[0] - 1}')
            self.prev_button.setIcon(QIcon('images/arrow-left.png'))
        if self.pages[0] == self.pages[1]:  # last question
            self.next_button.setText('')
            self.next_button.setIcon(QIcon('images/plus-page.png'))
        else:
            self.next_button.setText(f'{self.pages[0] + 1}')
            self.next_button.setIcon(QIcon('images/arrow-right.png'))

        self.check_data_before_save()

    def show_answer(self):
        answer_type = self.answer_type_list.currentIndex() + 1
        if answer_type == 1:  # radio
            answer = int(self.question['A']) if self.question['A'] else -1
            self.answer_textbox.setPlainText('')
            self.radio_group = QButtonGroup(self)
            for i, text in enumerate(self.question['choices']):
                radio_button = RadioButton(text)
                self.radio_group.addButton(radio_button, i)
                self.answer_choices_v_layout.addWidget(radio_button)
                if i == answer:
                    radio_button.setChecked(True)
            self.radio_group.buttonToggled.connect(self.on_radio_button_select)  # type: ignore
        elif answer_type == 2:  # checkbox
            answers = list(map(int, self.question['A'].split(';'))) if self.question['A'] else []
            self.answer_textbox.setPlainText('')
            self.check_group = QButtonGroup(self)
            self.check_group.setExclusive(False)
            for i, text in enumerate(self.question['choices']):
                checkbox = CheckBox(text)
                self.check_group.addButton(checkbox, i)
                self.answer_choices_v_layout.addWidget(checkbox)
                if i in answers:
                    checkbox.setChecked(True)
            self.check_group.buttonToggled.connect(self.on_checkbox_select)  # type: ignore
        else:  # editbox
            self.answer_textbox.setPlainText(self.question['A'])
        self.add_answer_button.setEnabled(False)

    def on_radio_button_select(self):
        self.question['A'] = str(self.radio_group.checkedId())
        self.check_data_before_save()

    def on_checkbox_select(self):
        self.question['A'] = ';'.join(
            [str(i) for i, button in enumerate(self.check_group.buttons()) if button.isChecked()])
        self.check_data_before_save()

    def on_prev_button(self):
        self.save_question()
        self.delete_widgets(self.answer_choices_v_layout)
        self.new_question = False
        self.pages[0] -= 1
        self.generate_q_data()
        self.show_question()

    def on_next_button(self):
        self.save_question()
        self.delete_widgets(self.answer_choices_v_layout)
        is_last = self.pages[0] == self.pages[1]  # last question
        self.new_question = is_last
        if is_last:
            self.pages[1] += 1
        self.pages[0] += 1
        self.generate_q_data()
        self.show_question()

    def on_delete_button(self):
        reply = QMessageBox.question(self, 'Удаление вопроса',
                                     'Вы действительно хотите удалить этот вопрос\nи все данные в нём?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.new_question:
                self.pages[0] -= 1
            else:
                self.questions.pop(self.pages[0] - 1)
                if self.pages[0] == self.pages[1]:  # last question
                    self.pages[0] -= 1
            self.pages[1] -= 1
            self.delete_widgets(self.answer_choices_v_layout)
            self.new_question = False
            self.generate_q_data()
            self.show_question()

    def on_answer_text_changed(self):
        text = self.answer_textbox.toPlainText()
        enabled = self.answer_type_list.currentIndex() < 2 and bool(text) and text not in self.question['choices']
        self.add_answer_button.setEnabled(enabled)
        self.check_data_before_save()

    def on_add_answer_button(self):
        self.delete_widgets(self.answer_choices_v_layout)
        self.question['choices'].append(self.answer_textbox.toPlainText())
        self.answer_textbox.setPlainText('')
        self.answer_type_list.setEnabled(False)
        self.show_answer()
        self.check_data_before_save()

    def check_data_before_save(self):
        q_text = self.question_text.toPlainText()  # question entered
        a_type = self.answer_type_list.currentIndex() + 1
        a_text = self.answer_textbox.toPlainText()  # answer entered for type 3
        if a_type < 3:
            choice = bool(self.question['A']) and len(self.question['choices']) > 1
        else:
            choice = bool(a_text)
        result = bool(q_text) and choice
        self.prev_button.setEnabled(result and self.pages[0] > 1)
        self.next_button.setEnabled(result)
        self.save_button.setEnabled(result)
        self.delete_button.setEnabled(self.pages[1] > 1)

    def save_question(self):
        if self.new_question:
            self.questions.append({})
        answer_type = self.answer_type_list.currentIndex() + 1
        question = self.questions[self.pages[0] - 1]
        question['type'] = answer_type
        question['Q'] = self.question_text.toPlainText()
        if answer_type == 1:  # radio
            question['choices'] = [choice for choice in self.question['choices']]
            question['A'] = str(self.radio_group.checkedId())
        elif answer_type == 2:  # checkbox
            question['choices'] = [choice for choice in self.question['choices']]
            question['A'] = ';'.join(
                [str(i) for i, button in enumerate(self.check_group.buttons()) if button.isChecked()])
        else:  # editbox
            question['choices'] = []
            question['A'] = self.answer_textbox.toPlainText()
        question['weight'] = int(self.weight_spinbox.text())
        question['shuffle'] = self.shuffle_checkbox.isChecked()
        question['show_result'] = self.show_result_checkbox.isChecked()
        question['note'] = self.note_text.toPlainText()

    def save_quiz(self):
        self.save_question()
        quiz_data = loader.get_json_data(QUIZ_DATA)
        if self.is_new:
            quiz_data.append(dict())
            quiz = quiz_data[-1]
            quiz['id'] = self.quiz_id
            quiz['name'] = self.quiz_name
            quiz['playsound'] = self.playsound
        else:
            quiz = get_filtered_data('id', self.quiz_id, quiz_data)
        quiz['questions'] = self.questions
        loader.save_data(QUIZ_DATA, quiz_data)
        self.open_control_quiz_window()


def count_percent(n: int, total: int) -> float:
    return 0 if total == 0 else round(n / total * 100, 2)


def get_filtered_data(key: str, value: str, data: list) -> dict:
    """Filter for dict:\n
    data[key] == value in source dict"""
    return list(filter(lambda x: x[key] == value, data))[0]


# Unhandled exception interceptor
def excepthook(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle('Fusion')
    window = WelcomeWindow()
    window.show()
    sys.excepthook = excepthook
    sys.exit(app.exec())  # запуск цикла приложения
