from django.shortcuts import render
from .models import User
from django.core.files.storage import FileSystemStorage
import re
import cv2
import pytesseract
from django.conf import settings
from django.http import JsonResponse
import numpy as np
import os
def index(request):
    return render(request,'index.html')

def apires(request):
    return JsonResponse({
       "message" : 122344
    })


framewidth = 720
frameheight = 720

def getContours(img,imgCountour,th):
    contours,hierachy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
   
    rotateit = False
    warp = imgCountour.copy()
    for cnt in contours:
        area = cv2.contourArea(cnt)
        #print(area)
        if area > th:
          #  print(area)
            cv2.drawContours(imgCountour,cnt,-1,(255,0,255),7)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
           # print(len(approx))
            x,y,w,h = cv2.boundingRect(approx)
            cv2.rectangle(imgCountour,(x,y),(x+w,y+h),(0,255,0),5)
            if x == None :
              x=0
              y=0
              w= imgContour.shape[0]
              h= imgContour.shape[1]


           # print(str(x)+" "+str(y)+" "+str(w)+" "+str(x))

            rect1 = np.float32([[x,y],[x+w,y],[x,y+h],[x+w,y+h]])
            rect2 = np.float32([[0,0],[w,0],[0,h],[w,h]])


            M = cv2.getPerspectiveTransform(rect1, rect2)
            warp = cv2.warpPerspective(imgCountour, M, (w, h))

            if w<h:
             # print("rotate")
              rotateit = True
        else :
          
          print("not en")

    return rotateit, warp


def preprocess(img):
    h,w,_ = img.shape
    if w>h :
        img = cv2.resize(img,(int(frameheight*(w/h)),frameheight))
     #   print(str(w)+" "+str(h))
    else:
       # print(str(w)+" r"+str(h))
        img = cv2.resize(img,(framewidth,int(framewidth*(h/w))))
    imageContour = img.copy()
    imgBlur = cv2.GaussianBlur(img,(7,7),1)
    imgGray = cv2.cvtColor(imgBlur,cv2.COLOR_BGR2GRAY)

    cannyImg = cv2.Canny(imgGray,72,164)

    kernal = np.ones((5,5))
    
    imgDil = cv2.dilate(cannyImg,kernal,iterations=6)
    imgDil = cv2.erode(imgDil,kernal,iterations=5)


    rot,warped= getContours(imgDil,imageContour,109317)

    if rot :
        warped = cv2.rotate(warped,cv2.ROTATE_90_COUNTERCLOCKWISE)

    return warped


def uploadImage(request):
    context = {}
    pno = 0
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    

    pi = request.FILES['image']
    fs = FileSystemStorage()
    print("request handling...")
    file_name = fs.save(pi.name,pi)
    print(file_name)
    img=cv2.imread(settings.MEDIA_ROOT+'\\'+pi.name)
    img = preprocess(img)

    #print(pytesseract.image_to_boxes(img))
    himg , wimg, _ = img.shape

    boxes = pytesseract.image_to_data(img)

    print(boxes)
    for x,b in enumerate(boxes.splitlines()) :
        if x!=0:
            b = b.split()
            if len(b)==12:
                if isValidPanCardNo(b[11]):
                    print(b[11])  
                    pno = b[11]              
    #            x,y,w,h = int (b[6]),int (b[7]),int (b[8]),int (b[9])
    #            cv2.rectangle(img,(x,y),(w+x,y+h),(0,0,255),3)
    #            cv2.putText(img,b[11],(x,y),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,255),2)
    print(img.shape)
    print(pi.name)
    print(pi.size)
    #return render(request,'index.html')
    context['pan'] = pno
    #context['imag'] = file_name
    os.remove(settings.MEDIA_ROOT+'\\'+pi.name)

    return render(request,'index.html', context)
    
#    return JsonResponse({
#       "pan number" : pno
#    })

# Create your views here.




def isValidPanCardNo(panCardNo):

    regex = "[A-Z]{5}[0-9]{4}[A-Z]{1}"

    p = re.compile(regex)

    if(panCardNo == None):
        return False
    if(re.search(p, panCardNo) and
       len(panCardNo) == 10):
        return True
    else:
        return False