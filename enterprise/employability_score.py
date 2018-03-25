# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 12:15:35 2017

@author: Shivank.r
Employability Score Calculation
Specified inputs are Job_id,Candiadates_id,Host_Ip,User Credentials like Username,Password,Database_Schema 
"""
import numpy as np
import pymysql
import pandas as pd
import sys
sys.path.insert(0,"/home/shivank/shivankalgo/scorealgo/enterprise")
import class_file
import json


def connect_to_db():
    return pymysql.connect(host="54.254.219.225",user="shivankalgo",passwd="shivank@algorithm",db="careerletics_new",charset="utf8mb4") 

#dbconnect=connect_to_db()
def Qualification_determination(jobid,dbconnect):
    Qualifications=pd.read_sql("select candidate_id,university_name,degree,aggregate from candidate_qualification where candidate_id in(select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    University_data=pd.read_sql("select `University Name`,`Model_Rank` from university_data",con=dbconnect)
    Qual_class=class_file.qualification_score(Qualifications,University_data)
    return Qual_class.calculator()
    
def Quality_exp(jobid,dbconnect):
    experience=pd.read_sql("select candidate_id,company_name,start_date,end_date from candidate_experience  where candidate_id in(select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    company_master=pd.read_sql("select TITLE from company_master",con=dbconnect)
    Qual_exp=class_file.Quality_Exp(experience,company_master)
    return Qual_exp.percentile_determiner()
    
def Creating_cluster(dbconnect,eps,number_clusters,threshold):
    skill_table=pd.read_sql("select candidate_id,master_skill_id from candidate_skill",con=dbconnect)
    master_skills=pd.read_sql("select skill_id,name from master_skills",con=dbconnect)
    master_skills.index=list(master_skills.skill_id)
    skills=list(map(lambda x:x.lower(),list(master_skills["name"])))
    skill_table["master_skill_id"]=skill_table.master_skill_id.apply(lambda x: master_skills.name[x].lower())
    mat=pd.DataFrame(np.zeros((len(skill_table.candidate_id.unique()),len(skills))))
    mat.columns=skills
    mat.index=skill_table.candidate_id.unique()
    for i in mat.index:
        mat.ix[i,list(skill_table.master_skill_id[skill_table.candidate_id==i])]=1
    rock=class_file.hclustering(mat,eps, number_clusters, threshold)
    a=rock.get_clusters()
    a=list(map(lambda x:list(map(lambda y:int(y),x)),a))
    a=dict(zip(range(len(a)),a))
    with open('data.json', 'w') as fp:
        json.dump(a, fp)
    return None

def Skill_score(jobid,dbconnect):
    """cluster1 upload"""
    with open('/home/shivank/shivankalgo/scorealgo/enterprise/data.json') as data_file:    
        cluster1 = json.load(data_file)
    cluster1=list(cluster1.values())
    
    skill_table=pd.read_sql("select A.candidate_id,B.name from candidate_skill A ,master_skills B where A.master_skill_id=B.Skill_id",con=dbconnect)
    cand_skill=pd.DataFrame(skill_table.candidate_id.unique(),columns=["candidate_id"])
    cand_skill["skills"]=cand_skill["candidate_id"].apply(lambda x:list(skill_table.name[skill_table.candidate_id==x]))
    cand_skill["skills"]=cand_skill["skills"].apply(lambda x: list(map(lambda y:y.title(),x)))
    cand_skill.index=cand_skill["candidate_id"]
    del cand_skill["candidate_id"]
    
    job_array=list(pd.read_sql("select  name from master_skills where skill_id in (select skill_id from listing_skill where job_id="+str(jobid)+")",con=dbconnect)["name"].apply(lambda x:x.title()))
    
    candidate_id=pd.read_sql("select candidate_id from master_id where job_id="+str(jobid),dbconnect)["candidate_id"].tolist()
    cand_skills=cand_skill.loc[candidate_id]
    cand_skills=cand_skills.dropna()
    
    def jaccard_coeff(c,d):
        return len(set(c).intersection(set(d)))/len(set(c).union(set(d)))
    
    def cd_prediction():
        jdcluster1=list(map(lambda x: np.mean(list(map(lambda y: jaccard_coeff(job_array,cand_skill.loc[y]["skills"]),x))),cluster1))
        return jdcluster1.index(max(jdcluster1))
    
    jd_cluster=cluster1[cd_prediction()]
    cand_skills["skills"]=cand_skills["skills"].apply(lambda x: np.mean(list(map(lambda y: jaccard_coeff(x,cand_skill.loc[y]["skills"]),jd_cluster))))
    cand_skills["skills"]=cand_skills["skills"].apply(lambda x: min(x*800,100))
    
    return cand_skills["skills"]
    
def final_score(jobid,connect_to_db):
    dbconnect=connect_to_db()
    a=pd.concat([Qualification_determination(jobid,dbconnect),Quality_exp(jobid,dbconnect),Skill_score(jobid,dbconnect)],axis=1)
    dbconnect.close()
    a.columns=["education_score_user","experience_score_user","skillset_score_user"]
    a=a.fillna(0)
    a["profile_score"]=(a.education_score_user+a.experience_score_user+a.skillset_score_user)/3.0
    a["skillset_score_e"]=a.skillset_score_user*100/max(a.skillset_score_user)
    a["education_score_e"]=a.education_score_user*100/max(a.education_score_user)
    a["experience_score_e"]=a.experience_score_user*100/max(a.experience_score_user)
    a=a.fillna(0)
    a["employability_score_e"]=(a.education_score_e+a.experience_score_e+a.skillset_score_e)/3.0
    a["employability_score_e"]=a["employability_score_e"]*100/max(a["employability_score_e"])
    a=a.applymap(lambda x:round(x,2))
    a=a.reset_index()
    a=a.rename(columns = {'index':'candidate_id'})
    return a
  
    
   
    
    
