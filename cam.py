import numpy as np, cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage
from numpy import ndarray

class Thread(QThread):

    nd_record_video = pyqtSignal(ndarray)   # 영상 저장할 때 쓰일 시그널
    video_emit = pyqtSignal(QImage)         # BGR-> RGB로 변환되어 송출될 컬러 시그널
    gray_video_emit = pyqtSignal(QImage)    # GRAY SCALE로 변환되어 송출될 흑백 시그널

    changeEdge = pyqtSignal(QImage)

    R_video = pyqtSignal(QImage)            # red 채널만 분리해 송출하는 시그널
    G_video = pyqtSignal(QImage)
    B_video = pyqtSignal(QImage)

    Y_video = pyqtSignal(QImage)            # yellow 색상이 되도록 r, g, b 컬러를 합성하여 송출하는 시그널
    M_video = pyqtSignal(QImage)
    C_video = pyqtSignal(QImage)




    def run(self):
        global cap
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read() # ret은 논리값, frame은 영상 정보. frame이 있으면 ret이 true가 된다

            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR 채널을 RGB로 변환
                height, width, channel = rgb_image.shape    # 컬러 채널을 높이, 너비, 컬러 채널로 분리한다
                bytes_per_line = channel * width
                """
                bytes per line? 
                    - row 하나에 있는 바이트 수
                    - 한 픽셀에 있는 채널 수 * row에 존재하는 픽셀 수로 구한다.                 
                """
                convert_to_qt = QImage(rgb_image, width, height, bytes_per_line, QImage.Format_RGB888)  # opencv 영상을 PyQt로 송출하기 위해 QImage로 변환
                convert_to_gray = convert_to_qt.convertToFormat(QImage.Format_Grayscale8)   # 변환된 QImage, Grayscale로 변환해 송출

                R, G, B = cv2.split(rgb_image)

                b_height, b_width  = B.shape
                b_qt = QImage(B.data, b_width, b_height, QImage.Format_Indexed8)

                g_height, g_width = G.shape
                g_qt = QImage(G.data, g_width, g_height, QImage.Format_Indexed8)

                r_height, r_width = R.shape
                r_qt = QImage(R.data, r_width, r_height, QImage.Format_Indexed8)

                zero = np.zeros((height, width, 1), dtype=np.uint8)

                Y = cv2.merge((R , G , zero))
                M = cv2.merge((R, zero, B))
                C = cv2.merge((zero, G, B))

                y_height, y_width, y_channel = Y.shape
                y_qt = QImage(Y.data, y_width, y_height, QImage.Format_RGB888)

                m_height, m_width, m_channel = M.shape
                m_qt = QImage(M.data, m_width, m_height, QImage.Format_RGB888)

                c_height, c_width, c_channel = C.shape
                c_qt = QImage(C.data, c_width, c_height, QImage.Format_RGB888)

                p1 = convert_to_qt.scaled(640, 480, Qt.KeepAspectRatio)
                p2 = convert_to_gray.scaled(640, 480, Qt.KeepAspectRatio)

                p_b = b_qt.scaled(640, 480, Qt.KeepAspectRatio)
                p_g = g_qt.scaled(640, 480, Qt.KeepAspectRatio)
                p_r = r_qt.scaled(640, 480, Qt.KeepAspectRatio)

                p_y = y_qt.scaled(640, 480, Qt.KeepAspectRatio)
                p_m = m_qt.scaled(640, 480, Qt.KeepAspectRatio)
                p_c = c_qt.scaled(640, 480, Qt.KeepAspectRatio)


                self.nd_record_video.emit(frame)

                self.video_emit.emit(p1)
                self.gray_video_emit.emit(p2)
                self.changeEdge.emit(p1)


                self.B_video.emit(p_b)
                self.G_video.emit(p_g)
                self.R_video.emit(p_r)

                self.Y_video.emit(p_y)
                self.M_video.emit(p_m)
                self.C_video.emit(p_c)

