# TODO:
#   - scrollbar
#   - participants
#   - setup for quizzes

import sys, pygame
import loader
from random import shuffle
from widget_settings import *

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QButtonGroup
# from PyQt6.QtGui import QPalette
from PyQt6.QtCore import Qt

QUIZ_DATA = 'data/quiz.json'
USER_DATA = 'data/user.json'
RESULT_SOUND = ['data/farts.wav', 'data/glee-30.wav']


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
        super().__init__('Выбор квиза', 500, 400)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        user_label = Label('Участник')
        user_h_layout = QHBoxLayout()
        user_h_layout.addWidget(user_label)

        self.quiz = loader.get_json_data(QUIZ_DATA)
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

        self.confirm_button = Button('Подтвердить', fixed_width=200)
        self.confirm_button.clicked.connect(self.on_click_confirm)

        # Status Bar
        self.progressbar = ProgressBar()

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(self.question_group)
        main_v_layout.addWidget(self.answer_group)
        # main_v_layout.addStretch()
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
            self.radio_group.buttonToggled.connect(self.on_radio_button_select)
            self.answer_v_layout.addStretch()  # чтобы не растягивались по всему layout
        elif self.answer_type == 2:  # checkbox
            self.answer_group.setTitle('Выберите один или несколько ответов')
            self.check_group = QButtonGroup(self)
            self.check_group.setExclusive(False)
            for case in choices:
                checkbox = CheckBox(case)
                self.check_group.addButton(checkbox)
                self.answer_v_layout.addWidget(checkbox)
            self.check_group.buttonToggled.connect(self.on_checkbox_select)
            self.answer_v_layout.addStretch()  # чтобы не растягивались по всему layout
        elif self.answer_type == 3:  # editbox
            self.answer_group.setTitle('Напишите ответ')
            self.edit_result = EditBox()
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

    def delete_widgets(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()
            if child_layout is not None:
                self.delete_widgets(child_layout)
                child_layout.deleteLater()


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
        super().__init__('Управление квизами', 570, 300)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label('Номер квиза')
        quiz_h_layout = QHBoxLayout()
        quiz_h_layout.addWidget(quiz_label)

        self.quiz = loader.get_json_data(QUIZ_DATA)
        self.quiz_list = [q['id'] for q in self.quiz]
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
        self.window = CreateQuizWindow(self.quiz_combo_box.currentText(), self.name_editbox.text())
        self.window.show()
        self.close()

    def on_quiz_number_change(self, text):
        self.change_button.setText('Изменить')
        self.to_save = False
        self.create_button.setEnabled(bool(text and not text in self.quiz_list))
        self.change_button.setEnabled(bool(text and text in self.quiz_list))
        self.delete_button.setEnabled(bool(text and text in self.quiz_list))
        if text and text in self.quiz_list:
            quiz = get_filtered_data('id', self.quiz_combo_box.currentText(), self.quiz)
            self.name_editbox.setText(quiz['name'])
            self.sound_checkbox.setChecked(quiz['playsound'])
        else:
            self.name_editbox.setText('')
            self.sound_checkbox.setChecked(True)

    def on_data_change(self):
        text = self.quiz_combo_box.currentText()
        if text in self.quiz_list:
            q_data = get_filtered_data('id', text, self.quiz)
            if self.sound_checkbox.isChecked() == q_data['playsound'] and self.name_editbox.text() == q_data['name']:
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
            pass


class CreateQuizWindow(Window):
    def __init__(self, quiz_id: str, quiz_name: str):
        self.quiz_id = quiz_id
        self.quiz_name = quiz_name
        super().__init__(f'Создание квиза {quiz_id}', 565, 300)
        self.setUpWindow()

    def setUpWindow(self):
        quiz_label = Label(f'Квиз {self.quiz_id}')

        quiz_name_label = Label('Название')
        quiz_name_h_layout = QHBoxLayout()
        quiz_name_h_layout.addWidget(quiz_name_label)

        self.name_editbox = EditBox(text=self.quiz_name)
        # self.name_editbox.textEdited.connect(self.on_data_change)
        quiz_name_h_layout.addWidget(self.name_editbox)

        self.save_button = Button('Сохранить', fixed_width=150)
        cancel_button = Button('Отменить', fixed_width=150)
        self.save_button.clicked.connect(self.open_control_quiz_window)
        cancel_button.clicked.connect(self.open_control_quiz_window)

        footer_buttons_h_layout = QHBoxLayout()
        footer_buttons_h_layout.addWidget(self.save_button)
        footer_buttons_h_layout.addStretch()
        footer_buttons_h_layout.addWidget(cancel_button)

        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(quiz_label)
        main_v_layout.addLayout(quiz_name_h_layout)
        main_v_layout.addLayout(footer_buttons_h_layout)
        self.setLayout(main_v_layout)

    def open_control_quiz_window(self):
        self.window = ControlQuizWindow()
        self.window.show()
        self.close()


def count_percent(n: int, total: int) -> float:
    return 0 if total == 0 else round(n / total * 100, 2)


def get_filtered_data(key: str, value: str, data: dict) -> dict:
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
