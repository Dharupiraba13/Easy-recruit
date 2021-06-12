from flask import Flask, url_for , request, redirect , session, g
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date,timedelta
from sqlalchemy.orm import backref
import sqlite3

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recsys.db'
app.secret_key = 'dhaneesh'

db = SQLAlchemy(app)

class User_acc(db.Model):
    __tablename__ = 'user_acc'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Address = db.Column(db.String(30))
    Skills = db.Column(db.String(100))
    Dob=db.Column(db.String(30))
    Age = db.Column(db.Integer)
    Status=db.Column(db.Integer)
    Sslc=db.Column(db.Float)
    Hlc=db.Column(db.Float)
    College = db.Column(db.String(200))
    Department = db.Column(db.String(30))
    CGPA = db.Column(db.Float)
    Resume = db.Column(db.LargeBinary)
    Experience = db.Column(db.Integer)
    status=db.Column(db.Integer)
    account = db.relationship("User", backref=backref("account", uselist=False))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    Email_id = db.Column(db.String(200),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    acc_id=db.Column(db.Integer,db.ForeignKey( 'user_acc.id'))


class Questions(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer,primary_key=True)
    Desc = db.Column(db.String(500),nullable=False)
    Op1 = db.Column(db.String(100))
    Op2 = db.Column(db.String(100))
    Op3 = db.Column(db.String(100))
    Op4 = db.Column(db.String(100))
    Ans=db.Column(db.String(100))

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Address = db.Column(db.String(30))
    Emp_name = db.Column(db.String(50),nullable=False)
    des= db.Column(db.String(500),nullable=False)
    Jobs = db.relationship('Job', backref='company', lazy=True)

class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer,primary_key=True)
    job_role = db.Column(db.String(50),nullable=False)
    job_des = db.Column(db.String(50),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_date = db.Column(db.Integer)
    skills_required = db.Column(db.String(100),nullable=False)
    experience = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)
    status= db.Column(db.Integer)

applied = db.Table('applied',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('applied_time', db.DateTime, default=datetime.utcnow),
    db.Column('assesment_date', db.String(30)),
    db.Column('assesment_time', db.String(30)),
    db.Column('assesment_score', db.Integer),
    db.Column('status', db.Integer)
)    


def connect_db():
    return sqlite3.connect('recsys.db')




@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']


def test_job():
    d = connect_db()
    query="SELECT * from job "
    cur = d.execute(query)
    job = [dict( id=row[0],Role=row[1],des=row[2].strip(),date=row[3],l_date=row[4],skills=row[5],exp=row[6],sal=row[7],cid=row[8]) for row in cur.fetchall()]
    today=date.today()
    for i in job:
        y1, m1, d1 = [int(x) for x in i['l_date'].split('-')]
        criteria=date(y1, m1, d1)   
        if today > criteria:
            query="UPDATE job SET status = '1' WHERE (id = '"+str(i['id'])+"')"
            print(query)
            cur=d.execute(query)
            d.commit()
    d.close()

global j_id


@app.route('/')
def home_page():
    test_job()
    return render_template('homepage.html')

@app.route('/login',methods=['POST', 'GET'])
def login():
    test_job()
    if request.method == 'POST':
        email = request.form.get('mail')
        pwd = request.form.get('pwd')
        if(email=='root' and pwd=='root'):
            return redirect('/admin')
        selectapplicant = User.query.filter_by(Email_id=email).first()
        selectcompany = Company.query.filter_by(Email_id=email).first()
        if selectapplicant and selectapplicant.Password == pwd:
            db = connect_db()
            query="select id,Email_id from user where Email_id='"+email+"' "
            cur = db.execute(query)
            ques = [dict( id=row[0],mail=row[1]) for row in cur.fetchall()]
            db.close()
            session['username']=ques[0]['id']
            return redirect('/student')
        elif selectcompany and selectcompany.Password == pwd:
            db = connect_db()
            query="select id,Email_id from company where Email_id='"+email+"' "
            cur = db.execute(query)
            ques = [dict( id=row[0],mail=row[1]) for row in cur.fetchall()]
            db.close()
            session['username']=ques[0]['id']
            return redirect('/company')
        else:
            message = "User with Given Credentials not found"
            return render_template('login.html',message=message)
    else:
        return render_template('login.html',message=None)

