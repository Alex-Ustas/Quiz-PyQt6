# TODO:
#   - QuizWindow: scrollbar
#   - CreateChangeQuizWindow: scrollbar
#   - add parameter weight for quiz

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
        html_text = """
        <h3><p><b>Автор:</b> Фадеичев Александр</p></h3>
        <p><b>Telegram:</b> @AlexUstas0</p>
        <p><b>email:</b> alex.ustas@internet.ru</p>
        <p><b>Версия:</b> 1.0 (2026.04)</p>
        """
        reply = QMessageBox.information(self, 'О программе', html_text)


class SelectQuizWindow(Window):
    def __init__(self):
        super().__init__('Выбор квиза', 500, 380)
        self.quizzes = Quiz()
        self.users = User()
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        quiz_list = self.quizzes.get_id_list()
        quiz_list.insert(0, 'Выберите квиз')
        self.quiz_combo_box = ComboList()
        self.quiz_combo_box.addItems(quiz_list)
        self.quiz_combo_box.currentIndexChanged.connect(self.on_select_quiz)
        quiz_h_layout.addWidget(self.quiz_combo_box)

        user_list = self.users.get_name_list()
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
        self.window = QuizWindow(self.quiz_combo_box.currentText(), self.user_combo_box.currentText())
        self.window.show()
        self.close()

    def on_select_quiz(self, index: int):
        self.quiz_name_label.setText(f'Название квиза:')
        self.quiz_questions_label.setText(f'Всего вопросов:')
        if index:
            selected_quiz = self.quizzes[self.quiz_combo_box.itemText(index)]
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
            user_id = self.user_combo_box.itemText(index)
            selected_user = self.users[user_id]
            answered, total, percent = self.users.get_total_score(user_id)
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
    def __init__(self, quiz_id: str, user_id: str):
        self.quiz = Quiz(quiz_id)
        self.user = User(user_id)
        self.question = 0  # question number
        self.answer_type = None  # answer type: 1 - radio, 2 - checkbox, 3 - editbox
        self.to_confirm = True  # switch for confirm button
        self.score = [0, 0, len(self.quiz.questions)]  # result: correct answers, total answered, total questions
        self.correct_answers = []

        super().__init__(f'Quiz {str(self.quiz)}', 1000, 800)
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
        q_data = self.quiz.questions[self.question]
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
        show_result = self.quiz.questions[self.question]['show_result']
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
            note = self.quiz.questions[self.question]['note']
            if note:
                self.note_label.setText(note)
                self.note_label.setHidden(False)

            self.score[0] += match
            self.score[1] += 1
            self.update_statusbar()
        else:  # next question
            if self.question == self.score[2] - 1:  # open result window
                self.window = ResultWindow(self.quiz.quiz_id, self.user.name, self.score)
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
        status_text = f'{self.user.name}: правильных ответов {self.score[0]} из {self.score[1]}'
        self.progressbar.set_values(self.score[0], self.score[1] - self.score[0], self.score[2], status_text)


class ResultWindow(Window):
    def __init__(self, quiz_id: str, user_id: str, score: list[int]):
        self.quiz = Quiz(quiz_id)
        self.user = User(user_id)
        self.score = score
        self.max_score = score[0] == score[1]
        super().__init__('Результат', 400, 250)
        self.setUpWindow()

    def setUpWindow(self):
        user_label = Label(self.user.name, fixed_height=0)
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setWordWrap(True)

        quiz_label = Label(str(self.quiz), fixed_height=0)
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

        if self.quiz.quiz_id not in self.user.results:
            attempt_text = 'Первая попытка'
            if self.max_score:
                attempt_text += '. Отличный результат!'
        else:
            quiz_results = self.user.results[self.quiz.quiz_id]
            attempt_text = f'Попытка {len(quiz_results) + 1}'
            if self.max_score or self.score[0] / self.score[1] > max([s[0] / s[1] for s in quiz_results]):
                attempt_text += '. Лучший результат!'
        attempt_label = Label(attempt_text, fixed_height=0)
        attempt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_style(attempt_label, 'color', 'green')

        answered, total, _ = self.user.get_total_score()
        answered += self.score[0]
        total += self.score[1]
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

        self.user.save_quiz_for_user(self.quiz.quiz_id, self.score)

    def open_main_window(self):
        self.window = WelcomeWindow()
        self.window.show()
        self.close()


