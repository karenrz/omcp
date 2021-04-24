import datetime
from flask import Flask, render_template,url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import jsonify
from flask import abort
from sqlalchemy import not_



app = Flask(__name__)
#change based on your machine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:SimonSimon@localhost:3306/clinic'
db = SQLAlchemy(app)

#chosen credentials for admin
adminUsername = "admin123"
adminPassword = "12345"

#table definition for patients
class patients(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    sex = db.Column(db.String(8))
    DoB = db.Column(db.DateTime)
    medication = db.Column(db.String(30))
    attachments = db.Column(db.String(30))
    email = db.Column(db.String(30))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(60))
    username = db.Column(db.String(60))
    password = db.Column(db.String(60))

    def __init__(self, fname, lname, sex, DoB, medication, attachments,
                 email, phone, address,username,password):
        super(patients, self).__init__(fname=fname, lname=lname, sex=sex,
                                       DoB=DoB, medication=medication, attachments=attachments,
                                       email=email, phone=phone, address=address,username=username,password=password)


#table definition for doctors
class doctors(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    specialization = db.Column(db.String(30))
    rate = db.Column(db.Integer)
    email = db.Column(db.String(30))
    phoneExt = db.Column(db.Integer)
    address = db.Column(db.String(60))
    username = db.Column(db.String(60))
    password = db.Column(db.String(60))

    def __init__(self, fname, lname, specialization, rate,
                 email, phoneExt, address, username,password):
        super(doctors, self).__init__(fname=fname, lname=lname, specialization=specialization,
                                      rate=rate, email=email, phoneExt=phoneExt, address=address,
                                      username=username,password=password)
        
    def serialize(self):
        return {
                    "id": self.id,
                    "fname": self.fname,
                    "lname": self.lname,
                    "specialization": self.specialization
                }


#table definition for appointments
class appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_doctorID = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    fk_patientID = db.Column(db.Integer, db.ForeignKey('patients.id'))
    paymentID = db.Column(db.Integer)
    startDate = db.Column(db.DateTime)
    creationDate = db.Column(db.DateTime)

    def __init__(self, fk_doctorID, fk_patientID, paymentID, startDate, creationDate):
        super(appointments, self).__init__(fk_doctorID=fk_doctorID, fk_patientID=fk_patientID,
                                           paymentID=paymentID, startDate=startDate,
                                           creationDate=creationDate)

    def serialize(self):
        return {
            'id': self.id,
            'Doctor': self.fk_doctorID,
            'Patient': self.fk_patientID,
            'Start Date': self.startDate
        }


#table definition for changed appointments to be used later for reports
class changedApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_doctorID = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    fk_patientID = db.Column(db.Integer, db.ForeignKey('patients.id'))
    paymentID = db.Column(db.Integer)
    startDate = db.Column(db.DateTime)
    creationDate = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

    def __init__(self, fk_doctorID, fk_patientID, paymentID, startDate, creationDate, status):
        super(changedApp, self).__init__(fk_doctorID=fk_doctorID, fk_patientID=fk_patientID,
                                         paymentID=paymentID, startDate=startDate,
                                         creationDate=creationDate, status=status)

    def serialize(self):
        status = "added" if self.status == 1 else "deleted"
        return {
            'id': self.id,
            'Doctor': self.fk_doctorID,
            'Patient': self.fk_patientID,
            'Start Date': self.startDate,
            'Status': status
        }



#route for admin adding appointments given their information
@app.route('/appointments', methods=['POST'])
def addAppointment():
    fk_doctorID = request.json['doctor']
    fk_patientID = request.json['patient']
    paymentID = request.json['paymentID']
    date = request.json['startDate']
    creationDate = datetime.datetime.now()
    
    date2 = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M")
    
    if(date2.minute!= 30 and date2.minute != 0):
       abort(400)
            
        
    query = appointments.query.filter_by(startDate=date).first()
    if(query):
       abort(400)
    

    ap = appointments(fk_doctorID=fk_doctorID,
                      fk_patientID=fk_patientID,
                      paymentID=paymentID,
                      startDate=date,
                      creationDate=creationDate)

    addedApp = changedApp(fk_doctorID=fk_doctorID,
                          fk_patientID=fk_patientID,
                          paymentID=paymentID,
                          startDate=date,
                          creationDate=creationDate,
                          status=1)

    db.session.add(ap)
    db.session.add(addedApp)
    db.session.commit()

    output = "Appoinment was added!"
    return jsonify(output)

#route for admin adding doctors given their information
@app.route('/doctors', methods=['POST'])
def addDoctor():
    fname = request.json['fname']
    lname = request.json['lname']
    specialization = request.json['specialization']
    rate = request.json['rate']
    email = request.json['email']
    phoneExt = request.json['phoneExt']
    address = request.json['address']
    username=request.json['username']
    password = request.json['password']

    dr = doctors(fname=fname,
                 lname=lname,
                 specialization=specialization,
                 rate=rate,
                 email=email,
                 phoneExt=phoneExt,
                 address=address,
                 username=username,
                 password=password
                 )

    db.session.add(dr)
    db.session.commit()

    output = "Doctor {} {} was added!".format(fname, lname)
    return jsonify(output)

#route for admin adding patients given their information
@app.route('/patients', methods=['POST'])
def addPatient():
    fname = request.json['fname']
    lname = request.json['lname']
    sex = request.json['sex']
    DoB = request.json['DoB']
    medication = request.json['medication']
    attachments = request.json['attachments']
    email = request.json['email']
    phone = request.json['phone']
    address = request.json['address']
    username=request.json['username']
    password = request.json['password']

    pat = patients(
        fname=fname,
        lname=lname,
        sex=sex,
        DoB=DoB,
        medication=medication,
        attachments=attachments,
        email=email,
        phone=phone,
        address=address,
        username=username,
        password=password
    )

    db.session.add(pat)
    db.session.commit()

    output = "Patient {} {} was added".format(fname, lname)
    return jsonify(output)


@app.route('/patients/<int:id>', methods=['DELETE'])
def deletePatient(id):
    patient = patients.query.filter_by(id=id).first()
    if patient:
        db.session.delete(patient)
        db.session.commit()
    else:
        abort(404)

    output = "Deleted patient with id {}".format(id)
    return jsonify(output)


@app.route('/doctors/<int:id>', methods=['DELETE'])
def deleteDoctor(id):
    doctor = doctors.query.filter_by(id=id).first()
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
    else:
        abort(404)

    output = "Deleted doctor with id {}".format(id)
    return jsonify(output)


@app.route('/appointments/<int:id>', methods=['DELETE'])
def deleteAppointment(id):
    appointment = appointments.query.filter_by(id=id).first()

    deletedApp = changedApp(fk_doctorID=appointment.fk_doctorID,
                            fk_patientID=appointment.fk_patientID,
                            paymentID=appointment.paymentID,
                            startDate=appointment.startDate,
                            creationDate=datetime.datetime.now(),
                            status=0)

    if appointment and deletedApp:
        db.session.delete(appointment)
        db.session.add(deletedApp)
        db.session.commit()
    else:
        abort(404)

    output = "Deleted appointment with id {}".format(id)
    return jsonify(output)

#updates report for the last 7 days
@app.route('/updateReport', methods=["POST"])
def updateChanges():
    START_DATE = datetime.datetime.now() - datetime.timedelta(days=7)
    END_DATE = datetime.datetime.now()
    changedApp.query.filter(not_(changedApp.startDate.between(START_DATE, END_DATE))).delete(synchronize_session='fetch')
    db.session.commit()
    output = "DATABASE UPDATED!"
    return jsonify(output)


#return reports objects as an array of queries
@app.route('/showReport', methods=["GET"])
def showReport():
    try:
        changed = changedApp.query.all()
        return jsonify([e.serialize() for e in changed])
    except Exception as e:
        return (str(e))

#change appointment based on a new date
@app.route('/updateAppointment', methods=['POST'])
def updateAppointment():
    id = request.json['id']
    start = request.json['startDate']
    match1 = appointments.query.filter_by(id=id).first()
    match2 = changedApp.query.filter_by(id=id).first()
    if match1:
        match1.startDate = start
        match2.startDate = start
        db.session.commit()
        output = "UPDATED!"
        return jsonify(output)
    else:
        abort(404)

#show all appointments of a patient
@app.route('/showPatientAppointment', methods=['GET'])
def showPatientAppointment():
    id = request.json['id']
    match = appointments.query.filter_by(fk_patientID=id).all()
    if match:
        return jsonify([e.serialize() for e in match])
    else:
        abort(404)
      
#show all appointments of a patient of a doctor
@app.route('/showDoctorAppointment', methods=['GET'])
def showDoctorAppointment():
    id = request.json['id']
    match = appointments.query.filter_by(fk_doctorID=id).all()
    if match:
        return jsonify([e.serialize() for e in match])
    else:
        abort(404)


@app.route('/Admin', methods=['GET','POST'])
def checkAdmin():
    username = request.form['username']
    password = request.form['password']
    if username != 'adminUsername' and password != 'adminPassword':
        return render_template('Admin.html')
    else:
        return render_template('Admin-Portal.html')
        
    


@app.route('/checkPatient', methods=['GET'])
def checkPatient():
    username = request.form['username']
    password = request.form['password']
    match = patients.query.filter_by(username=username, password = password).first()
    if request.form[match]:
        return jsonify(True)
        return render_template ("Client-Portal.html")
    else:
        return jsonify(False)
        return render_template("Sign-In.html")

@app.route('/checkDoctor', methods=['GET'])
def checkDoctor():
    username = request.json['username']
    password = request.json['password']
    match = doctors.query.filter_by(username=username, password = password).first()
    if match:
        return jsonify(True)
    else:
        return jsonify(False)
    
    
@app.route('/allDoctors', methods=["GET"])
def allDocs():
    try:
        dr = doctors.query.all()
        return jsonify([e.serialize() for e in dr])
    except Exception as e:
        return (str(e))
    
    
#returns times of appointments for a specific doctor on a specific day
@app.route("/specificAppointment", methods=["GET"])
def appt():
    doctor = request.json["drID"]
    time = request.json["time"]
    date = datetime.datetime.strptime(time,"%Y-%m-%d")
    counter = date
    counter = counter.replace(hour = 8, minute = 0)
    results = []
    while(counter.hour < 16):
        match = appointments.query.filter_by(fk_doctorID=doctor, startDate = counter).first()
        if not match:
            results.append(counter.strftime('%H:%M'))
        timeDelta = datetime.timedelta(minutes = 30)
        counter += timeDelta
    return jsonify(results)
           

        

if __name__ == '__main__':
    app.run()