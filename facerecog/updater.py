import mysql.connector
import shutil
import os

basedir = os.path.abspath(os.path.dirname(__file__))

while True:

    mydb = mysql.connector.connect(
    host='sg-evision-43665.servers.mongodirector.com',
    user='sgroot',
    password='rFLxVXDTCp8P^5OJ',
    database='db1'
    )
    
    # checking removal buffer
    mycursor = mydb.cursor(buffered=True)
    sql = "SELECT (eno) FROM rbuff"
    mycursor.execute(sql)
    r_enroll = mycursor.fetchone()
    mycursor.close()

    if r_enroll ==None:
        #commented to save memeory
        # print("All entries are removed")
        
        # Starting adder buffer

        while True:

            # checking buff table
            mycursor = mydb.cursor(buffered=True)
            sql = "SELECT * FROM buff"
            mycursor.execute(sql)
            enroll_name_img = mycursor.fetchone()
            mycursor.close


            if enroll_name_img ==None:
                #commented to save memeory
                # print("All entries are updated")
                # print("calling facerecog function")
                os.system('python facerecog.py')
                exit(0)

            enroll=enroll_name_img[0]
            name=enroll_name_img[1]
            img=enroll_name_img[2]
            pswd=enroll_name_img[3]
            enroll_str=str(enroll)


            # Checking main table
            # print(enroll)
            mycursor = mydb.cursor()
            sql = "SELECT sname FROM maintable WHERE eno=%s"
            mycursor.execute(sql,(enroll,))
            name_tuple = mycursor.fetchone()
            mydb.commit()
            if name_tuple!=None:
                # enrollment already exist so deleting from buff
                mycursor = mydb.cursor()
                sql_delete = "DELETE FROM buff WHERE eno = %s"
                mycursor.execute(sql_delete,(enroll,))
                mydb.commit()
                #commented to save memeory
                # print("Already exists.....")
                continue

            # Making changes in main file 
            temp = open('temp.txt', 'w')
            with open("facerecog.py", "r") as f:
                for a in f:
                    if a.startswith("known_face_names = [\n"):
                        a = a + "\"__" + enroll_str + "\",\n"
                    temp.write(a)
            temp.close()
            shutil.move('temp.txt', 'facerecog.py')

            temp = open('temp.txt', 'w')
            with open("facerecog.py", "r") as f:
                for a in f:
                    if a.startswith("known_face_encodings = ["):
                        a = a + "__" + enroll_str +"_face_encoding,\n"
                    temp.write(a)
            temp.close()
            shutil.move('temp.txt', 'facerecog.py')

            temp = open('temp.txt', 'w')
            with open("facerecog.py", "r") as f:
                for a in f:
                    if a.startswith("# who says comments are useless"):
                        a=a+"\n"+"__"+enroll_str+"_image = face_recognition.load_image_file(os.path.join(basedir,\""+"student_photos/"+enroll_str+".jpg\"))\n"+"__"+enroll_str+"_face_encoding = face_recognition.face_encodings(__"+enroll_str+"_image)[0]\n"
                    temp.write(a)
            temp.close()
            shutil.move('temp.txt', 'facerecog.py')

            # Enter data into main table
            mycursor = mydb.cursor()
            sql = "INSERT INTO maintable (eno,sname,pswd) VALUES (%s, %s, %s)"
            mycursor.execute(sql, (enroll,name,pswd))
            mydb.commit()
            mycursor.close()
            

            # Saving image file
            img_file = os.path.join(basedir, "student_photos")+"/"+enroll_str+".jpg"  
            with open(img_file, 'wb') as fh:
                fh.write(img)
    
            # Remove Data from buff table     
            mydeletecursor = mydb.cursor(buffered=True)
            sql_delete = "DELETE FROM buff WHERE eno = %s"
            mydeletecursor.execute(sql_delete,(enroll_str,))
            mydb.commit()
            mydeletecursor.close





    r_enroll=str(r_enroll[0])

    #Removing from main file 
    temp = open('temp.txt', 'w')
    with open("facerecog.py", "r") as f:
        for a in f:
            if a.find("__"+r_enroll)==-1:
                temp.write(a)
    temp.close()
    shutil.move('temp.txt', 'facerecog.py')

    # Removing photo from folder
    
    if os.path.isfile(os.path.join(basedir, "student_photos")+"/"+r_enroll+".jpg"):
        os.remove(os.path.join(basedir, "student_photos")+"/"+r_enroll+".jpg")
    
  

    # Checking main table
    cursormain = mydb.cursor()
    sql = "SELECT sname FROM maintable WHERE eno=%s"
    cursormain.execute(sql,(r_enroll,))
    name_tuple = cursormain.fetchone()
    mydb.commit()
    cursormain.close()
    if name_tuple!=None:      
        mycursor = mydb.cursor()
        sql_delete = "DELETE FROM maintable WHERE eno = %s"
        mycursor.execute(sql_delete,(r_enroll,))
        mydb.commit()
        mycursor.close()
        #commented to save memeory
        # print(f"removed {r_enroll} from maintable")  
    
    # Deleting from rbuff table
    mycursor = mydb.cursor()
    sql_delete = "DELETE FROM rbuff WHERE eno = %s"
    mycursor.execute(sql_delete,(r_enroll,))
    mydb.commit()
    mycursor.close()
    #commented to save memeory
    # print(f"removed {r_enroll} from rbuff")  
