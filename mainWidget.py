import numpy as np, cv2, sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from cam import Thread
from secondWidget import SecondWidget

ui = uic.loadUiType("mainTEST.ui")[0]

class TestClass(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.thread = Thread(self)
        self.second = SecondWidget(self, self.thread)
        self.actionEdge.triggered.connect(self.openSecondWidget)

    def qimg2nparr(self, frame):
        income_frame = frame.convertToFormat(QImage.Format_RGB888)
        h, w = income_frame.height(), income_frame.width()
        ptr = income_frame.constBits()
        ptr.setsize(h * w * 3)
        return np.frombuffer(ptr, np.uint8).reshape(h, w, 3)

    def openSecondWidget(self):
        self.second.move(2800, 200)
        self.second.show()

    def setImage(self, frame):
        height, width = self.origin_video.height(), self.origin_video.width()
        self.origin_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setRedImage(self, frame):
        height, width = self.r_video.height(), self.r_video.width()
        self.r_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setGreenImage(self, frame):
        height, width = self.g_video.height(), self.g_video.width()
        self.g_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setBlueImage(self, frame):
        height, width = self.b_video.height(), self.b_video.width()
        self.b_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))


    def openCamera(self):
        self.thread.video_emit.connect(self.setImage)
        self.thread.start()

    def RGB(self):
        self.thread.R_video.connect(self.setRedImage)
        self.thread.G_video.connect(self.setGreenImage)
        self.thread.B_video.connect(self.setBlueImage)
        self.thread.start()



    def MoveWidget(self):
        pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TestClass()
    widget.show()
    app.exec_()
