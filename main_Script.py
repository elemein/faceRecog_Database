import face_recognition
import cv2
import numpy as np
import sqlite3

# Connect to profiles.db; or create it if it doesnt exist.
connection = sqlite3.connect("profiles.db")
cursor = connection.cursor()

# Check if the profiles table exists. If not, create it.
try:
    cursor.execute("SELECT 1 FROM profiles LIMIT 1;")
    result = cursor.fetchone()

except sqlite3.OperationalError:
    cursor.execute(f"""CREATE TABLE profiles (
                        PersonID int,
                        Name varchar(255),
                        filePath varchar(255)
                        );""")
    connection.commit()
# ---

# Fill the table with database info.
cursor.execute("SELECT * FROM profiles;")
profile_table = cursor.fetchall()
known_encoding_names = []
known_encodings = []

# For each profile, add a face encoding.
for profile in profile_table:
    image = face_recognition.load_image_file(f"""{profile[2]}""")
    face_encoding = face_recognition.face_encodings(image)[0]

    known_encoding_names.append(profile[1])
    known_encodings.append(face_encoding)

# Initialize capture cam.
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a single frame of video and show it
    ret, raw_frame = video_capture.read()
    cv2.imshow('Video', raw_frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        break

    # If you press space.
    if k%256 == 32:

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        frame = raw_frame[:, :, ::-1]

        # Find face encoding
        try:
            face_encoding = face_recognition.face_encodings(frame)[0]
        except IndexError:
            print("No face found.")

        for enc in known_encoding_names:
            matches = face_recognition.compare_faces(known_encodings, face_encoding)

        if True in matches:
            first_match_index = matches.index(True)
            name = known_encoding_names[first_match_index]
            print(f'this is {name}')
        else:
            print('Unknown user.')

    a = not True

video_capture.release()
cv2.destroyAllWindows()