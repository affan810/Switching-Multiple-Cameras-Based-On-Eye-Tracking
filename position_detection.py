#This program is used for detection of the position of the iris

#import modules
import cv2
import mediapipe as mp
import numpy as np
import math

cap=cv2.VideoCapture(0)

#function to find the distance between two points
def euclidean_distance(x1,x2,y1,y2):
    distance=math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return distance

#function which uses mediapipe module to detect position
def main(frame1):
    frame_cnt=0
    LEFT_IRIS=[474,475,476,477]              
    RIGHT_IRIS=[469,470,471,472]
    LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
    RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]  

    mp_face_mesh = mp.solutions.face_mesh                   #creating face mesh using the mediapipe library
    pos=""
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True ,min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
            frame_cnt+=1
            frame = cv2.resize(frame1, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            frame_height, frame_width= frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            rgb_frame.flags.writeable = False
            results  = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                mesh_points=np.array([np.multiply([p.x,p.y],[frame_width,frame_height]).astype(int) for p in results.multi_face_landmarks[0].landmark])
                #getting coordinates of the iris
                x1=int(((mesh_points[LEFT_IRIS[1]][0])+(mesh_points[LEFT_IRIS[3]][0]))/2)
                y1=mesh_points[386][1]
                #getting coordinates of the corners of the eye
                xleft,yleft=mesh_points[362][0],mesh_points[362][1]
                xright, yright = mesh_points[263][0],mesh_points[263][1]
                center_to_right=euclidean_distance(x1,xright, y1, yright)
                left_to_right=euclidean_distance(xleft,xright, yleft, yright)
                ratio=center_to_right / left_to_right
                #getting coordinated of the top and bottom of the eye
                xtop,ytop=mesh_points[443][0],mesh_points[443][1]
                xbottom,ybottom =mesh_points[253][0] , mesh_points[253][1]
                center_to_top =euclidean_distance(x1,xtop,y1,ytop)
                top_to_bottom = euclidean_distance(xtop, xbottom, ytop, ybottom)
                ratio1 = center_to_top / top_to_bottom
                #comaparing ratios to detect the position accurately
                if ratio<=0.5 and ratio1<=0.5:
                    pos="left_top"
                elif ratio<=0.5 and ratio1>0.5:
                    pos="left bottom"
                elif ratio>0.5 and ratio1<=0.55:
                    pos="right_top"
                elif ratio>0.5 and ratio1>0.55:
                    pos="right_bottom"
                else:
                    pos="EYE CLOSED"
                print(pos)
            
            key = cv2.waitKey(2)
            if key==ord('q') or key ==ord('Q'):
                pass
            cv2.destroyAllWindows()
    if pos:
        return pos
    else:
        return None
        
if __name__=='__main__':
    while True:
        ret_val, frame = cap.read()
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.BORDER_DEFAULT)
        main(frame)
        if cv2.waitKey(1) == 27:
            break # esc to quit
    cv2.destroyAllWindows()
