import cv2
import numpy as np
class clKalman():
    def __init__(self):
        '''
        Init local variables and Kalman filter
        '''

        # 2d Kalman
        self.kalman = cv2.KalmanFilter(4, 2)

        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],[0, 1, 0, 1],[0, 0, 1, 0], [0, 0, 0, 1]],np.float32)

        self.kalman.processNoiseCov = np.array([[1, 0, 0 ,0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]],np.float32) * 0.01

        # state variables
        self.last_measurement = np.array((2, 1), np.float32)
        self.current_measurement = np.array((2, 1), np.float32)
        self.last_prediction = np.zeros((2, 1), np.float32)
        self.current_prediction = np.zeros((2, 1), np.float32)

        # correction => take from measurement, add to correction
        self.xi = 0
        self.yi = 0


    def predictAndUpdate(self,x,y,correct=True):
        '''
        Makes the update and correction phase from Kalman
        :param x: first parameter to estimeate in a 2d space
        :param y: secound parameter to estimate in a 2d space
        :param correct: if active, measurement correction take place, otherwise just predict.
        Usefull if it is lost the measurement, then we can realy only on estimation.
        :return: last estimation, current estimate
        '''
        self.last_prediction = self.current_prediction
        self.last_measurement = self.current_measurement
        self.current_measurement = np.array([[np.float32(x-self.xi)], [np.float32(y-self.yi)]])

        # correct and predict, if is the case
        if correct:
            self.kalman.correct(self.current_measurement)
        self.current_prediction = self.kalman.predict()

        self.current_prediction = [self.current_prediction[0]+self.xi, self.current_prediction[1]+self.yi]

        return self.last_prediction, self.current_prediction

    def getStateVariables(self):
        '''
        Helper to return internal variables
        :return: last/current measurement values; last / current prediction values; array of (2,1)
        '''
        return self.last_measurement, self.current_measurement, self.last_prediction, self.current_prediction

    def init(self,x,y):
        '''
        State initialization
        :param x: init x value
        :param y: init y value
        :return:
        '''
        self.xi = x
        self.yi = y