class ControlQuizWindow(Window):
    def __init__(self):
        self.to_save = False  # switch for save/change
        self.quiz = Quiz()
        self.quiz_list = self.quiz.get_id_list()
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
        self.create_button.clicked.connect(self.open_create_cnahge_window)
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

    def open_create_cnahge_window(self):
        data = (self.quiz_combo_box.currentText(), self.name_editbox.text(), self.sound_checkbox.isChecked())
        self.window = CreateChangeQuizWindow(data)
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
            quiz = self.quiz[self.quiz_combo_box.currentText()]
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
            q_data = self.quiz[quiz_id]
            if self.sound_checkbox.isChecked() == q_data['playsound'] and quiz_name == q_data['name']:
                self.change_button.setText('Изменить')
                self.to_save = False
            else:
                self.change_button.setText('Сохранить')
                self.to_save = True

    def on_change_button(self):
        if self.to_save:
            self.quiz[self.quiz_combo_box.currentText()]['name'] = self.name_editbox.text()
            self.quiz[self.quiz_combo_box.currentText()]['playsound'] = self.sound_checkbox.isChecked()
            self.quiz.save()
            self.change_button.setText('Изменить')
            self.to_save = False
        else:
            self.open_create_cnahge_window()

    def on_delete_button(self):
        quiz_id = self.quiz_combo_box.currentText()
        reply = QMessageBox.question(self, 'Удаление квиза',
                                     f'Вы действительно хотите удалить квиз\n{quiz_id} {self.name_editbox.text()}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.quiz[quiz_id]
            self.quiz_list = self.quiz.get_id_list()
            self.name_editbox.setText('')
            self.sound_checkbox.setChecked(True)
            self.quiz_combo_box.clear()
            self.quiz_combo_box.addItems(self.quiz_list)
            self.quiz_combo_box.setCurrentText('')

            users = User()
            users.remove_quiz(quiz_id)
            self.quiz.save()


class CreateChangeQuizWindow(Window):
    def __init__(self, quiz_data: tuple):
        self.quiz_id, self.quiz_name, self.playsound = quiz_data
        self.quiz = Quiz(self.quiz_id)
        self.new_question = self.is_new = not bool(self.quiz.quiz)
        self.questions = self.quiz.questions  # data for all questions
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
            self.question = self.quiz.get_default_question_data()
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

        # navigation section
        self.show_navigation_buttons()
        self.change_order_spinbox.blockSignals(True)
        self.change_order_spinbox.setMaximum(self.pages[1])
        self.change_order_spinbox.setValue(self.pages[0])
        self.change_order_spinbox.blockSignals(False)

        self.check_data_before_save()

    def show_answer(self):
        answer_type = self.answer_type_list.currentIndex() + 1
        if answer_type == 1:  # radio
            answer = int(self.question['A']) if self.question['A'] else -1
            self.answer_textbox.setPlainText('')
            self.radio_group = QButtonGroup(self)
            for i, text in enumerate(self.question['choices']):
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
            answers = list(map(int, self.question['A'].split(';'))) if self.question['A'] else []
            self.answer_textbox.setPlainText('')
            self.check_group = QButtonGroup(self)
            self.check_group.setExclusive(False)
            for i, text in enumerate(self.question['choices']):
                delete_answer_button = Button('', fixed_width=28, fixed_height=27, icon_size=16)
                delete_answer_button.setIcon(QIcon('images/delete.png'))
                delete_answer_button.clicked.connect(lambda checked, idx=i: self.on_delete_answer_button(idx))

                checkbox = CheckBox(text)
                if i in answers:
                    checkbox.setChecked(True)

                answer_choices_h_layout = QHBoxLayout()
                answer_choices_h_layout.addWidget(delete_answer_button)
                answer_choices_h_layout.addWidget(checkbox)

                self.check_group.addButton(checkbox, i)
                self.check_group.addButton(delete_answer_button)
                self.answer_choices_v_layout.addLayout(answer_choices_h_layout)
            self.check_group.buttonToggled.connect(self.on_checkbox_select)  # type: ignore

        else:  # editbox
            self.answer_textbox.setPlainText(self.question['A'])
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
        del self.question['choices'][index]
        answer_type = self.answer_type_list.currentIndex() + 1
        if answer_type == 1:  # radio
            answer = int(self.question['A']) if self.question['A'] else -1
            if index == answer:
                self.question['A'] = ''
            if answer > index:
                self.question['A'] = str(answer - 1)
        else:  # checkbox
            answers = list(map(int, self.question['A'].split(';'))) if self.question['A'] else []
            if index in answers:
                answers.remove(index)
            answers = [a if a < index else a - 1 for a in answers]
            self.question['A'] = ';'.join(map(str, answers))

        self.show_answer()
        self.check_data_before_save()
        self.answer_type_list.setEnabled(len(self.question['choices']) == 0)

    def on_radio_button_select(self):
        self.question['A'] = str(self.radio_group.checkedId())
        self.check_data_before_save()

    def on_checkbox_select(self):
        answer_id, answers = 0, []
        for button in self.check_group.buttons():
            if isinstance(button, CheckBox):
                if button.isChecked():
                    answers.append(answer_id)
                answer_id += 1
        self.question['A'] = ';'.join(map(str, answers))
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
            question['A'] = self.question['A']
        elif answer_type == 2:  # checkbox
            question['choices'] = [choice for choice in self.question['choices']]
            question['A'] = self.question['A']
        else:  # editbox
            question['choices'] = []
            question['A'] = self.answer_textbox.toPlainText()
        question['weight'] = int(self.weight_spinbox.text())
        question['shuffle'] = self.shuffle_checkbox.isChecked()
        question['show_result'] = self.show_result_checkbox.isChecked()
        question['note'] = self.note_text.toPlainText()
        self.change_order_spinbox.setEnabled(True)

    def save_quiz(self):
        self.save_question()
        self.quiz[self.quiz_id] = (self.quiz_name, self.playsound, self.questions)
        self.quiz.save()
        self.open_control_quiz_window()


class ControlUserWindow(Window):
    def __init__(self):
        super().__init__('Участники', 550, 530)
        self.users = User()
        self.quizzes = Quiz()
        self.history = []
        self.start_index = 0
        self.max_items = 7
        self.setUpWindow()

    def setUpWindow(self):
        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        user_list = self.users.get_name_list()
        self.user_combo_box = ComboList(editable=True)
        self.user_combo_box.addItems(user_list)
        self.user_combo_box.setCurrentText('')
        self.user_combo_box.currentTextChanged.connect(self.on_user_name_change)
        user_h_layout.addWidget(self.user_combo_box)

        self.user_quizzes_label = SmallLabel('Пройдено квиз:')
        self.user_answers_label = SmallLabel('Правильных ответов:')

        info_v_layout = QVBoxLayout()
        info_v_layout.addWidget(self.user_quizzes_label)
        info_v_layout.addWidget(self.user_answers_label)

        info_group = Group('Общая информация', fixed_height=80)
        info_group.setLayout(info_v_layout)

        self.history_v_layout = QVBoxLayout()

        self.history_up_button = Button('', fixed_width=50)
        self.history_up_button.setIcon(QIcon('images/arrow-up.png'))
        self.history_up_button.clicked.connect(self.on_history_up_button)
        self.history_down_button = Button('', fixed_width=50)
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
        user_list = self.users.get_name_list()
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
            del self.users[name]
            self.users.save()
            self.user_combo_box.clear()
            self.user_combo_box.addItems(self.users.get_name_list())
            self.user_combo_box.setCurrentText('')

    def user_info(self):
        name = self.user_combo_box.currentText()
        selected_user = User(name)
        color = 'blue'
        if selected_user.user:
            answered, total, percent = self.users.get_total_score(name)
            self.user_quizzes_label.setText(f'Участником пройдено квиз: {len(selected_user.results)}')
            self.user_answers_label.setText(f'Правильных ответов {answered} из {total} ({percent:.2f}%)')
            color = 'green'
            if 90 <= percent < 100:
                color = 'orange'
            elif total > answered:
                color = 'red'
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
        if selected_user.user:
            self.history = []
            for quiz_id, results in selected_user.results.items():
                answered = sum([case[0] for case in results])
                total = sum([case[1] for case in results])
                name = self.quizzes[quiz_id]['name']
                name = name if len(name + quiz_id) < 35 else name[:35 - len(quiz_id)] + '...'
                self.history.append([quiz_id, name, answered, total, len(results)])
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
            history_progress_bar = ProgressBar()
            percent = count_percent(h[2], h[3])
            text = f'{h[0]} {h[1]}, попытки: {h[4]}, {h[2]} из {h[3]} ({percent}%)'
            history_progress_bar.set_values(h[2], h[3] - h[2], h[3], text)
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
    def __init__(self, user_id=None):
        self.users = self.load()
        self.user = self[user_id]
        self.name = user_id if user_id else ''
        self.results = self[user_id]['results'] if self.user else {}

    def __len__(self):
        return len(self.users)

    def __getitem__(self, user_id):
        user = list(filter(lambda x: x['name'] == user_id, self.users))
        return user[0] if user else {}

    def __delitem__(self, index):
        if isinstance(index, str):
            del self.users[self.get_index_by_name(index)]
        else:
            del self.users[index]

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.user)

    def get_name_list(self):
        return [self.users[i]['name'] for i in range(len(self))]

    def get_total_score(self, name=None):
        user = self[name] if name else self.user
        if user:
            answered = sum([rank[0] for quiz in user['results'].values() for rank in quiz])
            total = sum([rank[1] for quiz in user['results'].values() for rank in quiz])
            return answered, total, count_percent(answered, total)
        else:
            return 0, 0, 0

    def get_index_by_name(self, name: str):
        index_list = list(filter(lambda q: q[1]['name'] == name, enumerate(self.users)))
        return index_list[0][0] if index_list else None

    def add_user(self, name, save=True):
        if not name in self.get_name_list():
            self.users.append({'name': name, 'results': {}})
            if save:
                self.save()

    def remove_quiz(self, quiz_id: str, save=True):
        for user in self.users:
            user['results'].pop(quiz_id, None)
        if save:
            self.save()

    @staticmethod
    def load():
        return loader.get_json_data(USER_DATA)

    def save(self):
        loader.save_data(USER_DATA, self.users)

    def save_quiz_for_user(self, quiz_id: str, score: list):
        loader.save_user_data(USER_DATA, self.name, quiz_id, score)


