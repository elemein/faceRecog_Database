import face_recognition
import cv2
import numpy as np
import sqlite3
import time
import tkinter

# Connect to profiles.db; or create it if it doesnt exist.
connection = sqlite3.connect("profiles.db")
cursor = connection.cursor()

# Check if the profiles table exists. If not, create it.
try:
    cursor.execute("SELECT 1 FROM profiles LIMIT 1;")
    result = cursor.fetchone()

except sqlite3.OperationalError:
    cursor.execute(f"""CREATE TABLE profiles (
                        Name varchar(255),
                        filePath varchar(255)
                        );""")
    connection.commit()

# Fill the table with database info.
cursor.execute("SELECT * FROM profiles;")
profile_table = cursor.fetchall()
known_encoding_names = []
known_encodings = []

# For each profile, add a face encoding.
for profile in profile_table:
    image = face_recognition.load_image_file(f"""{profile[1]}""")
    face_encoding = face_recognition.face_encodings(image)[0]

    known_encoding_names.append(profile[0])
    known_encodings.append(face_encoding)

# Initialize capture cam.
video_capture = cv2.VideoCapture(0)
display_string = ''
start = time.time()
addFace = False
input_name = 'a'
start = time.time() - 6

master = tkinter.Tk()

def getEntry(en):
    global input_name
    input_name = entry.get()

    master.destroy()

label = tkinter.Label(master, text="What is your name?")
label.grid(row=0, sticky=tkinter.W)

entry = tkinter.Entry(master)
entry.grid(row=0, column=1)

entry.bind('<Return>', getEntry)

while True:
    # Grab a single frame of video and show it
    ret, raw_frame = video_capture.read()

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        break

    # If you press space.
    if k%256 == 32:
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        frame = raw_frame[:, :, ::-1]

        if (time.time()) < (start + 5):
            if addFace == True:
                master.mainloop()

                filename = 'a'.join(input_name.split())

                cursor.execute(f"""INSERT INTO profiles VALUES ('{input_name}', '{filename}.png' );""")
                connection.commit()

                unknown = cv2.imread('unknownFace.png')
                cv2.imwrite(f'{filename}.png', unknown)

                cursor.execute("SELECT * FROM profiles;")
                profile_table = cursor.fetchall()

                for profile in profile_table:
                    image = face_recognition.load_image_file(f"""{profile[1]}""")
                    face_encoding = face_recognition.face_encodings(image)[0]

                    known_encoding_names.append(profile[0])
                    known_encodings.append(face_encoding)

        else:
            addFace = False

        # Find face encoding
        try:
            face_encodings = face_recognition.face_encodings(frame)

            if len(face_encodings) > 1:
                display_string = 'One face at a time please.'
                start = time.time()

            else:
                for known_name in known_encoding_names:
                    matches = face_recognition.compare_faces(known_encodings, face_encodings[0])

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_encoding_names[first_match_index]
                    display_string = f'Hello {name}!'
                    start = time.time()
                else:
                    display_string = 'Unknown Face. Press [SPACE] again to add.'
                    start = time.time()

                    cv2.imwrite('unknownFace.png', frame)
                    addFace = True

        except IndexError:
            display_string = 'No faces found.'
            start = time.time()

    if (time.time()) < (start + 5):
        raw_frame = cv2.putText(raw_frame, display_string, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
    else:
        raw_frame = cv2.putText(raw_frame, 'Press [SPACE] to recognize faces.', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        raw_frame = cv2.putText(raw_frame, '[ESC] to quit.', (50, 100),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
    cv2.imshow('Video', raw_frame)

video_capture.release()
cv2.destroyAllWindows()