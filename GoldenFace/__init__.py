#-- GoldenFace 1.0 (Face Golden Ratio & Cosine Similarity Library)--
# Author      : Umit Aksoylu
# Date        : 15.05.2020
# Description : Facial Cosine Similarity,Face Golden Ratio Calculation And Facial Landmark Detecting/Drawing Library
# Website     : http://umit.space
# Mail        : umit@aksoylu.space
# Github      : https://github.com/Aksoylu/GoldenFace

import cv2
from . import goldenMath
from . import functions
from . import landmark
import time
import pkg_resources
import numpy as np

class goldenFace:

    img = ""
    image_gray = ""
    landmark_detector = None
    face_detector = None

    def __init__(self, path):
        if isinstance(path, str):
            self.img = cv2.imread(path)
        else:
            self.img = path
        
        if self.img is None:
            raise ValueError("Could not load image. Please check the path or input array.")

        self.image_gray =cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        
        # Optimize: Load models only once
        if goldenFace.landmark_detector is None:
            goldenFace.landmark_detector = cv2.face.createFacemarkLBF()
            filepath = pkg_resources.resource_filename(__name__, "landmark.yaml")
            goldenFace.landmark_detector.loadModel(filepath)
        
        if goldenFace.face_detector is None:
            goldenFace.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

        self.landmark_detector = goldenFace.landmark_detector
        self.face_detector = goldenFace.face_detector

        self.faces = self.face_detector.detectMultiScale(self.image_gray, 1.3, 5)

        for faceBorders in self.faces:
            (x,y,w,h) = faceBorders
            self.faceBorders = faceBorders
            _, self.landmarks = self.landmark_detector.fit(self.image_gray, self.faces)
            self.landmarks = (self.landmarks[0].astype(int), )
            self.facePoints = landmark.detectLandmark(self.landmarks)
            for key, value in self.facePoints.items():
                self.facePoints[key] = [int(val) for val in value]


            break

    def drawFaceCover(self,color):
        (x,y,w,h) = self.faceBorders
        self.img =  cv2.rectangle(self.img,(x,y),(x+w, y+h),color,2)

    def drawLandmark(self,color):
        self.img = landmark.drawLandmark(self.img, self.landmarks,color)

    def drawMask(self,color):
        self.img  = goldenMath.drawMask(self.img,self.faceBorders,self.facePoints,color)

    def drawTGSM(self,color):
        self.img = goldenMath.drawTGSM(self.img,self.faceBorders,self.facePoints,color)

    def drawVFM(self,color):
        self.img = goldenMath.drawVFM(self.img,self.faceBorders,self.facePoints,color)

    def drawTZM(self,color):
        self.img = goldenMath.drawTZM(self.img,self.faceBorders,self.facePoints,color)

    def drawLC(self,color):
        self.img = goldenMath.drawLC(self.img,self.faceBorders,self.facePoints,color)

    def drawTSM(self,color):
        self.img = goldenMath.drawTSM(self.img,self.faceBorders,self.facePoints,color)

    def calculateTGSM(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        return goldenMath.calculateTGSM(self.faceBorders,self.facePoints)

    def calculateVFM(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        return goldenMath.calculateVFM(self.faceBorders,self.facePoints)

    def calculateTZM(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        return goldenMath.calculateTZM(self.faceBorders,self.facePoints)

    def calculateTSM(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        return goldenMath.calculateTSM(self.faceBorders,self.facePoints)

    def calculateLC(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        return goldenMath.calculateLC(self.faceBorders,self.facePoints)

    def geometricRatio(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        TZM = goldenMath.calculateTZM(self.faceBorders,self.facePoints)
        TGSM = goldenMath.calculateTGSM(self.faceBorders,self.facePoints)
        VFM = goldenMath.calculateVFM(self.faceBorders,self.facePoints)
        TSM = goldenMath.calculateTSM(self.faceBorders,self.facePoints)
        LC = goldenMath.calculateLC(self.faceBorders,self.facePoints)

        avg = (TZM + TGSM + VFM + TSM + LC)  /5
        return 100- avg

    def face2Vec(self):
        goldenMath.unitSize =goldenMath.calculateUnit(self.facePoints)
        vector = goldenMath.face2Vec(self.faceBorders,self.facePoints)
        return vector

    def faceSimilarity(self,vector2):
        return goldenMath.vectorFaceSimilarity(self.face2Vec(),vector2)

    #Golden similarity
    def similarityRatio(self):
        facevec = self.face2Vec()
        filepath = pkg_resources.resource_filename(__name__, "goldenFace.json")
        goldenFace = functions.loadFaceVec(filepath)
        similarity = goldenMath.vectorFaceSimilarity(facevec,goldenFace)

        return similarity

    def getLandmarks(self):
        return self.landmarks

    def getFacialPoints(self):
        
        return self.facePoints

    def drawFacialPoints(self,color):
        self.img = goldenMath.drawFacialPoints(self.img,self.facePoints,color)

    def drawLandmarks(self,color):
        self.img = goldenMath.drawLandmarks(self.img,self.landmarks,color)


    def getFaceBorder(self):
        return self.faceBorders

    def writeImage(self,name):
        cv2.imwrite(name, self.img)

    def saveFaceVec(self,path):
        functions.saveFaceVec(self.face2Vec(),path)



