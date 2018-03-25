# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 21:31:04 2017

@author: Shivank.r
"""
import pandas as pd
import funnel_filter
import Skillset_matching
import Experience_Scores
import jd_similarity

def Combine_scores(jobid):
    exp_score=Experience_Scores.Final(jobid)
    exp_score.columns=["candidate_id","promotion_score","relevant_exp_score","total_exp_score"]
    skill_score=Skillset_matching.Skillset_scores(jobid)
    education_score=jd_similarity.University_calculation(jobid)
    education_score.columns=["candidate_id","aggregate_score","tier_score"]
    #education_score['aggregate_score']=education_score["aggregate_score"].apply(lambda x:round(x,2))
    filtrd_candlist=list(map(lambda x: int(x),funnel_filter.main(jobid)))
    result=pd.merge(exp_score,skill_score,how="left",on="candidate_id")
    result=pd.merge(result,education_score,how="left",on="candidate_id")
    result=result.fillna(0);result=result.reset_index(drop=True);
    result["employability_score"]=result.promotion_score+result.relevant_exp_score+result.total_exp_score+result.tier_score+result.aggregate_score+result.skill_score
    result["employability_score"]=result["employability_score"].apply(lambda x:x/6.0)
    result["employability_score"][result["candidate_id"].isin(list(set(result["candidate_id"])-set(filtrd_candlist)))]=0
    result["employability_score"]=result["employability_score"].apply(lambda x:round(x,2))
    return result

#if __name__ == '__main__':
#    Combine_scores(270)    
