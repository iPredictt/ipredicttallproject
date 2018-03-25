# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 11:32:09 2017

@author: Shivank.r
"""
import pymysql
import numpy as np
from itertools import groupby
from datetime import datetime
import pandas as pd
import operator
from collections import Counter
import math

def connect_to_db():
    return pymysql.connect(host="54.254.219.225",user="shivankalgo",passwd="shivank@algorithm",db="careerletics_new",charset="utf8mb4") 

def data_read(jobid):
    dbconnect=connect_to_db()
    expdata=pd.read_sql("select * from candidate_experience  where candidate_id in(select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    df2= expdata.copy(deep=True)
    """Removing null values"""
    df2=df2[pd.notnull(df2['start_date'])]
    df2=df2[pd.notnull(df2['end_date'])]
    df2=df2.reset_index(drop=True)
    return(df2)

def promotion(jobid):
    df2=data_read(jobid)
    """Finding Experience Days"""
    date_format = "%Y-%m-%d"
    End_date=list(map(str,df2.end_date))
    Start_date=list(map(str,df2.start_date))
    End_date=list(map(lambda x:(datetime.strptime(x, date_format)), End_date))
    Start_date=list(map(lambda x:(datetime.strptime(x, date_format)), Start_date))
    Exp=list(map(operator.sub,End_date, Start_date))
    Exp= list(map(lambda x:((x.days)/365.0), Exp))
    Exp=list(map(lambda x:(-x) if x<0 else x, Exp))
    Exp=list(map(lambda x:round(x,2), Exp))
    """Exp is also the promotion list"""
    df4 = pd.DataFrame({'Experience': Exp})
    Exp_DF=pd.concat([df2,df4], axis=1)
    Exp_DF=Exp_DF[Exp_DF.Experience!=0]
    return(Exp_DF)

def exp(jobid):
    Exp_DF=promotion(jobid)
    df1=list(Exp_DF.candidate_id)
    df1= pd.DataFrame({'Candidate_Id': df1})
    df2=list(Exp_DF.Experience)
    df2=pd.DataFrame({'Experience': df2})
    exp_DF=pd.concat([df1,df2], axis=1)
    return(exp_DF)
    

def relevant_exp(jobid):
    Exp_DF=promotion(jobid)
    '''Groupby candidate_id and candidate_experience_id'''
    Gp=list(zip(Exp_DF.candidate_id,Exp_DF.candidate_experience_id))
    Gp=[list(j) for i, j in groupby(Gp, lambda x:x[0])]
    """Candidate_experience_id having relevant experience"""
    Candidate_experience_id=list(map(lambda x:x[0][1],Gp))
    df6=list(zip(Exp_DF.candidate_id,Exp_DF.Experience))
    """Groupby Candidate_id and Experience"""
    df8=[list(j) for i, j in groupby(df6, lambda x:x[0])]
    Relevant_Experience= list(map(lambda x:x[0],df8))
    Relevant_Experience_List= list(map(lambda x:x[1],Relevant_Experience))
    """Final_Dataframe having relevant experience only"""
    df3=Exp_DF[(Exp_DF['Experience'].isin(Relevant_Experience_List))&(Exp_DF['candidate_experience_id'].isin(Candidate_experience_id))]
    df1=list(df3.candidate_id)
    df1= pd.DataFrame({'Candidate_Id': df1})
    df2=list(df3.Experience)
    df2=pd.DataFrame({'Relevant_Experience': df2})
    Relevant_Exp=pd.concat([df1,df2], axis=1)
    Relevant_Exp=Relevant_Exp.drop_duplicates(subset='Candidate_Id',keep='first')
    return(Relevant_Exp)



def total_exp(jobid):
    Exp_DF=promotion(jobid)
    df6=list(zip(Exp_DF.candidate_id,Exp_DF.Experience))
    df6=sorted(df6, key=lambda x: x[0])
    "df7 is the list of candidate_id with total experience"""
    df7=[(i, sum(map(lambda x:x[1],j))) for i, j in groupby(df6, lambda x:x[0])]
    df7= list(map(lambda x:(x[0],math.ceil(x[1]*100)/100),df7))
    df1=list(map(lambda x:x[0],df7))
    df1= pd.DataFrame({'Candidate_Id': df1})
    df2=list(map(lambda x:x[1],df7))
    df2= pd.DataFrame({'Total_Experience': df2})
    Total_Exp=pd.concat([df1,df2], axis=1)
    """Total_Experience is also equal to the tenure of the person"""
    return(Total_Exp)

