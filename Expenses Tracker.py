import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit
from PyQt5.QtCore import Qt, QDate
import sqlite3

class ExpensesTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Expenses Tracker")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setup_ui()

        # Connect to SQLite database
        self.connection = sqlite3.connect("expenses.db")
        self.create_table()

        # Load initial data
        self.load_data()

    def setup_ui(self):
        # Widgets
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.description_edit = QLineEdit()
        self.amount_edit = QLineEdit()
        self.add_button = QPushButton("Add Expense")
        self.expenses_table = QTableWidget()

        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_edit)
        input_layout.addWidget(QLabel("Description:"))
        input_layout.addWidget(self.description_edit)
        input_layout.addWidget(QLabel("Amount:"))
        input_layout.addWidget(self.amount_edit)
        input_layout.addWidget(self.add_button)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.expenses_table)

        self.central_widget.setLayout(layout)

        # Table setup
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setHorizontalHeaderLabels(["ID", "Date", "Description", "Amount"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Connect signals
        self.add_button.clicked.connect(self.add_expense)
        self.expenses_table.itemDoubleClicked.connect(self.edit_expense)

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL
            )
        ''')
        self.connection.commit()

    def load_data(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()

        self.expenses_table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            for col, value in enumerate(expense):
                item = QTableWidgetItem(str(value))
                self.expenses_table.setItem(row, col, item)

    def add_expense(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.description_edit.text()
        amount = self.amount_edit.text()

        if date and description and amount:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)", (date, description, amount))
            self.connection.commit()

            self.load_data()
            self.clear_input_fields()
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def edit_expense(self, item):
        row = item.row()
        col = item.column()

        if col == 0:  # ID column, prevent editing ID
            return

        current_value = item.text()
        new_value, ok = QInputDialog.getText(self, "Edit Expense", f"Enter new value for {self.expenses_table.horizontalHeaderItem(col).text()}", text=current_value)

        if ok and new_value:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE expenses SET {self.expenses_table.horizontalHeaderItem(col).text().lower()} = ? WHERE id = ?", (new_value, self.expenses_table.item(row, 0).text()))
            self.connection.commit()

            self.load_data()

    def clear_input_fields(self):
        self.date_edit.setDate(QDate.currentDate())
        self.description_edit.clear()
        self.amount_edit.clear()

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpensesTracker()
    window.show()
    sys.exit(app.exec_())
