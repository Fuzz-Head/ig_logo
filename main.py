import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QComboBox, QSlider
)
from PySide6.QtCore import Qt

from image_processor import process_image, save_image
from preview_widget import ImagePreview


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Instagram Logo Tool")
        self.setGeometry(200, 200, 500, 600)

        self.setAcceptDrops(True)

        self.image_paths = []
        self.logo_path = ""

        layout = QVBoxLayout()

        # -------- Drag & Drop --------
        self.drop_label = QLabel("Drag & Drop Images Here")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet(
            "border: 2px dashed gray; padding: 20px;"
        )

        # -------- Preview --------
        self.preview = ImagePreview()

        # -------- Buttons --------
        btn_images = QPushButton("Select Images")
        btn_images.clicked.connect(self.select_images)

        btn_logo = QPushButton("Select Logo")
        btn_logo.clicked.connect(self.select_logo)

        self.logo_label = QLabel("No logo selected")

        # -------- Position --------
        self.position_dropdown = QComboBox()
        self.position_dropdown.addItems([
            "Top-Left", "Top-Right",
            "Bottom-Left", "Bottom-Right",
            "Center"
        ])
        self.position_dropdown.currentIndexChanged.connect(self.update_preview)

        # -------- Shape --------
        self.shape_dropdown = QComboBox()
        self.shape_dropdown.addItems(["Square", "Circle"])
        self.shape_dropdown.currentIndexChanged.connect(self.update_preview)

        # -------- Size --------
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(5)
        self.size_slider.setMaximum(50)
        self.size_slider.setValue(20)
        self.size_slider.valueChanged.connect(self.update_preview)

        self.size_label = QLabel("Size: 20%")

        # -------- Padding --------
        self.padding_slider = QSlider(Qt.Horizontal)
        self.padding_slider.setMinimum(0)
        self.padding_slider.setMaximum(50)
        self.padding_slider.setValue(10)
        self.padding_slider.valueChanged.connect(self.update_preview)

        self.padding_label = QLabel("Padding: 10px")

        # -------- Process --------
        btn_process = QPushButton("Process All Images")
        btn_process.clicked.connect(self.process_images)

        # -------- Layout --------
        layout.addWidget(self.drop_label)
        layout.addWidget(self.preview)

        layout.addWidget(btn_images)
        layout.addWidget(btn_logo)
        layout.addWidget(self.logo_label)

        layout.addWidget(QLabel("Position"))
        layout.addWidget(self.position_dropdown)

        layout.addWidget(QLabel("Logo Shape"))
        layout.addWidget(self.shape_dropdown)

        layout.addWidget(self.size_label)
        layout.addWidget(self.size_slider)

        layout.addWidget(self.padding_label)
        layout.addWidget(self.padding_slider)

        layout.addWidget(btn_process)

        self.setLayout(layout)

    # -------- Drag & Drop --------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        files = []

        for url in event.mimeData().urls():
            path = url.toLocalFile().strip()

            if os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg")):
                files.append(path)

        print("Dropped files:", files)

        self.image_paths = files
        self.drop_label.setText(f"{len(files)} images loaded")

        self.update_preview()

    # -------- File Select --------
    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg)"
        )
        if files:
            self.image_paths = files
            self.drop_label.setText(f"{len(files)} images selected")
            self.update_preview()

    def select_logo(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file:
            self.logo_path = file.strip()
            self.logo_label.setText("Logo selected")
            self.update_preview()

    # -------- Preview --------
    def update_preview(self):
        self.size_label.setText(f"Size: {self.size_slider.value()}%")
        self.padding_label.setText(f"Padding: {self.padding_slider.value()}px")

        if not self.image_paths or not self.logo_path:
            return

        try:
            preview_image = process_image(
                self.image_paths[0],
                self.logo_path,
                position=self.position_dropdown.currentText(),
                scale_percent=self.size_slider.value(),
                padding=self.padding_slider.value(),
                shape=self.shape_dropdown.currentText()
            )

            self.preview.update_preview(preview_image)

        except Exception as e:
            print(f"Preview error: {e}")

    # -------- Processing --------
    def process_images(self):
        print("BUTTON CLICKED")
        print("Images:", self.image_paths)
        print("Logo:", self.logo_path)

        if not self.image_paths or not self.logo_path or self.logo_path.strip() == "":
            self.drop_label.setText("❌ Select images & logo first!")
            return

        success_count = 0
        errors = []

        for path in self.image_paths:
            print(f"Processing: {path}")

            try:
                processed = process_image(
                    path,
                    self.logo_path,
                    position=self.position_dropdown.currentText(),
                    scale_percent=self.size_slider.value(),
                    padding=self.padding_slider.value(),
                    shape=self.shape_dropdown.currentText()
                )

                # Save in same folder
                folder = os.path.dirname(path)
                filename = os.path.basename(path)
                new_filename = f"logo_{filename}"

                output_path = os.path.join(folder, new_filename)

                print(f"Saving to: {output_path}")

                save_image(processed, output_path)

                if os.path.exists(output_path):
                    success_count += 1
                else:
                    errors.append(f"Not saved: {filename}")

            except Exception as e:
                print(f"ERROR: {e}")
                errors.append(str(e))

        # -------- Final UI Update --------
        if success_count > 0:
            message = f"✅ Saved {success_count} images in original folders"
        else:
            message = "❌ No images saved!"

        if errors:
            message += f"\n⚠ {len(errors)} errors (check console)"

        self.drop_label.setText(message)

        print("\n---- DEBUG LOG ----")
        for err in errors:
            print(err)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())