import cv2
import face_recognition
import pickle
from mysqlClass import MySQLClass

found = False
exit_video_loop = False
counter = 0
video_name = "en.mp4"
video_capture = cv2.VideoCapture(video_name)
fps = int(video_capture.get(cv2.CAP_PROP_FPS) / 2) + 1
print(fps)

myGenDB = MySQLClass.getInstance()


while True:
    ret, frame = video_capture.read()

    if counter % fps == 0:
        print(counter)
        all_faces = myGenDB.select_query("SELECT face_id, face_vector "
                                         "FROM Face", (), "dummy")
        # Grab a single frame of video

        # Get the current position in milliseconds
        current_time_ms = video_capture.get(cv2.CAP_PROP_POS_MSEC)

        # Convert milliseconds to minutes and seconds
        minutes = int(current_time_ms // 60000)  # 1 minute = 60000 milliseconds
        seconds = int((current_time_ms % 60000) // 1000)  # remainder divided by 1000 milliseconds

        # Format time as MM:SS
        time_formatted = f"{minutes:02d}:{seconds:02d}"

        print(f"Current Time: {time_formatted}")

        # Break from the loop if no frame is found
        if not ret:
            break

        # Convert the image from BGR color (which OpenCV uses) to RGB color
        rgb_frame = frame[:, :, ::-1]
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(bgr_frame)
        face_encodings = face_recognition.face_encodings(bgr_frame, face_locations)

        i = 0

        for face_encoding in face_encodings:

            match_found = False

            for face_id, face_vector in all_faces:
                face_vector = pickle.loads(face_vector)
                if face_recognition.compare_faces([face_vector], face_encoding, tolerance=0.8)[0]:
                    match_found = True
                    break

            if not match_found:

                face_encoding_blob = pickle.dumps(face_encoding)
                myGenDB.update_query(f"""INSERT INTO Face (face_vector) VALUES (%s)""", (face_encoding_blob,), "dummy")
                last_insert_id = myGenDB.select_query("SELECT MAX(face_id) FROM Face", (), "dummy")[0][0]
                myGenDB.update_query(f"INSERT INTO Face_Occurrence (face_id, video_name, video_time) "
                                     f"VALUES (%s, %s, %s)", (last_insert_id, video_name, time_formatted), "dummy")

                # Unpack the positions (top, right, bottom, left)
                top, right, bottom, left = face_locations[i]

                # You can access the actual face itself like this:
                face_image = rgb_frame[top:bottom, left:right]

                # Convert the face from RGB back to BGR color to save with OpenCV
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)

                # Save the image or you can display it if you want
                cv2.imwrite(f"photos/face_{last_insert_id}.jpg", face_image_bgr)
            else:
                myGenDB.update_query(f"INSERT INTO Face_Occurrence (face_id, video_name, video_time) "
                                     f"VALUES (%s, %s, %s)", (face_id, video_name, time_formatted), "dummy")

            i += 1

    counter += 1
# Release the video capture
video_capture.release()
