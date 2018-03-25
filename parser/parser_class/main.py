# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:20:45 2018

@author: ipredictt
"""
import Initial_processing
import variable_codes
import Docx_class
import Pdf_class
import json
def final_output_json(filepath):
    file1,typ=Initial_processing.file_converter(filepath)
    if typ=="doc":
        resume=Docx_class.Docx_class(file1)
    if typ=="pdf":
        resume=Pdf_class.Pdf_class(file1)
    final_output={}
    for i in ['DOB','Location','Gender','Name','Mobile','Email']:
        if len(resume.keyword_tag_dict[i]['tagged_relations'])>=1:
            final_output[i]=resume.keyword_tag_dict[i]['tagged_relations'][0]
        else:
            final_output[i]=""
    final_output["Skills"]=variable_codes.skills(resume.keyword_tag_dict["Skills"])
    final_output["Education"]=variable_codes.education(resume.keyword_tag_dict["Education"])
    final_output["Experience"]=variable_codes.experience(resume.keyword_tag_dict["Experience"])
    return json.dumps(final_output, indent=4)
    
#temp=resume.keyword_tag_dict["Education"]
