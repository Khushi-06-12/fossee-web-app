import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QDialog, QDialogButtonBox, QFormLayout,
    QGroupBox, QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json


API_BASE_URL = 'http://localhost:8000/api/equipment'


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit()
        
        layout.addRow('Username:', self.username_input)
        layout.addRow('Password:', self.password_input)
        layout.addRow('Email (optional):', self.email_input)
        
        self.is_register = False
        self.register_button = QPushButton('Register')
        self.login_button = QPushButton('Login')
        self.register_button.clicked.connect(self.toggle_mode)
        self.login_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.login_button)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
        
        self.token = None
    
    def toggle_mode(self):
        if not self.is_register:
            self.is_register = True
            self.register_button.setText('Switch to Login')
            self.login_button.setText('Register')
        else:
            self.is_register = False
            self.register_button.setText('Register')
            self.login_button.setText('Login')
    
    def accept(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Username and password are required')
            return
        
        try:
            endpoint = 'auth/register/' if self.is_register else 'auth/login/'
            data = {'username': username, 'password': password}
            if self.is_register and email:
                data['email'] = email
            
            response = requests.post(f'{API_BASE_URL}/{endpoint}', json=data)
            
            if response.status_code in [200, 201]:
                self.token = response.json().get('token')
                super().accept()
            else:
                error_msg = response.json().get('error', 'Authentication failed')
                QMessageBox.warning(self, 'Error', error_msg)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Connection error: {str(e)}')


class ApiThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, method, url, headers=None, data=None, files=None):
        super().__init__()
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.data = data
        self.files = files
    
    def run(self):
        try:
            if self.method == 'GET':
                response = requests.get(self.url, headers=self.headers)
            elif self.method == 'POST':
                if self.files:
                    response = requests.post(self.url, headers=self.headers, files=self.files)
                else:
                    response = requests.post(self.url, headers=self.headers, json=self.data)
            
            if response.status_code < 400:
                self.finished.emit(response.json())
            else:
                error_msg = response.json().get('error', 'Request failed')
                self.error.emit(error_msg)
        except Exception as e:
            self.error.emit(str(e))


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_type_distribution(self, type_distribution):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        types = list(type_distribution.keys())
        counts = list(type_distribution.values())
        
        ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax.set_title('Equipment Type Distribution')
        
        self.canvas.draw()
    
    def plot_averages(self, averages):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        metrics = ['Flowrate', 'Pressure', 'Temperature']
        values = [averages['flowrate'], averages['pressure'], averages['temperature']]
        
        ax.bar(metrics, values, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax.set_ylabel('Average Value')
        ax.set_title('Average Values')
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def plot_flowrate_pressure(self, equipment_data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        flowrates = [item['flowrate'] for item in equipment_data[:20]]
        pressures = [item['pressure'] for item in equipment_data[:20]]
        indices = list(range(len(flowrates)))
        
        ax2 = ax.twinx()
        
        line1 = ax.plot(indices, flowrates, 'b-', label='Flowrate', linewidth=2)
        line2 = ax2.plot(indices, pressures, 'r-', label='Pressure', linewidth=2)
        
        ax.set_xlabel('Equipment Index')
        ax.set_ylabel('Flowrate', color='b')
        ax2.set_ylabel('Pressure', color='r')
        ax.set_title('Flowrate vs Pressure (First 20 Equipment)')
        ax.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token = None
        self.current_dataset_id = None
        self.summary = None
        self.equipment_data = []
        self.history = []
        
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel('Chemical Equipment Parameter Visualizer')
        self.title_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.logout_button = QPushButton('Logout')
        self.logout_button.clicked.connect(self.show_login)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)
        main_layout.addLayout(header_layout)
        
        # Upload section
        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QVBoxLayout()
        self.upload_button = QPushButton('Select CSV File')
        self.upload_button.clicked.connect(self.select_file)
        self.file_label = QLabel('No file selected')
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_label)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)
        
        # History section
        history_group = QGroupBox('Upload History (Click to load)')
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        # Summary section
        summary_group = QGroupBox('Summary Statistics')
        summary_layout = QVBoxLayout()
        self.summary_label = QLabel('No data loaded')
        summary_layout.addWidget(self.summary_label)
        self.pdf_button = QPushButton('Generate PDF Report')
        self.pdf_button.clicked.connect(self.generate_pdf)
        summary_layout.addWidget(self.pdf_button)
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Charts section
        charts_group = QGroupBox('Visualizations')
        charts_layout = QHBoxLayout()
        
        self.chart1 = ChartWidget()
        self.chart2 = ChartWidget()
        self.chart3 = ChartWidget()
        
        charts_layout.addWidget(self.chart1)
        charts_layout.addWidget(self.chart2)
        charts_layout.addWidget(self.chart3)
        
        charts_group.setLayout(charts_layout)
        main_layout.addWidget(charts_group)
        
        # Table section
        table_group = QGroupBox('Equipment Data')
        table_layout = QVBoxLayout()
        self.table = QTableWidget()
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
    
    def show_login(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.token = dialog.token
            self.load_history()
        else:
            if not self.token:
                sys.exit()
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '', 'CSV Files (*.csv)'
        )
        
        if file_path:
            self.file_label.setText(f'Selected: {os.path.basename(file_path)}')
            self.upload_file(file_path)
    
    def upload_file(self, file_path):
        headers = {'Authorization': f'Token {self.token}'}
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            
            thread = ApiThread('POST', f'{API_BASE_URL}/upload/', headers=headers, files=files)
            thread.finished.connect(self.on_upload_success)
            thread.error.connect(self.show_error)
            thread.start()
    
    def on_upload_success(self, data):
        self.current_dataset_id = data.get('dataset_id')
        self.file_label.setText(f'Uploaded: {data.get("dataset_name")}')
        QMessageBox.information(self, 'Success', 'File uploaded successfully!')
        self.load_history()
        self.load_dataset(self.current_dataset_id)
    
    def load_history(self):
        headers = {'Authorization': f'Token {self.token}'}
        thread = ApiThread('GET', f'{API_BASE_URL}/history/', headers=headers)
        thread.finished.connect(self.on_history_loaded)
        thread.error.connect(self.show_error)
        thread.start()
    
    def on_history_loaded(self, data):
        self.history = data.get('history', [])
        self.history_list.clear()
        for item in self.history:
            display_text = f"{item['name']} - {item['equipment_count']} equipment - {item['uploaded_at']}"
            self.history_list.addItem(display_text)
    
    def on_history_item_clicked(self, item):
        index = self.history_list.row(item)
        if index < len(self.history):
            dataset_id = self.history[index]['id']
            self.load_dataset(dataset_id)
    
    def load_dataset(self, dataset_id):
        headers = {'Authorization': f'Token {self.token}'}
        
        # Load summary
        thread1 = ApiThread('GET', f'{API_BASE_URL}/summary/{dataset_id}/', headers=headers)
        thread1.finished.connect(self.on_summary_loaded)
        thread1.error.connect(self.show_error)
        thread1.start()
        
        # Load equipment data
        thread2 = ApiThread('GET', f'{API_BASE_URL}/data/{dataset_id}/', headers=headers)
        thread2.finished.connect(self.on_data_loaded)
        thread2.error.connect(self.show_error)
        thread2.start()
    
    def on_summary_loaded(self, data):
        self.summary = data
        summary_text = f"""
Total Equipment: {data['summary']['total_count']}
Average Flowrate: {data['summary']['averages']['flowrate']}
Average Pressure: {data['summary']['averages']['pressure']}
Average Temperature: {data['summary']['averages']['temperature']}
        """
        self.summary_label.setText(summary_text.strip())
        
        # Update charts
        if self.summary:
            self.chart1.plot_type_distribution(self.summary['summary']['type_distribution'])
            self.chart2.plot_averages(self.summary['summary']['averages'])
    
    def on_data_loaded(self, data):
        self.equipment_data = data.get('data', [])
        self.update_table()
        
        # Update flowrate vs pressure chart
        if self.equipment_data:
            self.chart3.plot_flowrate_pressure(self.equipment_data)
    
    def update_table(self):
        self.table.setRowCount(len(self.equipment_data))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        
        for row, item in enumerate(self.equipment_data):
            self.table.setItem(row, 0, QTableWidgetItem(item['equipment_name']))
            self.table.setItem(row, 1, QTableWidgetItem(item['equipment_type']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['flowrate']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['pressure']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item['temperature']:.2f}"))
        
        self.table.resizeColumnsToContents()
    
    def generate_pdf(self):
        if not self.current_dataset_id:
            QMessageBox.warning(self, 'Error', 'No dataset selected')
            return
        
        headers = {'Authorization': f'Token {self.token}'}
        
        try:
            response = requests.get(
                f'{API_BASE_URL}/pdf/{self.current_dataset_id}/',
                headers=headers,
                stream=True
            )
            
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF', f'equipment_report_{self.current_dataset_id}.pdf',
                    'PDF Files (*.pdf)'
                )
                
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF report generated successfully!')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error generating PDF: {str(e)}')
    
    def show_error(self, message):
        QMessageBox.critical(self, 'Error', message)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
