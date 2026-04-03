from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Preview")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(300)

    def update_preview(self, pil_image):
        if pil_image is None:
            return

        # Keep aspect ratio
        pil_image.thumbnail((300, 300))

        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            QImage.Format_RGBA8888
        )

        pixmap = QPixmap.fromImage(qimage)
        self.setPixmap(pixmap)