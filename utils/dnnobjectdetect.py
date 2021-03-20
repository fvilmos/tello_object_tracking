import cv2
import numpy as np

class DnnObjectDetect():
    """
    Using a Dnn model to detect face

    """
    def __init__(self, MODEL='./data/opencv_face_detector.caffemodel', PROTO='./data/deploy.prototxt', CONFIDENCE=0.8, DETECT='Face'):
        """
        init function 
        Args:
            MODEL (str, optional): caffemodel. Defaults to './data/opencv_face_detector.caffemodel'.
            PROTO (str, optional): prototxt. Defaults to './data/deploy.prototxt'.
            DETECT (str, optional): Type of object to be detected ['Face', 'Person']. Default is 'Face'.
        """

        if DETECT == 'Face':
            self.network = cv2.dnn.readNetFromCaffe(PROTO, MODEL)      
        if DETECT == 'Person':
            self.network = cv2.dnn.readNetFromTensorflow(MODEL,PROTO)    

        self.type = DETECT
        self.confidence = CONFIDENCE

    def detect(self,img, size=(300,300)):
        """
        Detect the face
        Args:
            img ([type]): image

        Returns:
            [type]: list of detected faces
        """

        detections = []
        tp =[]
        h,w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img,size))
        self.network.setInput(blob)

        det = self.network.forward()
        for d in det:
            conf = d[0,0,2]

            # process just high confidence detections
            if conf > self.confidence:
                # set classID - if person detection is active
                classId = None
                if self.type == 'Person':
                    classId = int(d[0, 0, 1])

                    # check object type detected, 1 is person
                    if  classId == 1:
                        bbox = (d[0,0,3:7]* np.array([w,h,w,h])).astype(int)
                        bbox = (bbox[0],bbox[1],bbox[2]-bbox[0],bbox[3]-bbox[1])
                        detections.append(bbox)
                        
                        # construct target point, [midx,midy,position to track]
                        # check area related to the full image
                        area_frame = w*h
                        area_det = detections[0][2] * detections[0][3]

                        # multiply with 10, to keep the compatibility between detectors
                        area_ratio = int((area_det/area_frame)*1000)

                        tp = [detections[0][0] + detections[0][2]//2, detections[0][1] + detections[0][3]//3, area_ratio]
                else:

                    bbox = (d[0,0,3:7]* np.array([w,h,w,h])).astype(int)
                    bbox = (bbox[0],bbox[1],bbox[2]-bbox[0],bbox[3]-bbox[1])

                    # calculate center point
                    detections.append(bbox)
                    tp = [detections[0][0] + detections[0][2]//2, detections[0][1] + detections[0][3]//2, detections[0][3]]

        return tp, detections

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