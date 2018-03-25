# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 12:50:47 2018

@author: Shivank.r
"""
import slate
import re
import itertools
import Initial_processing
import pandas as pd
import variable_codes
#from dateutil import parser
class Pdf_class:
    def __init__(self,filepath):
        f=open(filepath,"rb") 
        self.doc = slate.PDF(f)
        f=f.close()
        self.keys=pd.read_excel('/home/shivank/parser/parser_class/all_resumes_keywords_final.xlsx',encoding = 'iso-8859-1')
        self.doc_processing()
        self.resume_string="\n".join(self.doc)
        self.relations=Initial_processing.relations(self.resume_string)
        self.relations=[[k.lower().strip(),v.strip()] for k,v in self.relations ]
        self.keywords=[]
        self.tagged_para=[]
        self.imp_keywords()
        self.bifurcation()
        self.tagged_relations()
        self.keyword_tag_dict = {'Experience':{'tagged_relations':[],'tagged_para':[],'tagged_data': []},'Skills':{'tagged_relations':[],'tagged_para':[],'tagged_data': []},'Mobile' : {'tagged_relations':[],'tagged_para':[],'tagged_data': []},'Education':{'tagged_relations':[],'tagged_para':[],'tagged_data': []},'DOB':{'tagged_relations':[],'tagged_para':[],'tagged_data': []},'Name':{'tagged_relations':[],'tagged_para':[],'tagged_data': []},'Location' : {'tagged_relations':[],'tagged_para':[],'tagged_data': []} ,'Email': {'tagged_relations':[],'tagged_para':[],'tagged_data': []} ,'Gender' : {'tagged_relations':[],'tagged_para':[],'tagged_data': []}}
        self.keyword_tag_extract()                                      
    def doc_processing(self):
        self.doc=list(map(lambda x: re.sub(r"\uf0a7","",re.sub("\uf0b7","",x)),self.doc))
        self.doc=list(itertools.chain.from_iterable(list(map(lambda x:x.splitlines(),self.doc))))
        self.doc=list(map(lambda x:x.strip(),self.doc))
        self.doc=list(filter(lambda x: x!="",self.doc))
    def imp_keywords(self):
        for i in self.doc:
            if re.sub("[\:\-\'\t\\\/]","",i.lower().strip()) in self.keys[self.keys["Heading"]=="Header"]["keyword"].tolist():
                self.keywords.append(i.strip())
    def bifurcation(self):
            for i,key in enumerate(self.keywords):
                if i==len(self.keywords)-1:
                    self.tagged_para.append([key,self.doc[self.doc.index(key)+1:]])
                else:
                   self.tagged_para.append([key,self.doc[self.doc.index(key)+1:self.doc.index(self.keywords[i+1])]]) 

    def tagged_relations(self):
        keywds = pd.read_csv('/home/shivank/parser/parser_class/relation_keywords.csv',encoding="iso-8859-1")
        keywds = keywds[keywds['keyword'].isin(list(map(lambda x:x[0],self.relations)))][keywds['keyword tag'] != 'Remove']
        keywds['value'] = keywds['keyword'].apply(lambda x: [y[1]  for y in self.relations if y[0].lower()==x])
        keywds['value'][keywds['keyword tag']!="Skills"]=keywds['value'][keywds['keyword tag']!="Skills"].apply(lambda x:x[0])
        keywds['value'][keywds['keyword tag']=="Skills"]=keywds['value'][keywds['keyword tag']=="Skills"].apply(lambda x:','.join(x))
        self.relations={keywds['keyword tag'][i]:keywds['value'][i] for i in  keywds.index}
                               
    def keyword_tag_extract(self):
        self.keywords_dict = self.keys[self.keys['keyword tag'] != 'Remove'].groupby('keyword tag')['keyword'].apply(list).to_dict()
        for i in self.tagged_para:
            if re.sub("[\:\-\'\t\\\/]","",i[0].lower().strip()) in self.keywords_dict['Experience']:
                self.keyword_tag_dict['Experience']['tagged_para'].append(i[1])
            elif re.sub("[\:\-\'\t\\\/]","",i[0].lower().strip()) in self.keywords_dict['Education']:
                self.keyword_tag_dict['Education']['tagged_para'].append(i[1])            
            elif re.sub("[\:\-\'\t\\\/]","",i[0].lower().strip()) in self.keywords_dict['Skills']:
                self.keyword_tag_dict['Skills']['tagged_para'].append(i[1])       
        if 'Skills' in list(self.relations.keys()):
            for i in self.relations['Skills']:
                self.keyword_tag_dict['Skills']['tagged_relations'].append(i)               
        if 'DOB' in list(self.relations.keys()):
            self.keyword_tag_dict['DOB']['tagged_relations'].append(self.relations['DOB'])
        else:
            self.keyword_tag_dict['DOB']['tagged_relations'].append(variable_codes.dob(self.resume_string))
        if 'Mobile' in list(self.relations.keys()):
            self.keyword_tag_dict['Mobile']['tagged_relations'].append(self.relations['Mobile'])
        else:        
            self.keyword_tag_dict['Mobile']['tagged_relations'].append(variable_codes.mobile(self.resume_string))
        if 'Email' in list(self.relations.keys()):
            self.keyword_tag_dict['Email']['tagged_relations'].append(self.relations['Email'])
        else:
            self.keyword_tag_dict['Email']['tagged_relations'].append(variable_codes.email(self.resume_string))
        if 'Name' in list(self.relations.keys()):
            self.keyword_tag_dict['Name']['tagged_relations'].append(self.relations['Name'])
        else:
            self.keyword_tag_dict['Name']['tagged_relations'].append(variable_codes.names_extractor(self.resume_string))
        if 'Gender' in list(self.relations.keys()):
            self.keyword_tag_dict['Gender']['tagged_relations'].append(self.relations['Gender'])
#        else:
#           self.keyword_tag_dict['Gender']['tagged_relations'].append(variable_codes.gender_prediction(name))
        if 'Location' in list(self.relations.keys()):
            self.keyword_tag_dict['Location']['tagged_relations'].append(self.relations['Location'])
        else:
            self.keyword_tag_dict['Location']['tagged_relations'].append(variable_codes.location_parse(self.resume_string))

            
