# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 14:54:29 2017

@author: ipredictt
"""
import pandas as pd
import numpy as np
import re
import math
from operator import add

class qualification_score:
    def __init__(self,Qualifications,University_data):
        self.qualifications=Qualifications
        self.university_data=University_data
        self.stopwords=["of","in","are","and","on","am","for"]
        self.blist=["b","hons","bachelors","undergraduate","bachelor",'bhmct', 'blsc', 'bas', 'barch', 'ba bed', 'ballb', 'ba', 'baslp', \
                    'bams', 'bba llb', 'bba', 'bbm', 'bbs', 'bcom', 'bcj', 'bca', 'bcs', 'bds', 'bdes', 'bed ai', 'bed', 'bes', 'beled',\
                    'be', 'bftech', 'bfia', 'bfa', 'bfs', 'bgl', 'bhms','bhtm', 'bhm', 'bism', 'blm', 'llb', 'bl', 'blis', 'blit', 'bmlt',\
                    'bmrsc', 'bmt', 'mbbs', 'bmr', 'bnysc', 'bot', 'both', 'boptom', 'bpharma', 'bpe', 'bped', 'bpt', 'bpr', 'bscbed', 'bse',\
                    'bsced', 'bs', 'bsms', 'bsw', 'bslllb', 'bsla', 'bta', 'bums', 'kamil e tob o jarahat',\
                    'bvsc', 'btech', 'btc', 'bhed', 'ugbt', 'ugtt', 'ugt']
        self.mlist=["master","masters","m",'ma', 'msc', 'mcom', 'me','mtech', 'llm',\
                    'mca', 'mba', 'mpharma', 'march', 'mds', 'mhms', 'mams', 'md', 'mhhm',\
                    'mped', 'med','pgpex', 'pgdba',"pgdm","pmp","post","pgdie"]
        self.dlist=["doctor","doctorate","phd"]
        self.citylist=['Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Ahmedabad', 'Chennai', 'Kolkata', 'Surat', \
        'Pune', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Visakhapatnam', 'Indore', 'Thane', 'Bhopal',\
        'Pimpri-Chinchwad', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Coimbatore', 'Agra', 'Madurai', \
        'Nashik', 'Vijayawada', 'Faridabad', 'Meerut', 'Rajkot', 'Kalyan-Dombivali', 'Vasai-Virar', 'Varanasi',\
        'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Navi Mumbai', 'Allahabad', 'Ranchi', 'Howrah',\
        'Jabalpur', 'Gwalior', 'Jodhpur', 'Raipur', 'Kota', 'Guwahati', 'Chandigarh', 'Thiruvananthapuram', \
        'Solapur', 'Hubballi', 'Tiruchirappalli[25]', 'Bareilly', 'Moradabad', 'Mysore', 'Tiruppur', 'Gurgaon',\
        'Aligarh', 'Jalandhar', 'Bhubaneswar', 'Salem', 'Mira-Bhayandar', 'Warangal', 'Guntur', 'Bhiwandi', \
        'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur', 'Bhilai', 'Cuttack', 'Firozabad',
        'Kochi', 'Nellore', 'Bhavnagar', 'Dehradun', 'Durgapur', 'Asansol', 'Rourkela', 'Nanded', 'Kolhapur',\
        'Ajmer', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Loni', 'Siliguri', 'Jhansi', 'Ulhasnagar', 'Jammu', \
        'Sangli-Miraj & Kupwad', 'Mangalore', 'Erode', 'Belgaum', 'Ambattur', 'Tirunelveli', 'Malegaon', 'Gaya',\
        'Jalgaon', 'Udaipur', 'Maheshtala', 'Davanagere', 'Kozhikode', 'Akola', 'Kurnool', 'Rajpur Sonarpur', \
        'Rajahmundry', 'Bokaro', 'South Dumdum', 'Bellary', 'Patiala', 'Gopalpur', 'Agartala', 'Bhagalpur',\
        'Muzaffarnagar', 'Bhatpara', 'Panihati', 'Latur', 'Dhule', 'Tirupati', 'Rohtak', 'Korba', 'Bhilwara', \
        'Berhampur', 'Muzaffarpur', 'Ahmednagar', 'Mathura', 'Kollam', 'Avadi', 'Kadapa', 'Kamarhati', 'Sambalpur',\
        'Bilaspur', 'Shahjahanpur', 'Satara', 'Bijapur', 'Rampur', 'Shivamogga', 'Chandrapur', 'Junagadh', \
        'Thrissur', 'Alwar', 'Bardhaman', 'Kulti', 'Kakinada', 'Nizamabad', 'Parbhani', 'Tumkur', 'Khammam', \
        'Ozhukarai', 'Bihar Sharif', 'Panipat', 'Darbhanga', 'Bally', 'Aizawl', 'Dewas', 'Ichalkaranji', 'Karnal',\
        'Bathinda', 'Jalna', 'Eluru', 'Kirari Suleman Nagar', 'Barasat', 'Purnia', 'Satna', 'Mau', 'Sonipat',\
        'Farrukhabad', 'Sagar', 'Rourkela', 'Durg', 'Imphal', 'Ratlam', 'Hapur', 'Arrah', 'Karimnagar', \
        'Anantapur', 'Etawah', 'Ambernath', 'North Dumdum', 'Bharatpur', 'Begusarai', 'New Delhi', 'Gandhidham',\
        'Baranagar', 'Tiruvottiyur', 'Puducherry', 'Sikar', 'Thoothukudi', 'Rewa', 'Mirzapur', 'Raichur',\
        'Pali', 'Ramagundam', 'Haridwar', 'Vijayanagaram', 'Katihar', 'Nagarcoil', 'Sri Ganganagar', \
        'Karawal Nagar', 'Mango', 'Thanjavur', 'Bulandshahr', 'Uluberia', 'Murwara', 'Sambhal', 'Singrauli',\
        'Nadiad', 'Secunderabad', 'Naihati', 'Yamunanagar', 'Bidhan Nagar', 'Pallavaram', 'Bidar', 'Munger', \
        'Panchkula', 'Burhanpur', 'Raurkela Industrial Township', 'Kharagpur', 'Dindigul', 'Gandhinagar',\
        'Hospet', 'Nangloi Jat', 'English Bazar', 'Ongole', 'Deoghar', 'Chapra', 'Haldia', 'Khandwa', 'Nandyal',\
        'Chittoor', 'Morena', 'Amroha', 'Anand', 'Bhind', 'Bhalswa Jahangir Pur', 'Madhyamgram', 'Bhiwani', \
        'Navi Mumbai Panvel Raigad', 'Baharampur', 'Ambala', 'Morvi', 'Fatehpur', 'Rae Bareli', 'Khora', 'Bhusawal',\
        'Orai', 'Bahraich', 'Vellore', 'Mahesana', 'Sambalpur', 'Raiganj', 'Sirsa', 'Danapur', 'Serampore', \
        'Sultan Pur Majra', 'Guna', 'Jaunpur', 'Panvel', 'Shivpuri','Surendranagar Dudhrej', 'Unnao',\
        'Hugli-Chinsurah', 'Alappuzha', 'Kottayam', 'Shimla', 'Karaikudi', 'Adilabad', 'Amaravati',\
        'Bangalore', 'Madras','Bombay','Andhra Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Delhi',\
        'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', \
        'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Mizoram', 'Odisha', 'Orissa', 'Puducherry', 'Punjab',\
        'Rajasthan', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',"Hamirpur",\
        'Silchar','Tiruchirappalli']
        self.dummy={0:0,1:['x'],2:['y'],3:['z']}
        self.scores=None
        self.data_processing();
        self.scorres();

    def data_processing(self):
        self.qualifications["degree"]=self.qualifications["degree"].apply(lambda x: re.sub("\.","",x.lower()).split())
        self.citylist=list(map(lambda x:x.lower(),self.citylist))
        self.university_data["Model_Rank"][self.university_data[self.university_data["University Name"].apply(lambda x: "indian" in x.lower())].index]=1
        self.university_data["Model_Rank"][self.university_data[self.university_data["University Name"].apply(lambda x: "national" in x.lower())].index]=1
        self.university_data["Acrony"]=self.university_data["University Name"].apply(lambda x: " ".join(list(reversed(re.sub("of","",re.match('university of [a-z]+',x.lower()).group(0)).split()))) if re.match('university of [a-z]+',x.lower())!=None else x.lower())
        self.university_data["Acrony"]=self.university_data["Acrony"].apply(lambda x: self.function([w for w in re.sub(r'[0-9\.()]',"",x).split() if w not in self.stopwords]))
        self.university_data["University Name"]=self.university_data["University Name"].apply(lambda x: " ".join(list(reversed(re.sub("of","",re.match('university of [a-z]+',x.lower()).group(0)).split()))) if re.match('university of [a-z]+',x.lower())!=None else x.lower())
        self.university_data["University Name"]=self.university_data["University Name"].apply(lambda x: " ".join([w for w in re.sub(r'[0-9\.()]',"",x).split() if w not in self.stopwords]))
        self.university_data=self.university_data[self.university_data["Model_Rank"]==1]
        self.qualifications["university_name"]=self.qualifications["university_name"].apply(lambda x: " ".join(list(reversed(re.sub("of","",re.match('university of [a-z]+',x.lower()).group(0)).split()))) if re.match('university of [a-z]+',x.lower())!=None else x.lower())
        
    def scorres(self):
        self.scores=pd.Series(np.zeros(len(self.qualifications.candidate_id.unique())))
        self.scores.index=self.qualifications.candidate_id.unique()
        
    def function(self,s):
        t=s[0][0]
        for i in range(1,len(s)-1):
            t=t+s[i][0]
        if s[-1] in self.citylist:
            return t+" "+s[-1]
        return t+s[-1][0]

    def calculator(self):
        self.qualifications.degree=self.qualifications.degree.apply(lambda x: ['x'] if len(set(self.blist).intersection(set(x)))!=0 else x)
        self.qualifications.degree=self.qualifications.degree.apply(lambda x: ['y'] if len(set(self.mlist).intersection(set(list(x))))!=0 else x)
        self.qualifications.degree=self.qualifications.degree.apply(lambda x: ['z'] if len(set(self.dlist).intersection(set(list(x))))!=0 else x)
        self.qualifications.degree=self.qualifications.degree.apply(lambda x: 0 if x not in [['x'],['y'],['z']] else x)
        self.qualifications.degree=self.qualifications.degree.apply(lambda x: list(self.dummy.keys())[list(self.dummy.values()).index(x)])
        self.qualifications.university_name=self.qualifications.university_name.apply(lambda x: 1 if x in self.university_data["University Name"].tolist() else x)
        self.qualifications.university_name=self.qualifications.university_name.apply(lambda x: 1 if x in self.university_data["Acrony"].tolist() else 0)
        self.qualifications=self.qualifications[self.qualifications["degree"]!=0]
        self.qualifications["aggregate"]=self.qualifications.aggregate.apply(lambda x: 0 if x>100 else x)
        self.qualifications["aggregate"]=self.qualifications.aggregate.apply(lambda x: x*10 if 4<x<10 else x)
        self.qualifications["aggregate"]=self.qualifications.aggregate.apply(lambda x: x*25 if x<4 else x)
        #self.qualifications=self.qualifications.applymap(lambda x: float(x))
        self.qualifications=self.qualifications.astype(float)
        self.qualifications=self.qualifications.groupby("candidate_id").mean()
        self.qualifications["degree"]=self.qualifications.degree.apply(lambda x: x*50)
        self.qualifications["university_name"]=self.qualifications.university_name.apply(lambda x: x*100)
        self.qualifications["Qualification_score"]=self.qualifications.degree.apply(lambda x:x**2)+self.qualifications.aggregate.apply(lambda x:x**2)+self.qualifications.university_name.apply(lambda x:x**2)
        self.qualifications["Qualification_score"]=self.qualifications["Qualification_score"].apply(lambda x:math.sqrt(x)*0.578)
        self.scores[self.qualifications.index]=self.qualifications["Qualification_score"]
        return self.scores

        
class Quality_Exp:
    def __init__(self,experience,company_master):
        self.experience=experience
        self.company_master=company_master
        self.stop_words=["pvt.","ltd","inc.","m/s.","pvt","limited","private","m/s","co"]
        self.answer=None
        self.series_creator()
        self.data_processing()
        self.experience_calculator()
        self.eff_experience()
        
    def experience_calculator(self):
        #self.experience[["start_date","end_date"]]=self.experience[["start_date","end_date"]].applymap(lambda x: datetime.strptime(x,"%Y-%m-%d"))
        self.experience["Experience"]=self.experience.end_date-self.experience.start_date
        self.experience["Experience"]=self.experience["Experience"].apply(lambda x:abs(x)).dt.days/365       
    
    def series_creator(self):
        self.answer=pd.Series(np.zeros(len(self.experience.candidate_id.unique())))
        self.answer.index=list(self.experience.candidate_id.unique())
        
    def data_processing(self):
        self.experience=self.experience.dropna().reset_index(drop=True)
        self.experience["company_name"]=self.experience["company_name"].apply(lambda x: " ".join([w for w in x.lower().split() if w not in self.stop_words]))
        self.company_master["TITLE"]=self.company_master["TITLE"].apply(lambda x:" ".join([w for w in x.lower().split() if w not in self.stop_words]))    
    
    def eff_experience(self):
        self.experience["Eff Experience"]=self.experience["company_name"].apply(lambda x: int(x in self.company_master["TITLE"])+1)
        self.experience["Eff Experience"]=self.experience["Eff Experience"]*self.experience["Experience"]

    def percentile_determiner(self):
        Subsetted_data=self.experience[["candidate_id","Eff Experience","Experience"]]
        Subsetted_data=Subsetted_data.groupby("candidate_id").sum()
        Subsetted_data["Percentilerank"]=Subsetted_data["Eff Experience"].apply(lambda x: (x/max(Subsetted_data["Eff Experience"]))*100)
        self.answer[Subsetted_data.index]=Subsetted_data["Percentilerank"]
        return self.answer     
        
        
        
        
        
class hclustering:
    def __init__(self, data, eps, number_clusters, threshold = 0.5):
        self.data = data;
        self.eps = eps;
        self.number_clusters = number_clusters;
        self.threshold = threshold;
        self.clusters = None;
        self.degree_normalization = 1.0 + 2.0 * ( (1.0 - threshold) / (1.0 + threshold) );
        self.adjacency_matrix = None;
        self.mapped=None
        self.dictconverter()
        self.create_adjacency_matrix()
        self.process()
        self.mapper()
     
    def process(self):
        self.clusters = [[index] for index in range(len(self.data))];
        while (len(self.clusters) > self.number_clusters):
            indexes = self.find_pair_clusters(self.clusters);
            if (indexes != [-1, -1]):
                self.clusters[indexes[0]] += self.clusters[indexes[1]];
                self.clusters.pop(indexes[1]); 
            else:
                break;
    def dictconverter(self):
        self.data=self.data.reset_index()
        self.mapped=dict(zip(list(range(len(self.data))),list(self.data["index"])))
        del self.data["index"]
        
                    
    def get_clusters(self):
        return self.clusters; 
        
    def jaccard_coeffecient(self,c,d):
        indexes=tuple(np.where(np.array(list(map(add,c,d)))==0)[0])
        c=np.delete(np.array(c),indexes)
        d=np.delete(np.array(d),indexes)       
        return len(np.where(c-d==0)[0])/(len(np.where(c!=0)[0])+len(np.where(d!=0)[0])-len(np.where(c-d==0)[0]))
        
    def create_adjacency_matrix(self):
        size_data = len(self.data);
        self.adjacency_matrix=np.zeros((size_data,size_data))
        for i in range(0, size_data):
            for j in range(i + 1, size_data):
                if self.jaccard_coeffecient(self.data.loc[i].tolist(),self.data.loc[j].tolist())>self.eps:
                    self.adjacency_matrix[i,j]=1        
                    self.adjacency_matrix[j,i]=1
    def mapper(self):
        self.clusters=list(map(lambda x: list(map(lambda y: self.mapped[y],x)),self.clusters))
        self.data.index=list(map(lambda x: self.mapped[x],list(self.data.index)))
    
    def find_pair_clusters(self, clusters):       
        maximum_goodness = 0.0;
        cluster_indexes = [-1, -1];
        for i in range(0, len(clusters)):
            for j in range(i + 1, len(clusters)):
                goodness = self.calculate_goodness(clusters[i], clusters[j]);
                if (goodness > maximum_goodness):
                    maximum_goodness = goodness;
                    cluster_indexes = [i, j];
        return cluster_indexes;    

    def calculate_links(self, cluster1, cluster2):
        number_links = 0
        for index1 in cluster1:
            for index2 in cluster2:
                number_links += self.adjacency_matrix[index1][index2];
        return number_links;    
    
    def calculate_goodness(self, cluster1, cluster2):
        number_links = self.calculate_links(cluster1, cluster2);
        devider = (len(cluster1) + len(cluster2)) ** self.degree_normalization - len(cluster1) ** self.degree_normalization - len(cluster2) ** self.degree_normalization;
        return (number_links / devider);
    
    
