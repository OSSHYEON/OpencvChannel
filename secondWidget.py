import numpy as np, cv2, datetime
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog


class SecondWidget(QDialog):

    def __init__(self, parent=None, thread=None):
        super(SecondWidget, self).__init__(parent)
        loadUi('secondTEST.ui', self)
        self.parent = parent
        self.thread=thread
        self.thread.video_emit.connect(self.camera_connect)
        self.now = datetime.datetime.now().strftime("%d_%H-%M-%S")

    def camera_connect(self, frame):
        self.lbl_origin.setPixmap(QPixmap.fromImage(frame))


    def CannySlot(self):
        self.thread.video_emit.connect(self.CannyEdge)


    def qimg2nparr(self, frame):
        income_frame = frame.convertToFormat(QImage.Format_RGB888)
        h, w = income_frame.height(), income_frame.width()
        ptr = income_frame.constBits()
        ptr.setsize(h * w * 3)
        return np.frombuffer(ptr, np.uint8).reshape(h, w, 3)


    def CannyEdge(self, frame):
        narr_frame = self.qimg2nparr(frame)
        dst = cv2.Canny(narr_frame, 100, 200)
        h, w = dst.shape
        edge = QImage(dst.data, w, h, QImage.Format_Grayscale8)
        self.lbl_edge.setPixmap(QPixmap.fromImage(edge).scaled(h, w, Qt.KeepAspectRatio))


    def setMagentaImage(self, frame):
        height, width = self.m_video.height(), self.m_video.width()
        self.m_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setYellowImage(self, frame):
        height, width = self.y_video.height(), self.y_video.width()
        self.y_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setCyanImage(self, frame):
        height, width = self.c_video.height(), self.c_video.width()
        self.c_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def Magenta(self):
        self.thread.M_video.connect(self.setMagentaImage)


    def Yellow(self):
        self.thread.Y_video.connect(self.setYellowImage)

    def Cyan(self):
        self.thread.C_video.connect(self.setCyanImage)

    def SaveVideoStart(self):
        date = datetime.datetime.now()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.image_save = cv2.VideoWriter(str(date)+".avi", fourcc, 29.97, (640, 480))
        self.thread.nd_record_video.connect(self.SaveVideo)

    def SaveVideo(self, frame):
        self.image_save.write(frame)

    def SaveVideoStop(self):
        self.image_save.release()


    def Left(self):
        hsize = self.lbl_edge.geometry()
        if hsize.x() > 0:
            hsize.moveLeft(hsize.x() - 100)
            self.lbl_edge.setGeometry(hsize)
            print(hsize.x())
        if hsize.x() < 0:
            pass

    def Right(self):
        hsize = self.lbl_edge.geometry()
        if hsize.x() >= -80 and hsize.x() < 430:
            hsize.moveLeft(hsize.x() + 100)
            self.lbl_edge.setGeometry(hsize)
        print(hsize.x())