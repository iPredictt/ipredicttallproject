import smtplib
import pymysql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
##connection = pymysql.connect(host='54.254.219.225',user='shivankalgo',password='shivank@algorithm',db='careerletics',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
##cursor = connection.cursor()


def send_error(user,job):
    connection = pymysql.connect(host='54.254.219.225',user='shivankalgo',password='shivank@algorithm',db='careerletics_new',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `candidate_id`,`name`,`email`,`uuid`  FROM `candidate` WHERE candidate_id =%s"
            cursor.execute(sql,(user))
            result = cursor.fetchone()
            receipent = result["email"]
            name = result["name"]
            uuid = result["uuid"]
            sql1 = "select job_listing.name_of_company,jobtitle.PositionTitle from job_listing JOIN jobtitle ON (job_listing.JobTitleId = jobtitle.JobTitleId) WHERE job_id =%s"
            cursor.execute(sql1,(job))
            result1 = cursor.fetchone()
            company = result1["name_of_company"]
            title = result1["PositionTitle"]
    finally:
        connection.close()
        
    msg = MIMEMultipart('alternative')
    msg['From'] = "amber-hr@careerletics.com"
    msg['To'] = receipent
    msg['Subject'] = 'Careerletics HR-Mail'
    message = """    <html>
      <body>
        <div><div>Dear """+ name.title()+ """,</div><br><div>We are pleased to inform you
            that your resume is being considered for your application as a """+ title +""" at """+ company +""".</div>
            <BR><div>More information is required by our HR team before we can process your application further.
            Please provide the information by clicking on the following link <a href=https://chatbot.careerletics.com/chatbot.html?id="""+ uuid +""">
            Click Here</a>.</div><br><div>
            Thank you for your co-operation.</div><br><div>
            <font color=#0000ff>Regards,</font></div><div><font color=#0000ff><br></font></div>
            <div><font color=#0000ff>Amber</font></div><div><font color=#0000ff>Team CareerLetics.</font></div><div><br></div>
           </div>
      </body>
    </html>
    """

    part2 = MIMEText(message, 'html')
    msg.attach(part2)
        
        
    
    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.ehlo()
        session.starttls()
        session.login("amber-hr@careerletics.com", 'ipredictt@123')
        
        
    except smtplib.SMTPAuthenticationError as e:
        print ("Incorrect username/password combination")
    except smtplib.SMTPException as e:
        print ("Authentication failed")
        
    
    try:
        session.sendmail("amber-hr@careerletics.com",receipent,msg.as_string())
        print("Successfully sent email to"+" " +receipent)
    except smtplib.SMTPException as e:
        print ("Error: unable to send email", e)
            
    finally:
        session.close()




