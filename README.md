# Tello drone object tracker

The DJI Tello drone provides interfacing capability through UDP frames, see the SDK[1,2]. This project implements an object tracker (Person, Face) using the live stream from the drone while sending positioning commands back, control loop is done with 2D Kalman filters (constant velocity model). On the video stream, the statistical information from the drone is overlayed, useful to verify the battery or the WiFi signal strength.

The following features are available (see command-line flags):
- Follow the object detected (left/ right/ forward/ backward / up / down, centering trough rotation)
- Point of interest tracking (Drone stays on the same location, keeps the height, but rotates towards the object detected)
- Movement mime (Drone keeps the height, instead of rotation towards to the detected object slides left / rights keeping the object-centered)
- Manual mode: takeoff/ land / left / right / up / down

<p align="center"> 
    <img src="./info/output.gif" alt="400" width="400">
</p>

The object detection part is done with deep learning, using a pre-trained models (face detection, mobilenet for object tracking). Details about files can be found on the OpenCV site, see dnn module [3,5].

### How to use

1. Clone the repository;
2. Start the drone, connect to the Tello hotspot with your PC/ laptop;
3. Start the program, wait till the video stream is displayed;
4. Use the 't' - key for takeoff, the drone will hover at 50 cm, after the object is detected tracking starts automatically;
5. Keep your finger on the 'l' key (land) - for emergency stop :).

Typical usage (object detection / tracking):
```
python3 tello_object_tracking.py -proto ./data/ssd_mobilenet_v1_coco_2017_11_17.pbtxt -model ./data/frozen_inference_graph.pb -obj Person -dconf 0.4

DEBUG for mode

python3 tello_object_tracking.py -proto ./data/ssd_mobilenet_v1_coco_2017_11_17.pbtxt -model ./data/frozen_inference_graph.pb -obj Person -debug True -video ./data/<your video.avi> -dconf 0.4
```
Command line list:

```
usage: tello_object_tracking.py [-h] [-model MODEL] [-proto PROTO] [-obj OBJ]
                                [-dconf DCONF] [-debug DEBUG] [-video VIDEO]
                                [-vsize VSIZE] [-th TH] [-tv TV] [-td TD]
                                [-tr TR]

Tello Object tracker. keys: t-takeoff, l-land, v-video, q-quit w-up, s-down,
a-ccw rotate, d-cw rotate

optional arguments:
  -h, --help    show this help message and exit
  -model MODEL  DNN model caffe or tensorflow, see data folder
  -proto PROTO  Prototxt file, see data folder
  -obj OBJ      Type of object to track. [Face, Person], default = Face
  -dconf DCONF  Detection confidence, default = 0.7
  -debug DEBUG  Enable debug, lists messages in console
  -video VIDEO  Use as inputs a video file, no tello needed, debug must be
                True
  -vsize VSIZE  Video size received from tello
  -th TH        Horizontal tracking
  -tv TV        Vertical tracking
  -td TD        Distance tracking
  -tr TR        Rotation tracking
```

### TODO
 - Improve object detection using better performing models. 
 - Introduce a tracker in combination with object detection to spare CPU time.
 - Use odometry information to prevent drifting (if is the case)
 - add pose recognition for visual commands

Any contribution is welcomed! 

# Resources


1. [Tello SDK 1.3.0.0](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf)
2. [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
3. [OpenCV](https://github.com/opencv/opencv)
4. [Kalman filter intro](https://www.kalmanfilter.net/kalmanmulti.html)
5. [Model sources](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)


/Enjoy.