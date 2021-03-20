import cv2
import threading
import numpy as np
from . import safethread
from . import kalman
from . import dnnobjectdetect


class FollowObject():
    """
    Commands the Drone to follow an object, defined by the loaded model (curretly a face).
    Horizontal / vertical / FW/BackW / yaw are controlled, using Kalman filters.
    """

    def __init__(self, tello, MODEL='',PROTO='', CONFIDENCE=0.8, DETECT='Face', DEBUG=False) -> None:
        
        # face detector
        if MODEL !='' and PROTO!='':
            self.dnnfacedetect = dnnobjectdetect.DnnObjectDetect(MODEL,PROTO, CONFIDENCE=CONFIDENCE, DETECT=DETECT)
        else:
            self.dnnfacedetect = dnnobjectdetect.DnnObjectDetect(CONFIDENCE=CONFIDENCE,DETECT=DETECT)

        self.tello = tello

        # Kalman estimators
        self.kf = kalman.clKalman()
        self.kfarea= kalman.clKalman()

        # ticker for timebase
        self.ticker = threading.Event()

        #init 
        self.track = False

        self.img = None
        self.det = None
        self.tp = None

        # tracking options
        self.use_vertical_tracking = True
        self.use_rotation_tracking = True
        self.use_horizontal_tracking = True
        self.use_distance_tracking = True

        # distance between object and drone
        self.dist_setpoint = 100
        self.area_setpoint = 13

        self.cx = 0
        self.cy = 0

        # use this option to print debug data
        self.debug = DEBUG

        # processing frequency (to spare CPU time)
        self.cycle_counter = 1
        self.cycle_activation = 10

        # Kalman estimator scale factors
        self.kvscale = 6
        self.khscale = 4
        self.distscale = 3

        self.wt = safethread.SafeThread(target=self.__worker).start()
    
    def set_default_distance(self,DISTANCE=100):
        """
        Set distance from tracked object

        Args:
            DISTANCE (int, optional): [description]. Defaults to 100.
        """
        self.dist_setpoint = DISTANCE
    
    def set_default_area(self,DISTANCE=13):
        """
        Set area ration of person tracking

        Args:
            DISTANCE (int, optional): [description]. Defaults to 100.
        """
        self.area_setpoint = DISTANCE

    
    def set_tracking(self, HORIZONTAL=False, VERTICAL=True, DISTANCE=True, ROTATION=True):
        """
        Set tracking options
        Args:
            HORIZONTAL (bool, optional): Defaults to True.
            VERTICAL (bool, optional): Defaults to True.
            DISTANCE (bool, optional): Defaults to True.
        """

        self.use_vertical_tracking = VERTICAL
        self.use_horizontal_tracking = HORIZONTAL
        self.use_distance_tracking = DISTANCE
        self.use_rotation_tracking = ROTATION


    def set_image_to_process(self, img):
        """Image to process

        Args:
            img (nxmx3): RGB image
        """
        self.img = img
    
    def set_detection_periodicity(self,PERIOD=10):
        """
        Sets detection periodicity.
        Args:
            PERIOD (int, optional): detection timebase ~5ms*PERIOD. Defaults to 10.
        """
        self.cycle_activation = PERIOD

    def safety_limiter(self,leftright,fwdbackw,updown,yaw, SAFETYLIMIT=30):
        """
        Implement a safety limiter if values exceed defined threshold

        Args:
            leftright ([type]): control value for left right
            fwdbackw ([type]): control value for forward backward
            updown ([type]): control value up down
            yaw ([type]): control value rotation
        """
        val = np.array([leftright,fwdbackw,updown,yaw])

        # test uppler lover levels
        val[val>=SAFETYLIMIT] = SAFETYLIMIT
        val[val<=-SAFETYLIMIT] = -SAFETYLIMIT

        return val[0],val[1],val[2],val[3]



    def __worker(self):
        """Worker thread to process command / detections
        """

        # time base
        self.ticker.wait(0.005)

        # process image, command tello
        if self.img is not None and self.cycle_counter % self.cycle_activation == 0:

            dist = 0
            vy = 0
            vx,rx = 0,0
            # work on a local copy
            img = self.img.copy()

            # detect face
            tp,det = self.dnnfacedetect.detect(img)

            if  len(det) > 0:
                self.det = det
                self.tp = tp
                
                # init estimators
                if self.track == False:
                    h,w = img.shape[:2]
                    self.cx = w//2
                    self.cy = h//2
                    self.kf.init(self.cx,self.cy)

                    # compute init 'area', ignor x dimension
                    self.kfarea.init(1,tp[1])
                    self.track = True

                # process corrections, compute delta between two objects
                _,cp = self.kf.predictAndUpdate(self.cx,self.cy,True)

                # calculate delta over 2 axis
                mvx = -int((cp[0]-tp[0])//self.kvscale)
                mvy = int((cp[1]-tp[1])//self.khscale)

                if self.use_distance_tracking:
                    # use detection y value to estimate object distance
                    obj_y = tp[2]

                    _, ocp = self.kfarea.predictAndUpdate(1, obj_y, True)

                    dist = int((ocp[1]-self.dist_setpoint)//self.distscale)

                # Fill out variables to be sent in the tello command
                # don't combine horizontal and rotation
                if self.use_horizontal_tracking:
                    rx = 0
                    vx = mvx
                if self.use_rotation_tracking:
                    vx = 0
                    rx = mvx

                if self.use_vertical_tracking:
                    vy = mvy

                # limit signals if is the case, could save your tello
                vx,dist,vy,rx = self.safety_limiter(vx,dist,vy,rx,SAFETYLIMIT=40)

                cmd = "rc {leftright} {fwdbackw} {updown} {yaw}".format(leftright=vx,fwdbackw=-dist,updown=vy,yaw=rx)
                self.tello.send_cmd(cmd)
                
                if self.debug:
                   print (cmd, str(self.cycle_counter))

            else:
                # no detection, keep position
                cmd = "rc {leftright} {fwdbackw} {updown} {yaw}".format(leftright=0,fwdbackw=0,updown=0,yaw=0)
                self.tello.send_cmd(cmd)
                self.det = None
                
        self.cycle_counter +=1


                 
    def draw_detections(self,img, HUD=True, ANONIMUS=False):
        """Draw detections on an image

        Args:
            img (nxmx3): RGB image array
            HUD (boolean): overlay tello information
        """
        sizef = 0.5
        typef = cv2.FONT_HERSHEY_SIMPLEX
        color = [0,255,255]
        sizeb = 2
        if img is not None:

            h,w = img.shape[:2]

            if HUD and self.tello.state_value is not None and len(self.tello.state_value)>0:
                hud =self.tello.state_value
                cv2.putText(img,str('Battery') + ": " + str(hud[21]),(w//2-100,20),typef,sizef,color,sizeb)
                cv2.putText(img,str('Height') + ": " + str(hud[19]),(30,20),typef,sizef,color,sizeb)
                cv2.putText(img,str('Tof') + ": " + str(hud[17]),(30,40),typef,sizef,color,sizeb)
                cv2.putText(img,str('Temp') + ": " + str(hud[15]),(w//2+100,20),typef,sizef,color,sizeb)
                cv2.putText(img,str('Baro') + ": " + str(hud[23]),(w//2+100,40),typef,sizef,color,sizeb)
                cv2.putText(img,str('Acceleration') + ": " + 'agx'+ " "+ str(hud[-6]) + ' agy'+ " "+ str(hud[-4]) + ' agz'+ " "+ str(hud[-2]),(30,h-30),typef,sizef,color,sizeb)

                for ev in self.tello.eventlist:
                    ret = ev['cmd']
                    if ret is not None and ret == 'wifi?':
                        cv2.putText(img,str(ev['info']) + ": " + str(ev['val']),(w//2-100,40),typef,sizef,color,sizeb)

            # handle detection visualization
            if self.det is not None:            
                for val in self.det:
                    if ANONIMUS:
                        cv2.rectangle(img,(val[0],val[1]),(val[0]+val[2],val[1]+val[3]),[0,255,0],-1)
                    else:
                        cv2.rectangle(img,(val[0],val[1]),(val[0]+val[2],val[1]+val[3]),[0,255,0],2)
                    
                    cv2.circle(img,(self.tp[0],self.tp[1]),3,[0,0,255],-1)
                cv2.circle(img,(int(w/2),int(h/2)),4,[0,255,0],1)
                cv2.line(img,(int(w/2),int(h/2)),(self.tp[0],self.tp[1]),[0,255,0],2)
