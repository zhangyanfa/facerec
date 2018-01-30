# -*- coding: utf-8 -*-

import socket
import numpy as np
import random, time
import struct
import face_recognition
import os, sys, cv2


# socket info
TCP_IP = '' # no specialized ip means using whatever ip.
TCP_PORT = 5001

face_list = list()

face_images = list()
face_encoding_list = list()


def encodingImages(filepath):
    pathDir =  os.listdir(filepath)
    for allDir in pathDir:
        print(allDir)
        fileName = allDir[0:allDir.index(".")]
        face_list.append(fileName)
        image = face_recognition.load_image_file("/root/face_recognition/face_images/" + allDir)
        encoding = face_recognition.face_encodings(image)[0]
        #face_images.append( image )
        face_encoding_list.append( encoding )


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


## main ##

if __name__ == '__main__':

    st = time.time()
    encodingImages("./face_images")

    print(face_list)
    et = time.time()

    print (et-st)
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    print("Listening on port ",TCP_PORT," ...")

    while True:
        try:
            conn, addr = s.accept()
            #conn.settimeout(5)
            #print "connected by: ",addr

            while True:
                length = recvall(conn,16)
                if not length:
                    print("No connection")
                    break

                stringData = recvall(conn, int(length))
                if not stringData:
                    print("No data received")
                    break

                data = np.fromstring(stringData, dtype='uint8')
                decimg=cv2.imdecode(data,1)
               
                #decimg = decimg[:, :, (2, 1, 0)]
                face_frame = decimg

                # Find all the faces and face enqcodings in the frame of video
                face_locations = face_recognition.face_locations(face_frame)
                face_encodings = face_recognition.face_encodings(face_frame, face_locations)

                x1,y1,x2,y2 = 0,0,0,0
                # Loop through each face in this frame of video
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # See if the face is a match for the known face(s)

                    match = face_recognition.compare_faces(face_encoding_list, face_encoding, 0.4)
                    print(match)

                    name = 'Unknow'
                    for idx, m in enumerate(match):
                        if(m):
                            #print(idx, "===", m)
                            name = face_list[idx]
                            break
                    print(left, top, right, bottom)
                    print("this is= : ",name)

                    if name != 'Unknow' :
                        x1 = int(left)
                        y1 = int(top)
                        x2 = int(right)
                        y2 = int(bottom)
                        

                        class_name = name

                        struct_str1 = struct.pack('!iiii%ds' % len(class_name),x1,y1,x2,y2,class_name.encode('utf-8'))
                        conn.send(str(len(struct_str1)).ljust(16).encode('utf-8'))
                        conn.send(struct_str1)
                    

                struct_str2 = struct.pack('!iiii%ds' % len('end'),x1,y1,x2,y2,'end'.encode('utf-8'))
                conn.send(str(len(struct_str2)).ljust(16).encode('utf-8'))
                conn.send(struct_str2)
                cv2.waitKey(1)

        except Exception as e:
            print(e)
            print('Disconnect with: ',addr)
            continue

    s.close()