@app.route('/register-student',methods=['POST', 'GET'])
def registerstudent():
    if request.method == 'POST':
        cname = request.form['cname']
        password= request.form['password']
        email= request.form['email']
        tel= request.form.get('tel')
        address= request.form['address']
        dob= request.form['dob']
        age= request.form['age']
        sslc= request.form['sslc']
        hlc= request.form['hlc']
        college= request.form['college']
        dname= request.form['dname']
        cgpa= request.form['cgpa']
        files = request.files['resume']
        exp= request.form['exp']
        list1=request.form.getlist('l1')
        skills=""
        for i in list1:
            if(i!=None):
                skills=skills+" "+i
        query =User.query.filter_by(Email_id=email).first()
        if(query!=None):
            message = "Email-id already available"
            return render_template('register-student.html',message=message)
        data = User_acc(Name=cname,Password=password,Email_id=email,Contact=tel,Skills=skills,Address=address,Dob=dob,Age=age,Sslc=sslc,Hlc=hlc,College=college,Department=dname,CGPA=cgpa,Resume=files.read(),Experience=exp)
        data1=User(Email_id=email,Password=password,account=data)
        try:
            db.session.add(data)
            db.session.add(data1)
            db.session.commit() 
            return render_template('login.html')
        except:
            return "error adding values to database"
    else:
        return render_template('register-student.html')


@app.route('/register-company',methods=['POST', 'GET'])
def registercompany():
    if request.method == 'POST':
        cname = request.form['cname']
        ename= request.form['ename']
        designation= request.form['designation']
        address= request.form.get('address')
        password= request.form['password']
        email= request.form['email']
        message=None
        query =Company.query.filter_by(Email_id=email).first()
        if(query!=None):
            message = "Email-id already available"
            return render_template('register-company.html',message=message)
        data = Company(Name=cname,Password=password,Email_id=email,Address=address,Emp_name=ename,des=designation)      
        try:
            db.session.add(data)
            db.session.commit() 
            return render_template('login.html')
        except:
            return "error adding values to database"
    else:
        return render_template('register-company.html',message=None)

@app.route('/student',methods=['POST', 'GET'])
def student():
    test_job()
    return render_template('student.html')

@app.route('/student/view_job',methods=['POST', 'GET'])
@app.route('/view_job',methods=['POST', 'GET'])
def view_job():
    d = connect_db()
    query="SELECT * from job WHERE id NOT IN (SELECT job_id from applied where user_id='"+str(g.user)+"') AND status is NULL"
    cur = d.execute(query)
    job = [dict( id=row[0],Role=row[1],des=row[2].strip(),date=row[3],l_date=row[4],skills=row[5],exp=row[6],sal=row[7],cid=row[8],button=1) for row in cur.fetchall()]
    query="select id,Name,Email_id from company"
    cur = d.execute(query)
    company = [dict( id=row[0],Name=row[1],Email=row[2]) for row in cur.fetchall()]
    d.close()
    for i in job:
        for j in company:
            if(i['cid']==j['id']):
                i['cid']=j['Name']
    if request.method=='POST':
        res=request.form.get('button')
        if res!=None:
            d = connect_db()
            time=datetime.utcnow()
            query="INSERT INTO applied (job_id,user_id,applied_time) VALUES( '"+str(res)+"','"+str(g.user)+"','"+str(time)+"' );"
            try:
                cur = d.execute(query)
                d.commit()
                d.close()
            except:
                print('hi')
            return render_template('student.html')
    return render_template('view_job.html',job=job)

