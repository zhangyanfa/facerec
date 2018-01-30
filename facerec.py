# -*- coding: utf-8 -*-
import socket
import face_recognition
import cv2
import os


face_list = list()

face_images = list()
face_encoding_list = list()

idx = 0
def encodingImages(filepath):
    pathDir =  os.listdir(filepath)
    for allDir in pathDir:
        print allDir
        fileName = allDir[0:allDir.index(".")]
        face_list.append(fileName)
        image = face_recognition.load_image_file("./face_images/" + allDir)
        encoding = face_recognition.face_encodings(image)[0]
        #face_images.append( image )
        face_encoding_list.append( encoding )
        #child = os.path.join('%s%s' % (filepath, allDir))
        #print child.decode('gbk') # .decode('gbk')是解决中文显示乱码问题


encodingImages("./face_images")

print face_list

video_capture = cv2.VideoCapture(0)

while True :
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)

        match = face_recognition.compare_faces(face_encoding_list, face_encoding, 0.4)
        print match

        name = "Unknown"
        for idx, m in enumerate(match):
            if(m):
                print idx, "===", m
                name = face_list[idx]

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()