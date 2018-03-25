import smtplib
import pymysql
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
##connection = pymysql.connect(host='54.254.219.225',user='shivankalgo',password='shivank@algorithm',db='careerletics',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
##cursor = connection.cursor()

def score_calc(job):
    connection =pymysql.connect(host='54.254.219.225', database='careerletics_new', user='shivankalgo',
                                password='shivank@algorithm',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try:
        with connection.cursor() as cursor:
            sql=("select DISTINCT * from ((select job_listing.*,jobtitle.PositionTitle,master_city.name from job_listing " +
             "inner join jobtitle on jobtitle.JobTitleId=job_listing.JobTitleId " +
             "inner join master_city on master_city.city_id=job_listing.city_id) as jobDetails " +
             "inner join (select " +
             "candidate.*,`chatbot`.`current_ctc`, `chatbot`.`expected_ctc`, `chatbot`.`current_location`,"+
             "`chatbot`.`expected_location`,`chatbot`.`notice_period`,  `chatbot`.`reason_of_leaving`,"+
             "job_id,workExp,Position,NumJobs from `candidate` " +
             "inner join `master_id` on  `master_id`.`candidate_id`=`candidate`.`candidate_id` " +
             "inner join `candidate_skill` on `candidate_skill`.`candidate_id` = `candidate`.`candidate_id` " +
             "inner join `chatbot` on `chatbot`.`candidate_id` = `candidate`.`candidate_id` " +
             "inner join `candidate_derived` on `candidate_derived`.`candidate_id` = `candidate`.`candidate_id` " +
             "inner join (select  sum(datediff(end_Date,Start_Date) / 365) as workExp,count(candidate_experience_id) as NumJobs,"+
             "group_concat(designation separator ', ') as Position, candidate_id " +
             "from `candidate_experience` group by `candidate_experience`.`candidate_id`) as totExp on " +
             " `totExp`.`candidate_id`= `candidate`.`candidate_id` " +
             ") as candidate1 on candidate1.job_id=jobDetails.job_id) where jobDetails.job_id=%s")

            cursor.execute(sql,job)
            result = cursor.fetchone()
            #print(result)
            while result is not None:
                DJL_match = 1
                TI_match = 1
                Leader_match = 1
                Notice_period = 1
                Leaving_reason = 1

                #print(result["name_of_company"])
                comPerYr=0
                prf_location = result["expected_location"]
                if (result["name"]==result["expected_location"]):
                    DJL_match = 0
                if (result["notice_period"]==None):
                    notice_period=0
                else:
                    notice_period = result["notice_period"]
                totExp = result["workExp"]
                if (totExp>0):
                    comPerYr = int(result["NumJobs"])/totExp
                if (notice_period < 3):
                    Notice_period = 0
                if  (result["expected_ctc"]!=None):
                    expSalary = result["expected_ctc"]
                else:
                    expSalary=0
                position=result["Position"]
                if (position == result["PositionTitle"]):
                    Leader_match = 0
                if  (result["ctc_from"]!=None):
                    ctcFrom = result["ctc_from"]
                else:
                    ctcFrom=0
                if ( expSalary > ctcFrom):
                    leave_reson = 0
                if (result["travelling_involved"] == 1):
                    TI_match = 1
                else:
                    TI_match = 0

                leave_reson = result["reason_of_leaving"];
                if ((leave_reson != None) | (leave_reson != "")):
                    lReson = 0
                Leaving_reason = lReson + Notice_period + DJL_match + Leader_match;

                empPOD = (DJL_match + TI_match + Leader_match + Notice_period + Leaving_reason + comPerYr) * 5;
                #print(empPOD)
                sql="update candidate_derived set probability_of_decline="+str(empPOD) +" where candidate_id="+str(result["candidate_id"])
                cursor2 = connection.cursor()
                cursor2.execute(sql)
                connection.commit();
                cursor2.close()
                result = cursor.fetchone()
        print("pod done")
        sql2=(" update candidate_derived A,master_id B1 set A.employability_score=(select distinct employability_score_e " +
        " from user_score B where A.candidate_id=B.candidate_id limit 1) where A.candidate_id=B1.candidate_id and B1.job_id=%s")
        cursor3 = connection.cursor()
        cursor3.execute(sql2,job)
        connection.commit()
        cursor3.close()
        sql3 = (" update job_listing set ScoreAlgo_state=0 where job_id=%s")
        cursor4 = connection.cursor()
        cursor4.execute(sql3, job)
        connection.commit()
        cursor4.close()
        print("update pod done")
    finally:
        cursor.close()
        connection.close()
        print("done")



