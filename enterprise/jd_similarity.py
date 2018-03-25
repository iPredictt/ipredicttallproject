# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 12:24:49 2017

@author: Shivank.r
"""
import pymysql
import numpy as np
import pandas as pd
import itertools
import re


def connect_to_db():
    return pymysql.connect(host="54.254.219.225",user="shivankalgo",passwd="shivank@algorithm",db="careerletics_new",charset="utf8mb4") 
    
def University_calculation(jobid):
    """Query of minmum Tier and CGPA on job id"""
    min_cgpa=90
    """~~~~~~~~~"""
    dbconnect= connect_to_db()
    Candidate_qualifications=pd.read_sql("select candidate_id,university_name,institute_name,aggregate from candidate_qualification where candidate_id in(select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    College_data=pd.read_sql("select * from college_tiers",con=dbconnect)
    Candidate_qualifications["aggregate"]=Candidate_qualifications["aggregate"].apply(lambda x: 0 if  x<0 or x>100 else x)
    Candidate_qualifications["aggregate"]=Candidate_qualifications["aggregate"].apply(lambda x: x*10 if 5<x<10 else x)
    Candidate_qualifications["aggregate"]=Candidate_qualifications["aggregate"].apply(lambda x: 25*x if 0<x<4 else x)

    def Aggregate():
        Unique_candids=Candidate_qualifications[["candidate_id","aggregate"]].groupby("candidate_id").mean()
        Unique_candids["aggregate"]=Unique_candids["aggregate"].apply(lambda x:x-min_cgpa)
        minval=min(Unique_candids["aggregate"])
        maxval=max(Unique_candids["aggregate"])
        Unique_candids["aggregate"]=Unique_candids["aggregate"].apply(lambda x:(x-minval)*100/(maxval-minval))
        Unique_candids=Unique_candids.reset_index()
        return Unique_candids
        
    def University_name():
        stop_words=["of","on","for","the","&","and"]
        unique_candids=list(np.unique(Candidate_qualifications["candidate_id"]))
        candidate_univdict={}
        for i in unique_candids:
            candidate_univdict[i]=Candidate_qualifications[["university_name","institute_name"]][Candidate_qualifications["candidate_id"]==i].values.tolist()
        candidate_univdict={k:list(map(lambda x:list(filter(lambda y:str(y).strip() not in["","None"],x)),v)) for k,v in candidate_univdict.items()}
        candidate_univdict={k: np.unique(list(itertools.chain.from_iterable(v))).tolist() for k,v in candidate_univdict.items()}
        for i in candidate_univdict.keys():
            for j in candidate_univdict[i]:
                 if j in list(map(lambda x: str(x).lower(),College_data["College"].tolist())):
                    candidate_univdict[i][candidate_univdict[i].index(j)]=list(College_data["Tier"][College_data["College"]==j])[0]
                    continue;
                 if j in list(map(lambda x: str(x).lower(),College_data["College"].tolist())):
                    candidate_univdict[i][candidate_univdict[i].index(j)]=list(College_data["Tier"][College_data["Ancronym"]==j])[0]
                    continue;
                 else:
                    Processed_collegedata=pd.DataFrame(College_data["College"].apply(lambda x: [i for i in re.sub("[\.-]"," ",x.lower()).split() if i not in stop_words]))
                    Processed_collegedata["Ancronym"]=College_data["Ancronym"].apply(lambda x: [i for i in re.sub("[\.-]"," ",x.lower()).split() if i not in stop_words])
                    val=[w for w in re.sub("[\.-]"," ",j.lower()).split() if w not in stop_words]
                    Processed_collegedata["College"]=Processed_collegedata["College"].apply(lambda x:(len(set(val).intersection(set(x))))/len(set(val).union(set(x))))
                    Processed_collegedata["Ancronym"]=Processed_collegedata["Ancronym"].apply(lambda x:(len(set(val).intersection(set(x))))/len(set(val).union(set(x))))
                    maxval=Processed_collegedata.max().idxmax()
                    if Processed_collegedata[maxval].idxmax()>0.5:
                        candidate_univdict[i][candidate_univdict[i].index(j)]=College_data.ix[Processed_collegedata[maxval].idxmax(),"Tier"]
                    else:
                        candidate_univdict[i][candidate_univdict[i].index(j)]=3
        
        candidate_univdict={k:100/min(v) for k,v in candidate_univdict.items() if len(v)>0}
        College_score=pd.DataFrame.from_dict(candidate_univdict,orient="index")
        College_score=College_score.reset_index()
        College_score.columns=["candidate_id","Tier_score"]
        return College_score
    result=pd.merge(Aggregate(),University_name(),how="outer",on="candidate_id")
    result=pd.merge(pd.DataFrame(np.unique(Candidate_qualifications["candidate_id"]),columns=["candidate_id"]),result,how="left",on="candidate_id")
    result=result.fillna(0)
    return result
    
#if __name__ == '__main__':
#    University_calculation(270)    
