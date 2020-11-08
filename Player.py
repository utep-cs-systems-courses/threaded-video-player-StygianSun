#! /usr/bin/env python3
from threading import Thread, Semaphore, Lock
import cv2, time

class ProducerAndConsumer():
    def __init__(self, capacity):
        self.queue = []
        self.full = Semaphore(0)
        self.empty = Semaphore(24)
        self.lock = Lock()
        self.capacity = capacity
    def insertFrame(self, frame):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(frame)
        self.lock.release()
        self.full.release()
        return
    def getFrame(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop()
        self.lock.release()
        self.empty.release()
        return frame

class FrameExtractor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.vidCap = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.vidCap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.count = 0
    def run(self):
        global frameQ
        success, img = self.vidCap.read()

        while True:
            if success and len(frameQ.queue) <= frameQ.capacity:
                frameQ.insertFrame(img)
                success, img = self.vidCap.read()
                print(f'Reading frame {self.count}')
                self.count += 1
            if self.count == self.totalFrames:
                frameQ.insertFrame(-1)
                break
        return

class GrayscaleConvertor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.count = 0
    def run(self):
        global frameQ
        global grayScaleQ

        while True:
            if frameQ.queue and len(grayScaleQ.queue) <= grayScaleQ.capacity:
                frame = frameQ.getFrame()
                if type(frame) == int and frame == -1:
                    grayScaleQ.insertFrame(-1)
                    break
                print(f'Converting Frame {self.count}')
                grayScaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                grayScaleQ.insertFrame(grayScaleFrame)
                self.count += 1
        return
    
class FrameDisplayer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0
    def run(self):
        global grayScaleQ

        while True:
            if grayScaleQ.queue:
                frame = grayScaleQ.getFrame()
                if type(frame) == int and frame == -1:
                    break
                print(f'Displaying Frame {self.count}')
                cv2.imshow('Chungus Video', frame)
                self.count += 1
                if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
        return

        
frameQ = ProducerAndConsumer(9)
grayScaleQ = ProducerAndConsumer(9)

extractFrames = FrameExtractor()
extractFrames.start()
convertFrames = GrayscaleConvertor()
convertFrames.start()
displayFrames = FrameDisplayer()
displayFrames.start()
