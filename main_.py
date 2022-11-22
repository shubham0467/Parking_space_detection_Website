from flask import Flask, render_template, Response, request, json, jsonify
import cv2
import pickle
import cvzone
import numpy as np
from flask_mysqldb import MySQL
import json
from datetime import datetime

# Parking Space

app = Flask(__name__)
cap = cv2.VideoCapture("carPark.mp4")
# cap=cv2.VideoCapture(0)


def generate_frames():
    while True:

        # read the camera frame
        success, img = cap.read()

        if not success:
            break
        else:
            with open('CarParkPos', 'rb') as f:
                posList = pickle.load(f)
            width, height = 107, 48

            def checkParkingSpace(imgPro):
                spaceCounter = 0

                for pos in posList:
                    x, y = pos

                    imgCrop = imgPro[y:y + height, x:x + width]
                    # cv2.imshow(str(x * y), imgCrop)
                    count = cv2.countNonZero(imgCrop)

                    if count < 900:
                        color = (0, 255, 0)
                        thickness = 5
                        spaceCounter += 1
                    else:
                        color = (0, 0, 255)
                        thickness = 2

                    cv2.rectangle(img, pos, (pos[0] + width,
                                             pos[1] + height), color, thickness)
                    # cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                    #                 thickness=2, offset=0, colorR=color)

                cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                                   thickness=5, offset=20, colorR=(0, 200, 0))
            while True:

                if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, img = cap.read()
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
                imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                     cv2.THRESH_BINARY_INV, 25, 16)
                imgMedian = cv2.medianBlur(imgThreshold, 5)
                kernel = np.ones((3, 3), np.uint8)
                imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

                checkParkingSpace(imgDilate)
                ret, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Database


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pragya'
app.config['MYSQL_DB'] = 'parkingGarage'


mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        name_ = request.form['name']
        email_id = request.form['email']
        vehicle_number = request.form['vehicle-number']
        vehicle_type = request.form['vehicle-type']
        # if vehicle_type=="two":
        #     types="2"
        # elif vehicle_type=="four":
        #     types="4"
        # else:
        #     types="0"
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"""INSERT INTO registration VALUES ('{name_}', '{email_id}', '{vehicle_number}', '{vehicle_type}', now());""")
        mysql.connection.commit()
        cursor.close()

    return render_template("index.html")


@app.route('/helpDesk')
def helpDesk():
    return render_template('helpDesk.html')


@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')


@app.route('/parking')
def parking():
    return render_template('parking.html')


@app.route('/parking/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# read file
# with open('list.json', 'r') as myfile:
#     data = myfile.read()

# print(data)
# @app.route('/publicAmenities',methods=["GET"])
# def query():
#     # if request.method == "GET":
#     #     data_=data
#     #     # getting input with name = fname in HTML form
#     #     first_name = request.form.get("fname")
#     #     # getting input with name = lname in HTML form
#     #     last_name = request.form.get("lname")
#     #     return "Your name is "+first_name + last_name
#     return render_template("publicAmenities.html", jsonfile=json.dumps(data))
    # return jsonify(data_)

@app.route('/publicAmenities')
def publicAmentites():
    return render_template('PublicAmenitiesFirst.html')
# def data():

# def get_login():
#     mycursor = mysql.connection.cursor()

#     mycursor.execute("SELECT current_ FROM registration ORDER BY current_ DESC LIMIT 1")

#     myresult = mycursor.fetchall()

#     timestamps = []
#     for r in myresult:
#         timestamps.append(r[0].strftime('%D %H:%M:%S'))
#     # print(timestamps)
#     timestamps_=timestamps[0]


@app.route('/publicFees')
def get_time():
    # if request.method == 'POST':
    mycursor = mysql.connection.cursor()
    mycursor.execute(
        "SELECT current_ FROM registration ORDER BY current_ DESC LIMIT 1")
    myresult = mycursor.fetchall()
    timestamps = []
    for r in myresult:
        timestamps.append(r[0])
    # print(timestamps)
    timestamps_ = timestamps[0]
    # print(timestamps)
    # print("--------")
    # print(timestamps_)
    currenttime = datetime.now()
    duration = currenttime-timestamps_
    d_secs = duration.total_seconds()
    d_hrs = d_secs//(60*60)
    if d_hrs <= 1:
        fees = """You've parked for less than or equal to an hour"""
        fee = "Rs. 10"
    elif d_hrs > 1:
        fee = f"""Rs. {10+((d_hrs-1)*5)}"""
        fees = f"You've parked for {d_hrs} hours"
    feeshtml = f'''
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

    <title>Parking Fees</title>
    </head>
    <body class="bg-dark" style="margin-top: 20vh;">
    <div class="card text-center text-dark bg-light" >
        <div class="card-header">
        Parking Ticket
        </div>
        <div class="card-body">
        <h2 class="card-title">{ fees }</h2>
        <h1 class="card-title">To Pay : { fee }</h1>
        <div class="container border-top border-bottom mt-4 mb-2 py-2">
            <h5 class="card-text text-muted">Summary</h5>
            <p class="card-text">Login Time : { timestamps_ }</p>
            <p class="card-text">Current Time : { currenttime }</p>
            <p class="card-text">Duration : { d_hrs } hours</p>
        </div>
        </div>
        <div class="card-footer text-muted">
        Thanks for using Parking Garage!
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
    </body>
</html>

'''
    with open("templates/fees.html", "w") as f:
        f.write(feeshtml)

    return render_template("fees.html")


if __name__ == "__main__":
    app.run(debug=True)
