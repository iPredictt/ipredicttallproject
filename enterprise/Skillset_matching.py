# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 17:15:21 2017

@author: Shivank.r
"""
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from nltk.corpus import wordnet as wn
from itertools import product
import pymysql
import itertools



def connect_to_db():
    return pymysql.connect(host="54.254.219.225",user="shivankalgo",passwd="shivank@algorithm",db="careerletics_new",charset="utf8mb4") 


def Skillset_scores(jobid):
    dbconnect=connect_to_db()
    """Stop Words"""
    stoplist = set('for a of the and to in skills skill as core basic'.split())
    """Jd Skills Query"""
    required_skills = list(pd.read_sql("select A.job_id,B.name from listing_skill A,master_skills B where A.skill_id=B.skill_id and A.job_id="+str(jobid),con=dbconnect)["name"])
    required_skills = list(map(lambda x:' '.join(filter(lambda y:y not in stoplist,x.lower().split())),required_skills))
    """Candidate Skills"""
    cand_skill=pd.read_sql("select A.candidate_id,B.name from candidate_skill A ,master_skills B where A.master_skill_id=B.Skill_id and candidate_id in ("+"select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    cand_skill.columns=["candidate_id","skills"]
    skill_data=pd.DataFrame(cand_skill.candidate_id.unique(),columns=["candidate_id"])
    skill_data["skills"]=skill_data["candidate_id"].apply(lambda x:list(cand_skill.skills[cand_skill.candidate_id==x]))
    skill_data.skills = skill_data.skills.apply(lambda x:list(filter(lambda y:str(y).strip() not in ['','None','nan'],x)))
    skill_data.skills = skill_data.skills.apply(lambda x:list(map(lambda y:' '.join(list(filter(lambda z:z not in stoplist,y.lower().split()))),x)))
    skill_data.skills = skill_data.skills.apply(lambda x:list(filter(lambda y:y.strip() not in ['','None','nan'],x)))
    
    def similar(a, b):
        return (SequenceMatcher(None, a, b).ratio())
        
    def similar_better(w1,list1):
        return(max(similar(w1,x) for x in list1))
    
    
    def compare(word1, word2):
        ss1 = wn.synsets(word1)
        ss2 = wn.synsets(word2)
        list1 = [s1.wup_similarity(s2) for s1,s2 in product(ss1, ss2)]
        try:
            return(max(x for x in list1 if x is not None))
        except ValueError:
            return(0)
    
    def compare_better(w1,list1):
        return(max(semetric_sem_sim(w1,x) for x in list1))
     
    def sem_sim(a,b):
        a = a.split()
        b= b.split()
        score = 0.0
        count =0.0
        for word1 in a:
            best_score = max([compare(word1,word2) for word2 in b])
            if best_score is not None:
                score += best_score
                count +=1
        score /= count
        return(score) 
    
    def semetric_sem_sim(a,b):
        return (sem_sim(a,b)+sem_sim(b,a))/2 
        
    Unique_skills=list(map(lambda x: str(x),list(np.unique(list(itertools.chain.from_iterable(list(skill_data["skills"])))))))
    
    def desired(Skill_keyword):
        check =[]
        for i in Unique_skills:
            if similar(Skill_keyword,i)>0.8:
                check.append(i)
        return(check)
    
    valuable_skills=[]
    for i in required_skills:
        check=desired(i)
        valuable_skills.extend(check)
        Unique_skills=list(set(Unique_skills)-set(check))
    
    skill_data["skills"]=skill_data["skills"].apply(lambda x:(sum(list(map(lambda x: 1 if x in valuable_skills else 0,x)))/len(x)))
    skill_data.columns=["candidate_id","skill_score"]
    minval=min(skill_data["skill_score"])
    maxval=max(skill_data["skill_score"])
    skill_data["skill_score"]=skill_data["skill_score"].apply(lambda x:(x-minval)*100/(maxval-minval))
    skill_data["skill_score"]=skill_data["skill_score"].apply(lambda x:round(x,2))
    return  skill_data

