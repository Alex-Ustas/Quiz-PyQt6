# TODO:
#   - QuizWindow: scrollbar for answer
#   - CreateChangeQuizWindow: scrollbar

import sys, pygame, json
from random import shuffle
from copy import deepcopy
from widget_settings import *
from typing import Dict, List, Any, Tuple
from datetime import datetime as dt
from dataclasses import dataclass

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QButtonGroup, QMessageBox, QScrollArea
from PyQt6.QtCore import Qt

VERSION = '2.01 (2026.06)'
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
        button_users.clicked.connect(self.open_control_user_window)
        button_about = Button('О программе')
        button_about.clicked.connect(self.on_click_about)

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(button_run_quiz)
        main_v_layout.addWidget(button_control_quiz)
        main_v_layout.addWidget(button_users)
        main_v_layout.addWidget(button_about)
        self.setLayout(main_v_layout)

    def open_select_quiz_window(self):
        self.window = SelectQuizWindow()
        self.window.show()
        self.close()

    def open_control_quiz_window(self):
        self.window = ControlQuizWindow()
        self.window.show()
        self.close()

    def open_control_user_window(self):
        self.window = ControlUserWindow()
        self.window.show()
        self.close()

    def on_click_about(self):
        name = [1060, 1072, 1076, 1077, 1080, 1095, 1077, 1074, 32, 1040, 1083, 1077, 1082, 1089, 1072, 1085, 1076,
                1088]
        fio = ''.join([chr(c) for c in name])
        html_text = f"""
        <h3><p><b>Автор:</b> {fio}</p></h3>
        <p><b>Telegram:</b> @AlexUstas0</p>
        <p><b>email:</b> alex.ustas@internet.ru</p>
        <p><b>Версия:</b> {VERSION}</p>
        """
        reply = QMessageBox.information(self, 'О программе', html_text)


class SelectQuizWindow(Window):
    def __init__(self):
        super().__init__('Выбор квиза', 500, 380)
        self.quizzes = QuizManager()
        self.users = UserManager()
        self.selected_quiz = Quiz('')
        self.selected_user = User('')
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        quiz_list = self.quizzes.get_quiz_ids()
        quiz_list.insert(0, 'Выберите квиз')
        self.quiz_combo_box = ComboList()
        self.quiz_combo_box.addItems(quiz_list)
        self.quiz_combo_box.currentIndexChanged.connect(self.on_select_quiz)
        quiz_h_layout.addWidget(self.quiz_combo_box)

        user_list = self.users.get_all_names()
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
        self.window = QuizWindow(self.selected_quiz, self.selected_user)
        self.window.show()
        self.close()

    def on_select_quiz(self, index: int):
        self.quiz_name_label.setText(f'Название квиза:')
        self.quiz_questions_label.setText(f'Всего вопросов:')
        if index:
            quiz_id = self.quiz_combo_box.itemText(index)
            self.selected_quiz = self.quizzes[quiz_id]
            score = self.selected_quiz.get_total_score()
            self.quiz_name_label.setText(f'Название квиза: {self.selected_quiz.name}')
            self.quiz_questions_label.setText(f'Всего вопросов: {len(self.selected_quiz.questions)}, баллов: {score}')
        if self.user_combo_box.currentIndex():
            self.on_select_user(self.user_combo_box.currentIndex())
        self.can_run(index, self.user_combo_box.currentIndex())

    def on_select_user(self, index: int):
        self.user_quizzes_label.setText('Участником пройдено квиз:')
        self.user_answers_label.setText('Правильных ответов:')
        self.user_attempts_label.setText('')
        color = 'green'
        if index:
            user_id = self.user_combo_box.itemText(index)
            self.selected_user = self.users[user_id]
            score = self.selected_user.get_total_score()
            score_text = (f'Правильных ответов {score[0]} из {score[1]} ({score[4]:.2f}%), ' +
                          f'баллов {score[2]} из {score[3]} ({score[5]:.2f}%)')
            self.user_quizzes_label.setText(f'Участником пройдено квиз: {len(self.selected_user.results)}')
            self.user_answers_label.setText(score_text)
            color = score[-1]
            if self.quiz_combo_box.currentIndex():
                quiz_id = self.quiz_combo_box.currentText()
                text = f'Квиз {quiz_id}: не пройдено'
                if quiz_id in self.selected_user.results:
                    results = self.selected_user.results[quiz_id]
                    best_result = [r for r in results if r[2] / r[3] == max([res[2] / res[3] for res in results])][0]
                    text = f'Квиз {quiz_id}: было попыток: {len(results)}, лучший результат {best_result[2]} из {best_result[3]}'
                self.user_attempts_label.setText(text)
        for widget in [self.user_quizzes_label, self.user_answers_label, self.user_attempts_label]:
            change_style(widget, 'color', color)
        self.can_run(index, self.quiz_combo_box.currentIndex())

    def can_run(self, quiz_index: int, user_index: int):
        self.button_run_quiz.setEnabled(bool(quiz_index * user_index))