@app.route('/assessment',methods=['POST', 'GET'])
def assessment():
    db = connect_db()
    cur = db.execute('select * from question')
    ques = [dict( Id=row[0],Desc=row[1],Op1=row[2],Op2=row[3],Op3=row[4],Op4=row[5],Ans=row[6]) for row in cur.fetchall()]
    db.close()
    #question.query.all()
    array=['ans1','ans2','ans3','ans4','ans5','ans6','ans7','ans8','ans9','ans10','ans11','ans12','ans13','ans14','ans15']
    if(request.method=='POST'):
        global j_id
        result=[]
        j=1
        score=0
        for i in array:
            a = request.form.get(i)
            if(i==None):
                result.append('-1')
            else:
                result.append(a)
                if(a==ques[j]['Ans']):
                    score=score+1
            j+=1
        d = connect_db()
        date1=date.today()
        time=datetime.now().time()
        query="UPDATE applied SET assesment_date = '"+str(date1)+"',assesment_time='"+str(time)+"',assesment_score='"+str(score)+"' WHERE (job_id = '"+str(j_id)+"' AND user_id='"+str(g.user)+"')"
        cur = d.execute(query)
        d.commit()
        d.close()
        return (render_template('result.html',score=score))    
    return render_template('assessment.html',ques=ques)

@app.route('/assessment_main',methods=['POST', 'GET'])
def assessment_main():
    d = connect_db()
    global j_id 
    query="SELECT * from job WHERE id IN (SELECT job_id from applied where user_id='"+str(g.user)+"' AND assesment_score is NULL) and status is NULL"
    cur = d.execute(query)
    job = [dict( id=row[0],Role=row[1],des=row[2].strip(),date=row[3],l_date=row[4],skills=row[5],exp=row[6],sal=row[7],cid=row[8],button=1) for row in cur.fetchall()]
    query="select id,Name,Email_id from company"
    cur = d.execute(query)
    company = [dict( id=row[0],Name=row[1],Email=row[2]) for row in cur.fetchall()]
    d.commit()
    d.close()
    for i in job:
        for j in company:
            if(i['cid']==j['id']):
                i['cid']=j['Name'] 
    length=len(job)
    if(length<20):
        num=20-length
    for i in range(num):
        job.append(dict( id=' ',Role=' ',des=' ',date=' ',l_date=' ',skills=' ',exp=' ',sal=' ',cid=' ',button=None)) 
    if request.method=='POST':
        res=request.form.get('button')
        if res!=None:
            j_id=res
            return redirect('/assessment')
    return render_template('assessment_main.html',job=job)
 
@app.route('/status',methods=['POST', 'GET'])
def status():
    d = connect_db()
    query="SELECT * from applied where user_id='"+str(g.user)+"' AND assesment_score is NOT NULL"
    cur = d.execute(query)
    applied = [dict( job_id=row[0],user_id=row[1],score=row[5],Status=row[6],cname="") for row in cur.fetchall()]
    query="select id,job_role,company_id from job"
    cur = d.execute(query)
    job = [dict( id=row[0],role=row[1],c_id=row[2]) for row in cur.fetchall()]
    query="select id,Name from company"
    cur = d.execute(query)
    company = [dict( id=row[0],name=row[1]) for row in cur.fetchall()]
    for i in applied:
        for j in job:
            if(i['job_id']==j['id']):
                i['job_id']=j['role']
                for k in company:
                    if(j['c_id']==k['id']):
                        i['cname']=k['name'] 
        if(i['Status']==None):
            i['Status']='Pending'
        else:
            i['Status']='Selected'
    length=len(applied)
    if(length<20):
        num=20-length
    for i in range(num):
        applied.append(dict( job_id=' ',user_id=' ',score=' ',Status=' ',cname=' ')) 
    d.close()
    return render_template('status.html',applied=applied)

@app.route('/profile',methods=['POST', 'GET'])
def profile():
    d = connect_db()
    query="SELECT * from User_acc where id='"+str(g.user)+"'"
    cur = d.execute(query)
    user = [dict( id=row[0],name=row[1],pwd=row[2],mail=row[3],contact=row[4],address=row[5],skills=row[6],Dob=row[7],age=row[8],sslc=row[9],hlc=row[10],college=row[11],department=row[12],cgpa=row[13],exp=row[15],status=row[16]) for row in cur.fetchall()]
    d.close()
    for i in user:
        if(i['status']==None):
            i['status']='Unemployed'
        else:
            i['status']='Employed'
    return render_template('profile.html',user=user)

@app.route('/company',methods=['POST', 'GET'])
def company():
    test_job()
    return render_template('company.html')

