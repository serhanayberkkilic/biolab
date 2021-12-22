import sys
from typing import Counter
from pymongo import MongoClient
import json
import datetime
import cv2
import mediapipe as mp
import time

from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog,QApplication, QMessageBox, QStackedWidget

cluster=MongoClient("mongodbserver")
db=cluster['biomek_data']
doctors=db['doctors']
members=db['members']
update0=db['Update0']
with open('il_ilce.json', 'r') as j:
     contents = json.loads(j.read())


class login_Screen(QDialog):
    def __init__(self):
        super(login_Screen,self).__init__()
        loadUi('login.ui',self)
        self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)# password line hided

class signup_Screen(QDialog):
    def __init__(self):
        super(signup_Screen,self).__init__()
        loadUi('sign_up.ui',self)
        self.sign_up_password.setEchoMode(QtWidgets.QLineEdit.Password)# password line hided
        self.sign_up_password2.setEchoMode(QtWidgets.QLineEdit.Password)# password line hided

class signup_choose_Screen(QDialog):
    def __init__(self):
        super(signup_choose_Screen,self).__init__()
        loadUi('sign_up_choose.ui',self)

class signup_doctor_Screen(QDialog):
    def __init__(self):
        super(signup_doctor_Screen,self).__init__()
        loadUi('sign_up_doctor.ui',self)

class signup_member_Screen(QDialog):
    def __init__(self):
        super(signup_member_Screen,self).__init__()
        loadUi('sign_up_member.ui',self)

class login_doctor_Screen(QDialog):
    def __init__(self):
        super(login_doctor_Screen,self).__init__()
        loadUi('login_doctor.ui',self)

class login_member_Screen(QDialog):
    def __init__(self):
        super(login_member_Screen,self).__init__()
        loadUi('login_member.ui',self)

class member_video_Screen(QDialog):
    def __init__(self):
        super(member_video_Screen,self).__init__()
        loadUi('video.ui',self)


#####################################################################################################################################################################


def opencv(self,index0):
    video0=member_video_Screen()
    widget.addWidget(video0)
    widget.setCurrentIndex(widget.currentIndex()+1)
    video0.login_member_bck.clicked.connect(self.login_member)

    if index0==0:
        video0.video_label_info.setText('Please Rise your Left Hand')
    else:
        video0.video_label_info.setText('Please Rise your Right Hand')

    
    self.video_stop_values=False #Close Cap release values
    self.counter_hand0=0 #hand counter value
    self.counter_hand0_close=0
    def stop_video():
        self.video_stop_values=True
    
    def hand_detection(image):
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_hands = mp.solutions.hands

            def get_label(index,results): #0 left 1 right
                    output = None
                    for classification in results.multi_handedness:
                        if classification.classification[0].index == index:
                            label = classification.classification[0].label
                            output = label
                    return output
            
            def hand_counter():
                x_9, y_9 = hand_landmarks.landmark[9].x*640, hand_landmarks.landmark[9].y*480
                x1_12, y1_12 = hand_landmarks.landmark[12].x*640, hand_landmarks.landmark[12].y*480
               

                if y1_12>y_9:
                    time.time
                    self.counter_hand0_close+=1


                if y_9>y1_12 and self.counter_hand0_close>1:
                    self.counter_hand0+=1
                    self.counter_hand0_close=0
                video0.video_label_counter.setText(f'Counter : {self.counter_hand0}')
                return self.counter_hand0

            with mp_hands.Hands(min_detection_confidence=0.7,min_tracking_confidence=0.7,max_num_hands=1) as hands: # Detecetion just one hand 
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks: # Right and left hand detection
                    for hand_landmarks in results.multi_hand_landmarks:

                        if get_label(index0,results)=='Left':
                            mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())
                            if  hand_counter() ==10:
                                stop_video()
    
                            return image
                        if get_label(index0,results)=='Right':
                            mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())
   
                            if  hand_counter() ==10:
                                stop_video()
                            return image
                return image

    def conver_pix_map(image):
            h, w, ch = image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_BGR888)
            p = convert_to_Qt_format.scaled(640, 480,Qt.KeepAspectRatio)
            qt_img = QPixmap.fromImage(p)
            return qt_img
    
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        else:
            video0.video_label.setPixmap(conver_pix_map(hand_detection(image)))
            if cv2.waitKey(10) & self.video_stop_values == True:
                cap.release()
                self.login_member()
                break

            video0.login_member_view_finsh_btn.clicked.connect(stop_video)

        
    return self.counter_hand0

