# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 17:51:19 2017

@author: admin
"""

import pandas as pd
import pymysql
import difflib


def connect_to_db():
    return pymysql.connect(host="54.254.219.225",user="shivankalgo",passwd="shivank@algorithm",db="careerletics_new",charset="utf8mb4") 

def funnel_filter(job_id) :
        dbconnect=connect_to_db()
        jd_data=pd.read_sql("select job_id,A2.name,minimum_years_of_experience,ctc_from,ctc_to,minimum_degree_earned, "
                        +" minimum_expected_college_tier,cgpa_category,1 as Notice_period,1 as minExp,0 as minLoc,1 as minDgr,1 as minNotcprd,1 as minCTC from job_listing A1 "
                        +" left join master_city A2 on A1.city_id=A2.city_id where job_id= "+str(job_id),con=dbconnect)
    
        experience_data=pd.read_sql("select job_id,A1.candidate_id,current_location,expected_location,current_ctc,expected_ctc,notice_period,workYrs "
                        +" from chatbot A1 left join ((select candidate_id,sum(datediff(end_date,start_date) / 365) as workYrs "
                        +" from candidate_experience group by candidate_id "
                        +") A2, master_id A3) on A1.candidate_id=A2.candidate_id "
                        +" and A1.candidate_id=A3.candidate_id where job_id= "+str(job_id),con=dbconnect)
                        
        qualification_data=pd.read_sql("select job_id,A2.* from master_id A1 left join "
                                  +" (select candidate_id,degree,1 as DegVal,institute_name,university_name from candidate_qualification where "
                                  +" (lower(degree) like 'b%')  or (lower(degree) like 'ca%') or (lower(degree) like 'charter%') "
                                  +" or (lower(degree) like '%engineer%') or (lower(degree) like 'c.a%') "
                                  +"  union all"
                                  +"  select candidate_id,degree,2 as DegVal,institute_name,university_name from candidate_qualification where "
                                  +"  (lower(degree) like 'm%') or (lower(degree) like 'post%')"
                                  +"  union all"
                                  +"  select candidate_id,degree,3 as DegVal,institute_name,university_name from candidate_qualification where "
                                  +"  (lower(degree) like 'ph.%') or (lower(degree) like 'doct%') or (lower(degree) like 'phd%')) A2"
                                  +" on A1.candidate_id=A2.candidate_id where job_id= "+str(job_id),con=dbconnect)
     
        jd_data.fillna(0,inplace=True)
        experience_data['current_location'].fillna('0',inplace=True)
        experience_data['expected_location'].fillna('Mumbai',inplace=True)
        experience_data['current_ctc'].fillna(0,inplace=True)
        experience_data['expected_ctc'].fillna(0,inplace=True)
        experience_data['notice_period'].fillna(0,inplace=True)
        
        qualification_grpData=qualification_data.groupby('candidate_id').max().reset_index()
        min_year_exp=jd_data.ix[0,'minimum_years_of_experience']
        max_ctc=jd_data.ix[0,'ctc_to']
        location=jd_data.ix[0,'name']
        min_degree=jd_data.ix[0,'minimum_degree_earned']
        notice_period=jd_data.ix[0,'Notice_period']
        expLst=Exp_filter(experience_data,min_year_exp)
        ctcLst=CTC_filter(experience_data,max_ctc)
        locLst=Location_filter(experience_data,location)
        dgrLst=Degree_filter(qualification_grpData,min_degree)
        noticepdLst=NoticePrd_filter(experience_data,notice_period)
        funnelLst=[]
        flagFnlLst=0

        if ((jd_data.ix[0,'minLoc']==1)):
            funnelLst=locLst
            flagFnlLst=1
        if ((jd_data.ix[0,'minExp']==1) & (flagFnlLst==0)):
           funnelLst=expLst
           flagFnlLst=1
        elif (jd_data.ix[0,'minExp']==1):
           funnelLst= list(set(funnelLst).intersection(set(expLst)))
        if ((jd_data.ix[0,'minDgr']==1) &  (flagFnlLst==0)):
           funnelLst=dgrLst
           flagFnlLst=1
        elif (jd_data.ix[0,'minDgr']==1):
           funnelLst= list(set(funnelLst).intersection(set(dgrLst)))
        if ((jd_data.ix[0,'minNotcprd']==1) & (flagFnlLst==0)):
           funnelLst=noticepdLst
           flagFnlLst=1
        elif(jd_data.ix[0,'minNotcprd']==1):
           funnelLst= list(set(funnelLst).intersection(set(noticepdLst)))
        if ((jd_data.ix[0,'minCTC']==1) & (flagFnlLst==0)):
           funnelLst=ctcLst
           flagFnlLst=1
        elif(jd_data.ix[0,'minCTC']==1):
           funnelLst= list(set(funnelLst).intersection(set(ctcLst)))
           
        if (flagFnlLst==0):
           funnelLst=list(set(expLst) | set(dgrLst) | set(ctcLst) | set(noticepdLst) | set(locLst))
         
        print(len(funnelLst))    
        return funnelLst

def loc_compare(loc1,loc2):
    try:
        seq = difflib.SequenceMatcher()
        #print (loc1,loc2)
        seq.set_seqs(loc1, loc2)
        return  seq.ratio()*100
    except:
        return 0

#experience_data['curLoc_ratio'] = experience_data['current_location'].apply(lambda x:loc_compare('mum',x))
#df_filter1=df2[df2['workYrs']>=min_year_exp]
def Exp_filter(experience_data,min_year_exp):
    a=list(experience_data.candidate_id[experience_data.workYrs>=min_year_exp])
    return a                     

def CTC_filter(experience_data,max_ctc):
    b=list(experience_data.candidate_id[(experience_data.expected_ctc*1.3<=max_ctc) | (experience_data.expected_ctc<=max_ctc) ] )
    return b

def Location_filter(experience_data,location):
    experience_data['curLoc_ratio'] = experience_data['current_location'].apply(lambda x:loc_compare(location,x))
    experience_data["expectLoc_ratio"] = experience_data["expected_location"].apply(lambda x:loc_compare(location,x))
    c=list(experience_data.candidate_id[(experience_data.curLoc_ratio>=60) | (experience_data.expectLoc_ratio>=60) ] )
    return c

def Degree_filter(qualification_data,min_degree):
    d=list(qualification_data.candidate_id[qualification_data.DegVal>=min_degree])
    return d

def NoticePrd_filter(experience_data,notice_period):
    e=list(experience_data.candidate_id[experience_data.notice_period<=notice_period])
    return e

def main(job_id):
    return  funnel_filter(job_id)
    