def promo_list(jobid):
    Exp_DF=promotion(jobid)
    df6=list(zip(Exp_DF.candidate_id,Exp_DF.Experience))
    df6=list(map(lambda x:(x[0],math.ceil(x[1]*100)/100),df6))
    df6=sorted(df6, key=lambda x: x[0])
    Candidate_id=list(map(lambda x:x[0],df6))
    Count=list(Counter(Candidate_id).values())
    Candidate_id=list(set(list(map(lambda x:x[0],df6))))
    df7=[(i, sum(map(lambda x:x[1],j))) for i, j in groupby(df6, lambda x:x[0])]
    df7= list(map(lambda x:(x[0],math.ceil(x[1]*100)/100),df7))
    Total_Exp=list(map(lambda x:x[1],df7))
    Promo_l=list(np.divide(Total_Exp,Count))
    Promo_l = list(map(lambda x:math.ceil(x*100)/100,Promo_l))
    df1=pd.DataFrame({'Candidate_Id':Candidate_id})
    df2=pd.DataFrame({'Promotion_Avg': Promo_l})
    df3=pd.DataFrame({'Number_Of_Promotions': Count})
    Promo_df=pd.concat([df1,df2,df3], axis=1)
    return(Promo_df)

def score(jobid):
    Total_Exp=total_exp(jobid)
    l1=list(Total_Exp.Total_Experience)
    l4=pd.DataFrame({'Total_Experience_Score':[65]*len(Total_Exp[Total_Exp.Total_Experience>math.ceil(np.percentile(l1,93.94)*100)/100])})
    df9=Total_Exp[Total_Exp.Total_Experience>math.ceil(np.percentile(l1,93.94)*100)/100]
    df9=df9.reset_index(drop=True)
    df10=pd.concat([df9,l4], axis=1)
    l1=sorted(list(Total_Exp.Total_Experience))
    l1a=sorted([np.percentile(l1,5),np.percentile(l1,10),np.percentile(l1,15),np.percentile(l1,20),np.percentile(l1,25),np.percentile(l1,30),np.percentile(l1,35),np.percentile(l1,40),np.percentile(l1,45),np.percentile(l1,50),np.percentile(l1,55),np.percentile(l1,60),np.percentile(l1,65),np.percentile(l1,70),np.percentile(l1,75),np.percentile(l1,80),np.percentile(l1,85),np.percentile(l1,90),np.percentile(l1,95)])
    l1b=np.array(l1a, dtype=np.float)
    l1c=list(np.gradient(np.gradient(l1b)))
    l1d=[ n for n,i in enumerate(l1c) if i>min(math.pow(0.1,30),0.200) ][0]
    y=(math.ceil((l1a[l1d]+l1a[l1d-1])*100)/100)/2.0
    df11=Total_Exp[Total_Exp.Total_Experience<=y]
    df11=df11.reset_index(drop=True)
    a=(100-0)/((y)-0)
    b=pd.DataFrame({'Total_Experience_Score':list(map(lambda x:math.ceil((a*x)*100)/100,list(df11.Total_Experience)))})
    df12=pd.concat([df11,b], axis=1)
    df13=Total_Exp[(Total_Exp.Total_Experience>y)&(Total_Exp.Total_Experience<=math.ceil(np.percentile(l1,93.94)*100)/100)]
    df13=df13.reset_index(drop=True)
    d=(65-100)/(math.ceil(np.percentile(l1,93.94)*100)/100-y)
    e=100+(d*(-y))
    c=pd.DataFrame({'Total_Experience_Score':list(map(lambda x:math.ceil(((d*x)+e)*100)/100,list(df13.Total_Experience)))})
    df14=pd.concat([df13,c], axis=1)
    Final_Score=pd.concat([df10,df12,df14],axis=0)
    return(Final_Score)

def score2(jobid):
    Relevant_Exp=relevant_exp(jobid)
    l1=list(Relevant_Exp.Relevant_Experience)
    l4=pd.DataFrame({'Relevant_Experience_Score':[65]*len(Relevant_Exp[Relevant_Exp.Relevant_Experience>math.ceil(np.percentile(l1,98.524)*100)/100])})
    df9=Relevant_Exp[Relevant_Exp.Relevant_Experience>math.ceil(np.percentile(l1,98.524)*100)/100]
    df9=df9.reset_index(drop=True)
    df10=pd.concat([df9,l4], axis=1)
    l1=sorted(list(Relevant_Exp.Relevant_Experience))
    l1a=sorted([np.percentile(l1,5),np.percentile(l1,10),np.percentile(l1,15),np.percentile(l1,20),np.percentile(l1,25),np.percentile(l1,30),np.percentile(l1,35),np.percentile(l1,40),np.percentile(l1,45),np.percentile(l1,50),np.percentile(l1,55),np.percentile(l1,60),np.percentile(l1,65),np.percentile(l1,70),np.percentile(l1,75),np.percentile(l1,80),np.percentile(l1,85),np.percentile(l1,90),np.percentile(l1,95)])
    l1b=np.array(l1a, dtype=np.float)
    l1c=list(np.gradient(np.gradient(l1b)))
    l1d=[ n for n,i in enumerate(l1c) if i>min(math.pow(0.1,30),0.050) ][0]
    y=(math.ceil((l1a[l1d]+l1a[l1d-1])*100)/100)/2.0
    df11=Relevant_Exp[Relevant_Exp.Relevant_Experience<=y]
    df11=df11.reset_index(drop=True)
    a=(100-0)/((y)-0)
    b=pd.DataFrame({'Relevant_Experience_Score':list(map(lambda x:math.ceil((a*x)*100)/100,list(df11.Relevant_Experience)))})
    df12=pd.concat([df11,b], axis=1)
    df13=Relevant_Exp[(Relevant_Exp.Relevant_Experience>y)&(Relevant_Exp.Relevant_Experience<=math.ceil(np.percentile(l1,98.524)*100)/100)]
    df13=df13.reset_index(drop=True)
    d=(65-100)/(math.ceil(np.percentile(l1,98.524)*100)/100-y)
    e=100+(d*(-y))
    c=pd.DataFrame({'Relevant_Experience_Score':list(map(lambda x:math.ceil(((d*x)+e)*100)/100,list(df13.Relevant_Experience)))})
    df14=pd.concat([df13,c], axis=1)
    Final_Score2=pd.concat([df10,df12,df14],axis=0)
    return(Final_Score2)

