# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 11:11:05 2017

@author: ipredictt
"""

import xml.etree.cElementTree as ET
import pickle
from nltk.util import ngrams
import os
import requests
import json

def parser(data64,filename):
    url="http://rest.rchilli.com/RChilliParser/Rchilli/parseResumeBinary"
    userkey='0001111'
    version = "7.0.0"
    subuserid = "test"
    headers = {'content-type': 'application/json'}
    body =  """{"filedata":\""""+data64+"""\","filename":\""""+ filename+"""\","userkey":\""""+ userkey+"""\",\"version\":\""""+version+"""\",\"subuserid\":\""""+subuserid+"""\"}"""
    response = requests.post(url,data=body,headers=headers)    
    strData=response.text 
    resume = json.loads(strData)

    alphabet=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    def gender_features(word):
        '''feature_set'''
        features={}
        word=word.split()[0].lower()
        wor=word.replace(' ','')
        bigr=list(ngrams(list(wor),2))
        trigr=list(ngrams(list(wor),3))
        big=[''.join(i) for i in bigr]    
        tri=[''.join(i) for i in trigr]
        
        fname=os.path.realpath("/home/shivank/shivankalgo/scorealgo/enterprise/parserpickle/bigram_pickle")
        file1=open(fname,"rb")
        bigram_list=pickle.load(file1)    
        fname2=os.path.realpath("/home/shivank/shivankalgo/scorealgo/enterprise/parserpickle/trigram_pickle")
        file2=open(fname2,"rb")
        trigram_list=pickle.load(file2)
        for b in big:
            features['contains_bigram({})'.format(b)] = (b in bigram_list)
        for t in tri:
            features['contains_trigram({})'.format(t)] = (t in trigram_list)
        features['contains_last_letter({})'.format(wor[-1])] = (wor[-1] in alphabet)
        return features

    def gender_predict(name):
        '''load pickle file'''
        fname=os.path.realpath('/home/shivank/shivankalgo/scorealgo/enterprise/parserpickle/Gender_model')
        file=open(fname,"rb")
        classifier=pickle.load(file)
        file.close()

        '''predict gender'''
        try:
            return classifier.classify(gender_features(name))
        except:
            return 'No Gender Found'
     
    '''entities extraction from the parsed resume'''
    email = resume['ResumeParserData']['Email']
    dob = resume['ResumeParserData']['DateOfBirth']
    first_name = resume['ResumeParserData']['FirstName']
    middle_name = resume['ResumeParserData']['Middlename']
    last_name = resume['ResumeParserData']['LastName']
    fullname = resume['ResumeParserData']['FullName']
    contact_no = resume['ResumeParserData']['Mobile']
    location = resume['ResumeParserData']['City']
    try:
        skills = list(map(lambda x : x['Skill'],resume['ResumeParserData']['SkillKeywords']['SkillSet']))
    except:
        skills = []
    def experience_generation(list_exp):
        exp = {}
        try:
            exp['designation'] = list_exp['JobProfile']['Title']
        except:
            exp['designation'] = ' '
        try:
            exp['Employer'] = list_exp['Employer']
        except:
            exp['Employer'] = ' '
        try:
            exp['EndDate'] = list_exp['EndDate']
        except:
            exp['EndDate'] = ' '
        try:
            exp['StartDate'] = list_exp['StartDate']
        except:
            exp['StartDate'] =  ' '
        try:
            exp['location'] = list_exp['JobLocation']['EmployerCity']
        except:
            exp['location'] = ' '
        return exp

    def education_generation(list_exp):
        exp = {}
        try:
            exp['Aggregate'] = list_exp['Aggregate']['MeasureType'] + ': ' + list_exp['Aggregate']['Value']
        except:
            exp['Aggregate'] = ' '
        try:
            exp['degree_type'] = list_exp['Degree']
        except:
            exp['degree_type'] = ' '
        try:
            exp['location'] = list_exp['Institution']['City']
        except:
            exp['location'] = ' '
        try:
            exp['StartDate'] = list_exp['StartDate']
        except:
            exp['StartDate'] =  ' '
        try:
            exp['institute'] = list_exp['Institution']['Name']
        except:
            exp['institute'] = ' '
        try:
            exp['end_date'] = list_exp['EndDate']
        except:
            exp['end_Date'] = ' '
        return exp

    experience = list(map(experience_generation,resume['ResumeParserData']['SegregatedExperience']['WorkHistory']))
    education = list(map(education_generation,resume['ResumeParserData']['SegregatedQualification']['EducationSplit']))
    if fullname == '':
        if (first_name != '') & (last_name != ''):
            gender = gender_predict(first_name + ' ' + last_name)
        elif (first_name != '') & (last_name == ''):
            gender  = gender_predict(first_name)
        else:
            gender = gender_predict(fullname)
    else:
        gender = gender_predict(fullname)


    '''xml formation code'''

    root = ET.Element("root")
    header = ET.SubElement(root,"header")
    personal_details = ET.SubElement(header,"personaldetails")
    ET.SubElement(personal_details, "fullname").text = fullname
    ET.SubElement(personal_details, "firstname").text = first_name
    ET.SubElement(personal_details, "lastname").text = last_name
    ET.SubElement(personal_details, "mobile").text = contact_no
    ET.SubElement(personal_details, "location").text = location
    ET.SubElement(personal_details, "dateofbirth").text = dob
    ET.SubElement(personal_details, "email_id").text = email
    ET.SubElement(personal_details, "gender").text = gender

    experience_1=ET.SubElement(header,"experience")
    for i in range(len(experience)):
        experience_node = ET.SubElement(experience_1, "Experience"+str(i+1))
        ET.SubElement(experience_node, 'employer').text = experience[i]['Employer']
        ET.SubElement(experience_node, 'enddate').text = experience[i]['EndDate']
        ET.SubElement(experience_node, 'startdate').text = experience[i]['StartDate']
        ET.SubElement(experience_node, 'designation').text = experience[i]['designation']
        ET.SubElement(experience_node, 'location').text = experience[i]['location']

    education_1=ET.SubElement(header,"education")
    for i in range(len(education)):
        education_node = ET.SubElement(education_1, "Education"+str(i+1))
        ET.SubElement(education_node, 'institute').text = education[i]['institute']
        ET.SubElement(education_node, 'aggregate').text = education[i]['Aggregate']
        ET.SubElement(education_node, 'enddate').text = education[i]['end_date']
        ET.SubElement(education_node, 'startdate').text = education[i]['StartDate']
        ET.SubElement(education_node, 'degree').text = education[i]['degree_type']
        ET.SubElement(education_node, 'location').text = education[i]['location']


    skills_1=ET.SubElement(header,"skills")
    skills_1.text = ', '.join(skills)
    return ET.tostring(root)
