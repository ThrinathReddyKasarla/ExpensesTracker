import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit, QComboBox
from PyQt5.QtCore import Qt, QDate
import sqlite3
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import style

style.use("ggplot")

class ExpensesTracker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Expenses Tracker")
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setup_ui()

        # Connect to SQLite database
        self.connection = sqlite3.connect("expenses.db")
        self.create_table()

        # Load initial data
        self.load_data()
        self.update_chart()

    def setup_ui(self):
        # Widgets
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.description_edit = QLineEdit()
        self.amount_edit = QLineEdit()
        self.category_combobox = QComboBox()
        self.add_button = QPushButton("Add Expense")
        self.expenses_table = QTableWidget()
        self.chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.chart_ax = self.chart_canvas.figure.add_subplot(111)

        # Categories for the combo box
        self.categories = ["Groceries", "Utilities", "Transportation", "Entertainment", "Others"]
        self.category_combobox.addItems(self.categories)

        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_edit)
        input_layout.addWidget(QLabel("Description:"))
        input_layout.addWidget(self.description_edit)
        input_layout.addWidget(QLabel("Amount:"))
        input_layout.addWidget(self.amount_edit)
        input_layout.addWidget(QLabel("Category:"))
        input_layout.addWidget(self.category_combobox)
        input_layout.addWidget(self.add_button)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.expenses_table)
        layout.addWidget(self.chart_canvas)

        self.central_widget.setLayout(layout)

        # Table setup
        self.expenses_table.setColumnCount(5)
        self.expenses_table.setHorizontalHeaderLabels(["ID", "Date", "Description", "Amount", "Category"])
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
                amount REAL NOT NULL,
                category TEXT NOT NULL
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

    def update_chart(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()

        categories, amounts = zip(*data)
        self.chart_ax.clear()
        self.chart_ax.bar(categories, amounts, color='blue')
        self.chart_ax.set_title('Expense Distribution by Category')
        self.chart_ax.set_xlabel('Category')
        self.chart_ax.set_ylabel('Total Amount')
        self.chart_ax.figure.canvas.draw()

    def add_expense(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.description_edit.text()
        amount = self.amount_edit.text()
        category = self.category_combobox.currentText()

        if date and description and amount:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO expenses (date, description, amount, category) VALUES (?, ?, ?, ?)",
                           (date, description, amount, category))
            self.connection.commit()

            self.load_data()
            self.update_chart()
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
            self.update_chart()

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
