import json
import sqlite3


class Model(object):
    def __init__(self):
        self.db_connection = Model.create_db()

    def __del__(self):
        self.db_connection.cursor().close()
        self.db_connection.close()

    @staticmethod
    def create_db():
        db_connection = sqlite3.connect(":memory:")
        cursor = db_connection.cursor()
        cursor.execute("CREATE TABLE categories ( id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE )")
        cursor.execute("CREATE TABLE questions ( id INTEGER PRIMARY KEY AUTOINCREMENT, sentence TEXT NOT NULL UNIQUE, "
                       "type TEXT NOT NULL, categoryid INTEGER, FOREIGN KEY(categoryid) REFERENCES categories(id) )")
        db_connection.commit()
        return db_connection

    def populate_from_json(self, json_file_path):
        with open(json_file_path) as data_file:
            data = json.load(data_file)
        for entry in data:
            self.add_question(entry['question'], entry['type'], entry['category'])

    def add_category(self, name):
        category_id = None
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.db_connection.commit()
            category_id = cursor.lastrowid
        except sqlite3.IntegrityError, exception:
            print exception
            category_id = self.get_category_id(name)
        return category_id

    def get_category_id(self, category_name):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return None

    def get_question_id(self, question):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id FROM questions WHERE sentence=?", (question,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return None

    def get_questions_of_type(self, truth_or_dare):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM questions WHERE type=?", (truth_or_dare.lower(),))
        return cursor.fetchall()

    def get_questions_of_type_and_category(self, truth_or_dare, category_id):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM questions WHERE type=? and categoryid=?", (truth_or_dare.lower(), category_id))
        return cursor.fetchall()

    def get_question_with_id(self, question_id):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM questions WHERE rowid=?", (question_id,))
        return cursor.fetchone()

    def add_question(self, sentence, truth_or_dare, category_name):
        category_id = self.add_category(category_name)
        question_and_category_id = None
        if category_id is not None:
            question_id = None
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("INSERT INTO questions (sentence, type, categoryid) VALUES (?,?,?)",
                               (sentence, truth_or_dare.lower(), category_id))
                self.db_connection.commit()
                question_id = cursor.lastrowid
            except sqlite3.IntegrityError, exception:
                print exception
                question_id = self.get_question_id(sentence)
            finally:
                question_and_category_id = question_id, self.get_question_with_id(question_id)[3]
        return question_and_category_id

    def get_all_categories(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name FROM categories")
        return cursor.fetchall()

    def get_all_questions(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM questions")
        return cursor.fetchall()
