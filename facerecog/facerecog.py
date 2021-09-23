import face_recognition
import cv2
from mysql.connector import catch23
import numpy as np
import mysql.connector
import time
import array as arr
import threading
import os

basedir = os.path.abspath(os.path.dirname(__file__))

mydb = mysql.connector.connect(
    host='sg-evision-43665.servers.mongodirector.com',
    user='sgroot',
    password='rFLxVXDTCp8P^5OJ',
    database='db1'
)

# who says comments are useless 

__1_image = face_recognition.load_image_file(os.path.join(basedir,"student_photos/1.jpg"))
__1_face_encoding = face_recognition.face_encodings(__1_image)[0]




# Create arrays of known face encodings and their names
known_face_encodings = [
__1_face_encoding,
]


known_face_names = [
"__1",
]

# Initialize 
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
att =set()

def p_record():
    mycursor = mydb.cursor()
    sql = "insert into total (np,dt) values (%s,%s)"
    val=("1",time.strftime("%Y/%m/%d"))
    mycursor.execute(sql,val)
    mydb.commit()
        #---------------------------------------------------------------

def att_upload(att,i):
        for e in att:
            if (e=="Unknown")or(e=="unknown"):
                continue
            e=e[2:]
            mycursor = mydb.cursor()
            sql = "INSERT INTO att (eno,pno,dt) VALUES (%s, %s,%s)"
            val=(e,i,time.strftime("%Y/%m/%d"))
            mycursor.execute(sql, val)
            mydb.commit()
            atdt=time.strftime("%Y/%m/%d")
            print(f"Eno:{e} attended pno:{i} on date:{atdt}")


#--------------------function to detact time interval-------------
def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]    

shour = arr.array('i',[0]*100)
smini = arr.array('i',[0]*100)
ehour = arr.array('i',[0]*100)
emini = arr.array('i',[0]*100)


# # --------------------for manual period timing input-------------------------
# periods=int(input("enter number of periods"))
# for j in range(1,periods+1):

#     x = input(f"Enter starting time in HH:MM for period {j}\n")
#     a,b = [int(i) for i in x. split(":")]
#     shour[j]=int(a)
#     smini[j]=int(b)
#     x = input(f"Enter ending time in HH:MM for period {j}\n")
#     a,b = [int(i) for i in x. split(":")]
#     ehour[j]=int(a)
#     emini[j]=int(b)

# -------------------for fethching period details from database-------------------------
mycursor = mydb.cursor()
sql = "SELECT np FROM noper"
mycursor.execute(sql)    
tmprr = mycursor.fetchone()
periods=tmprr[0]
#commented to save memeory
# print(f'periods={periods}')
t=time.localtime()

for j in range(1,periods+1):    
    z=str(j)
    mycursor = mydb.cursor()
    sql = "SELECT sh FROM timetable WHERE pno = %s"
    val=(z,)
    mycursor.execute(sql, val)    
    t0 = mycursor.fetchone()

    mycursor = mydb.cursor()
    sql = "SELECT sm FROM timetable WHERE pno = %s"
    val=(z,)
    mycursor.execute(sql, val)    
    t1 = mycursor.fetchone()
    
    mycursor = mydb.cursor()
    sql = "SELECT eh FROM timetable WHERE pno = %s"
    val=(z,)
    mycursor.execute(sql, val)    
    t2 = mycursor.fetchone()
    
    mycursor = mydb.cursor()
    sql = "SELECT em FROM timetable WHERE pno = %s"
    val=(z,)
    mycursor.execute(sql, val)    
    t3 = mycursor.fetchone()
    
    mydb.commit()
    
    shour[j]=t0[0]
    smini[j]=t1[0]
    ehour[j]=t2[0]
    emini[j]=t3[0]


## -----------------------for printing all period details------------------------- 
# for j in range(1,periods+1):
#     print(f'starting hr for p{j} is {shour[j]}')
#     print(f'starting min for p{j} is {smini[j]}')
#     print(f'ending hr for p{j} is {ehour[j]}')
#     print(f'ending min for p{j} is {emini[j]}')

#---------------------------main timing & task loop----------------------------------
while(True):
    m=time.localtime()
    for i in range(1,periods+1):
        if(emini[i])==0:
            emini[i]=60
        m=time.localtime()
        if is_between(str(m.tm_hour)+":"+str(m.tm_min),(str(shour[i])+":"+str(smini[i]),str(ehour[i])+":"+str(emini[i]-1))):
            video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            # video_capture = cv2.VideoCapture("http://192.168.31.55:4747/video")
            att.clear()
            while(1):
                m=time.localtime()
                # print(f"im period {i} running......")

                ret, frame = video_capture.read()

                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Only process every other frame of video to save time
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # If a match was found in known_face_encodings, just use the first one.
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        if known_face_names:
                            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame


                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    att.add(name)


                # Display the resulting image
                cv2.imshow('Video', frame)
                                
                # Hit 'q' on the keyboard to quit!
                if(cv2.waitKey(1) & 0xFF == ord('q')):
                    break
                
                if(m.tm_hour==ehour[i] and m.tm_min==emini[i]):
                    #commented to save memeory
                    # print("Period Ended")

                    video_capture.release()
                    cv2.destroyAllWindows()

                    # print(att)
                    
                    #---------updating total num of recorded periods------------
                    th1=threading.Thread(target=p_record())
                    if(len(att)!= 0):
                        th2=threading.Thread(target=att_upload(att,i))
                    break 
                    # exit(0)
                        

                
                    
        else:
            # print('no period')
            os.system("python updater.py")
            exit(0)