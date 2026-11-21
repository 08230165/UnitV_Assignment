
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)
from PyQt6.QtCore import Qt


class GreetingWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Window configuration
        self.setWindowTitle("Welcome App | PyQt6")
        self.resize(450, 320)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)

        # Heading
        heading = QLabel("Welcome!")
        heading.setObjectName("heading")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Instruction
        instruction = QLabel(
            "Press the button to receive a greeting."
        )
        instruction.setObjectName("instruction")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Greeting message
        self.message = QLabel(
        )
        self.message.setObjectName("message")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Action button
        self.greet_button = QPushButton("Say Hello")
        self.greet_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.greet_button.setFixedHeight(48)

        # Connect button signal to handler
        self.greet_button.clicked.connect(self.say_hello)

        # Add widgets
        layout.addWidget(heading)
        layout.addWidget(instruction)
        layout.addWidget(self.message)
        layout.addWidget(self.greet_button)

        self.setLayout(layout)

        # Application stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F7FC;
                font-family: 'Segoe UI';
            }

            QLabel#heading {
                color: #1E3A8A;
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#instruction {
                color: #475569;
                font-size: 13px;
            }

            QLabel#message {
                color: #2563EB;
                font-size: 15px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)

    def say_hello(self):
        """Update the greeting when the button is clicked."""
        self.message.setText("Hello! Have a wonderful day.")
        self.greet_button.setText("Greeted!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = GreetingWindow()
    window.show()

    sys.exit(app.exec())
