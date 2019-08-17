import csv
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

def email_admin():    
    admins=[]
    
    f = open("./receivers.txt", "r")
    for line in f:
            admins.append(line.strip("\n "))
    f.close()    
    emailfrom = "coursesapi19@gmail.com"
    emailto = ", ".join(admins)
    fileToSend = "courses.csv"
    username = "coursesapi19@gmail.com"
    password = "pythoncourse19"
                            
    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = "[CoursesAPI] New course added"
                            
    body = """
    Dear admin, 
    New course has been added to collection. Details are sent in attachment. """
    msg.attach(MIMEText(body, 'plain'))
    
    
    fp = open(fileToSend, "rb")
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    with open('courses.csv',"r", newline='') as csvfile:
          rows=sum(1 for row in csvfile)  
    if emailto and rows==2:                       
            server = smtplib.SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username,password)
            server.sendmail(emailfrom, emailto, msg.as_string())
            server.quit()



        

                    
        