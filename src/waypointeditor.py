#!/usr/bin/env python

""" 
Waypoint Editor

Copyright (C) 2025, Robert Oostenveld

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import copy
import math
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QFormLayout, QWidget, QFileDialog, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPlainTextEdit, QDialog, QPushButton
)

def isvalid(s):
    """
    Check if a string can be converted to a positive float, this is needed for teh configuration tab
    """
    try:
        return float(s)>0
    except ValueError:
        return False        


class AboutDialog(QDialog):
    """
    A simple dialog that shows the about text
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Get the parent window position and size
        position = parent.pos()
        size = parent.size()
        px = position.x()
        py = position.y()
        sx = size.width()
        sy = size.height()

        # Set the position and size of the help dialog
        self.setGeometry(int(px + sx/2 - 150), int(py + sy/2 - 50), 300, 100)
        self.setWindowTitle("About")

        # Create a layout and add a label with help text
        layout = QVBoxLayout()
        help_text = QLabel("Waypoint Editor\n(C) 2025, Robert Oostenveld", self)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Add a close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class HelpDialog(QDialog):
    """
    A simple dialog that shows the help text
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Get the parent window position and size
        position = parent.pos()
        size = parent.size()
        px = position.x()
        py = position.y()
        sx = size.width()
        sy = size.height()

        # Set the position and size of the help dialog
        self.setGeometry(int(px + sx/2 - 150), int(py + sy/2 - 50), 300, 100)
        self.setWindowTitle("Help")

        # Create a layout and add a label with help text
        layout = QVBoxLayout()
        help_text = QLabel("Press Z to clear the last point.\nPress C to clear all points.", self)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Add a close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class ImageTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setMouseTracking(True)  # Enable mouse tracking
        self.setFocusPolicy(Qt.StrongFocus)  # Set focus policy to accept keyboard events
        self.pixmap = None  # Store the image as a QPixmap
        self.offset = [0, 0]  # Offset to center the image
        self.points = []  # List to store points
        self.pixels_to_pixels = 0 # Scale factor between the image pixels and the screen pixels

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = event.pos()
            x = (point.x()-self.offset[0]) / self.pixels_to_pixels
            y = (point.y()-self.offset[1]) / self.pixels_to_pixels
            if x<0 or x>self.pixmap.width() or y<0 or y>self.pixmap.height():
                # Don't add points that fall outside the image
                return
            # Add the clicked point to the list
            point.setX(int(x))
            point.setY(int(y))
            self.points.append(point)
            self.parent.update_all()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:  # Clear canvas when 'C' is pressed
            self.points = []
        if event.key() == Qt.Key_Z:  # Undo last point when 'Z' is pressed
            if self.points:
                self.points.pop()
        self.parent.update_all()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother lines

        # Draw the image if it exists
        if self.pixmap:
            w = self.pixmap.width()
            h = self.pixmap.height()
            self.pixels_to_pixels = min(self.width() / w, self.height() / h)
            self.offset[0] = (self.width() - int(w * self.pixels_to_pixels)) / 2
            self.offset[1] = (self.height() - int(h * self.pixels_to_pixels)) / 2
            painter.drawPixmap(int(self.offset[0]), int(self.offset[1]), int(w * self.pixels_to_pixels), int(h * self.pixels_to_pixels), self.pixmap)

        # Draw points
        pen = QPen(QColor(0, 255, 0), 10)  # Green points, 10px size
        painter.setPen(pen)
        for point in self.points:
            point = copy.deepcopy(point)
            point.setX(int(point.x() * self.pixels_to_pixels + self.offset[0])) 
            point.setY(int(point.y() * self.pixels_to_pixels + self.offset[1]))
            painter.drawPoint(point)
            pen = QPen(QColor(0, 0, 255), 10)  # Blue points, 10px size
            painter.setPen(pen)

        # Draw lines connecting the points
        pen = QPen(QColor(255, 0, 0), 2)  # Red line, 2px thickness
        painter.setPen(pen)
        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                p1 = copy.deepcopy(self.points[i - 1])
                p1.setX(int(p1.x() * self.pixels_to_pixels + self.offset[0]))
                p1.setY(int(p1.y() * self.pixels_to_pixels + self.offset[1]))
                p2 = copy.deepcopy(self.points[i])
                p2.setX(int(p2.x() * self.pixels_to_pixels + self.offset[0]))
                p2.setY(int(p2.y() * self.pixels_to_pixels + self.offset[1]))
                painter.drawLine(p1, p2)

        self.update()


class WaypointsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time (s)", "X (meter)", "Y (meter)", "Angle (degrees)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)


class SettingsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent           = parent
        self.layout           = QFormLayout(self)
        self.width_pixels     = QLineEdit(parent=self)
        self.depth_pixels     = QLineEdit(parent=self)
        self.length_pixels    = QLineEdit(parent=self)
        self.pixels_per_meter = QLineEdit(parent=self)
        self.width_meter      = QLineEdit(parent=self)
        self.depth_meter      = QLineEdit(parent=self)
        self.length_meter     = QLineEdit(parent=self)
        self.total_duration   = QLineEdit(parent=self)
        self.total_rotation   = QLineEdit(parent=self)
        self.average_speed    = QLineEdit(parent=self)
        self.angular_speed    = QLineEdit(parent=self)

        self.width_pixels.setReadOnly(True)
        self.depth_pixels.setReadOnly(True)
        self.length_pixels.setReadOnly(True)
        self.width_meter.setReadOnly(True)
        self.depth_meter.setReadOnly(True)
        self.length_meter.setReadOnly(True)
        self.average_speed.setReadOnly(True)
        self.angular_speed.setReadOnly(True)

        bg_color = self.palette().color(QPalette.Window).name()
        bg_color = QColor(229, 229, 229).name()

        self.width_pixels.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.depth_pixels.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.length_pixels.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.width_meter.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.depth_meter.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.length_meter.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.average_speed.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")
        self.angular_speed.setStyleSheet(f"QLineEdit {{ background-color: {bg_color}; border: 2px solid {bg_color}; }}")

        self.layout.addRow("Stage width (pixels):", self.width_pixels)
        self.layout.addRow("Stage depth (pixels):", self.depth_pixels)
        self.layout.addRow("Total length (pixels):", self.length_pixels)
        self.layout.addRow("Scale (pixels/meter):", self.pixels_per_meter)
        self.layout.addRow("", QLabel(" "))
        self.layout.addRow("Stage width (meter):", self.width_meter)
        self.layout.addRow("Stage depth (meter):", self.depth_meter)
        self.layout.addRow("Total length (meter):", self.length_meter)
        self.layout.addRow("Total duration (second):", self.total_duration)
        self.layout.addRow("Total rotation (degrees):", self.total_rotation)
        self.layout.addRow("Average speed (meter/second):", self.average_speed)
        self.layout.addRow("Angular speed (degrees/second):", self.angular_speed)

    def paintEvent(self, event):
        
        if self.parent.image_tab.pixmap:
            self.depth_pixels.setText(f'{self.parent.image_tab.pixmap.height()}')
            self.width_pixels.setText(f'{self.parent.image_tab.pixmap.width()}')

        try:
            depth_meter = self.parent.image_tab.pixmap.height() / float(self.pixels_per_meter.text())
            if depth_meter < 0:
                raise ValueError
            self.depth_meter.setText(f'{depth_meter:.2f}')
            width_meter = self.parent.image_tab.pixmap.width() / float(self.pixels_per_meter.text())
            if width_meter < 0:
                raise ValueError
            self.width_meter.setText(f'{width_meter:.2f}')
        except (ValueError, ZeroDivisionError):
            self.depth_meter.setText("")
            self.width_meter.setText("")

        length_pixels = 0
        for i in range(0, len(self.parent.image_tab.points)-1):
            dx = self.parent.image_tab.points[i+1].x() - self.parent.image_tab.points[i].x()
            dy = self.parent.image_tab.points[i+1].y() - self.parent.image_tab.points[i].y()
            length_pixels += math.sqrt(dx*dx + dy*dy);
        self.length_pixels.setText(f'{length_pixels:.0f}')

        try:
            length_meter = length_pixels / float(self.pixels_per_meter.text())
            if length_meter < 0:
                raise ValueError
            self.length_meter.setText(f'{length_meter:.2f}')
        except (ValueError, ZeroDivisionError):
            length_meter = 0
            self.length_meter.setText(str(""))

        try:
            total_duration = float(self.total_duration.text())
            if total_duration < 0:
                raise ValueError
            average_speed = length_meter / total_duration
            self.average_speed.setText(f'{average_speed:.3f}')
        except (ValueError, ZeroDivisionError):
            average_speed = 0
            self.average_speed.setText(str(""))

        try:
            total_duration = float(self.total_duration.text())
            total_rotation = float(self.total_rotation.text())
            angular_speed = total_rotation / total_duration
            self.angular_speed.setText(f'{angular_speed:.0f}')
        except (ValueError, ZeroDivisionError):
            self.angular_speed.setText(str(""))
        
        self.parent.update_all()


class ExportTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout(self)
        self.text = QPlainTextEdit(self)
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)
        

class WaypointEditor(QMainWindow):
    """
    The main window of the application. It consists of four tabs:
    - Image: to display the image and the waypoints
    - Settings: to configure the scale and the duration
    - Waypoints: to display the waypoints as a table
    - Export: to export the waypoints
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waypoint Editor')
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        # Create the tabs
        self.settings_tab = SettingsTab(self)
        self.waypoints_tab = WaypointsTab(self)
        self.image_tab = ImageTab(self)
        self.export_tab = ExportTab(self)
    
        # Add the tabs to the central widget
        self.central_widget.addTab(self.image_tab, "Image")
        self.central_widget.addTab(self.settings_tab, "Settings")
        self.central_widget.addTab(self.waypoints_tab, "Waypoints")
        self.central_widget.addTab(self.export_tab, "Waypoints as CSV")
        self.central_widget.setCurrentIndex(0)

        # Create a menu bar
        self.menu_bar = self.menuBar()

        # Create a "File" menu
        file_menu = self.menu_bar.addMenu('File')
        help_menu = self.menu_bar.addMenu('Help')

        # Add an "New Image" action to the "File" menu
        new_menu = file_menu.addMenu('New image')
        new_menu.addAction("1x1 meter").triggered.connect(lambda: self.new_image(1, 1))
        new_menu.addAction("1x2 meter").triggered.connect(lambda: self.new_image(1, 2))
        new_menu.addAction("1x3 meter").triggered.connect(lambda: self.new_image(1, 3))
        new_menu.addSeparator()
        new_menu.addAction("2x1 meter").triggered.connect(lambda: self.new_image(2, 1))
        new_menu.addAction("2x2 meter").triggered.connect(lambda: self.new_image(2, 2))
        new_menu.addAction("2x3 meter").triggered.connect(lambda: self.new_image(2, 3))
        new_menu.addAction("2x4 meter").triggered.connect(lambda: self.new_image(2, 4))
        new_menu.addSeparator()
        new_menu.addAction("3x1 meter").triggered.connect(lambda: self.new_image(3, 1))
        new_menu.addAction("3x2 meter").triggered.connect(lambda: self.new_image(3, 2))
        new_menu.addAction("3x3 meter").triggered.connect(lambda: self.new_image(3, 3))
        new_menu.addAction("3x4 meter").triggered.connect(lambda: self.new_image(3, 4))
        new_menu.addAction("3x5 meter").triggered.connect(lambda: self.new_image(3, 5))
        new_menu.addAction("3x6 meter").triggered.connect(lambda: self.new_image(3, 6))
        new_menu.addSeparator()
        new_menu.addAction("4x1 meter").triggered.connect(lambda: self.new_image(4, 1))
        new_menu.addAction("4x2 meter").triggered.connect(lambda: self.new_image(4, 2))
        new_menu.addAction("4x3 meter").triggered.connect(lambda: self.new_image(4, 3))
        new_menu.addAction("4x4 meter").triggered.connect(lambda: self.new_image(4, 4))
        new_menu.addAction("4x5 meter").triggered.connect(lambda: self.new_image(4, 5))
        new_menu.addAction("4x8 meter").triggered.connect(lambda: self.new_image(4, 8))
        new_menu.addSeparator()
        new_menu.addAction("5x2 meter").triggered.connect(lambda: self.new_image(5, 2))
        new_menu.addAction("5x5 meter").triggered.connect(lambda: self.new_image(5, 5))
        new_menu.addAction("5x10 meter").triggered.connect(lambda: self.new_image(5, 10))
        new_menu.addSeparator()
        new_menu.addAction("6x3 meter").triggered.connect(lambda: self.new_image(6, 3))
        new_menu.addAction("6x6 meter").triggered.connect(lambda: self.new_image(6, 6))
        new_menu.addAction("6x9 meter").triggered.connect(lambda: self.new_image(6, 9))
        new_menu.addSeparator()
        new_menu.addAction("8x2 meter").triggered.connect(lambda: self.new_image(8, 2))
        new_menu.addAction("8x4 meter").triggered.connect(lambda: self.new_image(8, 4))
        new_menu.addAction("8x8 meter").triggered.connect(lambda: self.new_image(8, 8))

        # Add an "Open Image" action to the "File" menu
        open_image = QAction('Open image', self)
        open_image.triggered.connect(self.open_image)
        file_menu.addAction(open_image)

        # Add a "Close Image" action to the "File" menu
        close_image = QAction('Close image', self)
        close_image.triggered.connect(self.close_image)
        file_menu.addAction(close_image)

        # Add an "Help" action to the "Help" menu
        show_help = QAction('Help', self)
        show_help.triggered.connect(self.show_help)
        help_menu.addAction(show_help)

        # Add an "About" action to the "Help" menu
        show_about = QAction('About', self)
        show_about.triggered.connect(self.show_about)
        help_menu.addAction(show_about) # on macOS this will be shown in the application menu

    def close_image(self):
        self.image_tab.pixmap = None
        self.image_tab.points = []
        self.update_all()

    def new_image(self, x, y):
        resolution = 300
        self.settings_tab.pixels_per_meter.setText(f'{resolution}')
        self.image_tab.pixmap = QPixmap(x*resolution, y*resolution) 
        self.image_tab.pixmap.fill(Qt.white)
        qp = QPainter(self.image_tab.pixmap)
        gray = QPen(Qt.lightGray, 1)
        black = QPen(Qt.darkGray, 1)

        # Draw grid lines 
        for i in range(0, x):
            qp.setPen(gray)
            qp.drawLine((i+0)*resolution+75, 0, (i+0)*resolution+75, y*resolution)
            qp.drawLine((i+1)*resolution+74, 0, (i+1)*resolution+74, y*resolution)
            qp.drawLine((i+0)*resolution+150, 0, (i+0)*resolution+150, y*resolution)
            qp.drawLine((i+1)*resolution+149, 0, (i+1)*resolution+149, y*resolution)
            qp.drawLine((i+0)*resolution+225, 0, (i+0)*resolution+225, y*resolution)
            qp.drawLine((i+1)*resolution+224, 0, (i+1)*resolution+224, y*resolution)

            qp.setPen(black)
            qp.drawLine((i+0)*resolution-0, 0, (i+0)*resolution-0, y*resolution)
            qp.drawLine((i+1)*resolution-1, 0, (i+1)*resolution-1, y*resolution)

        for i in range(0, y):
            qp.setPen(gray)
            qp.drawLine(0, (i+0)*resolution+75, x*resolution, (i+0)*resolution+75)
            qp.drawLine(0, (i+1)*resolution+74, x*resolution, (i+1)*resolution+74)
            qp.drawLine(0, (i+0)*resolution+150, x*resolution, (i+0)*resolution+150)
            qp.drawLine(0, (i+1)*resolution+149, x*resolution, (i+1)*resolution+149)
            qp.drawLine(0, (i+0)*resolution+225, x*resolution, (i+0)*resolution+225)
            qp.drawLine(0, (i+1)*resolution+224, x*resolution, (i+1)*resolution+224)

            qp.setPen(black)
            qp.drawLine(0, (i+0)*resolution-0, x*resolution, (i+0)*resolution-0)
            qp.drawLine(0, (i+1)*resolution-1, x*resolution, (i+1)*resolution-1)
        self.update_all()

    def open_image(self, file_name=None):
        if not file_name:
            # Open a file dialog to select an image file
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if file_name:
            # Load the image into a QPixmap
            self.image_tab.pixmap = QPixmap(file_name)
            self.update_all()
        self.update_all()

    def show_help(self):
        # Create and show the help dialog
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

    def show_about(self):
        # Create and show the help dialog
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def update_all(self):
        """
        Update all tabs in a consistent fashion, i.e., the values from the settings tab are used 
        together with the points from the image tab to update the waypoints tab and the export tab.
        """
        has_points   = len(self.image_tab.points) > 0
        has_scale    = isvalid(self.settings_tab.pixels_per_meter.text())
        has_duration = isvalid(self.settings_tab.total_duration.text())
        has_rotation = isvalid(self.settings_tab.total_rotation.text())

        if has_scale:
            pixels_per_meter = float(self.settings_tab.pixels_per_meter.text())
        else:
            pixels_per_meter = 0

        if has_duration:
            total_duration = float(self.settings_tab.total_duration.text())
        else:
            total_duration = 0

        if has_rotation:
            total_rotation = float(self.settings_tab.total_rotation.text())
        else:
            total_rotation = 0

        segment = [0]   # the first segment is always 0 
        for i in range(0, len(self.image_tab.points)-1):
            dx = self.image_tab.points[i+1].x() - self.image_tab.points[i].x()
            dy = self.image_tab.points[i+1].y() - self.image_tab.points[i].y()
            segment.append(math.sqrt(dx*dx + dy*dy)) 

        # normalize the total length of all segments to one
        length_pixels = sum(segment)
        for i in range(1, len(segment)):
            segment[i] = segment[i] / length_pixels

        self.waypoints_tab.table.setRowCount(len(self.image_tab.points)) # this will also empty the table when needed
        if has_points and has_scale:
            x0 = self.image_tab.points[0].x()
            y0 = self.image_tab.points[0].y()
            for i, point in enumerate(self.image_tab.points):
                time = sum(segment[0:i+1]) * total_duration
                x = (point.x() - x0) / pixels_per_meter
                y = (point.y() - y0) / pixels_per_meter
                # Convert to stage coordinates:
                # - positive x is away from the audience
                # - positive y is to the left
                # - positive angle is counter clockwise
                stage_x = -y
                stage_y = -x
                angle = sum(segment[0:i+1]) * total_rotation
                self.waypoints_tab.table.setItem(i, 0, QTableWidgetItem(f'{time:.1f}'))
                self.waypoints_tab.table.setItem(i, 1, QTableWidgetItem(f'{stage_x:.3f}'))
                self.waypoints_tab.table.setItem(i, 2, QTableWidgetItem(f'{stage_y:.3f}'))
                self.waypoints_tab.table.setItem(i, 3, QTableWidgetItem(f'{angle:.0f}'))

        self.export_tab.text.setPlainText('') # this will also empty the text when needed
        if has_points:
            for i in range(0, self.waypoints_tab.table.rowCount()):
                time  = self.waypoints_tab.table.item(i, 0).text()
                x     = self.waypoints_tab.table.item(i, 1).text()
                y     = self.waypoints_tab.table.item(i, 2).text()
                angle = self.waypoints_tab.table.item(i, 3).text()
                self.export_tab.text.appendPlainText(f'{time},{x},{y},{angle}')

        self.image_tab.update()
        self.settings_tab.update()
        self.waypoints_tab.update()
        self.export_tab.update()


def main():
    """
    The main entry point for the application when started as the script created by the pip installer.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Waypoint Editor")
    viewer = WaypointEditor()
    viewer.new_image(4, 3) # start with a default stage size of 4x3 meters
    viewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    """
    The main entry point for the application when started from the command line.
    """
    main()
