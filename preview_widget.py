from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class ImagePreview(QLabel):
    def __init__(self, parent=None):
        super().__init__()

        self.parent_app = parent
        self.setAlignment(Qt.AlignCenter)

        self.dragging = False
        self.last_pos = None

    def update_preview(self, pil_image):

        if pil_image is None:
            return

        img = pil_image.copy()
        img.thumbnail((800, 600))

        data = img.tobytes("raw", "RGBA")

        qimage = QImage(
            data,
            img.width,
            img.height,
            QImage.Format_RGBA8888
        )

        self.setPixmap(QPixmap.fromImage(qimage))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):

        if not self.dragging:
            return

        delta = event.pos() - self.last_pos
        self.last_pos = event.pos()

        self.parent_app.offset_x_slider.setValue(
            self.parent_app.offset_x_slider.value() + delta.x()
        )

        self.parent_app.offset_y_slider.setValue(
            self.parent_app.offset_y_slider.value() + delta.y()
        )

    def mouseReleaseEvent(self, event):
        self.dragging = False