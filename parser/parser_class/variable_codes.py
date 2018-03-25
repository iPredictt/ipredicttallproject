# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 12:30:58 2017

@author: Shivank.r
Compiled Functions Resume Parser 
Name Location Gender Email Dob Phone
"""
import re
import pickle
import nltk
import itertools
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import pandas as pd
from nltk.tokenize import sent_tokenize
from itertools import product
import en_core_web_sm 
nlp = en_core_web_sm.load()

def spacy_entities(f):
    doc = nlp(f)
    temp=[]
    for entity in doc.ents:
        temp.append([entity.text, entity.label_])
    return temp

def extract_candidate_chunks(text, grammar=r'KT: {<NNP>+?}'):
    
    # exclude candidates that are stop words or entirely punctuation
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                    for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(word for word, pos, chunk in group) for key, group in itertools.groupby(all_chunks, lambda x:x[2] != 'O') if key]

    return candidates
    
def probablity(name):
    file=open("/home/shivank/parser/parser_class/Probabs.pkl","rb")
    unigrams=pickle.load(file)
    file.close()
    if len(name.strip())==0:
        return 0
    name=name.split()
    return sum(list(map(lambda x:unigrams[x] if x in unigrams.keys() else 0,name)))/len(name)
    
def names_extractor(text):
    text_split=re.sub("\t","\n",text)
    text_split=re.sub(r"[-:,\d]","",text_split)
    text_split=re.sub('\s\s+',"\n",text_split).splitlines()
    level1_farzi=["cv","page","name","summary","objective","resume","curriculum","vitae",'résumé',"education","qualifications","skills","academics","experience","career","title","personal","details"]
    level2_farzi=["mobile","email","phone",'contact',"address","location","current"]
    for i in text_split[: min(5,len(text_split))]:
        for z in level1_farzi:
            i=re.sub(z,"",i,flags=re.I) 
        for z in level2_farzi:
            i=re.sub(z+".*","",i,flags=re.I) 
        i=re.sub(" of "," ",i)
        if len(i.split())>4 or len(i.split())==0 or len(i)<4:
            continue
        if re.sub("^[A-z. ]+$","",i.strip())=="" and all(list(map(lambda x:x[0].isupper(),i.strip().split()))) and probablity(i)<6*10**-4:
            return i.strip()
    #list(filter(lambda x:))
    out=extract_candidate_chunks(text, grammar=r'KT: {<NNP> <NNP> <NNP>?}')
    probabs=list(map(lambda x: probablity(x),out))
    if len(probabs)>0:
        return out[probabs.index(min(probabs))]
    return ''

def location_parse(resume):
    master_city = pd.read_excel('/home/shivank/parser/parser_class/final_cities_list.xlsx')
    city_list = list(set(master_city['City'].apply(lambda x : x.lower())))
    cities_population = pd.read_csv('/home/shivank/parser/parser_class/cities_by_population.csv')
    sorted_cities = list(cities_population['city'].apply(lambda x : x.lower()))
    x = resume.lower()
    def get_ngrams(text, n ):
        n_grams = ngrams(word_tokenize(text), n)
        return [' '.join(grams) for grams in n_grams]
    
    def grams_generation(grams_list,tokenize_data):
        final_grams_list = []
        if len(tokenize_data) != 0:
            for i in product(grams_list,tokenize_data):
                final_grams_list.append(get_ngrams(i[1],i[0]))
            final_grams_list = list(itertools.chain.from_iterable(final_grams_list))
            final_grams_list = list(map(lambda x : re.sub('[\:\&\,\)\(\-]',' ',x),final_grams_list))
            final_grams_list = list(map(lambda x : re.sub('[^\x00-\x7F]','', x),final_grams_list))
            final_grams_list = list(map(lambda x : re.sub('\.',' ',x).strip(),final_grams_list))
            return final_grams_list
        else:
            return final_grams_list
    tokenize_data = sent_tokenize(x)
    final_list = grams_generation([1,2,3],tokenize_data)
    locations = list(set(final_list).intersection(set(city_list)))
    if len(locations) == 0:
        return ''
    if len(locations) == 1:
        return locations[0]
    
    def check_position_locations(tokenize_data):
        loc_list = ['location','place']
        present_list = ['present address','current location','current address','present','postal address','current company']
        def product_iterations(location_list,tokenize_data,grams_list):
            count = 0
            extract_list = []
            for y in product(location_list,tokenize_data):
                if count < (len(tokenize_data)- 1):
                    if y[0] in y[1]:
                        extract_list.append(y[1])
                        extract_list.append(tokenize_data[count + 1])
                    count += 1
                elif count == len(tokenize_data) - 1:
                    if y[0] in y[1]:
                        extract_list.append(y[1])
                    count = 0
            grams_word = grams_generation(grams_list,list(set(extract_list)))
            return grams_word
        final_word = product_iterations(present_list,tokenize_data,[1,2,3])
        final_word1 = product_iterations(loc_list,tokenize_data,[1,2,3])
        location = list((set(city_list).intersection(set(final_word))))
        if len(location)==0:
            location=list((set(city_list).intersection(set(final_word1))))
        return location
    position_locations = check_position_locations(tokenize_data)
    if len(position_locations) == 1:
        return position_locations[0]
    if len(position_locations) > 1:
        locations = position_locations
    word_tokenized_data = ' '.join(list(itertools.chain.from_iterable(list(map(lambda x : word_tokenize(x.lower()),tokenize_data)))))
    split_data = word_tokenized_data[0:75] + word_tokenized_data[-75:]
    final_locations = list(filter(lambda x : x in split_data,locations))
    if len(final_locations) == 0:
        final_locations = locations
    if len(final_locations) == 1:
        return final_locations[0]
    locations_list = ['delhi','gurgaon','gurugram','noida','hyderabad','mumbai','kolkata','calcutta',
                              'chennai','madras','secunderabad','ahmedabad','jaipur','bangalore','pune',
                              'vishakapatnam','vizaq','bhubaneswar','lucknow','indore']
    filter_locations = list(filter(lambda x : x in locations_list,final_locations))
    if len(filter_locations) == 1:
        return filter_locations[0]
    if len(filter_locations) > 1:
        final_locations = filter_locations
    final_locations_list = ['delhi','hyderabad','mumbai','kolkata','chennai','pune','bangalore','noida','gurgaon']
    filter_locations = list(filter(lambda x : x in final_locations_list,final_locations))
    if len(filter_locations) == 1:
        return filter_locations[0]
    elif len(filter_locations) > 1:
        final_locations_1 = filter_locations
        start_index_dict = {i : [m.start() for m in re.finditer(i,x)] for i in final_locations_1}
        reversed_dict = {int(val): key for key in start_index_dict for val in start_index_dict[key]}
        sorted_list = sorted(reversed_dict.items(),key = lambda x : x[0])
        return sorted_list[0][1]
    else:
        population_sorted = list(filter(lambda x : x in sorted_cities,final_locations))
        if len(population_sorted) > 0:
            return population_sorted[0]
        else:
            start_index_dict = {i : [m.start() for m in re.finditer(i,x)] for i in final_locations}
            reversed_dict = {int(val): key for key in start_index_dict for val in start_index_dict[key]}
            sorted_list = sorted(reversed_dict.items(),key = lambda x : x[0])
            return sorted_list[0][1]


def email(string):
	email_id=re.findall( r'([\w._]+@[\w.]+)', string)
	if email_id:
		return ("/".join(email_id))
	else:
		return ""

def mobile(string):
	mobile_no=re.findall(' \+?\d[- \d]{3,9}[\d]{4,10}\d',string)
	if mobile_no:
		return("/".join(mobile_no))
	else:
		return ""

def dob(resume_string):
    for i in resume_string.split("\n"):
        t=re.match("([Dd][Aa][tT][eE][- ]?[oO][Ff][- ]?[Bb][iI][rR][Tt][hH][:\- ]*\D(?:\d{2}(?:[ ]*|th|rd))(?:\s)*(?:[\/])*(?:[jJ]an(?:uary)?|[fF]eb(?:ruary)?|[mM]ar(?:ch)?|[aA]pr(?:il)?|[mM]ay?|[jJ]une?|[jJ]uly?|[aA]ug(?:ust)?|[sS]ep(?:t(?:ember)?)?|[oO]ct(?:ober)?|[nN]ov(?:ember)?|[Dd]ec(?:ember)?)(?:\s|,)(?:[\s]*)(?:\d{4}))|([Dd]\.?[Oo]\.?[Bb][:\- ]*\D(?:\d{2}(?:[ ]*|th|rd))(?:\s)*(?:[jJ]an(?:uary)?|[fF]eb(?:ruary)?|[mM]ar(?:ch)?|[aA]pr(?:il)?|[mM]ay?|[jJ]une?|[jJ]uly?|[aA]ug(?:ust)?|[sS]ep(?:t(?:ember)?)?|[oO]ct(?:ober)?|[nN]ov(?:ember)?|[Dd]ec(?:ember)?)(?:\s|,)(?:[\s]*)(?:\d{4}))|([Dd][Aa][tT][eE][- ]?[oO][Ff][- ]?[Bb][iI][rR][Tt][hH][:\- ]*.*\d)|([Dd]\.?[Oo]\.?[Bb][:\- ]*.*\d)",i)
        if t:
            return re.findall(r"\D(?:\d{2}(?:[ ]*|th|rd))(?:\s)*(?:[\/])*(?:[jJ]an(?:uary)?|[fF]eb(?:ruary)?|[mM]ar(?:ch)?|[aA]pr(?:il)?|[mM]ay?|[jJ]une?|[jJ]uly?|[aA]ug(?:ust)?|[sS]ep(?:t(?:ember)?)?|[oO]ct(?:ober)?|[nN]ov(?:ember)?|[Dd]ec(?:ember)?)(?:\s|,)(?:[\s]*)(?:\d{4}))|([Dd]\.?[Oo]\.?[Bb][:\- ]*\D(?:\d{2}(?:[ ]*|th|rd))(?:\s)*(?:[jJ]an(?:uary)?|[fF]eb(?:ruary)?|[mM]ar(?:ch)?|[aA]pr(?:il)?|[mM]ay?|[jJ]une?|[jJ]uly?|[aA]ug(?:ust)?|[sS]ep(?:t(?:ember)?)?|[oO]ct(?:ober)?|[nN]ov(?:ember)?|[Dd]ec(?:ember)?)(?:\s|,)(?:[\s]*)(?:\d{4}))|([Dd][Aa][tT][eE][- ]?[oO][Ff][- ]?[Bb][iI][rR][Tt][hH][:\- ]*.*\d)|([Dd]\.?[Oo]\.?[Bb][:\- ]*.*\d",t.group(0))[0]
    return ""
      
def skills(skill):
    skills_output=[]
    skill_data=pd.read_csv("/home/shivank/parser/parser_class/skill_master.csv")["Skills"].apply(lambda x:str(x).lower()).tolist()
    skill["tagged_data"]=list(itertools.chain.from_iterable(list(map(lambda x: list(map(lambda y:" ".join(y),x)),skill["tagged_data"]))))
    skill["tagged_para"]=list(itertools.chain.from_iterable(skill["tagged_para"]))
    skills_list=" ".join(list(itertools.chain.from_iterable(list(skill.values())))).lower().strip()
    for i in skill_data:
        if i in skills_list:
            skills_output.append(i)
    return skills_output
        
        
#def education(education):
    
    
    
  
def experience(experience_data):
    
    keys=["Tenure","Organization Name","Organizaton","Year Of Experience","Sr. No",\
          "Designation/Role","Sr No","Date Of Joining","S. No","From Year","Year","Tenure (Yr.)","To Date"\
          ,"Role/Designation","Role/Title","Name Of Company","Job Role","Duration","Designation","To Year","Organisation",\
          "Roles","Work Duration","Period","Dates","Employer Name","Last Designation","Total Experience","Software Tools",\
          "Period In Years","Job Title","Effective Date","Employer","Organization","Name Of The Organization",
          "Time Period","Company Name","End Date","Sr.No.","Time Duration","From","Profile","Yrs. Exp.",\
          "Position","Company","From (Date)","To","Last Designation Held","From Date","Date","To (Date)"]
    keys_dict={"Company":["Organization Name","Organizaton","Name Of Company","Organisation","Employer Name","Employer","Organization","Name Of The Organization","Company Name","Company"],"Designation":["Designation/Role","Role/Designation","Role/Title","Job Role","Designation","Last Designation","Job Title","Position","Last Designation Held"],"Start Date":["Date Of Joining","From Year","Effective Date","From","From (Date)","From Date","Date","Start Date"],"End Date":["Tenure","Year Of Experience","Year","To Date","Duration","To Year","Work Duration","Period","Dates","Total Experience","Period In Years","Time Period","End Date","Time Duration","Yrs. Exp.","To","To (Date)"]}
#    relation_key={"Company":["Employer"],"Start_date":[],"End_date":["Duration"],"Designation":["Designation"]}
    
    final_data=pd.DataFrame(columns=["Company","Designation","Start Date","End_Date"])
    if len(experience_data["tagged_data"])>=0:
        tagged_data=list(filter(lambda x:  set(list(map(lambda y: y.title(),x[0]))).intersection(set(keys)),experience_data["tagged_data"] ))
        if len(tagged_data)>=1:
            tagged_data=tagged_data[0]
            fst_row=list(map(lambda x: x.title(),tagged_data[0]))
            fst_column=list(map(lambda x: x.title(),list(map(lambda x:x[0],tagged_data )) ))  
            if len(set(fst_row).intersection(set(keys)))>len(set(fst_column).intersection(set(keys))):
                tagged_data=pd.DataFrame(tagged_data[1:],columns=tagged_data[0])
            if len(set(fst_row).intersection(set(keys)))<len(set(fst_column).intersection(set(keys))):
                tagged_data=list(map(list, zip(*tagged_data)))
                tagged_data=pd.DataFrame(tagged_data[1:],columns=tagged_data[0])
            final_data=pd.DataFrame(columns=["Company","Designation","Start Date","End Date"])
            for i in tagged_data.columns:
                for j in keys_dict.keys():
                    if i.title() in keys_dict[j]:
                        final_data[j]=tagged_data[i]
            final_data=final_data.to_dict(orient="records")   
            return final_data
    elif len(experience_data["tagged_para"])>=0:
        des_data=pd.read_csv("/home/shivank/parser/parser_class/designation_master.csv",encoding="iso-8859-1")["designation_name"].tolist()
        exp=experience_data["tagged_para"]
        exp1=list(map(lambda x: "\n".join(x).lower(),exp))
        temp_list=[0]*len(exp1)
        for i in des_data:
            for j,val in enumerate(exp1):
                if i in val:
                    temp_list[j]=temp_list[j]+1
        exp=exp[temp_list.index(max(temp_list))]
        exp=list(filter(lambda x: x.strip()!="",exp))
        exp=list(map(lambda x:x.lower(),exp))
        designation = []
        for i,c in enumerate(exp):
            des_filter = list(filter(lambda x : x in c.lower(),des_data))
            if len(des_filter) != 0:
                designation.append((max(des_filter,key = len),i))
        data_extracted=[]
        for i in designation:
            if i[1]==0:
                data_extracted.append([""]+exp[i[1]:i[1]+2])
            else:
                data_extracted.append(exp[i[1]-1:i[1]+2])
        
        spacy_extraction=list(map(lambda x: list(map(lambda y:spacy_entities(y),x)),data_extracted))
        dates_list=list(map(lambda y: list(itertools.chain.from_iterable(y)),spacy_extraction))
        dates_list=list(map(lambda t:list(filter(lambda z: z[1]=="DATE",t)),dates_list))
        dates_list=list(map(lambda t:list(map(lambda y:y[0] ,t)) if len(t)>0 else [],dates_list))
        for i,k in enumerate(dates_list):
            for v in k:
                for q in dates_list[i+1:]:
                    if v in q:
                        q.remove(v)
        dates_list = list(map(lambda x : ' '.join(x),dates_list))
        #dates=[x[0] for x in itertools.groupby(dates)]
        final_data = pd.DataFrame([['',designation[i][0],"",dates_list[i]] for i in list(range(len(designation)))],columns = ["Company","Designation","Start Date","End Date"])
        final_data=final_data.to_dict(orient="records") 
        return final_data
    final_data=final_data.to_dict(orient="records")    
    return final_data
#    if len(experience["tagged_para"])>=0:
#        tagged_para=experience["tagged_para"][0]
#        relations=list(map(lambda y: y.split(":-") if ":-" in y else y.split(":"),list(itertools.chain.from_iterable(list(map(lambda x:re.findall("((?:[A-z][A-z\s\’\-\.]+)(?::-|:)(?:[\s]*(?:[\w\\\/\-\\@+\'\.\,\(\)]+[\s]?)+\s?))",x),tagged_para ))))))
#        c=0
#        for i,x in enumerate(relations):
#            for j in relation_key.keys():
#                    if x[0].title() in relation_key[j]:
#                        c+=1
#                        relations[i][0]=j
#        if c>2:
#            final_data=[["Company","Designation","End_Date"]]
#            count={"Company":,"Designation":}
#            temp=[[""]*3]*(int(len(relations)/3)+1)
#            for i in relations:
#                if i in :
#                    
#            experience_para=list(map(lambda x: x["tagged_para"] if "tagged_para" in x.keys() else [],experience1))
#        experience_para=list(filter(lambda x:x!=[],experience_para))
#        experience_para=list(map(lambda x: x[0],experience_para))
#        
#        experience_para=list(map(lambda x: list(map(lambda y:tre(y),x)),experience_para))
#        experience={"tagged_para":[experience_para[0]]}
#        relation=list(map(lambda y:list(map(lambda x:re.findall("((?:[A-z][A-z\s\’\-\.]+)(?::-|:)(?:[\s]*(?:[\w\\\/\-\\@+\'\.\,\(\)]+[\s]?)+\s?))",x),y )),experience_para))
#        relation=list(itertools.chain.from_iterable(relation))
#        relation=list(itertools.chain.from_iterable(relation))
#        relation=list(map(lambda x: x.split(":-") if ":-" in x else x.split(":"),relation))
#        
#        keys=list(map(lambda x: x[0],relation))
#        experience1=list(map(lambda x: x["Experience"] if "Experience" in x.keys() else {},data))
#        experience_tables=list(map(lambda x: x["tagged_data"] if "tagged_data" in x.keys() else [],experience1))
#        experience_tables=list(filter(lambda x:x!=[],experience_tables))
#        experience_tables=list(map(lambda x: x[0],experience_tables))
#        
#
#
#            

def education(education_data):
    edu_keys={'Percentage': ['Aggregate %', 'Percentage/Cgpa', '% Marks', '% \r\n(%=Dgpa*10)', '% Scored', 'Marks In Percentage', 'Grade/Percentage', 'Aggregate (%)', 'Aggregate (In %)', 'Mark', 'Degree/Course', 'Percentage/Grade', 'Percentage Marks', '(%/Gpa)', 'Cgpa / %', 'Aggregate', '% Of Marks', '% Of Mark', 'Percentage / Cgpa / Grade', 'Cpi/Percentage', '%/Cgpa', 'Score', 'Marks %', '%Of Marks', '%', 'Cgpa/Percentage', 'Percentage Obtained', 'Percentage(%)/Grade', 'Degree', '%  Marks', '% / Cgpa', 'Class/Grade', 'Division (%)', 'Marks Obtained', 'Grade/ Percentage', 'Result', 'Percentage(%)', 'Grade Marks/', 'Gpa / Percentage', 'Percentage%', 'Percentage (%)', 'Cgpa/Marks (%)', 'Marks Secured', 'Cgpa', 'Grade/\r\nMarks', 'Cgpa/\r\nPercentage\r\nOf Marks', 'Agg. Percentage', 'Cgpa/ Percentage', '%Age', 'Cpa', 'Percent', 'Marks (%)', '% Marks Cgpa', '% Mark', 'Marks', 'Percent/Grade', 'Mark In %', 'Percentage\xa0%', 'Percentage %', 'Cgpa/%', 'Grade', 'Percentage/ Cgpa', '% /Cgpa', 'Percentage', 'Degree And Period'], 'Degree': ['Academic Course', 'Course Of Study', 'Course/Examination', 'Degree/ Certificate', 'Academic Qualification', 'Qualification Category', 'Degree And Branch', 'Degree/Class', 'Name Of Examination', 'Education & Training', 'Exam\r\nPassed', 'Examination / Degree', 'Academic', 'Degree/Course', 'Course Name', 'Name Of Qualified Exam', 'Class', 'Exam / Degree', 'Education', 'Degree / Qualification', 'Degree / Diploma / Certificate', 'Certificate', 'Title Of Degree', 'Educational Qualifications', 'Degree (Specialization)', 'Course And Specialization', 'Name Of Qualification – Degree/Diploma', 'Qualification – Degree / Diploma / Certificate', 'Degree/ Program', 'Course/Degree', 'Certification', 'Exam Passed', 'Degree', 'Qualifications', 'Examination/Board', 'Exam.\r\nPassed', 'Exam', 'Qualification', 'Educational Qualification', 'Name Of The Exam', 'Degree / Examination', 'Course', 'Degree And Date', 'Degree / Certificate', 'Name Of Exam', 'Degree/ Examination', 'Degree/ Education Level', 'Title Of The Degree With Branch', 'Degree / Board', 'Group', 'Examination\r\n/ Degree', 'Examination', 'Class/Degree', 'Level Of Study', 'Examination Passed', 'Degree/Certificate'], 'End Date': ['Graduated', 'Graduation Date', 'Year Of Graduation', 'Date Of Duration', 'Passed Out Year', 'Year Of Completion', 'Year Of \r\n  Passing', 'Year Of\r\nPassing', 'To', 'Month &Year Of Passing', 'Graduation\r\nYear', 'Month-Year Of Passing', 'Month & Year Of Passing', 'Session', 'Year Of \r\nPassing', 'Year Of Passing', 'End Date(Dd-Mom-Yyyy)', 'Years', 'Passing Year', 'Year', 'Month/Year Of Passing', 'Pass Out Yr.', 'From Mm/Yy To Mm/Yy', 'Year Completed', 'Passed Out', 'Start - End'], 'Start Date': ['From', 'Start Date(Dd-Mom-Yyyy)', 'Year Of Appearance'], 'Institute': ['University/Board', 'Institution/ Board', 'Board/Univ.', 'College / Institution', 'College/Institution', 'Institute', 'Institute /\r\nUniversity', 'Institute/ University', 'College / School', 'Name Of College', 'School Studied', 'Board/\r\nUniversity', 'Name  Of  The\r\nInstitution', 'College/Institute', 'Name Of University', 'Board/Institute/ University', 'School / University', 'Board/University/ Institute', 'Institute (Board/University)', 'University/Board Of Education', 'Name Of Institute', 'Institute/Board', 'Board Or University', 'Institute, University/ Board', 'Institution', 'Institution/University', 'Board / \r\nUniversity', 'College/ Institute/ University', 'Name Of Institution', 'Board / University', 'Board/ University/ City', 'School/College', 'Board/Institution', 'Name Of The Institution', 'School', 'Board/University', 'Institute/ School', 'University & Institute', 'School & College', 'University/ Institute', 'University / Board', 'University/ Board', 'Univerity/Board', 'Name  Of Institution', 'Name Of School/College', 'School/Institute', 'College/Institute/Board', 'College / University / Institution', 'Institute/ Board', 'Institution Name', 'College / University', 'University', 'Institute/School, City', 'College/University', 'Institute / University', 'Institution / Board', 'Institute / University / Board', 'College & University', 'Name Of Board/University', 'School / College/ Board/ University', 'Course & Specializations', 'School/ College', 'School / Institution Name', 'College', 'University /Board', 'University/Institution', 'University/\r\nBoard', 'University / College / Institute', 'Institute & University', 'Board/ University', 'College/School', 'School/University', 'Institute/University', 'School/Institution', 'Institution / University']}
    if len(education_data['tagged_data']) != 0:
        table_keywords = ['board','university','school','class','college','percent','percentage','marks','institute','qualification','year','year completed','passing year','degree','cgpa','specialization','passed','course','academic','examination','duration','grade','major subject','graduation','score','academic qualification','year of passing','educational qualification','class','stream','branch','course name','exam','course of study','examination board','period','degree and branch','year of completion','academic course','discipline','major','level','level of study','year of appearance','marks secured','education','certification','certificate']
        education_tag_data = education_data['tagged_data']
        for i in education_tag_data:
            filter_data = i[0]
            index_list=[]
            for a,x1 in enumerate(filter_data):
                for j in edu_keys.keys():
                    if str(x1).title() in edu_keys[j]:
                        filter_data[a]=j
                        index_list.append(a)                        
            filtered_keys = []
            for x in filter_data:
                filtered_keywords = list(filter(lambda y : y in x.lower(),table_keywords))
                if len(filtered_keywords) > 0:
                    filtered_keys.append(i)
            if len(filtered_keys) > (len(filter_data) - 3):
                final_output = [[q[p] for p in index_list] for q in i]
                final_output = [dict(zip(final_output[0],a1)) for a1 in final_output[1:]]
                return final_output
                
    if (len(education_data['tagged_para']) != 0):
        degree_dict = {re.sub('\.','',(' '+a1.lower().strip() + ' ')) : a1 for a1 in open('/home/shivank/parser/parser_class/ugdict .txt','r').read().split('\n')}
        degree_list = list(set(list(degree_dict.keys())))
        education_tag_para = education_data['tagged_para']
        education_list = []
        for i in education_tag_para:
            i = list(map(lambda y : re.sub('[\,\(\)\[\]\?]',' ',y),i))
            for x in i:
                degree_filter = list(filter(lambda y: y in (' '+re.sub('\.','',x.lower().strip()) + ' '),degree_list)) 
                final_edu_tag_para = []
                if len(degree_filter) > 0:
                    education_list.append(i)
                    education_para = list(filter(lambda x : x.strip() != '',education_list[0]))
                    final_edu_tag_para = ['']*len(education_para)
                    count= 0
                    if len(education_para) != 0:
                        for q,v in enumerate(education_para):
                            filter_degree = list(filter(lambda y: y in (' '+re.sub('\.','',v.lower().strip()) + ' '),degree_list)) 
                            if q == 0 :
                                condition_degree = filter_degree
                                final_edu_tag_para[count] = v
                                count +=1
                            elif len(filter_degree) == 0:
                                final_edu_tag_para[count-1] = final_edu_tag_para[count-1] + ' ' + v
                            elif len(filter_degree) >  0:
                                if len(condition_degree) == 0:
                                    final_edu_tag_para[count-1] = final_edu_tag_para[count-1] + ' ' + v
                                    count +=1
                                else:
                                    final_edu_tag_para[count] = final_edu_tag_para[count] + ' ' + v
                                    count +=1
                        final_edu_tag_para = list(filter(lambda x : x!='',final_edu_tag_para))
                    else:
                        final_edu_tag_para = []
                    break
            if len(final_edu_tag_para) > 0:
                break
        if len(final_edu_tag_para) == 0:
            return []
        else :
            import en_core_web_sm 
            nlp = en_core_web_sm.load()
            education_tag_spacy = []
            for i in final_edu_tag_para:
                doc = nlp(i)
                sentence_tag = []
                for entity in doc.ents:
                    sentence_tag.append((entity.text,entity.label_))
                education_tag_spacy.append(sentence_tag)
            education_tag_sep = [['Degree','End Date','Start Date','college/University','percentage/cgpa']]
            for q,i in enumerate(education_tag_spacy):
                candidate_edu = []
                filter_list = list(map(lambda y : y[0].lower(),list(filter(lambda x : (x[1] == 'ORG') or (x[1] == 'ORDINAL'),i))))
                date_list = list(map(lambda y : y[0],list(filter(lambda x : x[1] == 'DATE',i))))
                percent_list = list(map(lambda y : y[0],list(filter(lambda x : (x[1] == 'CARDINAL') or (x[1] == 'PERCENT'),i))))
                uni_list = filter_list
                degree_extract = list(filter(lambda x : x in re.sub('\.','',(' '+final_edu_tag_para[q].lower() + ' ')),degree_list))
                for a in filter_list:
                    for b in degree_list:
                        if b in (' '+re.sub('\.','',a) + ' '):
                            uni_list = list(set(uni_list) - set([a]))
                university_keys = ['college','university','school','technology']
                final_uni_keys = []
                for b in uni_list:
                    check_len_uni = len(list(filter(lambda x : x in b.lower(),university_keys)))
                    if check_len_uni > 0:
                        final_uni_keys.append(b)
                if (len(final_uni_keys) == 0):
                    final_uni_keys = uni_list
                if len(degree_extract) >= 1:
                    candidate_edu.append(degree_dict[degree_extract[0]])
                else:
                    candidate_edu.append('')
                candidate_edu.append(' '.join(date_list))
                candidate_edu.append(' ')
                candidate_edu.append(' '.join(final_uni_keys))
                candidate_edu.append(' '.join(percent_list))
                education_tag_sep.append(candidate_edu)
            education_tag_sep = [dict(zip(education_tag_sep[0],values)) for values in education_tag_sep[1:]]
            return education_tag_sep
    else:
        return []
