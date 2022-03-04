import numpy as np, cv2, datetime
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog


class SecondWidget(QDialog):    # QDialog 상속받아 second widget 생성

    def __init__(self, parent=None, thread=None):   # __init__에서 parent 명시, 부모 클래스로부터 thread 받아와 연결
        super(SecondWidget, self).__init__(parent)
        loadUi('secondTEST.ui', self)
        self.parent = parent
        self.thread=thread
        self.thread.video_emit.connect(self.camera_connect)
        self.now = datetime.datetime.now().strftime("%d_%H-%M-%S")

    def camera_connect(self, frame):
        self.lbl_origin.setPixmap(QPixmap.fromImage(frame))


    def CannySlot(self):    # Canny Edge 검출에 사용될 슬롯 연결
        self.thread.video_emit.connect(self.CannyEdge)  # Canny Edge 함수 호출


    def qimg2nparr(self, frame):    # 입력받는 frame 을 numpy array로 변환하는 함수
        income_frame = frame.convertToFormat(QImage.Format_RGB888)  # 입력 받는 frame을 PyQt5 QImage로 변환
        h, w = income_frame.height(), income_frame.width()
        ptr = income_frame.constBits()  # const : 상수, bits: frame의 비트. QImage로 변환한 frame 정보 중 상수인 비트만 받음
        ptr.setsize(h * w * 3)  # 상수인 비트만 따로 담은 frame의 크기를 QImage로 변환된 frame의 높이 * 너비 * 채널의 수로 설정한다
        return np.frombuffer(ptr, np.uint8).reshape(h, w, 3)    # numpy의 frombuffer 함수를 사용해 상수 비트 정보를 1차원 배열로 읽은 다음, 다시 3차원 배열로 변환한다.


    def CannyEdge(self, frame):
        narr_frame = self.qimg2nparr(frame) # numpy array로 변환된 영상 정보 받아
        dst = cv2.Canny(narr_frame, 100, 200)   # Canny 함수로 Canny Edge 검출
        h, w = dst.shape
        edge = QImage(dst.data, w, h, QImage.Format_Grayscale8) # numpy array 형태인 데이터를 다시 QImage로 변환
        self.lbl_edge.setPixmap(QPixmap.fromImage(edge).scaled(h, w, Qt.KeepAspectRatio))   # 변환된 QImage PyQt Label에 송출


    def SobelSlot(self):    # Sobel Edge 검출에 사용될 슬롯 연결
        self.thread.video_emit.connect(self.SobelEdge)  # Sobel Edge 함수 호출

    def SobelEdge(self, frame):
        """
                cv2.Sobel(src, ddepth, dx, dy, ksize, scale, delta, borderType)
                src : 입력이미지
                ddepth : 출력 이미지 형태. -1이면 입력 이미지와 동일한 데이터 형태로 출력됨
                dx : x방향 미분 차수
                dy : y방향 미분 차수
                kszie : 커널 크기. Sobel필터의 경우 1, 3 5, 7만 가능하며 default=3으로 지정되어 있다.
                scale : 비율
                delta : 오프셋
                borderType :  가장자리 픽셀 확장 방식
        """
        narr_image = self.qimg2nparr(frame)
        narr_image = cv2.cvtColor(narr_image, cv2.COLOR_BGR2GRAY)   # BGR 영상 GRAY 색상으로 변환

        # Sobel X
        dst4 = cv2.Sobel(narr_image, cv2.CV_32F, 1, 0)  # Sobel 함수 사용해 Sobel Edge 검출
        dst4 = cv2.convertScaleAbs(dst4)    # convertScaleAbs(), sobel x 결과에 절대값 적용하고 값 범위를 8비트 unsigned int로 변경

        # Sobel Y
        dst5 = cv2.Sobel(narr_image, cv2.CV_32F, 0, 1)
        dst5 = cv2.convertScaleAbs(dst5)

        # Sobel X + Sobel Y
        """
        이미지에 대한 산술 연산하는 addWeighted() 함수 사용
        함수 인자가 addWeighted(imgA, a, imgB, b, c) 일 때, 산술 식은 다음과 같다.
        result = (imgA * a) + (imgB * b) + c 
        """
        sobel_add = cv2.addWeighted(dst4, 1, dst5, 1, 0)


        sobel_h, sobel_w = sobel_add.shape  # Sobel X와 Sobel Y를 합한 sobel_add의 너비, 높이 측정
        sobel_edge = QImage(sobel_add.data, sobel_w, sobel_h, QImage.Format_Grayscale8) # QImage로 변환

        self.lbl_sobel.setPixmap(QPixmap.fromImage(sobel_edge).scaled(sobel_h, sobel_w, Qt.KeepAspectRatio))    # Label에 송출


    def Magenta(self):  # thread에서 magenta 색상으로 변환된 시그널 받아 setMagentaImage() 함수로 보냄
        self.thread.M_video.connect(self.setMagentaImage)

    def Yellow(self):
        self.thread.Y_video.connect(self.setYellowImage)

    def Cyan(self):
        self.thread.C_video.connect(self.setCyanImage)


    def setMagentaImage(self, frame):   # magenta 시그널 label에 송출
        height, width = self.m_video.height(), self.m_video.width()
        self.m_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setYellowImage(self, frame):
        height, width = self.y_video.height(), self.y_video.width()
        self.y_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def setCyanImage(self, frame):
        height, width = self.c_video.height(), self.c_video.width()
        self.c_video.setPixmap(QPixmap.fromImage(frame).scaled(width, height, Qt.KeepAspectRatio))

    def SaveVideoStart(self):   # 화면에 송출되는 영상 저장하는 함수
        """
            :date: datetime의 now()함수 사용해 녹화 시작 시간을 파일 이름으로 지정
            :fourcc: 영상 코덱 설정
            cv2.VideoWriter(파일이름, 코덱, 초당 프레임 수, 동영상 프레임 크기),
                - VideoWriter 클래스 이용해 프레임을 동영상 파일로 저장할 수 있다.
                - 영상을 저장하기 위해서 객체 생성한 다음
                - write() 함수 사용하여 프레임을 저장한다.

        """
        date = datetime.datetime.now()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.image_save = cv2.VideoWriter(str(date)+".avi", fourcc, 29.97, (640, 480))
        self.thread.nd_record_video.connect(self.SaveVideo) # 영상 저장하는 함수 호출

    def SaveVideo(self, frame):
        self.image_save.write(frame)    # cv2.VideoWriter.write(frame). SaveVideoStart() 함수에서 객체를 생성했으므로 프레임을 저장할 수 있다.

    def SaveVideoStop(self):
        self.image_save.release()


    def Left(self): # PyQt Label 이동하는 함수
        hsize = self.lbl_edge.geometry()
        if hsize.x() > 0:
            hsize.moveLeft(hsize.x() - 100)
            self.lbl_edge.setGeometry(hsize)
            print(hsize.x())
        if hsize.x() < 0:
            print("왼쪽으로 더 갈 수 없어여")

    def Right(self):
        hsize = self.lbl_edge.geometry()
        if hsize.x() >= -80 and hsize.x() < 430:
            hsize.moveLeft(hsize.x() + 100)
            self.lbl_edge.setGeometry(hsize)
        print(hsize.x())