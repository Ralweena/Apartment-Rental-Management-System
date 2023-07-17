#import libraries
from flask import Flask, redirect, render_template, flash, request, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import uuid
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
# app.secret_key = 'your secret key'
app.secret_key = "apartment_rental"

#code for connection
app.config['MYSQL_HOST'] = 'localhost' #hostname
app.config['MYSQL_USER'] = 'root' #username
app.config['MYSQL_PASSWORD'] = '' #password
#in my case password is null so i am keeping empty
app.config['MYSQL_DB'] = 'apartmentRental' #database name
# Intialize MySQL
mysql = MySQL(app)
           
@app.route('/')
def home() :
    return render_template('welcome.html')
    
    
@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin() :
    error = None
    if request.method == 'POST' and 'adminUsername' in request.form and 'adminPass' in request.form and 'securityPass' in request.form:
        if request.form['adminUsername'] != 'admin' or \
                request.form['adminPass'] != 'secret@123' or \
                request.form['securityPass'] != 'apartment':
            error = 'Invalid credentials'
        else:
            flash('You have logged in successfully!!')
            return redirect(url_for('AdminDashboard'))
    return render_template('AdminLogin.html', error=error)


@app.route('/AdminLogout')
def AdminLogout() :
    log2 = ''
    log2 = 'You have logged out successfully!!'
    return render_template('AdminLogin.html', log2=log2)


