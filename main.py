import csv
import io
import sqlite3
import sys

from random import choice, sample

from PyQt5.QtGui import QIcon, QPixmap

from googletrans import Translator
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QInputDialog, QDialog, QWidget, \
    QLabel, QMessageBox, QFileDialog

RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчъыьэюя'
ENGLISH_ALPHABET = 'abcdefghigklmnopqrstuvwsyz'


def check_language(wordd):  # функция проверки языка строки
    for i in RUSSIAN_ALPHABET:
        if i in wordd.lower():
            return 'ru'
    for i in ENGLISH_ALPHABET:
        if i in wordd.lower():
            return 'en'


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.lang = 'ru'
        self.connection = sqlite3.connect('database.db')
        self.initUi()

    def initUi(self):  # рендер главного окна
        uic.loadUi('main_window.ui', self)
        self.setFixedSize(400, 500)
        self.my_words.clicked.connect(self.my_words_render)
        self.learnt_words.clicked.connect(self.learnt_words_render)
        self.test.clicked.connect(self.test_render)
        self.language.clicked.connect(self.change_language)
        self.progress.hide()
        if self.lang == 'en':  # изменение текста виджетов в зависимости от языка
            self.setWindowTitle('Dictionary')
            self.main_label.setText('Dicrionary')
            self.learnt_words.setText('Learnt words')
            self.my_words.setText('My words')
            self.progress.setText('Progress')
            self.test.setText('Take a test')
            self.language.setIcon(QIcon('english.jpeg'))
        elif self.lang == 'ru':
            self.setWindowTitle('Словарь')
            self.main_label.setText('Словарь')
            self.learnt_words.setText('Изученные слова')
            self.my_words.setText('Мои слова')
            self.progress.setText('Прогресс')
            self.test.setText('Пройти тест')
            self.language.setIcon(QIcon('russian.png'))

    def my_words_render(self):  # рендер окна "Мои слова"
        uic.loadUi('my_words_window.ui', self)
        self.go_back.setIcon(QIcon('arrow-back-8.png'))
        self.go_back.clicked.connect(self.go_back_to_main_window)
        self.add_word.clicked.connect(self.addword)
        self.delete_items.clicked.connect(lambda: self.deleteitems('words_learn'))
        self.replace_items.clicked.connect(lambda: self.replaceitems('words_learn'))
        self.add_image.clicked.connect(self.addimage)
        self.render_table()
        if self.lang == 'ru':  # изменение текста виджетов в зависимости от языка
            self.add_word.setText('Добавить слово')
            self.delete_items.setText('Удалить')
            self.replace_items.setText('Переместить в изученное')
            self.setWindowTitle('Мои слова')
            self.tableWidget.setHorizontalHeaderLabels(['слово', 'перевод'])
            self.add_image.setText('Добавить изображение')
        elif self.lang == 'en':
            self.add_image.setText('Add image')
            self.add_word.setText('Add word')
            self.delete_items.setText('Delete')
            self.replace_items.setText('Move to learnt words')
            self.setWindowTitle('My words')
            self.tableWidget.setHorizontalHeaderLabels(['word', 'translation'])

    def learnt_words_render(self):  # рендер окна "Изученные слова"
        uic.loadUi('learnt_words_window.ui', self)
        self.go_back.setIcon(QIcon('arrow-back-8.png'))
        self.render_table_2()
        self.delete_items.clicked.connect(lambda: self.deleteitems('words_learnt'))
        self.replace_items.clicked.connect(lambda: self.replaceitems('words_learnt'))
        self.go_back.clicked.connect(self.go_back_to_main_window)
        if self.lang == 'ru':  # изменение текста виджетов в зависимости от языка
            self.delete_items.setText('Удалить')
            self.replace_items.setText('Переместить в изучаемые')
            self.setWindowTitle('Изученные слова')
            self.tableWidget.setHorizontalHeaderLabels(['слово', 'перевод'])
        elif self.lang == 'en':
            self.delete_items.setText('Delete')
            self.replace_items.setText('Move to my words')
            self.setWindowTitle('Learnt words')
            self.tableWidget.setHorizontalHeaderLabels(['word', 'translation'])

    def render_table(self):  # рендер таблицы в окне "Мои слова"
        query = 'SELECT english, russian, image FROM words_learn'
        res = self.connection.cursor().execute(query).fetchall()
        self.tableWidget.setColumnCount(3)
        if self.lang == 'ru':  # изменение текста виджетов в зависимости от языка
            self.tableWidget.setHorizontalHeaderLabels(['слово', 'перевод', 'картинка'])
        elif self.lang == 'en':
            self.tableWidget.setHorizontalHeaderLabels(['word', 'translation', 'image'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 2:
                    item = self.getImageLabel(str(elem))
                    self.tableWidget.setCellWidget(i, j, item)
                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        self.tableWidget.verticalHeader().setDefaultSectionSize(80)

    def test_render(self):  # рендер теста
        # получаем раздел по которому будет тест
        if self.lang == 'ru':  # изменение текста виджетов в зависимости от языка
            table, ok = QInputDialog.getItem(
                self, 'Выберите раздел', 'По какому разделу вы хотите пройти тест?',
                ('', 'Мои слова', "Изученные слова"), 0, False)
            if table == 'Мои слова':
                query = 'SELECT COUNT (*) FROM words_learn'
            elif table == 'Изученные слова':
                query = 'SELECT COUNT (*) FROM words_learnt'
            else:
                return
        elif self.lang == 'en':
            table, ok = QInputDialog.getItem(
                self, 'Select section', 'What section you would like to test?',
                ('', 'My words', "Learnt words"), 0, False)
            if table == 'My words':
                query = 'SELECT COUNT (*) FROM words_learn'
            elif table == 'Learnt words':
                query = 'SELECT COUNT (*) FROM words_learnt'
            else:
                return

        res = int(self.connection.cursor().execute(query).fetchone()[0])
        if res == 0:
            a = QMessageBox()
            if self.lang == 'ru':
                a.setWindowTitle('В таблице нет записей')
                a.setInformativeText('Добавьте хотя бы одно слово')
                a.exec()
                return
            elif self.lang == 'en':
                a.setWindowTitle('No records in the table')
                a.setInformativeText('Add at least one word')
                a.exec()
                return

        if ok:  # получаем кол-во слов в тесте
            if self.lang == 'ru':
                n, ok = QInputDialog.getInt(
                    self, "Введите количество строк", f"Сколько слов будет в тесте? \n максимум - {res}", 1, 1, res, 1)
            elif self.lang == 'en':
                n, ok = QInputDialog.getInt(
                    self, "enter number of lines", f"How many words will there be in the test? \n max - {res}", 1, 1,
                    res, 1)

        if table == 'Мои слова':
            query = 'SELECT english, russian FROM words_learn'
        elif table == 'My words':
            query = 'SELECT english, russian FROM words_learn'
        elif table == 'Изученные слова':
            query = 'SELECT english, russian FROM words_learnt'
        elif table == 'Learnt words':
            query = 'SELECT english, russian FROM words_learnt'
        words = self.connection.cursor().execute(query).fetchall()

        words = sample(words, k=n)  # берем n рандомных слов из базы данных
        self.right_answers = 0
        self.wrong_answers = []

        self.generate_task(words, 0, table)

    def render_table_2(self):  # рендер таблицы из окна "Изученные слова"
        query = 'SELECT english, russian,image FROM words_learnt'
        res = self.connection.cursor().execute(query).fetchall()
        self.tableWidget.setColumnCount(3)

        if self.lang == 'ru':  # изменение текста виджетов в зависимости от языка
            self.tableWidget.setHorizontalHeaderLabels(['слово', 'перевод', 'картинка'])
        elif self.lang == 'en':
            self.tableWidget.setHorizontalHeaderLabels(['word', 'translation', 'image'])

        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 2:
                    item = self.getImageLabel(str(elem))
                    self.tableWidget.setCellWidget(i, j, item)
                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.verticalHeader().setDefaultSectionSize(80)

    def getImageLabel(self, image):  # функция получения изображения для вставки в tableWidget
        imageLabel = QLabel()
        imageLabel.setText('')
        imageLabel.setScaledContents(True)
        pixmap = QPixmap(image)
        imageLabel.setPixmap(pixmap)
        return imageLabel

    def generate_task(self, words, idx, table):  # генерация одного впороса в тесте
        uic.loadUi('test_window.ui', self)
        self.go_back.setIcon(QIcon('arrow-back-8.png'))
        self.go_back.clicked.connect(self.go_back_to_main_window)

        if self.lang == 'en':
            self.submit.setText('Submit')
            self.setWindowTitle('Test')
            self.test_label.setText('Test')
        elif self.lang == 'ru':
            self.submit.setText('Ответить')
            self.setWindowTitle('Тест')
            self.test_label.setText('Тест')

        english_words = []
        russian_words = []

        with open('enlish__russian_words.csv', 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for i in reader:
                english_words.append(i['english'])
                russian_words.append(i['russian'])
        word = choice(words[idx])  # получение 4 рандомных слов из csv файла
        self.word.setText(word)

        if self.lang == 'ru':
            self.amount_left.setText("Осталось слов: " + str(len(words) - idx))
        elif self.lang == 'en':
            self.amount_left.setText("Words left: " + str(len(words) - idx))

        if check_language(word) == 'ru':  # изменение текста виджетов в зависимости от языка
            four_words = sample(english_words, k=4)
            if table == 'Мои слова':
                query = 'SELECT english FROM words_learn WHERE russian = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'My words':
                query = 'SELECT english FROM words_learn WHERE russian = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'Изученные слова':
                query = 'SELECT english FROM words_learnt WHERE russian = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'Learnt words':
                query = 'SELECT english FROM words_learnt WHERE russian = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]

        else:
            four_words = sample(russian_words, k=4)
            if table == 'Мои слова':
                query = 'SELECT russian FROM words_learn WHERE english = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'My words':
                query = 'SELECT russian FROM words_learn WHERE english = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'Изученные слова':
                query = 'SELECT russian FROM words_learnt WHERE english = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]
            elif table == 'Learnt words':
                query = 'SELECT russian FROM words_learnt WHERE english = ?'
                answer = self.connection.cursor().execute(query, (word,)).fetchone()[0]

        self.option_group.setExclusive(True)
        self.option_1.setText(four_words[0])
        self.option_2.setText(four_words[1])
        self.option_3.setText(four_words[2])
        self.option_4.setText(four_words[3])
        answer_option = choice([self.option_1, self.option_2, self.option_3, self.option_4])
        answer_option.setText(answer)
        self.submit.clicked.connect(
            lambda: self.check_answer(answer_option, self.option_group.checkedButton(), word, words, idx + 1, table))

    def check_answer(self, ans, given, word, words, idx, table):  # проверка ответа на вопрос и генерация следующего
        if ans == given:
            self.right_answers += 1
        else:
            self.wrong_answers.append([word, ans.text()])
        if idx < len(words):
            self.generate_task(words, idx, table)
        else:
            self.generate_end()

    def generate_end(self):  # рендер окна конца теста
        uic.loadUi('test_end_window.ui', self)

        if self.lang == 'ru':
            self.label_3.setText('Количество правильных ответов: ' + str(self.right_answers))
        elif self.lang == 'en':
            self.label_3.setText('The number of right answers: ' + str(self.right_answers))

        if self.lang == 'en':
            self.label.setText('The number of mistakes: ' + str(len(self.wrong_answers)))
        elif self.lang == 'ru':
            self.label.setText('Количество ошибок: ' + str(len(self.wrong_answers)))

        if self.lang == 'en':  # изменение текста виджетов в зависимости от языка
            self.setWindowTitle('Results')
            self.main_label.setText('The results')
            self.go_back.setText('Go back to main menu')
            self.label_2.setText('Mistakes in words:')
        elif self.lang == 'ru':
            self.setWindowTitle("Результаты")
            self.main_label.setText('Результаты текста')
            self.go_back.setText('Вернуться в главное меню')
            self.label_2.setText('Ошибки в словах:')

        for i in range(len(self.wrong_answers)):
            if check_language(self.wrong_answers[i][0]) == 'ru':
                self.wrong_answers[i] = self.wrong_answers[i][::-1]

        self.go_back.clicked.connect(self.go_back_to_main_window)
        self.tableWidget.setRowCount(0)

        for i, row in enumerate(self.wrong_answers):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def addword(self):  # добавление слова в таблицу
        try:
            eng = self.tableWidget.takeItem(self.tableWidget.rowCount() - 1, 0).text()
            if check_language(eng) == 'en':
                pass
            else:
                if self.lang == 'ru':
                    self.statusBar().showMessage('Введите слово на английском')
                else:
                    self.statusBar().showMessage("Enter english word")
                return
        except AttributeError:
            if self.lang == 'ru':
                self.statusBar().showMessage("Введите слово")
            elif self.lang == 'en':
                self.statusBar().showMessage('Enter the word')
            return
        try:
            rus = self.tableWidget.takeItem(self.tableWidget.rowCount() - 1, 1).text()
        except AttributeError:
            translator = Translator()
            rus = translator.translate(eng, 'ru')
            rus = rus.text
        try:
            self.connection.cursor().execute('''
            INSERT INTO words_learn(english, russian) VALUES (?,?)''', (eng, rus,))
            self.connection.commit()
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(str(eng)))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(str(rus)))
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        except sqlite3.IntegrityError:
            if self.lang == 'ru':
                self.statusBar().showMessage('Такое слово уже есть')
            elif self.lang == 'en':
                self.statusBar().showMessage('Such word already exists')

    def addimage(self):  # добавление изображения в таблицу
        if self.tableWidget.selectedIndexes():
            fname = QFileDialog.getOpenFileName(self, 'выбрать картинку', '', 'Картинка (*.jpg)')[0]
            word = ''
            for item in self.tableWidget.selectedIndexes():
                word = self.tableWidget.item(item.row(), 0).text()
            self.connection.cursor().execute('UPDATE words_learn SET image = ? WHERE english = ?', (fname, word,))
            self.connection.commit()
            self.render_table()
        else:
            if self.lang == 'ru':
                self.statusBar().showMessage('Выберите слово')
            elif self.lang == 'en':
                self.statusBar().showMessage('Choose a word')

    def deleteitems(self, table):  # удаление одного или нескольких элементов
        if self.tableWidget.selectedIndexes():

            if self.lang == 'ru':
                text, ok = QInputDialog.getText(self, 'Вы уверены?', "Введите ОК, если да")
            elif self.lang == 'en':
                text, ok = QInputDialog.getText(self, 'Are you sure?', "Enter Ok if yes")

            if (text.lower() == 'ok' or text.lower() == 'ок') and ok:
                words_to_delete = []
                for item in self.tableWidget.selectedIndexes():
                    words_to_delete.append(self.tableWidget.item(item.row(), 0).text())
                words_to_delete = set(words_to_delete)
                cur = self.connection.cursor()
                for word in words_to_delete:
                    if table == 'words_learn':
                        cur.execute('DELETE FROM words_learn WHERE english = ?', (word,))
                        self.render_table()
                    elif table == 'words_learnt':
                        cur.execute('DELETE FROM words_learnt WHERE english = ?', (word,))
                        self.render_table_2()
                    self.connection.commit()
                    if self.lang == 'ru':
                        self.statusBar().showMessage("Успешно удалено")
                    elif self.lang == 'en':
                        self.statusBar().showMessage("Deleted successfully")

    def replaceitems(self, table):  # перемещение одного или нескольких элементов в другую таблицу
        if self.tableWidget.selectedIndexes():

            if self.lang == 'ru':
                text, ok = QInputDialog.getText(self, 'Вы уверены?', "Введите ОК, если да")
            elif self.lang == 'en':
                text, ok = QInputDialog.getText(self, 'Are you sure?', "Enter Ok if yes")

            if (text.lower() == 'ok' or text.lower() == 'ок') and ok:
                words_to_delete = []
                for item in self.tableWidget.selectedIndexes():
                    words_to_delete.append(self.tableWidget.item(item.row(), 0).text())
                words_to_delete = set(words_to_delete)
                cur = self.connection.cursor()
                for word in words_to_delete:
                    if table == 'words_learn':
                        russian = \
                        cur.execute('SELECT russian, image FROM words_learn WHERE english = ?', (word,)).fetchall()[0]
                        cur.execute('DELETE FROM words_learn WHERE english = ?', (word,))
                        try:
                            cur.execute('INSERT INTO words_learnt(english,russian,image) VALUES (?,?,?)',
                                        (word, russian[0], russian[1],))
                            self.render_table()
                            self.connection.commit()
                            if self.lang == 'ru':
                                self.statusBar().showMessage("Успешно перемещено")
                            elif self.lang == 'en':
                                self.statusBar().showMessage('Moved successfully')
                        except sqlite3.IntegrityError:
                            self.statusBar().showMessage(f'Слово {word} уже есть в таблице')
                    elif table == 'words_learnt':
                        russian = \
                        cur.execute('SELECT russian,image FROM words_learnt WHERE english = ?', (word,)).fetchall()[0]
                        cur.execute('DELETE FROM words_learnt WHERE english = ?', (word,))
                        try:
                            cur.execute('INSERT INTO words_learn(english,russian,image) VALUES (?,?,?)',
                                        (word, russian[0], russian[1],))
                            self.render_table_2()
                            self.connection.commit()
                            if self.lang == 'ru':
                                self.statusBar().showMessage("Успешно перемещено")
                            elif self.lang == 'en':
                                self.statusBar().showMessage('Moved successfully')
                        except sqlite3.IntegrityError:
                            if self.lang == 'ru':
                                self.statusBar().showMessage(f'Слово "{word}" уже есть в таблице')
                            elif self.lang == 'en':
                                self.statusBar().showMessage(f'Word "{word}" is already in the table')

    def go_back_to_main_window(self):  # возвращение на главный экран
        uic.loadUi('main_window.ui', self)
        self.setFixedSize(400, 500)
        self.my_words.clicked.connect(self.my_words_render)
        self.learnt_words.clicked.connect(self.learnt_words_render)
        self.test.clicked.connect(self.test_render)
        self.language.clicked.connect(self.change_language)
        self.progress.hide()
        if self.lang == 'en':
            self.setWindowTitle('Dictionary')
            self.main_label.setText('Dictionary')
            self.learnt_words.setText('Learnt words')
            self.my_words.setText('My words')
            self.progress.setText('Progress')
            self.test.setText('Take a test')
            self.language.setIcon(QIcon('english.jpeg'))
        elif self.lang == 'ru':
            self.setWindowTitle('Словарь')
            self.main_label.setText('Словарь')
            self.learnt_words.setText('Изученные слова')
            self.my_words.setText('Мои слова')
            self.progress.setText('Прогресс')
            self.test.setText('Пройти тест')
            self.language.setIcon(QIcon('russian.png'))

    def change_language(self):  # смена языка приложения
        if self.lang == 'en':
            self.lang = 'ru'
        elif self.lang == 'ru':
            self.lang = 'en'
        self.initUi()

    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    def closeEvent(self, event):
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = MainWindow.except_hook
    sys.exit(app.exec_())