class QuizWindow(Window):
    def __init__(self, quiz: 'Quiz', user: 'User'):
        self.quiz = quiz
        self.user = user
        self.question = 0  # question number
        self.answer_type = None  # answer type: 1 - radio, 2 - checkbox, 3 - editbox
        self.to_confirm = True  # switch for confirm button
        # score: correct answers, total answered, correct score, total score, total questions
        self.score = [0, 0, 0, 0, len(self.quiz.questions)]
        self.correct_answers = []

        super().__init__(f'Quiz {str(self.quiz)}', 1000, 800)
        self.setUpWindow()

    def setUpWindow(self):
        # Question section
        self.question_label = LabelCode('Вопрос', fixed_height=0)
        self.question_label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.question_label)
        scroll_area.setWidgetResizable(True)

        question_v_layout = QVBoxLayout()
        question_v_layout.addWidget(scroll_area)
        self.question_group = Group('Вопрос')
        self.question_group.setLayout(question_v_layout)
        self.question_group.setFixedHeight(255)

        # Answer section
        self.answer_v_layout = QVBoxLayout()
        self.answer_group = Group('Выберите ответ')
        self.answer_group.setLayout(self.answer_v_layout)

        self.note_label = LabelNote('')
        self.note_label.setWordWrap(True)
        self.note_label.setHidden(True)

        # Confirm button section
        self.confirm_button = Button('Подтвердить', fixed_width=200)
        self.confirm_button.clicked.connect(self.on_click_confirm)

        # Progress Bar section
        self.progressbar = ProgressBar()

        # Main layout section
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
        q_data = self.quiz.questions[self.question]
        self.answer_type = q_data.type
        choices = q_data.choices
        if self.answer_type == 3:  # editbox
            self.correct_answers = [q_data.A]
        else:
            self.correct_answers = [choices[int(a)] for a in q_data.A.split(';')]
        if q_data.shuffle:
            shuffle(choices)

        self.question_label.setText(q_data.Q)
        weight = choose_plural(q_data.weight, ('балл', 'балла', 'баллов'))
        self.question_group.setTitle(f'Вопрос {self.question + 1} из {self.score[-1]} ({weight})')
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
        current_question = self.quiz.questions[self.question]
        show_result = current_question.show_result
        self.confirm_button.setText('Продолжить' if self.to_confirm else 'Подтвердить')
        if self.to_confirm:  # check and show current result
            match = 0
            if self.answer_type == 1:  # radio
                if self.radio_group.checkedButton().text() == self.correct_answers[0]:
                    match = 1
                if show_result:
                    for radio in self.radio_group.buttons():
                        if radio.text() == self.correct_answers[0]:
                            change_style(radio, 'color', 'green')
                        elif radio.isChecked():
                            change_style(radio, 'color', 'red')
            elif self.answer_type == 2:  # checkbox
                match = 1
                for checkbox in self.check_group.buttons():
                    if checkbox.isChecked() and checkbox.text() in self.correct_answers:
                        if show_result:
                            change_style(checkbox, 'color', 'green')
                    elif checkbox.isChecked() or checkbox.text() in self.correct_answers:
                        if show_result:
                            change_style(checkbox, 'color', 'red')
                        match = 0
            elif self.answer_type == 3:  # editbox
                if self.edit_result.text() == self.correct_answers[0]:
                    match = 1
                    if show_result:
                        change_style(self.edit_result, 'color', 'green')
                else:
                    if show_result:
                        change_style(self.edit_result, 'color', 'red')
                if match == 0 and show_result:
                    result_label = LabelCode(f'Правильный ответ: {self.correct_answers[0]}')
                    self.answer_v_layout.addWidget(result_label)
                    self.answer_v_layout.addStretch()

            # play sound
            if self.quiz.playsound:
                pygame.mixer.init()
                pygame.init()
                sound = pygame.mixer.Sound(RESULT_SOUND[match])
                sound.play()

            # show note
            note = current_question.note
            if note:
                self.note_label.setText(note)
                self.note_label.setHidden(False)

            self.score[0] += match
            self.score[1] += 1
            self.score[2] += current_question.weight * match
            self.score[3] += current_question.weight
            self.update_statusbar()
        else:  # next question
            if self.question == self.score[-1] - 1:  # open result window
                self.window = ResultWindow(self.quiz, self.user, self.score[:4])
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
        status_text = f'{self.user.name}: правильных ответов {self.score[0]} из {self.score[1]}, '
        status_text += f'баллов {self.score[2]} из {self.score[3]}'
        self.progressbar.set_values(self.score[2], self.score[3] - self.score[2],
                                    self.quiz.get_total_score(), status_text)