@app.route('/report',methods=['POST','GET'])
def report():
    d = connect_db()
    query="select job_id,user_id,assesment_score from applied WHERE job_id in(select id from job where company_id='"+str(g.user)+"') AND status IS NULL"
    cur = d.execute(query)
    user = [dict( j_id=row[0],u_id=row[1],score=row[2],j_name='',value=str(row[0])+' s '+str(row[1]),value1=str(row[0])+' ns '+str(row[1])) for row in cur.fetchall()]
    query="select id,job_role from job"
    cur = d.execute(query)
    job = [dict( id=row[0],name=row[1]) for row in cur.fetchall()]
    for i in user:
        for j in job:
            if(i['j_id']==j['id']):
                i['j_name']=j['name']
    d.close()
    if (request.method == 'POST'):
        res=request.form.get('button')
        d = connect_db()
        if res!=None:
            print(res)
            if(res[2]=='s'):
                query="UPDATE applied SET status='s' WHERE (job_id = '"+str(res[0])+"' AND user_id='"+str(res[4])+"')"
                cur = d.execute(query)
            elif(res[2:4]=='ns'):
                query="UPDATE applied SET status='ns' WHERE (job_id = '"+str(res[0])+"' AND user_id='"+str(res[5])+"')"
                cur = d.execute(query)
            d.commit()
            d.close()
            return redirect('/report')
        res=request.form['profile']
        if(res!=None):
            d = connect_db()
            query="SELECT * from User_acc where id='"+str(res)+"'"
            cur = d.execute(query)
            user = [dict( id=row[0],name=row[1],pwd=row[2],mail=row[3],contact=row[4],address=row[5],skills=row[6],Dob=row[7],age=row[8],sslc=row[9],hlc=row[10],college=row[11],department=row[12],cgpa=row[13],exp=row[15],status=row[16]) for row in cur.fetchall()]
            d.close()
            for i in user:
                if(i['status']==None):
                    i['status']='Unemployed'
                else:
                    i['status']='Employed'
        return render_template('company_profile.html',user=user)
    else:
        return render_template('report.html',user=user)

@app.route('/company/job',methods=['POST', 'GET'])
@app.route('/job',methods=['POST', 'GET'])
def job():
    if request.method == 'POST':
        job_role = request.form['job_role']
        job_desc= request.form['job_desc']
        last_date= request.form.get('last_date')
        exp= request.form['exp']
        salary= request.form['salary']
        list1=request.form.getlist('l1')
        skills=""
        date1= date.today()
        temp = date1 + timedelta(days=int(last_date))
        for i in list1:
            if(i!=None):
                skills=skills+" "+i
        data = Job(job_role=job_role,job_des=job_desc,date_created=date1,last_date=temp,experience=exp,salary=salary,skills_required=skills,company_id=g.user)      
        try:
            db.session.add(data)
            db.session.commit() 
            return render_template('company.html')
        except:
            return "error adding values to database"
    else:
        return render_template('job.html')
    

@app.route('/admin')
def admin():
   return render_template('admin.html')

@app.route('/edit_company')
def edit_company():
    d = connect_db()
    query="SELECT * from company "
    cur = d.execute(query)
    company = [dict( id=row[0],Name=row[1],pwd=row[2],email=row[3],address=row[4],ename=row[5],des=row[6]) for row in cur.fetchall()]
    d.close()
    return render_template('edit_company.html',company=company)

@app.route('/update_candidate')
def update_candidate():
    return render_template('update_candidate.html')

@app.route('/edit_candidate')
def edit_candidate():
    d = connect_db()
    query="SELECT * from User_acc"
    cur = d.execute(query)
    user = [dict( id=row[0],name=row[1],pwd=row[2],mail=row[3],contact=row[4],address=row[5],skills=row[6],Dob=row[7],age=row[8],sslc=row[9],hlc=row[10],college=row[11],department=row[12],cgpa=row[13],exp=row[15],status=row[16]) for row in cur.fetchall()]
    d.close()
    for i in user:
        if(i['status']==None):
            i['status']='Unemployed'
        else:
            i['status']='Employed'
    return render_template('edit_candidate.html',user=user)

@app.route('/logout')
def logout():
   session.pop('username', None)
   return render_template('homepage.html')



if __name__ == "__main__":
    app.run(debug=True)