import cv2
import numpy as np
import pytesseract as tess
import re

#list of state codes for Indian Number Plates
stateCodes=['AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'DN',
            'DD', 'DL', 'GA', 'GJ', 'HR', 'HP', 'JK',
            'KA', 'KL', 'LD', 'MP', 'MH', 'MN', 'ML',
            'MZ', 'NL', 'OR', 'PY', 'PN', 'RJ', 'SK',
            'TN', 'TS' , 'TR', 'UP', 'WB']

def identify(imgPath):
    '''Accepts an image path and returns set of possible registration numbers '''

    #Load the image
    img = cv2.imread(imgPath)
    # cv2.imshow("Image",img)
    # cv2.waitKey(0)
    
    processed=preprocessAndGetSegmentMasks(img)
    
    #find contours
    contours,hiearchy= cv2.findContours(processed,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #mark the contours for visualisation
    cv2.drawContours(img, contours, -1, (0,255,0), 1)
    # cv2.imshow("Image",processed)    
    # cv2.waitKey(0)

    #initialise empty set of detections
    detections=set()

    #for each contour, try finding registration number
    for i,cnt in enumerate(contours):
        #get the rectangle enclosing the contour
        min_rect= cv2.minAreaRect(cnt)

        #proceed only if rectangle is a good candidate
        if checkForRect(min_rect) :
            #crop out only the part of image consisting of contour
            x,y,w,h = cv2.boundingRect(cnt)
            plate_img= img[y:y+h, x:x+w]

            #proceed only if cropped image is a good candidate
            if isMostlyWhite(plate_img):
                
                #get average intensity of cropped image and enumerate for following range
                avg=np.mean(plate_img)
                for level in range(5,15):

                    # perform thresholding (to get b/w) of cropped image as preprocessing before OCR
                    # The threshold level is varied over loop iterations because
                    # satisfactory results were not obtained from
                    # using any single level due to varying lighting conditions in images
                    _,plate_img_bw= cv2.threshold(plate_img,
                                               avg*(level/10),
                                               255,
                                               cv2.THRESH_BINARY )

                    # Perform OCR
                    text= tess.image_to_string(plate_img_bw ,config="--user-patterns licencePlate.patterns" )

                    #optimization to ignore empty and whitespace strings
                    if text.strip():
                        # match with RegEx to filter registration number from any noisy text
                        # Note that we have included 8 in alphabets and O,Z in digits to be able to
                        # ignore tesseract confusion between similar looking characters
                        if(matched:=re.search(r"([A-Z8]{2})\s*([0-9OZ]{2})(?:\s|-)*([A-Z8]{2})(?:\s|-)*([0-9OZ]{4})",text.strip())):
                            # The different parts of registration number are separated out
                            # and any confusion is removed by replacing confusable characters with probable ones
                            p1=matched.group(1)
                            p1=re.sub("[8]","B",p1)
                            p2=matched.group(2)
                            p2=re.sub("[oO]","0",p2)
                            p2=re.sub("[zZ]","2",p2)
                            p3=matched.group(3)
                            p3=re.sub("[8]","B",p3)
                            p4=matched.group(4)
                            p4=re.sub("[oO]","0",p4)
                            p4=re.sub("[zZ]","2",p4)

                            # Include only if state code matches given list
                            if(p1 in stateCodes):
                                detections.add(p1 + p2 + p3 + p4)

                
                # cv2.imshow("Image",plate_img)    
                # cv2.waitKey(0)
    
    #cv2.destroyAllWindows()

    return detections


def preprocessAndGetSegmentMasks(img):

    #blur image to remove noise
    img2= cv2.GaussianBlur(img,(3,3),0)
    # cv2.imshow("Image",img2)
    # cv2.waitKey(0)

    #convert to greyscale
    img2= cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    img2= cv2.GaussianBlur(img2,(7,7),0)
    # cv2.imshow("Image",img2)
    # cv2.waitKey(0)
    
    #determine edges
    imgX= cv2.Sobel(img2,-1,1,0,ksize=-1)
    imgY= cv2.Sobel(img2,-1,0,1,ksize=-1)
    edgeMap= cv2.addWeighted(imgX,1,imgY,0,0)
    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0) 
    
    #threshold to convert to b/w
    _,edgeMap= cv2.threshold(edgeMap, 0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0) 

    #perform closing operation
    edgeMap= cv2.morphologyEx(edgeMap,
                              cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(30,18)))

    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0) 

    #perform opening operation to separate out individual objects 
    edgeMap= cv2.morphologyEx(edgeMap,
                              cv2.MORPH_OPEN,
                              cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(16,16)))
    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0) 

    #perform dilation to smoothen out some rough edges
    edgeMap= cv2.morphologyEx(edgeMap,
                              cv2.MORPH_DILATE,
                              cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(24,24)))
    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0) 

    #perform erosion to crop it to content on plate
    edgeMap= cv2.morphologyEx(edgeMap,
                              cv2.MORPH_ERODE,
                              cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(5,10)))
    # cv2.imshow("Image",edgeMap)
    # cv2.waitKey(0)

    return edgeMap


def isMostlyWhite(img):
    '''Accepts an image and returns True if image is bright, False otherwise '''
    avg= np.mean(img)
    if avg>100:
        return True
    else:
        return False


def checkForRect(rect):
    '''Accepts a RotatedRectangle from cv2 and
    determine if the width:height ratio is good enough
    for it to be a possible number plate'''
    angle= rect[2]
    w,h= rect[1]

    ratio= w/h

    if ratio>1 and angle<15:
        ratio=1/ratio
    
    if ratio>0.8 or ratio<0.15 :
        return False
    else:
        return True