def update(): #Every Monday update week
    date_time_mongo=[i for i in update0.find()][0]
    x= datetime.datetime(int(date_time_mongo['Year']),int(date_time_mongo['Month']),int(date_time_mongo['Day']))
    y=x.replace(day=x.day+7)
    if y<datetime.datetime.now() or y==datetime.datetime.now():
        newvalues = { "$set": { 'Monday':'None',
                                'Tuesday':'None',
                                'Wendsday':'None',
                                'Thursday':'None',
                                'Friday':'None',
                                'Saturday':'None',
                                'Sunday':'None'} } 
        for _ in [i['identity'] for i in members.find()]:
            members.update_one({ 'identity':_},newvalues)
        newvalues_date={ "$set": {'Year':y.strftime('%Y'),'Month':y.strftime('%m'),'Day':y.strftime('%d')}}
        update0.update_one({'name':'date'},newvalues_date) 

#####################################################################################################################################################################

class Welcome_Screen(QDialog):

    def __init__(self):
        super(Welcome_Screen,self).__init__()
        loadUi('welcomescreen.ui',self)
        self.welcome_log_btn.clicked.connect(self.gotologin)# login page
        self.welcome_new_btn.clicked.connect(self.gotosign_up)# new account page

    def show_popup(self,result):
        pass
        msg=QMessageBox()
        
        if result==1:
            msg.setWindowTitle('Succesfully')
            msg.setText('successful')
        else:
            msg.setWindowTitle('Fail')
            msg.setText('Fail')
        x=msg.exec_()
            
    def welcome_screen0(self): # Main page
        welcome=Welcome_Screen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def gotologin(self):#○ login page

        def check_username_login():
            self.username_login=login.login_username.text()
            self.password_login=login.login_password.text()
            
            if self.username_login=='' or self.password_login=='':
                login.label_err_msg_login.setText('Login failed (Username or password must be entered)')
                login.label_err_msg_login.setStyleSheet("color: red;")
            else:
                try:
                    if doctors.find_one({'identity':self.username_login})!=None and doctors.find_one({'identity':self.username_login})['identity']==self.username_login and doctors.find_one({'identity':self.username_login})['password']==self.password_login:
                            self.login_doctor()

                    
                    elif members.find_one({'identity':self.username_login})!=None and members.find_one({'identity':self.username_login})['identity']==self.username_login and members.find_one({'identity':self.username_login})['password']==self.password_login:
                            self.login_member()

                    else:
                        login.label_err_msg_login.setText('Login failed')
                        login.label_err_msg_login.setStyleSheet("color: red;")
                    
                except:
                    login.label_err_msg_login.setText('Login failed (Database Eror)')
                    login.label_err_msg_login.setStyleSheet("color: red;")

        login=login_Screen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
        login.login_back.clicked.connect(self.welcome_screen0)
        login.welcome_log_btn.clicked.connect(check_username_login)
    
    def gotosign_up(self):

        def check_password():
            self.username_signup=sign_up.sign_up_username.text()
            self.password_signup=sign_up.sign_up_password.text()
            self.password_signup1=sign_up.sign_up_password2.text()
            # identity emty check
            if self.username_signup =='' or self.password_signup =='' or self.password_signup1 =='':
                sign_up.sign_up_err_message.setText('Registration failed (Username or password must be entered)')
                sign_up.sign_up_err_message.setStyleSheet("color: red;")
            else: # Password control
                if self.password_signup!=self.password_signup1:
                    sign_up.sign_up_err_message.setText('password must be same')
                    sign_up.sign_up_err_message.setStyleSheet("color: red;")
                elif self.password_signup == self.password_signup1:
                    try: #Database user check   
                        if doctors.find_one({'identity':self.username_signup})!=None or members.find_one({'identity':self.username_signup})!=None:
                            sign_up.sign_up_err_message.setText('user already exists')
                            sign_up.sign_up_err_message.setStyleSheet("color: red;")
                        else:
                            self.gotosign_up_choose()
                    except Exception as e:
                        print(e) 
                        sign_up.sign_up_err_message.setText('Registration failed(Database Eror)')
                        sign_up.sign_up_err_message.setStyleSheet("color: red;")

        sign_up=signup_Screen()
        widget.addWidget(sign_up)
        widget.setCurrentIndex(widget.currentIndex()+1)
        sign_up.sign_up_back.clicked.connect(self.welcome_screen0)
        sign_up.sign_up_login_btn.clicked.connect(check_password)

    def gotosign_up_choose(self):
        sign_up_choose=signup_choose_Screen()
        widget.addWidget(sign_up_choose)
        widget.setCurrentIndex(widget.currentIndex()+1)
        sign_up_choose.sign_up_choose_back.clicked.connect(self.gotosign_up)
        sign_up_choose.sign_up_choose_doctor_btn.clicked.connect(self.gotosign_up_doctor)#Doctor page
        sign_up_choose.sign_up_choose_member_btn.clicked.connect(self.gotosign_up_member)#Member page
    
    def gotosign_up_doctor(self):

        def city_value():
            self.city_value0=sign_up_doctor.sign_up_doctor_city.currentRow()
            sign_up_doctor.sign_up_doctor_distirct.addItems([i['name'] for i in contents[self.city_value0]['districts']])
            return True
        
        def distirct_value():
            self.distirct_value=sign_up_doctor.sign_up_doctor_distirct.currentRow()
            return True
        
        def clear_values():
            sign_up_doctor.sign_up_doctor_name.clear()
            sign_up_doctor.sign_up_doctor_surname.clear()
            sign_up_doctor.sign_up_doctor_hospital.clear()
            sign_up_doctor.sign_up_doctor_distirct.clear()

        def create_account_doctor():
            name=sign_up_doctor.sign_up_doctor_name.text()
            surname=sign_up_doctor.sign_up_doctor_surname.text()
            hospital=sign_up_doctor.sign_up_doctor_hospital.text()
            birthday=sign_up_doctor.sign_up_doctor_date.text()
            if hospital== '' or name== '' or surname=='':
                sign_up_doctor.sign_up_doctor_msg.setText('Registration failed(name, surname and hospital must be entred)')
                sign_up_doctor.sign_up_doctor_msg.setStyleSheet("color: red;")
            else:
                city=contents[self.city_value0]['name']
                distirct=[i['name'] for i in contents[self.city_value0]['districts']][self.distirct_value]
                create_doctor_list={'identity':self.username_signup,
                                'password':self.password_signup,
                                'name':name,
                                'surname':surname,
                                'hospital':hospital,
                                'birthday':birthday,
                                'city':city,
                                'distirct':distirct}
                doctors.insert_one(create_doctor_list)
            
                if doctors.find_one(create_doctor_list):
                    self.welcome_screen0()
                    self.show_popup(result=1)
                else:
                    sign_up_doctor.sign_up_doctor_msg.setText('Registration failed')
                    sign_up_doctor.sign_up_doctor_msg.setStyleSheet("color: red;")
                    clear_values()
        
        sign_up_doctor=signup_doctor_Screen()
        widget.addWidget(sign_up_doctor)
        widget.setCurrentIndex(widget.currentIndex()+1)
        sign_up_doctor.sign_up_doctor_back.clicked.connect(self.gotosign_up_choose)
        sign_up_doctor.sign_up_doctor_city.addItems([i['name'] for i in contents])
        sign_up_doctor.sign_up_doctor_city.setCurrentRow(0)
    
        sign_up_doctor.sign_up_doctor_city_btn.clicked.connect(city_value)
        sign_up_doctor.sign_up_doctor_distirct_btn.clicked.connect(distirct_value)
        sign_up_doctor.sign_up_doctor_create.clicked.connect(create_account_doctor)

    def gotosign_up_member(self):
        
        def city_value():
            self.city_value0=sign_up_member.sign_up_member_city.currentRow()
            sign_up_member.sign_up_member_distirct.addItems([i['name'] for i in contents[self.city_value0]['districts']])
            return True
        
        def distirct_value():
            self.distirct_value=sign_up_member.sign_up_member_distirct.currentRow()
            return True

        def sign_up_member_doctor_combo_box():
            self.doctor_member0=sign_up_member.sign_up_member_doctor_combo
            self.doctor_member0.addItems([i['name']+i['surname'] for i in doctors.find()])
    
        def clear_values():
            sign_up_member.sign_up_member_name.clear()
            sign_up_member.sign_up_member_surname.clear()
            sign_up_member.sign_up_member_hospital.clear()
            sign_up_member.sign_up_member_distirct.clear()

        def create_account_member():
            name=sign_up_member.sign_up_member_name.text()
            surname=sign_up_member.sign_up_member_surname.text()
            hospital=sign_up_member.sign_up_member_hospital.text()
            birthday=sign_up_member.sign_up_member_date.text()
            doctor_member=self.doctor_member0.currentText()
            if hospital== '' or name== '' or surname=='':
                sign_up_member.sign_up_member_msg.setText('Registration failed(name, surname and hospital must be entred)')
                sign_up_member.sign_up_member_msg.setStyleSheet("color: red;")
            else:
                city=contents[self.city_value0]['name']
                distirct=[i['name'] for i in contents[self.city_value0]['districts']][self.distirct_value]
                create_member_list={'identity':self.username_signup,
                                'password':self.password_signup,
                                'name':name,
                                'surname':surname,
                                'hospital':hospital,
                                'birthday':birthday,
                                'city':city,
                                'distirct':distirct,
                                'doctor':doctor_member,
                                'Task1':'None',
                                'Task2':'None',
                                'Monday':'None',
                                'Tuesday':'None',
                                'Wednesday':'None',
                                'Thursday':'None',
                                'Friday':'None',
                                'Saturday':'None',
                                'Sunday':'None'}
                members.insert_one(create_member_list)
            
                if members.find_one(create_member_list): # check 
                    self.show_popup(result=1)
                    self.welcome_screen0()
                else:
                    sign_up_member.sign_up_member_msg.setText('Registration failed')
                    sign_up_member.sign_up_member_msg.setStyleSheet("color: red;")
                    clear_values()
        
        sign_up_member=signup_member_Screen()
        widget.addWidget(sign_up_member)
        widget.setCurrentIndex(widget.currentIndex()+1)
        sign_up_member_doctor_combo_box() 
        sign_up_member.sign_up_member_back.clicked.connect(self.gotosign_up_choose)
        sign_up_member.sign_up_member_city.addItems([i['name'] for i in contents])
        sign_up_member.sign_up_member_city.setCurrentRow(0)
    
        sign_up_member.sign_up_member_city_btn.clicked.connect(city_value)
        sign_up_member.sign_up_member_distirct_btn.clicked.connect(distirct_value)
        sign_up_member.sign_up_member_create.clicked.connect(create_account_member)

    def login_doctor(self):
        login_doctor0=login_doctor_Screen()
        widget.addWidget(login_doctor0)
        widget.setCurrentIndex(widget.currentIndex()+1)
        login_doctor0.login_doctor_back.clicked.connect(self.gotologin)

        doctor_name_login=doctors.find_one({'identity':self.username_login})
        doctor_name_login=doctor_name_login['name']+doctor_name_login['surname']
        login_doctor0.welcome_text_login_doctor.setText(f'Welcome {doctor_name_login}') # Login Screnn Welcome doctor.....

        def doctor_login_table():
            self.liste_doctor_login=[x for x in members.find({'doctor':f'{doctor_name_login}'})]
            login_doctor0.tableWidget.setRowCount(len(self.liste_doctor_login))
            row=0
            for person in self.liste_doctor_login:
                login_doctor0.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(person['name']))
                login_doctor0.tableWidget.setItem(row,1,QtWidgets.QTableWidgetItem(person['surname']))
                login_doctor0.tableWidget.setItem(row,2,QtWidgets.QTableWidgetItem(person['birthday']))
                login_doctor0.tableWidget.setItem(row,3,QtWidgets.QTableWidgetItem(person['Task1']))
                login_doctor0.tableWidget.setItem(row,4,QtWidgets.QTableWidgetItem(person['Task2']))
                login_doctor0.tableWidget.setItem(row,5,QtWidgets.QTableWidgetItem(person['Monday']))
                login_doctor0.tableWidget.setItem(row,6,QtWidgets.QTableWidgetItem(person['Tuesday']))
                login_doctor0.tableWidget.setItem(row,7,QtWidgets.QTableWidgetItem(person['Wednesday']))
                login_doctor0.tableWidget.setItem(row,8,QtWidgets.QTableWidgetItem(person['Thursday']))
                login_doctor0.tableWidget.setItem(row,9,QtWidgets.QTableWidgetItem(person['Friday']))
                login_doctor0.tableWidget.setItem(row,10,QtWidgets.QTableWidgetItem(person['Saturday']))
                login_doctor0.tableWidget.setItem(row,11,QtWidgets.QTableWidgetItem(person['Sunday']))

                row+=1

        def login_doctor_push_button():
            if login_doctor0.tableWidget.currentColumn()==3 or login_doctor0.tableWidget.currentColumn()==4:
                change_task_doctor_login_filter=self.liste_doctor_login[login_doctor0.tableWidget.currentRow()]['identity']

                if login_doctor0.tableWidget.currentColumn()==3:
                    login_doctor0.tableWidget.setItem(login_doctor0.tableWidget.currentRow(),3,QtWidgets.QTableWidgetItem('X'))
                    newvalues = { "$set": { 'Task1': 'X' } }
                    members.update_one({ 'identity': change_task_doctor_login_filter}, newvalues)
                elif login_doctor0.tableWidget.currentColumn()==4:
                    login_doctor0.tableWidget.setItem(login_doctor0.tableWidget.currentRow(),4,QtWidgets.QTableWidgetItem('X'))
                    newvalues = { "$set": { 'Task2': 'X' } }
                    members.update_one({ 'identity': change_task_doctor_login_filter}, newvalues)     
                doctor_login_table()

        def login_doctor_push_button_delete():
            if login_doctor0.tableWidget.currentColumn()==3 or login_doctor0.tableWidget.currentColumn()==4:
                change_task_doctor_login_filter=self.liste_doctor_login[login_doctor0.tableWidget.currentRow()]['identity']

            if login_doctor0.tableWidget.currentColumn()==3:
                login_doctor0.tableWidget.setItem(login_doctor0.tableWidget.currentRow(),3,QtWidgets.QTableWidgetItem('None'))
                newvalues = { "$set": { 'Task1': 'None' } }
                members.update_one({ 'identity': change_task_doctor_login_filter }, newvalues)
            elif login_doctor0.tableWidget.currentColumn()==4:
                login_doctor0.tableWidget.setItem(login_doctor0.tableWidget.currentRow(),4,QtWidgets.QTableWidgetItem('None'))
                newvalues = { "$set": { 'Task2': 'None' } }
                members.update_one({ 'identity': change_task_doctor_login_filter }, newvalues)     
            doctor_login_table()

        doctor_login_table()
        login_doctor0.doctor_login_give_task.clicked.connect(login_doctor_push_button)
        login_doctor0.doctor_login_delete_task.clicked.connect(login_doctor_push_button_delete)

    def login_member(self):
        login_member0=login_member_Screen()
        widget.addWidget(login_member0)
        widget.setCurrentIndex(widget.currentIndex()+1)
        login_member0.login_member_bck.clicked.connect(self.gotologin)

        member_name_login=members.find_one({'identity':self.username_login})
        member_name_login0=member_name_login['name']+member_name_login['surname']
        login_member0.welcome_label_member.setText(f'Welcome {member_name_login0}') # Login Screnn Welcome member....

        def member_login_table_and_combo_box():
            self.liste_member_login=[members.find_one({'identity':self.username_login})]
            login_member0.tableWidget.setRowCount(len(self.liste_member_login))
            row=0
            for person in self.liste_member_login:
                login_member0.tableWidget.setItem(row,0,QtWidgets.QTableWidgetItem(person['name']))
                login_member0.tableWidget.setItem(row,1,QtWidgets.QTableWidgetItem(person['surname']))
                login_member0.tableWidget.setItem(row,2,QtWidgets.QTableWidgetItem(person['doctor']))
                login_member0.tableWidget.setItem(row,3,QtWidgets.QTableWidgetItem(person['Task1']))
                login_member0.tableWidget.setItem(row,4,QtWidgets.QTableWidgetItem(person['Task2']))
                login_member0.tableWidget.setItem(row,5,QtWidgets.QTableWidgetItem(person['Monday']))
                login_member0.tableWidget.setItem(row,6,QtWidgets.QTableWidgetItem(person['Tuesday']))
                login_member0.tableWidget.setItem(row,7,QtWidgets.QTableWidgetItem(person['Wednesday']))
                login_member0.tableWidget.setItem(row,8,QtWidgets.QTableWidgetItem(person['Thursday']))
                login_member0.tableWidget.setItem(row,9,QtWidgets.QTableWidgetItem(person['Friday']))
                login_member0.tableWidget.setItem(row,10,QtWidgets.QTableWidgetItem(person['Saturday']))
                login_member0.tableWidget.setItem(row,11,QtWidgets.QTableWidgetItem(person['Sunday']))
                row+=1
                if person['Task1']!='None':
                    login_member0.login_member_comboBox.addItem("Task1")
                if person['Task2']!='None':
                    login_member0.login_member_comboBox.addItem("Task2")
          
        def login_member_make_btn_func():

            if login_member0.login_member_comboBox.currentText()=='Task1':
                output_task1=opencv(self,index0=0)
                if output_task1==10 or output_task1>10:

                    if members.find_one({ 'identity': member_name_login['identity']})[f'{datetime.datetime.now().strftime("%A")}']=='Task2 completed':
                        newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'Task1 and Task2 completed' } }
                        members.update_one({ 'identity': member_name_login['identity']}, newvalues)
                    else:
                        newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'Task1 completed' } }
                        members.update_one({ 'identity': member_name_login['identity']}, newvalues)
                else:
                    newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'could not be completed' } }
                    members.update_one({ 'identity': member_name_login['identity']}, newvalues)

            elif login_member0.login_member_comboBox.currentText()=='Task2':
                output_task2=opencv(self,index0=1)
                if output_task2==10 or output_task2>10:
                    
                    if members.find_one({ 'identity': member_name_login['identity']})[f'{datetime.datetime.now().strftime("%A")}']=='Task1 completed':
                        newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'Task1 and Task2 completed' } }
                        members.update_one({ 'identity': member_name_login['identity']}, newvalues)
                    else:
                        newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'Task2 completed' } }
                        members.update_one({ 'identity': member_name_login['identity']}, newvalues)
                else:
                    newvalues = { "$set": {f'{datetime.datetime.now().strftime("%A")}': 'could not be completed' } }
                    members.update_one({ 'identity': member_name_login['identity']}, newvalues)
            
           
        member_login_table_and_combo_box() # Update table
        login_member0.login_member_make_btn.clicked.connect(login_member_make_btn_func) # Do it task
    
    

            


update()
app=QApplication(sys.argv)
welcome=Welcome_Screen()
widget=QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.setWindowTitle('Biolab')
widget.setWindowIcon(QtGui.QIcon('555189.ico'))
widget.show()


try:
    sys.exit(app.exec_())
except:
    pass