@app.route('/TenantLogin', methods=['GET', 'POST'])
def TenantLogin() :
    error = None
    if request.method == 'POST' and 'username' in request.form and 'pswd1' in request.form :
        username = request.form['username']
        password = request.form['pswd1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s AND PSWD = % s', (username, password, ))
        account = cursor.fetchone()
        # If account exists in TENANT table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['T_ID']
            session['username'] = account['EMAIL']
            # Redirect to home page
            flash('You have logged in successfully!!')
            return redirect(url_for('TenantDashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            error = ' Invalid Username or Password !!'
    return render_template('TenantLogin.html', error=error)


@app.route('/Logout')
def Logout() :
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    log = ''
    log = 'You have logged out successfully!!'
    return render_template('TenantLogin.html', log=log)


@app.route('/Register', methods=['GET','POST'])
def Register():
    msg1 = ''
    log = ''
    #applying empty validation
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'phNo' in request.form and 'dob' in request.form and 'occupation' in request.form and 'gender' in request.form and 'email' in request.form and 'pswd' in request.form:
        #passing HTML form data into python variable
        fname = request.form['firstname']
        lname = request.form['lastname']
        ph = request.form['phNo']
        dob = request.form['dob']
        gender = request.form['gender']
        occupation = request.form['occupation']
        email = request.form['email']
        pswd = request.form['pswd']
        if len(ph) != 10 :
            msg1 = 'Phone No. must be of 10 digits!!'
            return render_template('TenantRegister.html', msg1=msg1)
        #creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s', (email,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg1 = 'Email already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO TENANT VALUES (% s, % s, NULL , % s, % s, % s , % s , % s , NULL, % s)', (fname, lname, ph, email, gender ,dob, occupation,pswd))
            mysql.connection.commit()
            #displaying message
            log = 'You have successfully registered !'
            return render_template('TenantLogin.html', log=log)          
    elif request.method == 'POST':
        msg1 = 'Please fill out the form !'
    return render_template('TenantRegister.html', msg1=msg1)


@app.route('/TenantRegister')
def tregister() :
    return render_template('TenantRegister.html')


#----------- ADMIN DASHBOARD----------------


@app.route('/AdminDashboard')
def AdminDashboard() :
    occ_apts=''
    unocc_apts=''
    t_tenants=''
    t_users=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
    cursor.execute('SELECT COUNT(T_ID) AS T_USERS FROM TENANT')
    mysql.connection.commit()
    result1=cursor.fetchone()
    t_users = result1['T_USERS'] 
    cursor.execute('SELECT COUNT(T_ID) AS T_TENANTS FROM TENANT WHERE ROOM_NO IS NOT NULL')
    mysql.connection.commit()
    result2=cursor.fetchone()
    t_tenants = result2['T_TENANTS'] 
    cursor.execute('SELECT COUNT(ROOM_NO) AS T_APTS FROM APARTMENT WHERE APT_STATUS = "Occupied"')
    mysql.connection.commit()
    result3=cursor.fetchone()
    occ_apts = result3['T_APTS'] 
    cursor.execute('SELECT COUNT(ROOM_NO) AS T_APTS FROM APARTMENT WHERE APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    result4=cursor.fetchone()
    unocc_apts = result4['T_APTS']  
    tot_apt = unocc_apts + occ_apts  
    cursor.execute('SELECT COUNT(BLOCK_NO) AS T_BLOCK FROM APARTMENT_BLOCK')
    mysql.connection.commit()
    result5=cursor.fetchone()
    tot_blck = result5['T_BLOCK']
    cursor.execute('SELECT SUM(R.RENT_FEE) AS T_RENT FROM RENT AS R, RENT_STATUS AS S WHERE R.RENT_ID = S.RENT_ID AND S.R_STATUS = "Paid"')
    mysql.connection.commit()
    result6=cursor.fetchone()
    tot_rent = result6['T_RENT'] 
    if tot_rent == None :
        tot_rent = 0
    return render_template('AdminDashboard.html', occ_apts=occ_apts, unocc_apts=unocc_apts, t_tenants=t_tenants, t_users=t_users, tot_apt=tot_apt, tot_blck=tot_blck, tot_rent=tot_rent)

@app.route('/TotalUsers')
def TotalUsers() :
    msg5=''   
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT')
    mysql.connection.commit()
    msg5=cursor.fetchall()
    return render_template('TotalUsers.html', msg5=msg5)


@app.route('/tenantReport', methods=['GET','POST'])
def tenantReport() :
    tenantReport=''
    msg6=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'tid' in request.form :
        #passing HTML form data into python variable
        T_ID = request.form['tid']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM TENANT WHERE T_ID = % s', (T_ID,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('DELETE FROM TENANT WHERE T_ID = % s',(T_ID,))
            mysql.connection.commit()
        else:
            msg6 = 'Tenant doesn\'t exists !'
    elif request.method == 'POST':
        msg6 = 'Please fill out the details !'
    cursor.execute('SELECT T_ID, FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT WHERE ROOM_NO IS NOT NULL')
    mysql.connection.commit()
    tenantReport=cursor.fetchall()
    return render_template('tenantReport.html', msg6=msg6,tenantReport=tenantReport)


@app.route('/ApartmentRooms', methods=['POST','GET'])
def ApartmentRooms() :
    msg2=''
    msg3=''
    aptTitle = ''
    description = ''
    area = ''
    Rent=0
    Room = 0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room' in request.form and 'block' in request.form and 'status' in request.form and 'rentPerMonth' in request.form:
        #passing HTML form data into python variable
        Room = request.form['room']
        Block = request.form['block']
        Status = request.form['status']
        Rent = request.form['rentPerMonth']
        aptTitle = request.form['apartmentTitle'] 
        description = request.form.get('desc')
        area = request.form['area']
        file1 = request.files['hall']
        file2 = request.files['kitchen']
        file3 = request.files['bedroom']
        file4 = request.files['extra']
        path = 'static/images/apartment'+Room
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        file1.save(os.path.join('static/images/apartment'+Room, secure_filename(file1.filename)))
        file2.save(os.path.join('static/images/apartment'+Room, secure_filename(file2.filename)))
        file3.save(os.path.join('static/images/apartment'+Room, secure_filename(file3.filename)))
        file4.save(os.path.join('static/images/apartment'+Room, secure_filename(file4.filename)))
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg2 = 'Apartment already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO APARTMENT VALUES (% s, % s, % s, % s)', (Room, Block, Rent, Status))
            mysql.connection.commit()
            cursor.execute('INSERT INTO APARTMENT_DETAILS VALUES (% s, % s, % s, % s)', (Room, aptTitle, area, description))
            mysql.connection.commit()
            Image_url = 'images/apartment'+Room
            cursor.execute('INSERT INTO APARTMENT_PHOTOS VALUES (% s, % s, %s, %s, %s, %s)', (Room, Image_url, file1.filename, file2.filename, file3.filename, file4.filename))
            mysql.connection.commit()
            #displaying message
            msg2 = 'You have successfully added an Apartment !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html',msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/UpdateApartment', methods=['GET','POST'])
def UpdateApartment():
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room1' in request.form and 'status1' in request.form and 'rentPerMonth1' in request.form :
        #passing HTML form data into python variable
        Room1 = request.form['room1']
        Status1 = request.form['status1']
        Rent1 = request.form['rentPerMonth1']
        area1 = request.form['up_area']
        title1 = request.form['up_title']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room1,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('UPDATE APARTMENT SET RENT_PER_MONTH = % s, APT_STATUS = % s WHERE ROOM_NO = % s',(Rent1,Status1,Room1))
            mysql.connection.commit()
            cursor.execute('UPDATE APARTMENT_DETAILS SET AREA = % s, APT_TITLE = % s WHERE ROOM_NO = % s',(area1,title1,Room1))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/DeleteApartment', methods=['GET','POST'])
def DeleteApartment() :
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room2' in request.form :
        #passing HTML form data into python variable
        Room2 = request.form['room2']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room2,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('SELECT PATHNAME FROM APARTMENT_PHOTOS WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
            path = cursor.fetchone()
            pathname = 'static/'+path['PATHNAME']
            shutil.rmtree(pathname, ignore_errors=False, onerror=None)
            cursor.execute('DELETE FROM APARTMENT WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/RentStatus')
def RentStatus() :
    rent_status=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT FNAME, LNAME, T.ROOM_NO, RENT_PER_MONTH, DUE_DATE, R_STATUS, LATE_FEE FROM RENT AS R, APARTMENT AS A, RENT_STATUS AS RS, TENANT AS T WHERE R.RENT_ID = RS.RENT_ID AND T.T_ID = R.T_ID AND A.ROOM_NO = T.ROOM_NO')
    mysql.connection.commit()
    rent_status=cursor.fetchall()
    # cursor.execute('CALL RENTUPDATE()')
    # mysql.connection.commit()
    return render_template('RentStatus.html',rent_status=rent_status)

@app.route('/UpdatedRentStatus')
def UpdatedRentStatus() :
    rent_status=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('CALL RENTUPDATE()')
    mysql.connection.commit()
    cursor.execute('SELECT FNAME, LNAME, T.ROOM_NO, RENT_PER_MONTH, DUE_DATE, R_STATUS, LATE_FEE FROM RENT AS R, APARTMENT AS A, RENT_STATUS AS RS, TENANT AS T WHERE R.RENT_ID = RS.RENT_ID AND T.T_ID = R.T_ID AND A.ROOM_NO = T.ROOM_NO')
    mysql.connection.commit()
    rent_status=cursor.fetchall()
    return render_template('RentStatus.html',rent_status=rent_status)

@app.route('/Backup')
def Backup() :
    backup_status=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT T_ID, FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT_BACKUP ')
    mysql.connection.commit()
    backup_status=cursor.fetchall()
    # cursor.execute('CALL RENTUPDATE()')
    # mysql.connection.commit()
    return render_template('backup.html',backup_status=backup_status)


#---------------------------------------------- TENANT DASHBOARD---------------------------------------------


@app.route('/TenantDashboard')
def TenantDashboard() :
    if 'loggedin' in session:
        return render_template('TenantDashboard.html')
    return render_template('TenantLogin.html')

@app.route('/RentApartment')
def rentApartment() :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    apartment=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('RentApartment.html',apartment=apartment, img_url=img_url)

@app.route('/Details', methods=['GET','POST'])
def Details() :
    Error=''
    Uname=''
    Tname=''
    PAddress=''
    aptNo=''
    TFatherName=''
    Date = date.today()
    rentAmt= 0
    Deposit= 0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'Username' in request.form and 'aptNo' in request.form and 'TFatherName' in request.form and 'PerAddr' in request.form :
        Uname = request.form['Username']
        aptNo = request.form['aptNo']
        TFatherName = request.form['TFatherName']
        PAddress = request.form['PerAddr']
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('SELECT RENT_PER_MONTH FROM APARTMENT WHERE ROOM_NO = %s AND APT_STATUS = "Unoccupied"',(aptNo,))
        mysql.connection.commit()
        res1 = cursor.fetchone()
        if t_id != None and res1 != None :
            cursor.execute('SELECT FNAME,LNAME FROM TENANT WHERE T_ID = %s',(t_id,))
            mysql.connection.commit()
            res = cursor.fetchone()
            Tname = res['FNAME']+' '+res['LNAME']
            rentAmt=res1['RENT_PER_MONTH']
            Deposit = rentAmt * 2
            return redirect(url_for('Contract', aptNo=aptNo ,Tname=Tname, TFatherName=TFatherName, PAddress=PAddress, Date=Date, rentAmt=rentAmt, Deposit=Deposit))
        else :
            Error = 'Invalid Username or Apartment No.!!'
    elif request.method == 'POST' :
        Error= 'Please fill out the form!'
    return render_template('Details.html', Error=Error)



@app.route('/alreadyTenant', methods=['GET','POST'])
def alreadyTenant() :
    Error=''
    Uname=''
    Tname=''
    aptNo=''
    rentAmt= 0
    PhNo=''
    late_fee=0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'Username' in request.form and 'aptNo' in request.form :
        Uname = request.form['Username']
        aptNo = request.form['aptNo']
        cursor.execute('SELECT T_ID, PH_NO FROM TENANT WHERE EMAIL = % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        PhNo = tid_list1['PH_NO']
        cursor.execute('SELECT LATE_FEE FROM RENT WHERE T_ID = % s',(t_id,))
        mysql.connection.commit()
        latefee_list = cursor.fetchone()
        late_fee = latefee_list['LATE_FEE']
        totAmt = int(rentAmt) + int(late_fee)
        # PhNo='9876543212'
        cursor.execute('SELECT RENT_PER_MONTH FROM APARTMENT WHERE ROOM_NO = %s AND APT_STATUS = "Occupied"',(aptNo,))
        mysql.connection.commit()
        res1 = cursor.fetchone()
        if t_id != None and res1 != None :
            cursor.execute('SELECT FNAME,LNAME FROM TENANT WHERE T_ID = %s',(t_id,))
            mysql.connection.commit()
            res = cursor.fetchone()
            Tname = res['FNAME']+' '+res['LNAME']
            rentAmt=res1['RENT_PER_MONTH']
            late_fee = late_fee
            totAmt = int(rentAmt) + int(late_fee)
            return redirect(url_for('Payment1', aptNo=aptNo ,Tname=Tname, Uname=Uname,PhNo=PhNo , rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt))
        else :
            Error = 'Invalid Username or Apartment No.!!'
    elif request.method == 'POST' :
        Error= 'Please fill out the form!'
    return render_template('alreadyTenant.html', Error=Error)


@app.route('/Contract/<aptNo>/<Tname>/<TFatherName>/<Uname>/<PAddress>/<Date>/<rentAmt>/<Deposit>', methods=['GET','POST'])
def Contract(aptNo,Tname, TFatherName, Uname, PAddress, Date, rentAmt, Deposit) :
    msg7=''
    late_fee=0
    totAmt=0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'UserName' in request.form and 'aptno' in request.form and 'rent-amt' in request.form and 'deposit' in request.form and 'start_date' in request.form and 'end_date' in request.form and 'pay_date' in request.form and 'terms' in request.form:
        #passing HTML form data into python variable
        end_date = request.form['end_date']
        # pay_date = request.form['pay_date']
        terms = request.form['terms']
        Username = request.form['UserName']
        Apt_no = request.form['aptno']
        start_date = request.form['start_date']
        Deposit = request.form['deposit']
        rentAmt = request.form['rent-amt']
        #creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #query to check given data is present in database or no
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Username,))
        mysql.connection.commit()
        tid_list2 = cursor.fetchone()
        T_id = tid_list2['T_ID']
        resDate = datetime.strptime(start_date, '%Y-%m-%d')
        due_date = resDate + relativedelta(months=+2)
        totAmt = int(rentAmt) + int(late_fee)
        #executing query to insert new data into MySQL
        cursor.execute('INSERT INTO CONTRACT VALUES ( NULL , % s, % s, % s , % s , % s , % s)', (T_id, Apt_no, start_date, end_date, Deposit ,terms))
        cursor.execute('INSERT INTO RENT VALUES ( NULL , % s, % s, % s , % s , NULL)', (rentAmt, T_id,due_date, late_fee))
        mysql.connection.commit()
        cursor.execute('SELECT RENT_ID FROM RENT WHERE T_ID = % s',(T_id,))
        mysql.connection.commit()
        rent_id_list = cursor.fetchone()
        rent_id = rent_id_list['RENT_ID']
        cursor.execute('INSERT INTO RENT_STATUS VALUES ( % s, % s)', (rent_id,'Unpaid'))
        cursor.execute('UPDATE TENANT SET ROOM_NO = % s WHERE T_ID = % s',(Apt_no,T_id))
        cursor.execute('UPDATE APARTMENT SET APT_STATUS = "Occupied" WHERE ROOM_NO = % s',(Apt_no,))
        mysql.connection.commit()
        cursor.execute('SELECT PH_NO FROM TENANT WHERE T_ID = % s',(T_id,))
        mysql.connection.commit()
        phone_no = cursor.fetchone()
        PhNo = phone_no['PH_NO']
        #displaying message
        flash('Hope you love Rooftop Apartments... ')
        return redirect(url_for('Payment', aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt))
    elif request.method == 'POST' :
        msg7 = 'Please fill out the form !'
    return render_template('contract.html', msg7=msg7, aptNo=aptNo , Date=Date, Tname=Tname, TFatherName=TFatherName, Uname=Uname, PAddress=PAddress, Date1=Date, rentAmt=rentAmt, Deposit=Deposit)


@app.route('/Payment/<aptNo>/<Tname>/<PhNo>/<Uname>/<rentAmt>/<late_fee>/<totAmt>', methods=['GET','POST'])
def Payment(aptNo,Tname,PhNo, Uname, rentAmt, late_fee, totAmt) :
    err=''
    Date = date.today()
    id = uuid.uuid1()
    fields = id.fields
    pay_id = fields[0]
    pay_date = date.today()
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'email' in request.form and 'roomNo' in request.form and 'acc-no' in request.form and 'cardNo' in request.form and 'cvv' in request.form :
        Uname = request.form['email']
        aptNo = request.form['roomNo']
        Acc_No = request.form['acc-no']
        card_No = request.form['cardNo']
        cvv = request.form['cvv']
        if len(card_No) != 11 and len(cvv) != 3:
            err = 'Invalid Card No or cvv!!'
            return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('SELECT RENT_ID FROM RENT WHERE T_ID= % s',(t_id,))
        mysql.connection.commit()
        rentid_list = cursor.fetchone()
        rent_id = rentid_list['RENT_ID']
        if t_id != None and aptNo != None :
            cursor.execute('INSERT INTO PAYMENT VALUES(% s, % s, % s, % s, % s)',(pay_id,Acc_No,t_id,Date,rentAmt))
            cursor.execute('UPDATE RENT SET PAYMENT_ID = % s WHERE RENT_ID = % s',(pay_id, rent_id))
            cursor.execute('UPDATE RENT_STATUS SET R_STATUS = "Paid" WHERE RENT_ID = % s',(rent_id,))
            mysql.connection.commit()
            pay_amt = rentAmt
            return redirect(url_for('Receipt',Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt))
    elif request.method == 'POST' :
        err= 'Please fill out the form!'
    return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)


@app.route('/Payment1/<aptNo>/<Tname>/<PhNo>/<Uname>/<rentAmt>/<late_fee>/<totAmt>', methods=['GET','POST'])
def Payment1(aptNo,Tname,PhNo, Uname, rentAmt, late_fee, totAmt) :
    err='Payment Unsuccessfull'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'email' in request.form and 'roomNo' in request.form and 'acc-no' in request.form :
        Uname = request.form['email']
        aptNo = request.form['roomNo']
        pay_date = request.form['pay_date']
        Acc_No = request.form['acc-no']
        id = uuid.uuid1()
        fields = id.fields
        pay_id = fields[0]
        Date = date.today()
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('SELECT RENT_ID FROM RENT WHERE T_ID= % s',(t_id,))
        mysql.connection.commit()
        rentid_list = cursor.fetchone()
        rent_id = rentid_list['RENT_ID']
        if t_id != None and aptNo != None :
            cursor.execute('INSERT INTO PAYMENT VALUES(% s, % s, % s, % s, % s)',(pay_id,Acc_No,t_id,Date,rentAmt))
            cursor.execute('UPDATE RENT SET PAYMENT_ID = % s WHERE RENT_ID = % s',(pay_id, rent_id))
            cursor.execute('UPDATE RENT_STATUS SET R_STATUS = "Paid" WHERE RENT_ID = % s',(rent_id,))
            mysql.connection.commit()
            pay_amt = rentAmt
            return redirect(url_for('Receipt',Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt))
    return render_template('Payment.html', err=err,aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)

 
 
@app.route('/Receipt/<Tname>/<pay_id>/<pay_date>/<pay_amt>', methods=['GET','POST'])
def Receipt(Tname,pay_id,pay_date,pay_amt) :
    return render_template('Reciept.html', Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt)


if __name__ == '__main__':
    app.run(port=5000,debug=True)