def score3(jobid):
    Promo_df=promo_list(jobid)
    l1=list(Promo_df.Promotion_Avg)
    l4=pd.DataFrame({'Promotion_Score':[65]*len(Promo_df[Promo_df.Promotion_Avg>math.ceil(np.percentile(l1,98.03)*100)/100])})
    df9=Promo_df[Promo_df.Promotion_Avg>math.ceil(np.percentile(l1,98.03)*100)/100]
    df9=df9.reset_index(drop=True)
    df10=pd.concat([df9,l4], axis=1)
    l1=sorted(list(Promo_df.Promotion_Avg))
    l1a=sorted([np.percentile(l1,5),np.percentile(l1,10),np.percentile(l1,15),np.percentile(l1,20),np.percentile(l1,25),np.percentile(l1,30),np.percentile(l1,35),np.percentile(l1,40),np.percentile(l1,45),np.percentile(l1,50),np.percentile(l1,55),np.percentile(l1,60),np.percentile(l1,65),np.percentile(l1,70),np.percentile(l1,75),np.percentile(l1,80),np.percentile(l1,85),np.percentile(l1,90),np.percentile(l1,95)])
    l1b=np.array(l1a, dtype=np.float)
    l1c=list(np.gradient(np.gradient(l1b)))
    l1d=[ n for n,i in enumerate(l1c) if i>min(math.pow(0.1,30),0.030) ][0]
    y=(math.ceil((l1a[l1d]+l1a[l1d-1])*100)/100)/2.0
    """Here I have calculated the double derivative and found the value where firstly it is greater than a certain threshold(0.030)"""
    df11=Promo_df[Promo_df.Promotion_Avg<=y]
    df11=df11.reset_index(drop=True)
    a=(100-0)/(y-0)
    b=pd.DataFrame({'Promotion_Score':list(map(lambda x:math.ceil((a*x)*100)/100,list(df11.Promotion_Avg)))})
    df12=pd.concat([df11,b], axis=1)
    df13=Promo_df[(Promo_df.Promotion_Avg>y)&(Promo_df.Promotion_Avg<=math.ceil(np.percentile(l1,98.03)*100)/100)]
    df13=df13.reset_index(drop=True)
    d=(65-100)/(math.ceil(np.percentile(l1,98.03)*100)/100-y)
    e=100+(d*(-y))
    c=pd.DataFrame({'Promotion_Score':list(map(lambda x:math.ceil(((d*x)+e)*100)/100,list(df13.Promotion_Avg)))})
    df14=pd.concat([df13,c], axis=1)
    Final_Score3=pd.concat([df10,df12,df14],axis=0)
    return(Final_Score3)
    


def Final(jobid):
    dbconnect=connect_to_db()
    expdata=pd.read_sql("select Candidate_id from candidate_experience  where candidate_id in(select candidate_id from master_id where job_id="+str(jobid)+")",con=dbconnect)
    expdata=expdata.drop_duplicates(subset=None, keep='first', inplace=False)
    try:
        Final_Score=score(jobid)
    except:
        Final_Score=pd.DataFrame(expdata["Candidate_id"])
        Final_Score["Total_Experience_Score"]=0
        Final_Score.columns=["Candidate_Id","Total_Experience_Score"]
    try:
        Final_Score2=score2(jobid)
    except: 
        Final_Score2=pd.DataFrame(expdata["Candidate_id"])
        Final_Score2["Relevant_Experience_Score"]=0
    try:
        Final_Score3=score3(jobid)
    except:
        Final_Score3=pd.DataFrame(expdata["Candidate_id"])
        Final_Score3["Promotion_Score"]=0
    Candidate_id=list(Final_Score.Candidate_Id)
    Tot_Exp_Score= list(Final_Score.Total_Experience_Score)
    Rel_Exp_Score= list(Final_Score2.Relevant_Experience_Score)
    Prom_Score= list(Final_Score3.Promotion_Score)
    Result =  pd.DataFrame({'Candidate_id':Candidate_id,'Total_Exp':Tot_Exp_Score,'Rel_Exp_Score':Rel_Exp_Score,'Promotion_Score':Prom_Score})
    Result=pd.merge(expdata,Result,how="left",on="Candidate_id")
    Result=Result.fillna(0)
    return Result


