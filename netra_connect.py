#There are two function which are called together using multiprocessing (no latency)
#1. to detect the position of the iris
#2. to send the respective frames to a third party application

#importing modules
import numpy as np
import cv2
import pyvirtualcam
import position_detection as pd
import multiprocessing as mp
import gc

pos=[]
camera=1  #setting the default camera for streaming
cap=[]
#declaring all cameras 
cap.append(cv2.VideoCapture(0))
cap[0].set(3,140)        #reducing the camera resolution to overcome USB bandwidth distribution
cap[0].set(4,100)
cap.append(cv2.VideoCapture(1))
cap[1].set(3,140)
cap[1].set(4,100)
cap.append(cv2.VideoCapture(3))
cap[2].set(3,140)
cap[2].set(4,100)
cap.append(cv2.VideoCapture(4))
cap[3].set(3,140)
cap[3].set(4,100)
cap.append(cv2.VideoCapture(5))
cap[4].set(3,140)
cap[4].set(4,100)

#function to send frames to third party applications
def send_cam(camera1,i):       
        global cap
        global camera
        global pos
        old_cam=camera1
        fmt = pyvirtualcam.PixelFormat.BGR      #declaring pyvirtualcam instance to send frames
        cam= pyvirtualcam.Camera(width=160, height=120, fps=20,fmt=fmt)
        while old_cam==camera:                  #the loop will continue until the camera is switched
            positions=[]
            file = open("file.txt","r")
            data = file.read().splitlines()         #data read from the file.txt, which is being continuously updated with the iris positions 
            positions=(data[-3:]).copy()
            ret, frame1=cap[camera].read()
            frame1 = cv2.resize(frame1, (160,120), interpolation=cv2.BORDER_DEFAULT)
            #cv2.imshow('my webcam', frame1)
            cam.send(frame1)                         #sending frames using the send() function
            cam.sleep_until_next_frame()
            if positions:
                        if len(positions)>=3:                   #last 3 postions are checked and the equivalent camera is updated
                            if positions[-1]=="left_top" and positions[-2]=="left_top" and positions[-3]=="left_top":
                                camera=1
                            elif positions[-1]=="left bottom" and positions[-2]=="left bottom" and positions[-3]=="left bottom":
                                camera=2
                            elif positions[-1]=="right_top" and positions[-2]=="right_top" and positions[-3]=="right_top":
                                camera=3
                            elif positions[-1]=="right_bottom" and positions[-2]=="right_bottom" and positions[-3]=="right_bottom":
                                camera=4
                            else:
                                pass
                        elif len(positions)==2 or len(positions)==1:
                            if positions[-1]=="left_top":
                                camera=1
                            elif positions[-1]=="left bottom":
                                camera=2
                            elif positions[-1]=="right_top":
                                camera=3
                            elif positions[-1]=="right_bottom":
                                camera=4
                        else:
                            print("no frames")
                            exit()
            else:
                    continue
            print("changed camera is: ",camera)
            if cv2.waitKey(1) == 27:
                    return None  # esc to quit
        else:                                 #once the camera is switched, this part gets executed
            cam.close()                       #the camera is closed as well as all its instances are deleted
            del cam
            collected=gc.collect(generation=2)
            del collected
            print("cam changed")
            send_cam(camera,i)                #recursively calling the same function by sending the new camera value


#function to detect position of the iris
def pos_detection():
    global pos    
    global camera
    while True:                              #looping to continuously detect iris position
        f = open("file.txt","a")             #opening and appending the positions to the file
        ret_val, frame = cap[0].read()
        pos.append(pd.main(frame)) 
        print(pos[-1])
        f.write(f"{pd.main(frame)}\n")       #calling the position detection module
        f.close()
        print("----------------------")
        
        if cv2.waitKey(1) == 27:
                        break  # esc to quit


#main funtion to perform multiprocessing
def main():
    p1=mp.Process(target=pos_detection)
    p2=mp.Process(target=send_cam, args=(camera,3, ))
    p1.start()
    p2.start()

if __name__=='__main__':               
    main()