class Quiz:
    def __init__(self, quiz_id=None):
        self.quizzes = self.load()
        self.quiz = self[quiz_id]
        self.quiz_id = quiz_id if quiz_id else ''
        self.name = self.quiz['name'] if self.quiz else ''
        self.questions = self.quiz['questions'] if self.quiz else []
        self.playsound = self.quiz['playsound'] if self.quiz else True

    def __len__(self):
        return len(self.quizzes)

    def __getitem__(self, quiz_id):
        quiz = list(filter(lambda x: x['id'] == quiz_id, self.quizzes))
        return quiz[0] if quiz else {}

    def __setitem__(self, quiz_id, data):
        quiz_name, playsound, questions = data
        quiz = self[quiz_id]
        if not bool(quiz):
            self.quizzes.append({})
            quiz = self.quizzes[-1]
            quiz['id'] = quiz_id
            quiz['name'] = quiz_name
            quiz['playsound'] = playsound
        quiz['questions'] = questions

    def __delitem__(self, index):
        if isinstance(index, str):
            del self.quizzes[self.get_index_by_id(index)]
        else:
            del self.quizzes[index]

    def __str__(self):
        return (self.quiz_id + ' ' + self.name).strip()

    def __repr__(self):
        return repr(self.quiz)

    def __contains__(self, item):
        return item in self.get_id_list()

    def __iter__(self):
        yield from self.quizzes

    def get_index_by_id(self, quiz_id: str):
        index_list = list(filter(lambda q: q[1]['id'] == quiz_id, enumerate(self.quizzes)))
        return index_list[0][0] if index_list else None

    def get_id_list(self):
        return [self.quizzes[i]['id'] for i in range(len(self))]

    @staticmethod
    def get_default_question_data():
        return {'type': 1,
                'Q': '',
                'choices': [],
                'A': '',
                'weight': 1,
                'shuffle': True,
                'show_result': True,
                'note': ''}

    @staticmethod
    def load():
        return loader.get_json_data(QUIZ_DATA)

    def save(self):
        loader.save_data(QUIZ_DATA, self.quizzes)


def count_percent(n: int, total: int) -> float:
    return 0 if total == 0 else round(n / total * 100, 2)


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