class ResultWindow(Window):
    def __init__(self, quiz: 'Quiz', user: 'User', score: List[int]):
        self.quiz = quiz
        self.user = user
        self.score = score
        self.max_score = score[0] == score[1]
        super().__init__('Результат', 400, 280)
        self.setUpWindow()

    def setUpWindow(self):
        user_label = Label(self.user.name, fixed_height=0)
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setWordWrap(True)

        quiz_label = Label(str(self.quiz), fixed_height=0)
        quiz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quiz_label.setWordWrap(True)

        percent = count_percent(self.score[0], self.score[1])
        score_percent = count_percent(self.score[2], self.score[3])
        score_text = (f'Правильных ответов {self.score[0]} из {self.score[1]} ({percent:.2f}%)\n' +
                      f'Набрано баллов {self.score[2]} из {self.score[3]} ({score_percent:.2f}%)')
        answer_label = Label(score_text, fixed_height=0)
        self.change_result_color(self.max_score, score_percent, answer_label)
        answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.quiz.quiz_id not in self.user.results:
            attempt_text = 'Первая попытка'
            if self.max_score:
                attempt_text += '. Отличный результат!'
        else:
            quiz_results = self.user.results[self.quiz.quiz_id]
            attempt_text = f'Попытка {len(quiz_results) + 1}'
            if self.max_score or self.score[2] / self.score[3] > max([s[2] / s[3] for s in quiz_results]):
                attempt_text += '. Лучший результат!'
        attempt_label = Label(attempt_text, fixed_height=0)
        attempt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_style(attempt_label, 'color', 'green')

        score = self.user.get_total_score()
        for i in range(4):
            score[i] += self.score[i]
        percent = count_percent(score[0], score[1])
        score_percent = count_percent(score[2], score[3])
        score_text = (f'Общий счет: {score[0]} из {score[1]} ({percent:.2f}%)\n' +
                      f'Набрано баллов: {score[2]} из {score[3]} ({score_percent:.2f}%)')
        total_score_label = Label(score_text, fixed_height=0)
        total_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_score_label.setWordWrap(True)
        self.change_result_color(score[0] == score[1], score_percent, total_score_label)

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

        users = UserManager()
        users.save_quiz_for_user(self.user.name, self.quiz.quiz_id, self.score)

    @staticmethod
    def change_result_color(best_result: bool, percent: float, label):
        if best_result:
            change_style(label, 'color', 'green')
        elif 90 <= percent < 100:
            change_style(label, 'color', 'orange')
        elif percent < 90:
            change_style(label, 'color', 'red')

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()


