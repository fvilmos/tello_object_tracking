###########################################
# Tello drone object tracker
# Author: fvilmos
###########################################

from utils.telloconnect import TelloConnect
from utils.followobject import FollowObject
import signal
import cv2
import argparse


if __name__=="__main__":

    # input arguments
    parser = argparse.ArgumentParser(description='Tello Object tracker. keys: t-takeoff, l-land, v-video, q-quit w-up, s-down, a-ccw rotate, d-cw rotate\n')
    parser.add_argument('-model', type=str, help='DNN model caffe or tensorflow, see data folder', default='')
    parser.add_argument('-proto', type=str, help='Prototxt file, see data folder', default='')
    parser.add_argument('-obj', type=str, help='Type of object to track. [Face, Person], default = Face', default='Face')
    parser.add_argument('-dconf', type=float, help='Detection confidence, default = 0.7', default=0.7)
    parser.add_argument('-debug', type=bool, help='Enable debug, lists messages in console', default=False)
    parser.add_argument('-video', type=str, help='Use as inputs a video file, no tello needed, debug must be True', default="")
    parser.add_argument('-vsize', type=list, help='Video size received from tello', default=(640,480))
    parser.add_argument('-th', type=bool, help='Horizontal tracking', default=False)
    parser.add_argument('-tv', type=bool, help='Vertical tracking', default=True)
    parser.add_argument('-td', type=bool, help='Distance tracking', default=True)
    parser.add_argument('-tr', type=bool, help='Rotation tracking', default=True)


    args = parser.parse_args()

    #processing speed
    pspeed = 1

    #img size
    imgsize=args.vsize

    # save video
    writevideo = False

    # signal handler
    def signal_handler(sig, frame):
        raise Exception

    # capture signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    if args.debug and args.video is not None:
        tello = TelloConnect(DEBUG=True, VIDEO_SOURCE=args.video)
    else:
        tello = TelloConnect(DEBUG=False)
    tello.set_image_size(imgsize)
    
    videow = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (imgsize))

    if tello.debug == True: pspeed = 30

    # ask stats periodically
    tello.add_periodic_event('wifi?',40,'Wifi')

    # wait till connected, than proceed
    tello.wait_till_connected()
    tello.start_communication()
    tello.start_video()

    fobj = FollowObject(tello, MODEL=args.model, PROTO=args.proto, CONFIDENCE=args.dconf, DEBUG=False, DETECT=args.obj)
    fobj.set_tracking( HORIZONTAL=args.th, VERTICAL=args.tv,DISTANCE=args.td, ROTATION=args.tr)

    while True:

        try:
            img = tello.get_frame()

            # wait for valid frame
            if img is None: continue

            imghud = img.copy()

            fobj.set_image_to_process(img)
            
            k = cv2.waitKey(pspeed)

        except Exception:
            tello.stop_video()
            tello.stop_communication()
            break
        
        fobj.draw_detections(imghud, ANONIMUS=False)
        cv2.imshow("TelloCamera",imghud)
        
        # write video
        if k ==ord('v'):
            if writevideo == False : writevideo = True
            else: writevideo = False
        
        if writevideo == True:
            videow.write(img)

        # exit
        if k == ord('q'):
            tello.stop_communication()
            break

        if k == ord('t'):
            tello.send_cmd('takeoff')
        
        if k == ord('l'):
            tello.send_cmd('land')

        if k == ord('w'):
            tello.send_cmd('up 20')
        
        if k == ord('s'):
            tello.send_cmd('down 20')

        if k == ord('a'):
            tello.send_cmd('cw 20')

        if k == ord('d'):
            tello.send_cmd('ccw 20')

    cv2.destroyAllWindows()



