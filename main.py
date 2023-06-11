import os
import sys
from multiprocessing import freeze_support

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt, QCoreApplication, QSize

from qt_material import apply_stylesheet

from main_window import MainWindow

# Extra stylesheets
extra = {
    'font_family': 'Roboto',
    'density_scale': '3',
    'button_shape': 'default',
}

theme = 'dark_amber.xml'


if __name__ == "__main__":
    # Set theme on in itialization
    if hasattr(Qt, 'AA_ShareOpenGLContexts'):
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    else:
        print("'Qt' object has no attribute 'AA_ShareOpenGLContexts'")

    app = QApplication([])
    freeze_support()
    app.processEvents()
    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(app.quit)

    apply_stylesheet(
        app,
        theme,
        invert_secondary=theme.startswith('light'),
        extra=extra,
    )

    window = MainWindow(extra, theme)
    window.show()

    app.exec()
