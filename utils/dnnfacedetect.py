import cv2
import numpy as np

class DnnFaceDetect():
    """
    Using a Caffe model to detect face

    """

    def __init__(self, CAFFEMODEL='./data/opencv_face_detector.caffemodel', PROTO='./data/deploy.prototxt', CONFIDENCE=0.8):
        """
        init 
        Args:
            CAFFEMODEL (str, optional): caffemodel. Defaults to './data/opencv_face_detector.caffemodel'.
            PROTO (str, optional): prototxt. Defaults to './data/deploy.prototxt'.
            CONFIDENCE (float, optional): detection conficence. Defaults to 0.8.
        """
        self.confidence = CONFIDENCE
        self.network = cv2.dnn.readNetFromCaffe(PROTO, CAFFEMODEL)        

    def detect(self,img):
        """
        Detect the face
        Args:
            img ([type]): image

        Returns:
            [type]: list of detected faces
        """

        detections = []
        h,w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img,(300,300)))
        self.network.setInput(blob)

        det = self.network.forward()
        for d in det:
            conf = d[0,0,2]
            if conf > self.confidence :
                bbox = (d[0,0,3:7]* np.array([w,h,w,h])).astype(int)
                bbox = (bbox[0],bbox[1],bbox[2]-bbox[0],bbox[3]-bbox[1])
                detections.append(bbox)

        return detections

    def draw_detections(self,det,img,COLOR=[0,255,0]):
        """
        Draw detections

        Args:
            det ([type]): list of detected faces
            img ([type]): image
            COLOR (list, optional): box color. Defaults to [0,255,0].
        """

        for d in det:
            cv2.rectangle(img,(d[0],d[1]),(d[2],d[3]),COLOR,2)
    

    def detect_and_draw(self,img):
        """
        Draw detection on an image
        Args:
            img ([type]): image to draw the detections
        """
        det = self.detect(img)
        self.draw_detections(det,img)