class ControlQuizWindow(Window):
    def __init__(self):
        self.to_save = False  # switch for save/change
        self.quizzes = QuizManager()
        self.quiz_list = self.quizzes.get_quiz_ids()
        super().__init__('Управление квизами', 570, 280)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        self.quiz_combo_box = ComboList(fixed_width=100, editable=True)
        self.quiz_combo_box.addItems(self.quiz_list)
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
        self.create_button.clicked.connect(self.open_create_change_window)
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

    def open_create_change_window(self):
        quiz_id = self.quiz_combo_box.currentText()
        if quiz_id not in self.quiz_list:
            quiz = Quiz(quiz_id, name=self.name_editbox.text(), playsound=self.sound_checkbox.isChecked())
        else:
            quiz = self.quizzes[quiz_id]
        self.window = CreateChangeQuizWindow(quiz)
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
            quiz = self.quizzes[self.quiz_combo_box.currentText()]
            self.name_editbox.setText(quiz.name)
            self.sound_checkbox.setChecked(quiz.playsound)
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
            q_data = self.quizzes[quiz_id]
            if self.sound_checkbox.isChecked() == q_data.playsound and quiz_name == q_data.name:
                self.change_button.setText('Изменить')
                self.to_save = False
            else:
                self.change_button.setText('Сохранить')
                self.to_save = True

    def on_change_button(self):
        if self.to_save:
            self.quizzes[self.quiz_combo_box.currentText()].name = self.name_editbox.text()
            self.quizzes[self.quiz_combo_box.currentText()].playsound = self.sound_checkbox.isChecked()
            self.quizzes.save_data()
            self.change_button.setText('Изменить')
            self.to_save = False
        else:
            self.open_create_change_window()

    def on_delete_button(self):
        quiz_id = self.quiz_combo_box.currentText()
        reply = QMessageBox.question(self, 'Удаление квиза',
                                     f'Вы действительно хотите удалить квиз\n{quiz_id} {self.name_editbox.text()}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.quizzes[quiz_id]
            self.quiz_list = self.quizzes.get_quiz_ids()
            self.name_editbox.setText('')
            self.sound_checkbox.setChecked(True)
            self.quiz_combo_box.clear()
            self.quiz_combo_box.addItems(self.quiz_list)
            self.quiz_combo_box.setCurrentText('')

            users = UserManager()
            users.remove_quiz_from_all(quiz_id)
            self.quizzes.save_data()


class CreateChangeQuizWindow(Window):
    def __init__(self, quiz: 'Quiz'):
        self.quiz = quiz
        self.questions = quiz.questions  # data for all questions
        self.new_question = self.is_new = not bool(self.questions)
        self.pages = [1, 1] if self.is_new else [1, len(self.questions)]  # current, total
        self.question = Question()
        self.generate_q_data()
        title = f'Создание' if self.is_new else f'Изменение'
        super().__init__(f'{title} квиза {self.quiz.quiz_id} {self.quiz.name}', 800, 800)
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
        self.answer_type_list.addItems(Question().types())
        self.answer_type_list.currentTextChanged.connect(self.on_answer_type_changed)
        answer_type_h_layout.addWidget(answer_type_label)
        answer_type_h_layout.addWidget(self.answer_type_list)

        answer_h_layout = QHBoxLayout()
        answer_label = Label('Введите ответ')
        self.answer_textbox = TextBox(fixed_height=50)
        self.answer_textbox.textChanged.connect(self.on_answer_text_changed)
        self.add_answer_button = Button('', fixed_width=50)
        self.add_answer_button.setIcon(QIcon('images/plus-page.png'))
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

        change_order_label = Label('Очередность вопроса')
        self.change_order_spinbox = EditSpin(fixed_width=50)
        self.change_order_spinbox.textChanged.connect(self.on_order_change)

        self.delete_button = Button('Удалить вопрос', fixed_width=200)
        self.delete_button.clicked.connect(self.on_delete_question_button)

        self.next_button = Button('', fixed_width=50)
        self.next_button.clicked.connect(self.on_next_button)

        navigation_h_layout = QHBoxLayout()
        navigation_h_layout.addWidget(self.prev_button)
        navigation_h_layout.addStretch()
        navigation_h_layout.addWidget(change_order_label)
        navigation_h_layout.addWidget(self.change_order_spinbox)
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
            self.question = Question()
        else:
            self.question = deepcopy(self.questions[self.pages[0] - 1])

    def show_question(self):
        self.question_group.setTitle(f'Вопрос {self.pages[0]} из {self.pages[1]}')
        self.answer_type_list.setEnabled(self.new_question)
        self.question_text.setPlainText(self.question.Q)
        self.answer_type_list.setCurrentIndex(self.question.type - 1)
        self.weight_spinbox.setValue(self.question.weight)
        self.shuffle_checkbox.setChecked(self.question.shuffle)
        self.show_result_checkbox.setChecked(self.question.show_result)
        self.note_text.setPlainText(self.question.note)

        self.show_answer()

        # navigation section
        self.show_navigation_buttons()
        self.change_order_spinbox.blockSignals(True)
        self.change_order_spinbox.setMaximum(self.pages[1])
        self.change_order_spinbox.setValue(self.pages[0])
        self.change_order_spinbox.blockSignals(False)

        self.check_data_before_save()

    def show_answer(self):
        answer_type = self.answer_type_list.currentIndex() + 1
        answer = self.question.get_answers()
        if answer_type == 1:  # radio
            self.answer_textbox.setPlainText('')
            self.radio_group = QButtonGroup(self)
            for i, text in enumerate(self.question.choices):
                delete_answer_button = Button('', fixed_width=28, fixed_height=27, icon_size=16)
                delete_answer_button.setIcon(QIcon('images/delete.png'))
                delete_answer_button.clicked.connect(lambda checked, idx=i: self.on_delete_answer_button(idx))

                radio_button = RadioButton(text)
                if i == answer:
                    radio_button.setChecked(True)

                answer_choices_h_layout = QHBoxLayout()
                answer_choices_h_layout.addWidget(delete_answer_button)
                answer_choices_h_layout.addWidget(radio_button)

                self.radio_group.addButton(radio_button, i)
                self.radio_group.addButton(delete_answer_button)
                self.answer_choices_v_layout.addLayout(answer_choices_h_layout)

            self.radio_group.buttonToggled.connect(self.on_radio_button_select)  # type: ignore

        elif answer_type == 2:  # checkbox
            self.answer_textbox.setPlainText('')
            self.check_group = QButtonGroup(self)
            self.check_group.setExclusive(False)
            for i, text in enumerate(self.question.choices):
                delete_answer_button = Button('', fixed_width=28, fixed_height=27, icon_size=16)
                delete_answer_button.setIcon(QIcon('images/delete.png'))
                delete_answer_button.clicked.connect(lambda checked, idx=i: self.on_delete_answer_button(idx))

                checkbox = CheckBox(text)
                if i in answer:
                    checkbox.setChecked(True)

                answer_choices_h_layout = QHBoxLayout()
                answer_choices_h_layout.addWidget(delete_answer_button)
                answer_choices_h_layout.addWidget(checkbox)

                self.check_group.addButton(checkbox, i)
                self.check_group.addButton(delete_answer_button)
                self.answer_choices_v_layout.addLayout(answer_choices_h_layout)
            self.check_group.buttonToggled.connect(self.on_checkbox_select)  # type: ignore

        else:  # editbox
            self.answer_textbox.setPlainText(answer)
        self.add_answer_button.setEnabled(False)

    def show_navigation_buttons(self):
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

    def on_delete_answer_button(self, index):
        self.delete_widgets(self.answer_choices_v_layout)
        del self.question.choices[index]
        answer_type = self.answer_type_list.currentIndex() + 1
        answer = self.question.get_answers()
        if answer_type == 1:  # radio
            if index == answer:
                self.question.A = ''
            if answer > index:
                self.question.A = str(answer - 1)
        else:  # checkbox
            if index in answer:
                answer.remove(index)
            answers = [a if a < index else a - 1 for a in answer]
            self.question.A = ';'.join(map(str, answers))

        self.show_answer()
        self.check_data_before_save()
        self.answer_type_list.setEnabled(len(self.question.choices) == 0)

    def on_radio_button_select(self):
        self.question.A = str(self.radio_group.checkedId())
        self.check_data_before_save()

    def on_checkbox_select(self):
        answer_id, answers = 0, []
        for button in self.check_group.buttons():
            if isinstance(button, CheckBox):
                if button.isChecked():
                    answers.append(answer_id)
                answer_id += 1
        self.question.A = ';'.join(map(str, answers))
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
            self.pages[1] += 1  # new question
            self.change_order_spinbox.setEnabled(False)
        self.pages[0] += 1
        self.generate_q_data()
        self.show_question()

    def on_delete_question_button(self):
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

    def on_answer_type_changed(self):
        self.question.type = self.answer_type_list.currentIndex() + 1
        self.check_data_before_save()

    def on_answer_text_changed(self):
        text = self.answer_textbox.toPlainText()
        enabled = self.answer_type_list.currentIndex() < 2 and bool(text) and text not in self.question.choices
        self.add_answer_button.setEnabled(enabled)
        self.check_data_before_save()

    def on_add_answer_button(self):
        self.delete_widgets(self.answer_choices_v_layout)
        self.question.choices.append(self.answer_textbox.toPlainText())
        self.answer_textbox.setPlainText('')
        self.answer_type_list.setEnabled(False)
        self.show_answer()
        self.check_data_before_save()

    def on_order_change(self):
        old_page = self.pages[0] - 1
        new_page = self.change_order_spinbox.value() - 1
        reply = QMessageBox.question(self, 'Изменение номера вопроса',
                                     f'Изменить номер вопроса\nс {old_page + 1} на {new_page + 1}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.questions[old_page], self.questions[new_page] = self.questions[new_page], self.questions[old_page]
            self.pages[0] = new_page + 1
            self.question_group.setTitle(f'Вопрос {self.pages[0]} из {self.pages[1]}')
            self.show_navigation_buttons()
            self.check_data_before_save()
        else:
            self.change_order_spinbox.blockSignals(True)
            self.change_order_spinbox.setValue(self.pages[0])
            self.change_order_spinbox.blockSignals(False)

    def check_data_before_save(self):
        q_text = self.question_text.toPlainText()  # question entered
        a_type = self.answer_type_list.currentIndex() + 1
        a_text = self.answer_textbox.toPlainText()  # answer entered for type 3
        if a_type < 3:
            choice = bool(self.question.A) and len(self.question.choices) > 1
        else:
            choice = bool(a_text)
        result = bool(q_text) and choice
        self.prev_button.setEnabled(result and self.pages[0] > 1)
        self.next_button.setEnabled(result)
        self.save_button.setEnabled(result)
        self.delete_button.setEnabled(self.pages[1] > 1)

    def save_question(self):
        if self.new_question:
            self.questions.append(Question())
        answer_type = self.answer_type_list.currentIndex() + 1
        question = self.questions[self.pages[0] - 1]
        question.type = answer_type
        question.Q = self.question_text.toPlainText()
        if answer_type == 1:  # radio
            question.choices = [choice for choice in self.question.choices]
            question.A = self.question.A
        elif answer_type == 2:  # checkbox
            question.choices = [choice for choice in self.question.choices]
            question.A = self.question.A
        else:  # editbox
            question.choices = []
            question.A = self.answer_textbox.toPlainText()
        question.weight = int(self.weight_spinbox.text())
        question.shuffle = self.shuffle_checkbox.isChecked()
        question.show_result = self.show_result_checkbox.isChecked()
        question.note = self.note_text.toPlainText()
        self.change_order_spinbox.setEnabled(True)

    def save_quiz(self):
        self.save_question()
        self.quiz.questions = self.questions
        quizzes = QuizManager()
        quizzes[self.quiz.quiz_id] = self.quiz
        self.open_control_quiz_window()


class ControlUserWindow(Window):
    def __init__(self):
        super().__init__('Участники', 550, 540)
        self.users = UserManager()
        self.quizzes = QuizManager()
        self.history = []
        self.start_index = 0
        self.max_items = 5
        self.setUpWindow()

    def setUpWindow(self):
        # Choose user section
        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        user_list = self.users.get_all_names()
        self.user_combo_box = ComboList(editable=True)
        self.user_combo_box.addItems(user_list)
        self.user_combo_box.setCurrentText('')
        self.user_combo_box.currentTextChanged.connect(self.on_user_name_change)
        user_h_layout.addWidget(self.user_combo_box)

        # Info section
        self.user_quizzes_label = SmallLabel('Пройдено квиз:')
        self.user_answers_label = SmallLabel('Правильных ответов:')

        info_v_layout = QVBoxLayout()
        info_v_layout.addWidget(self.user_quizzes_label)
        info_v_layout.addWidget(self.user_answers_label)

        info_group = Group('Общая информация', fixed_height=80)
        info_group.setLayout(info_v_layout)

        # History section
        self.history_v_layout = QVBoxLayout()

        self.history_up_button = Button('', fixed_width=48)
        self.history_up_button.setIcon(QIcon('images/arrow-up.png'))
        self.history_up_button.clicked.connect(self.on_history_up_button)
        self.history_down_button = Button('', fixed_width=48)
        self.history_down_button.setIcon(QIcon('images/arrow-down.png'))
        self.history_down_button.clicked.connect(self.on_history_down_button)
        history_v_buttons_layout = QVBoxLayout()
        history_v_buttons_layout.addWidget(self.history_up_button)
        history_v_buttons_layout.addStretch()
        history_v_buttons_layout.addWidget(self.history_down_button)

        history_h_layout = QHBoxLayout()
        history_h_layout.addLayout(self.history_v_layout)
        history_h_layout.addLayout(history_v_buttons_layout)
        history_group = Group('История')
        history_group.setLayout(history_h_layout)

        # Buttons section
        self.create_button = Button('Создать')
        self.delete_button = Button('Удалить')
        self.create_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.create_button.clicked.connect(self.on_create_user_button)
        self.delete_button.clicked.connect(self.on_delete_user_button)
        buttons_h_layout = QHBoxLayout()
        buttons_h_layout.addWidget(self.create_button)
        buttons_h_layout.addWidget(self.delete_button)

        button_back = Button('Главное окно')
        button_back.clicked.connect(self.open_main_window)

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(user_h_layout)
        main_v_layout.addWidget(info_group)
        main_v_layout.addWidget(history_group)
        main_v_layout.addLayout(buttons_h_layout)
        main_v_layout.addWidget(button_back)
        self.setLayout(main_v_layout)
        self.user_info()

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()

    def on_user_name_change(self, name: str):
        user_list = self.users.get_all_names()
        self.create_button.setEnabled(bool(name and not name in user_list))
        self.delete_button.setEnabled(bool(name and name in user_list))
        self.start_index = 0
        self.user_info()

    def on_create_user_button(self):
        name = self.user_combo_box.currentText()
        self.user_combo_box.addItem(name)
        self.users.add_user(name)
        self.user_combo_box.setCurrentText('')

    def on_delete_user_button(self):
        name = self.user_combo_box.currentText()
        reply = QMessageBox.question(self, 'Удаление участника',
                                     f'Вы действительно хотите удалить участника\n{name}?\nВсе данные по нему будут удалены!',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.users.remove_user(name)
            self.user_combo_box.clear()
            self.user_combo_box.addItems(self.users.get_all_names())
            self.user_combo_box.setCurrentText('')

    def user_info(self):
        name = self.user_combo_box.currentText()
        selected_user = self.users[name]
        color = 'blue'
        if name in self.users.get_all_names():
            score = selected_user.get_total_score()
            score_text = (f'Правильных ответов {score[0]} из {score[1]} ({score[4]:.2f}%), ' +
                          f'баллов {score[2]} из {score[3]} ({score[5]:.2f}%)')
            self.user_quizzes_label.setText(f'Участником пройдено квиз: {len(selected_user.results)}')
            self.user_answers_label.setText(score_text)
            color = score[-1]
        else:
            if name:
                self.user_quizzes_label.setText('Новый участник')
            else:
                color = 'red'
                self.user_quizzes_label.setText('Участник не указан')
            self.user_answers_label.setText('')
        for widget in [self.user_quizzes_label, self.user_answers_label]:
            change_style(widget, 'color', color)

        # history
        self.delete_widgets(self.history_v_layout)
        if name in self.users.get_all_names():
            self.history = []
            for quiz_id, results in selected_user.results.items():
                score = [sum([case[i] for case in results]) for i in range(4)]
                name = self.quizzes[quiz_id].name
                self.history.append([quiz_id, name, score, len(results)])
            self.history.reverse()
            flag = len(self.history) > self.max_items
            self.history_up_button.setVisible(flag)
            self.history_down_button.setVisible(flag)
            if flag:
                self.enable_history_buttons()
            self.show_history()
        else:
            self.history_up_button.setVisible(False)
            self.history_down_button.setVisible(False)

    def show_history(self):
        if self.max_items >= len(self.history):
            history = self.history
        else:
            history = self.history[self.start_index:self.start_index + self.max_items]
        for i in range(min(self.max_items, len(history))):
            h = history[i]
            score = h[2]
            text = (f'{h[0]} {h[1]}\nпопытки: {h[3]}, ' +
                    f'ответы: {score[0]} из {score[1]} ({count_percent(score[0], score[1])}%), ' +
                    f'баллы: {score[2]} из {score[3]} ({count_percent(score[2], score[3])}%)')
            history_progress_bar = ProgressBar(fixed_height=45)
            history_progress_bar.set_values(score[2], score[3] - score[2], score[3], text)
            self.history_v_layout.addWidget(history_progress_bar)
        self.history_v_layout.addStretch()

    def enable_history_buttons(self):
        self.history_up_button.setEnabled(self.start_index > 0)
        self.history_down_button.setEnabled(self.start_index + self.max_items < len(self.history))

    def on_history_up_button(self):
        self.start_index -= 1
        self.delete_widgets(self.history_v_layout)
        self.show_history()
        self.enable_history_buttons()

    def on_history_down_button(self):
        self.start_index += 1
        self.delete_widgets(self.history_v_layout)
        self.show_history()
        self.enable_history_buttons()


class User:
    """User defenition"""

    def __init__(self, name: str, results=None):
        self.name = name
        self.results = results or {}

    def get_total_score(self) -> List[Any]:
        """Calculate total user score"""
        # score: correct answers, total answered, correct score, total score,
        # percent for questions, percent for score, color for result text
        score = [0, 0, 0, 0, 0, 0, 'green']
        if not self.results:
            return score

        for i in range(4):
            score[i] = sum(rank[i] for quiz in self.results.values() for rank in quiz)

        percent_questions = count_percent(score[0], score[1])
        percent_score = count_percent(score[2], score[3])
        color = self._determine_color(percent_score, score)
        return score[:4] + [percent_questions, percent_score, color]

    @staticmethod
    def _determine_color(percent: float, score: List[int]) -> str:
        """Determine color for user status"""
        if 90 <= percent < 100:
            return 'orange'
        elif score[1] > score[0]:
            return 'red'
        return 'green'

    def add_quiz_result(self, quiz_id: str, score: List[int]) -> None:
        """Add quiz result"""
        self.results.setdefault(quiz_id, []).append(score + [dt.now().strftime('%d.%m.%Y %H:%M')])

    def remove_quiz(self, quiz_id: str) -> bool:
        """Remove quiz result. Return True, if quiz has been removed."""
        return self.results.pop(quiz_id, None) is not None

    def to_dict(self) -> Dict[str, Any]:
        """Transform object to dict for save"""
        return {'name': self.name, 'results': self.results}

    def __repr__(self) -> str:
        return f"User(name='{self.name}', quizzes={len(self.results)})"


class UserManager:
    """Manager for work with users collection"""

    def __init__(self, data_file=USER_DATA):
        self.data_file = data_file
        self._users: Dict[str, User] = {}  # Храним по имени для быстрого доступа
        self._load_data()

    def _load_data(self) -> None:
        """Load data from json file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._users = {user['name']: User(user['name'], user.get('results', {})) for user in data}
        except (FileNotFoundError, json.JSONDecodeError):
            self._users = {}

    def save_data(self) -> None:
        """Save data in json file"""
        data = [user.to_dict() for user in self._users.values()]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def __len__(self) -> int:
        return len(self._users)

    def __getitem__(self, user_name: str) -> User:
        if user_name not in self._users:
            return User(user_name)
        return self._users[user_name]

    def __delitem__(self, user_name: str) -> None:
        if user_name in self._users:
            del self._users[user_name]
            self.save_data()
        else:
            raise KeyError(f"User '{user_name}' not found")

    def __contains__(self, user_name: str) -> bool:
        return user_name in self._users

    def get_all_names(self) -> List[str]:
        """Get list of all user names"""
        return list(self._users.keys())

    def add_user(self, name: str, save: bool = True) -> bool:
        """Add new user. Return True, if user has been added successfully, False, if user already exists."""
        if name in self._users:
            return False
        self._users[name] = User(name)
        if save:
            self.save_data()
        return True

    def remove_user(self, user_name: str, save: bool = True) -> bool:
        """Remove user. Return True, if user removed successfully."""
        if user_name in self._users:
            del self._users[user_name]
            if save:
                self.save_data()
            return True
        return False

    def remove_quiz_from_all(self, quiz_id: str, save: bool = True) -> int:
        """Remove quiz from all users. Returns the number of users who had the test removed."""
        count = 0
        for user in self._users.values():
            if user.remove_quiz(quiz_id):
                count += 1
        if save and count > 0:
            self.save_data()
        return count

    def save_quiz_for_user(self, user_name: str, quiz_id: str, score: List[int], save: bool = True) -> bool:
        """Save quiz result for user. Return True, if result has been saved successfully."""
        if user_name not in self._users:
            return False
        self._users[user_name].add_quiz_result(quiz_id, score)
        if save:
            self.save_data()
        return True


@dataclass
class Question:
    """Represents a single quiz question"""
    type: int = 1  # 1 - radio, 2 - checkbox, 3 - editbox
    Q: str = ""  # question text
    choices: List[str] = None
    A: str = ""  # semicolon-separated answers
    weight: int = 1  # answer weight of successful result
    shuffle: bool = True  # need to shuffle answers every time a question is shown
    show_result: bool = True  # show correct answers if the answer is incorrect
    note: str = ""  # (optional) additional information after answer has been given

    def __post_init__(self):
        if self.choices is None:
            self.choices = []

    def __str__(self):
        if self.Q:
            answers = 1 if self.type == 3 else len(self.choices)
            answer_type = self.types()[self.type - 1].lower()
            return f'{self.Q}, тип: {answer_type}, ответов: {answers}'
        return ''

    def get_answers(self) -> int | List[int] | str:
        """Get all answers to a question depending on the type of question"""
        answers = self.A  # type = editbox
        if self.type == 1:  # radio
            answers = int(answers) if answers else -1
        elif self.type == 2:  # checkbox
            answers = list(map(int, answers.split(';'))) if answers else []
        return answers

    @staticmethod
    def types() -> List[str]:
        """List of all types of questions"""
        types = ['Один ответ', 'Несколько ответов', 'Текстовый ответ']
        return types


class Quiz:
    """Represents a single quiz with its metadata and questions"""

    def __init__(self, quiz_id: str, questions: List[Question] = None, name: str = "", playsound: bool = True):
        self.quiz_id = quiz_id
        self.name = name
        self.playsound = playsound
        self.questions = questions or []

    def add_question(self, question: Question) -> None:
        """Add a question to the quiz"""
        self.questions.append(question)

    def remove_question(self, index: int) -> bool:
        """Remove a question by index. Returns True if successful"""
        if 0 <= index < len(self.questions):
            del self.questions[index]
            return True
        return False

    def get_total_score(self) -> int:
        """Calculate total possible score (sum of all question weights)"""
        return sum(q.weight for q in self.questions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert quiz to dictionary for serialization"""
        return {
            'id': self.quiz_id,
            'name': self.name,
            'playsound': self.playsound,
            'questions': [
                {
                    'type': q.type,
                    'Q': q.Q,
                    'choices': q.choices,
                    'A': q.A,
                    'weight': q.weight,
                    'shuffle': q.shuffle,
                    'show_result': q.show_result,
                    'note': q.note
                }
                for q in self.questions
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quiz':
        """Create Quiz instance from dictionary"""
        quiz = cls(
            quiz_id=data['id'],
            name=data.get('name', ''),
            playsound=data.get('playsound', True)
        )
        for q_data in data.get('questions', []):
            question = Question(
                type=q_data['type'],
                Q=q_data['Q'],
                choices=q_data.get('choices', []),
                A=q_data['A'],
                weight=q_data.get('weight', 1),
                shuffle=q_data.get('shuffle', True),
                show_result=q_data.get('show_result', True),
                note=q_data.get('note', '')
            )
            quiz.add_question(question)
        return quiz

    def __repr__(self) -> str:
        return f"Quiz(id='{self.quiz_id}', name='{self.name}', questions={len(self.questions)})"

    def __str__(self):
        return (self.quiz_id + ' ' + self.name).strip()


class QuizManager:
    """Manager for handling multiple quizzes and their persistence"""

    def __init__(self, data_file=QUIZ_DATA):
        self.data_file = data_file
        self._quizzes: Dict[str, Quiz] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load quizzes from file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._quizzes = {quiz_data['id']: Quiz.from_dict(quiz_data) for quiz_data in data}
        except (FileNotFoundError, json.JSONDecodeError):
            self._quizzes = {}

    def save_data(self) -> None:
        """Save all quizzes to file"""
        data = [quiz.to_dict() for quiz in self._quizzes.values()]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def __len__(self) -> int:
        return len(self._quizzes)

    def __getitem__(self, quiz_id: str) -> Quiz:
        if quiz_id not in self._quizzes:
            raise KeyError(f"Quiz with ID '{quiz_id}' not found")
        return self._quizzes[quiz_id]

    def __setitem__(self, quiz_id: str, quiz: Quiz) -> None:
        self._quizzes[quiz_id] = quiz
        self.save_data()

    def __delitem__(self, quiz_id: str) -> None:
        if quiz_id in self._quizzes:
            del self._quizzes[quiz_id]
            self.save_data()
        else:
            raise KeyError(f"Quiz with ID '{quiz_id}' not found")

    def __contains__(self, quiz_id: str) -> bool:
        return quiz_id in self._quizzes

    def __iter__(self):
        return iter(self._quizzes.values())

    def get_quiz_ids(self) -> List[str]:
        """Get list of all quiz IDs"""
        return list(self._quizzes.keys())


def count_percent(n: int, total: int) -> float:
    """Сalculating percentage of successful answers from all questions"""
    return 0 if total == 0 else round(n / total * 100, 2)


def choose_plural(amount: int, declensions: Tuple[str, str, str]) -> str:
    """Show the number of subjects in the corresponding declension"""
    if amount % 10 == 1 and amount % 100 != 11:
        return f'{amount} {declensions[0]}'
    elif (amount % 10 == 2 and amount % 100 != 12 or
          amount % 10 == 3 and amount % 100 != 13 or
          amount % 10 == 4 and amount % 100 != 14):
        return f'{amount} {declensions[1]}'
    else:
        return f'{amount} {declensions[2]}'


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
    sys.exit(app.exec())
