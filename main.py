import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QComboBox,
    QSlider, QListWidget, QListWidgetItem, QGridLayout
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from image_processor import process_image, save_image
from preview_widget import ImagePreview


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Logo Tool")
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        self.image_paths = []
        self.logo_path = ""
        self.current_index = 0
        self.image_settings = {}

        main_layout = QVBoxLayout()

        # ---------- TOP ----------
        top = QHBoxLayout()

        btn_images = QPushButton("Add Images")
        btn_logo = QPushButton("Add Logo")
        btn_process = QPushButton("Process")

        btn_images.clicked.connect(self.select_images)
        btn_logo.clicked.connect(self.select_logo)
        btn_process.clicked.connect(self.process_images)

        self.status = QLabel("No images")

        top.addWidget(btn_images)
        top.addWidget(btn_logo)
        top.addWidget(btn_process)
        top.addStretch()
        top.addWidget(self.status)

        main_layout.addLayout(top)

        # ---------- CENTER ----------
        center = QHBoxLayout()

        self.thumb = QListWidget()
        self.thumb.setMaximumWidth(140)
        self.thumb.itemClicked.connect(self.select_thumbnail)

        center.addWidget(self.thumb)

        self.preview = ImagePreview(self)
        center.addWidget(self.preview, 1)

        main_layout.addLayout(center, 1)

        # ---------- CONTROLS (WITH LABELS) ----------
        controls = QGridLayout()

        self.position = QComboBox()
        self.position.addItems(["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right", "Center"])

        self.shape = QComboBox()
        self.shape.addItems(["Square", "Circle"])

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(5, 50)
        self.size_slider.setValue(20)

        self.padding_slider = QSlider(Qt.Horizontal)
        self.padding_slider.setRange(0, 10)
        self.padding_slider.setValue(5)

        self.offset_x_slider = QSlider(Qt.Horizontal)
        self.offset_x_slider.setRange(-3000, 3000)

        self.offset_y_slider = QSlider(Qt.Horizontal)
        self.offset_y_slider.setRange(-3000, 3000)

        # Row 1
        controls.addWidget(QLabel("Position"), 0, 0)
        controls.addWidget(self.position, 0, 1)

        controls.addWidget(QLabel("Shape"), 0, 2)
        controls.addWidget(self.shape, 0, 3)

        controls.addWidget(QLabel("Size"), 0, 4)
        controls.addWidget(self.size_slider, 0, 5)

        # Row 2
        controls.addWidget(QLabel("Padding"), 1, 0)
        controls.addWidget(self.padding_slider, 1, 1)

        controls.addWidget(QLabel("Offset X"), 1, 2)
        controls.addWidget(self.offset_x_slider, 1, 3)

        controls.addWidget(QLabel("Offset Y"), 1, 4)
        controls.addWidget(self.offset_y_slider, 1, 5)

        main_layout.addLayout(controls)

        self.setLayout(main_layout)

        # ---------- SIGNALS ----------
        self.position.currentIndexChanged.connect(self.update_preview)
        self.shape.currentIndexChanged.connect(self.update_preview)
        self.size_slider.valueChanged.connect(self.update_preview)
        self.padding_slider.valueChanged.connect(self.update_preview)
        self.offset_x_slider.valueChanged.connect(self.update_preview)
        self.offset_y_slider.valueChanged.connect(self.update_preview)

    # =====================================================
    # SETTINGS
    # =====================================================

    def save_settings(self):
        if not self.image_paths:
            return

        path = self.image_paths[self.current_index]

        self.image_settings[path] = {
            "position": self.position.currentText(),
            "shape": self.shape.currentText(),
            "size": self.size_slider.value(),
            "padding": self.padding_slider.value(),
            "x": self.offset_x_slider.value(),
            "y": self.offset_y_slider.value(),
        }

    def load_settings(self):
        path = self.image_paths[self.current_index]

        if path in self.image_settings:
            s = self.image_settings[path]

            self.position.setCurrentText(s["position"])
            self.shape.setCurrentText(s["shape"])
            self.size_slider.setValue(s["size"])
            self.padding_slider.setValue(s["padding"])
            self.offset_x_slider.setValue(s["x"])
            self.offset_y_slider.setValue(s["y"])

    # =====================================================
    # FILE SELECT
    # =====================================================

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Images")

        if not files:
            return

        self.load_images(files)

    def load_images(self, files):
        self.image_paths = files
        self.thumb.clear()

        for path in files:
            item = QListWidgetItem()
            item.setIcon(QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio))
            item.setData(Qt.UserRole, path)
            self.thumb.addItem(item)

        self.current_index = 0
        self.status.setText(f"{len(files)} images loaded")
        self.update_preview()

    def select_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Logo")

        if file:
            self.logo_path = file
            self.update_preview()

    # =====================================================
    # DRAG DROP (FIXED)
    # =====================================================

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):

        files = [u.toLocalFile() for u in event.mimeData().urls()]

        if not files:
            return

        if len(files) == 1:
            self.logo_path = files[0]
        else:
            self.load_images(files)

        self.update_preview()

    # =====================================================
    # THUMB
    # =====================================================

    def select_thumbnail(self, item):
        self.save_settings()
        path = item.data(Qt.UserRole)
        self.current_index = self.image_paths.index(path)
        self.load_settings()
        self.update_preview()

    # =====================================================
    # PREVIEW
    # =====================================================

    def update_preview(self):

        if not self.image_paths or not self.logo_path:
            return

        path = self.image_paths[self.current_index]

        img = process_image(
            path,
            self.logo_path,
            self.position.currentText(),
            self.size_slider.value(),
            self.padding_slider.value(),
            self.shape.currentText(),
            self.offset_x_slider.value(),
            self.offset_y_slider.value()
        )

        self.preview.update_preview(img)

    # =====================================================
    # PROCESS
    # =====================================================

    def process_images(self):

        self.save_settings()

        for path in self.image_paths:

            s = self.image_settings.get(path, {})

            img = process_image(
                path,
                self.logo_path,
                s.get("position", "Top-Left"),
                s.get("size", 20),
                s.get("padding", 5),
                s.get("shape", "Square"),
                s.get("x", 0),
                s.get("y", 0)
            )

            out = os.path.join(os.path.dirname(path), "logo_" + os.path.basename(path))
            save_image(img, out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())