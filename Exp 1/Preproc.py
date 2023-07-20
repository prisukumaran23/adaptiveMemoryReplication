#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 12:01:30 2022

@author: priyankasukumaran
"""
"""
! Need to add calc_bonus function. 

"""

import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from dprime import dprime
import re
import matplotlib.patches as mpatches
from statistics import stdev
from scipy import stats

pd.options.mode.chained_assignment = None  # default='warn'

sns.set_theme()
matplotlib.rc('figure', figsize=(8, 5))


def df_files(exp):
    ''' Gets files if single day/matches files if 2 day experiment '''
    if exp == '1a':
        path = 'Exp1a_RawData/' # Change to Github path
        df_files = get_files(path)
    elif exp == '1b':
        path = 'Exp1b_RawData/' # Change to Github path
        df_files = match_files(path)
    return df_files

def get_files(path):
    filenames = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
    merged_data = {}
    for file in range(0,len(filenames),1):
        merged_data[file] = pd.read_json(path+filenames[file],)
    return merged_data

def match_files(path):
    ''' Matches day 1 and day 2 files by Prolific ID '''
    path1 = path+'Day 1/'
    path2 = path+'Day 2/' 
    day1 = [pos_json for pos_json in os.listdir(path1) if pos_json.endswith('.json')]
    day2 = [pos_json for pos_json in os.listdir(path2) if pos_json.endswith('.json')]
    unmerged_day1 = {}
    unmerged_day2 = {}
    ID1 = []
    ID2 = []
    merged_data = {}
    for file in range(0,len(day1),1):
        unmerged_day1[file] = pd.read_json(path1+day1[file],)
        participant_id = unmerged_day1[file].loc[unmerged_day1[file]['trial_id'].isin(['prolificID']),'responses'].item()
        ID1.append(participant_id.partition('{"ParticipantID":"')[2].partition('"}')[0].strip())
    for file in range(0,len(day2),1):
        unmerged_day2[file] = pd.read_json(path2+day2[file],)
        participant_id = unmerged_day2[file].loc[unmerged_day2[file]['trial_id'].isin(['prolificID']),'responses'].item()
        ID2.append(participant_id.partition('{"ParticipantID":"')[2].partition('"}')[0].strip())    
    df1 = pd.DataFrame()
    df1['d1_ID'] = ID1
    df1['d1_filename'] = day1
    df2 = pd.DataFrame()
    df2['d2_ID'] = ID2
    df2['d2_filename'] = day2
    df3 = df1.merge(df2, left_on='d1_ID', right_on='d2_ID', how='inner')
    for file in range (0,len(df3['d1_filename']),1):
         merged_data[file] = pd.read_json(path1+df3['d1_filename'][file],).append(pd.read_json(path2+df3['d2_filename'][file],))
    return merged_data

def get_ID(unparsed_data):
    participant_id = unparsed_data.loc[unparsed_data['trial_id'].isin(['prolificID']),'responses'][4]
    ID = (participant_id.partition('{"ParticipantID":"')[2].partition('"}')[0])
    return ID 

def get_demographics(unparsed_data):
    data = unparsed_data[["responses","type","response",
                             "rt","category","trial_id","correct", "phase"]]
    age = re.sub("[^\d\.]", "", data.iloc[2,0])
    sex = re.sub(r'[^\w]', '', data.iloc[3,0])
    return age, sex

def get_phq(unparsed_data):
    data = unparsed_data.loc[unparsed_data['trial_id'].isin(['survey'])]
    data = data[["trial_index","response","trial_id"]]
    data = data.reset_index().drop(columns='index')
    if 46<data.iloc[3]['response']<78: phq_attention=1
    else: 
        phq_attention=-1    # did not pass attention check
    score = []
    for j in range(len(data)):
        if data.iloc[j]['response']<15: score.append(0)
        elif 15<=data.iloc[j]['response']<46: score.append(1)
        elif 46<=data.iloc[j]['response']<78: score.append(2)
        elif 78<=data.iloc[j]['response']: score.append(3)
    phq_score = sum(score) - score[3] - score[9]
    if phq_score<6: phq=0          # none-mild
    elif 6<=phq_score<11: phq=1    # moderate
    elif 11<=phq_score<17: phq=2   # moderately severe
    elif 17<=phq_score: phq=3      # severe
    return phq, phq_attention

def find_rew_cat(unparsed_data):
    ''' Returns the category which was rewarded higher for given participant  '''
    rew = unparsed_data.loc[unparsed_data['trial_id'].isin(['prolificID'])]
    rew_reset = rew.reset_index()
    high_rew = []
    low_rew = []
    if exp == '1b':
        if rew_reset['condition'][0] != rew_reset['condition'][1]:
            print(rew_reset['condition'][0],rew_reset['condition'][1],get_ID(unparsed_data))
            raise Exception('Reward conditions do not match. Error in matching Day 1 and Day 2 files.')
    if rew_reset['condition'][0] == 'Reward_Animals':
        subgroup = 'Reward_Animals'
        high_rew = 'Animal'
        low_rew = 'Object'
    elif rew_reset['condition'][0] == 'Reward_Objects':
        subgroup = 'Reward_Objects'
        high_rew = 'Object'
        low_rew = 'Animal'
    return high_rew, low_rew, subgroup

#def calc_bonus():
    
def get_survey(data):
    surveys = data.loc[data['trial_type'].isin(['survey-text'])]
    surveys = surveys.loc[surveys['trial_index']>200]['responses']
    surveys = surveys.reset_index()
    return surveys.responses[0],surveys.responses[1]
    
def calc_match_acc(data):
    '''Accuracy was calculated based on correct guessing of Japanese word within the given time (600ms). 
    Null responses (took more than 600ms to respond) were counted as incorrect.'''
    high_rew,low_rew,subgroup = find_rew_cat(data)
    match_data = data.loc[data['trial_id'].isin(['match'])]
    match_data = match_data.loc[match_data['phase'].isin(['Phase 1','Phase 2','Phase 3'])]
    match_count = match_data['correct'].value_counts()
    match_RT = np.mean(match_data[match_data['rt'].notna()]['rt'])
    
    ph1_match_data = match_data.loc[match_data['phase'].isin(['Phase 1'])]
    ph2_match_data = match_data.loc[match_data['phase'].isin(['Phase 2'])] 
    ph3_match_data = match_data.loc[match_data['phase'].isin(['Phase 3'])] 
    
    ph1_high = ph1_match_data.loc[ph1_match_data['category'].isin([high_rew])]
    ph1_low = ph1_match_data.loc[ph1_match_data['category'].isin([low_rew])]
    ph2_high = ph2_match_data.loc[ph2_match_data['category'].isin([high_rew])]
    ph2_low = ph2_match_data.loc[ph2_match_data['category'].isin([low_rew])]
    ph3_high = ph3_match_data.loc[ph3_match_data['category'].isin([high_rew])]
    ph3_low = ph3_match_data.loc[ph3_match_data['category'].isin([low_rew])]
    
    ph1_high_MA = ph1_high['correct'].value_counts()[1]
    ph1_low_MA = ph1_low['correct'].value_counts()[1]
    ph2_high_MA = ph2_high['correct'].value_counts()[1]
    ph2_low_MA = ph2_low['correct'].value_counts()[1]
    ph3_high_MA = ph3_high['correct'].value_counts()[1]
    ph3_low_MA = ph3_low['correct'].value_counts()[1]
        
    ph1_high_RT =  np.mean(ph1_high[ph1_high['rt'].notna()]['rt'])
    ph1_low_RT = np.mean(ph1_low[ph1_low['rt'].notna()]['rt'])
    ph2_high_RT = np.mean(ph2_high[ph2_high['rt'].notna()]['rt'])
    ph2_low_RT = np.mean(ph2_low[ph2_low['rt'].notna()]['rt'])
    ph3_high_RT = np.mean(ph3_high[ph3_high['rt'].notna()]['rt'])
    ph3_low_RT = np.mean(ph3_low[ph3_low['rt'].notna()]['rt'])
    out = [ph1_high_MA/16, ph1_low_MA/16, ph2_high_MA/16, ph2_low_MA/16, ph3_high_MA/16, ph3_low_MA/16,
           ph1_high_RT, ph1_low_RT, ph2_high_RT, ph2_low_RT, ph3_high_RT, ph3_low_RT, 
           match_count[1]/96, match_RT]
    return out
    
def get_phase(data):
    match_data = data.loc[data['trial_id'].isin(['match'])]
    ph1_match_data = match_data.loc[match_data['phase'].isin(['Phase 1'])]
    ph1_keys = ph1_match_data['word'].reset_index()
    ph2_match_data = match_data.loc[match_data['phase'].isin(['Phase 2'])]
    ph2_keys = ph2_match_data['word'].reset_index()
    ph3_match_data = match_data.loc[match_data['phase'].isin(['Phase 3'])]
    ph3_keys = ph3_match_data['word'].reset_index()
    return ph1_keys, ph2_keys, ph3_keys

def filter_highcert(memory_data, filterby):
    if filterby == 'High':
        memory_data = memory_data[memory_data['button_pressed'].isin(['0','1','4','5'])]
    elif filterby == 'Highest':
        memory_data = memory_data[memory_data['response'].isin(['0','5'])]
    elif filterby == 'None':
        memory_data = memory_data
    return memory_data

def calc_CR(memory_data):
    old_imgs = memory_data.loc[memory_data['type'].isin(['old_img'])]
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs)
    CR = hits-fa   
    return CR

def calc_HR_FA(memory_data):
    old_imgs = memory_data.loc[memory_data['type'].isin(['old_img'])]
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs)
    return hits, fa

def calc_DP(memory_data):
    old_imgs = memory_data.loc[memory_data['type'].isin(['old_img'])]
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs)
    if hits == 1.0:
        hits = 0.99
    elif hits == 0:
        hits = 0.01
    if fa == 1.0:
        fa = 0.99
    elif fa == 0:
        fa = 0.01
    DP = dprime(hits,fa,'diff')
    if np.isnan(DP):
        print(DP,print('hits', hits, 'fa',fa))
    return DP

def calc_CR_ph(old_imgs,memory_data):
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs) #common fa rate
    CR = hits-fa  
    return CR

def calc_HR_FA_ph(old_imgs,memory_data):
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs) #common fa rate
    return hits, fa

def calc_DP_ph(old_imgs,memory_data):
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs) #common fa rate
    if hits == 1.0:
        hits = 0.99
    elif hits == 0:
        hits = 0.01
    if fa == 1.0:
        fa = 0.99
    elif fa == 0:
        fa = 0.01
    DP = dprime(hits,fa,'diff')  
    return DP

def calc_RB_ph(old_imgs,memory_data):
    'calculates response bias'
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs) #common fa rate
    if hits == 1.0:
        hits = 0.99
    elif hits == 0:
        hits = 0.01
    if fa == 1.0:
        fa = 0.99
    elif fa == 0:
        fa = 0.01
    RB = -(stats.norm.ppf(hits) + stats.norm.ppf(fa))/2.0
    return RB

def calc_mem_RT(memory_data):
    memory_data = memory_data.loc[memory_data['trial_id'].isin(['rec_memory'])]
    RT = np.mean(memory_data['rt'])
    return RT

def create_summary_df(data, filterby, img_or_word):
    ''' filterby: 'None', High' or 'Highest' '''
    ID = get_ID(data)
    high_rew,low_rew,subgroup = find_rew_cat(data)
    memory_data = data.loc[data['trial_id'].isin(['rec_memory'])]
    memory_data = data.loc[data['img_or_word'].isin([img_or_word])]
    memory_data = memory_data[memory_data['button_pressed'].notna()]    #remove nan in response
    memory_data = filter_highcert(memory_data,filterby)
    
    high_memory = memory_data.loc[memory_data['category'].isin([high_rew])]
    low_memory = memory_data.loc[memory_data['category'].isin([low_rew])]
    ph1_keys,ph2_keys,ph3_keys =  get_phase(data)
    
    ph1_high = ph1_keys.merge(high_memory, left_on='word', right_on='word',how='inner')
    ph1_low = ph1_keys.merge(low_memory, left_on='word', right_on='word',how='inner')
    ph2_high = ph2_keys.merge(high_memory, left_on='word', right_on='word',how='inner')
    ph2_low = ph2_keys.merge(low_memory, left_on='word', right_on='word',how='inner')
    ph3_high = ph3_keys.merge(high_memory, left_on='word', right_on='word',how='inner')
    ph3_low = ph3_keys.merge(low_memory, left_on='word', right_on='word',how='inner')
    
    data_summary = [[ID, 'Age', get_demographics(data)[0]],
                   [ID, 'Sex', get_demographics(data)[1]],
                   #[ID, 'Bonus', calc_bonus(data)],
                   [ID, 'Overall Match Accuracy', calc_match_acc(data)[12]],
                   [ID, 'Overall Match RT', calc_match_acc(data)[13]],

                   [ID, 'CR Overall', calc_CR(memory_data)],
                   [ID, 'HR Overall', calc_HR_FA(memory_data)[0]],
                   [ID, 'FA Overall', calc_HR_FA(memory_data)[1]],
                   [ID, 'CR Overall High Reward', calc_CR(high_memory)],
                   [ID, 'CR Overall Low Reward', calc_CR(low_memory)],
                   [ID, 'CR Ph1 High Reward', calc_CR_ph(ph1_high,high_memory)],
                   [ID, 'CR Ph1 Low Reward', calc_CR_ph(ph1_low,low_memory)],
                   [ID, 'CR Ph2 High Reward', calc_CR_ph(ph2_high,high_memory)],
                   [ID, 'CR Ph2 Low Reward', calc_CR_ph(ph2_low,low_memory)],
                   [ID, 'CR Ph3 High Reward', calc_CR_ph(ph3_high,high_memory)],
                   [ID, 'CR Ph3 Low Reward', calc_CR_ph(ph3_low,low_memory)],
                   
                   [ID, 'DP Overall', calc_DP(memory_data)],
                   [ID, 'DP Overall High Reward', calc_DP(high_memory)],
                   [ID, 'DP Overall Low Reward', calc_DP(low_memory)],
                   [ID, 'DP Ph1 High Reward', calc_DP_ph(ph1_high,high_memory)],
                   [ID, 'DP Ph1 Low Reward', calc_DP_ph(ph1_low,low_memory)],
                   [ID, 'DP Ph2 High Reward', calc_DP_ph(ph2_high,high_memory)],
                   [ID, 'DP Ph2 Low Reward', calc_DP_ph(ph2_low,low_memory)],
                   [ID, 'DP Ph3 High Reward', calc_DP_ph(ph3_high,high_memory)],
                   [ID, 'DP Ph3 Low Reward', calc_DP_ph(ph3_low,low_memory)],
                   
                   [ID, 'PHQ Score', get_phq(data)[0]],
                   [ID, 'PHQ Attention Check', get_phq(data)[1]],
                   
                   [ID, 'Memory Test RT', calc_mem_RT(memory_data)],
                   [ID, 'Rewarded Category', high_rew]]
    
    data_trials = [[ID, subgroup, high_rew, 'Ph1', 'High Reward', 
                    calc_CR_ph(ph1_high,high_memory), calc_DP_ph(ph1_high,high_memory),
                    calc_match_acc(data)[0], calc_match_acc(data)[6], calc_RB_ph(ph1_high,high_memory),
                    calc_HR_FA_ph(ph1_high,high_memory)[0],calc_HR_FA_ph(ph1_high,high_memory)[1]],
                   [ID, subgroup, low_rew, 'Ph1', 'Low Reward', 
                    calc_CR_ph(ph1_low,low_memory), calc_DP_ph(ph1_low,low_memory),
                    calc_match_acc(data)[1], calc_match_acc(data)[7],calc_RB_ph(ph1_low,low_memory),
                    calc_HR_FA_ph(ph1_low,low_memory)[0],calc_HR_FA_ph(ph1_low,low_memory)[1]],
                   [ID, subgroup, high_rew, 'Ph2', 'High Reward', 
                    calc_CR_ph(ph2_high,high_memory), calc_DP_ph(ph2_high,high_memory),
                    calc_match_acc(data)[2], calc_match_acc(data)[8],calc_RB_ph(ph2_high,high_memory),
                    calc_HR_FA_ph(ph2_high,high_memory)[0],calc_HR_FA_ph(ph2_high,high_memory)[1]],
                   [ID, subgroup, low_rew, 'Ph2', 'Low Reward', 
                    calc_CR_ph(ph2_low,low_memory), calc_DP_ph(ph2_low,low_memory),
                    calc_match_acc(data)[3], calc_match_acc(data)[9],calc_RB_ph(ph2_low,low_memory),
                    calc_HR_FA_ph(ph2_low,low_memory)[0],calc_HR_FA_ph(ph2_low,low_memory)[1]],
                   [ID, subgroup, high_rew, 'Ph3', 'High Reward', 
                    calc_CR_ph(ph3_high,high_memory), calc_DP_ph(ph3_high,high_memory),
                    calc_match_acc(data)[4], calc_match_acc(data)[10],calc_RB_ph(ph3_high,high_memory),
                    calc_HR_FA_ph(ph3_high,high_memory)[0],calc_HR_FA_ph(ph3_high,high_memory)[1]],
                   [ID, subgroup, low_rew, 'Ph3', 'Low Reward', 
                    calc_CR_ph(ph3_low,low_memory), calc_DP_ph(ph3_low,low_memory),
                    calc_match_acc(data)[5], calc_match_acc(data)[11],calc_RB_ph(ph3_low,low_memory),
                    calc_HR_FA_ph(ph3_low,low_memory)[0],calc_HR_FA_ph(ph3_low,low_memory)[1]]]
    
    df_summary_part = pd.DataFrame(data_summary, columns = ['UserID','Condition','Value'])
    df_trials_part = pd.DataFrame(data_trials, columns = ['UserID','Rew_Subgroup','Category','Phase','Reward_Category','CR','DP','MA','RT','RB','HR','FA'])
    
    return df_summary_part, df_trials_part

def match_data_create(data):
    match_data = data[["trial_id","phase","rt","word","correct"]]
    match_data = match_data.loc[match_data["phase"].isin(['Phase 1','Phase 2','Phase 3'])] 
    match_data = match_data.loc[match_data["trial_id"].isin(['match'])] 
    match_data = match_data.rename({'rt': 'match_rt'}, axis='columns') # rename column correct to match word
    match_data = match_data.rename({'correct': 'match_corr'}, axis='columns') # rename column correct to match word
    match_data = match_data.drop(columns=['phase','trial_id'])
    return match_data

def create_regression_df(unparsed_data, img_or_word):
    data = unparsed_data[["word","responses","type","button_pressed",
                             "rt","category","trial_id","correct", "phase","img_or_word"]]
    data = data.loc[data['img_or_word'].isin([img_or_word])]
    data = data.loc[data['phase'].isin(['Rec_Memory'])] # remove other trial data
    data = data.loc[data['trial_id'].isin(['rec_memory'])] # remove feedblack slide data
    data_new_imgs = data.loc[data['type'].isin(['new_img'])] 

    ph1_keys,ph2_keys,ph3_keys = get_phase(unparsed_data)
    data_ph1 = ph1_keys.merge(data, left_on='word', right_on='word',how='inner')
    data_ph1.phase=1
    data_ph2 = ph2_keys.merge(data, left_on='word', right_on='word',how='inner')  
    data_ph2.phase=2
    data_ph3 = ph3_keys.merge(data, left_on='word', right_on='word',how='inner')  
    data_ph3.phase=3
    data = data_ph1.append(data_ph2)
    data = data.append(data_ph3)
    data = data.append(data_new_imgs)
    
    data.insert(loc=0, column='rew_cat', value=data['category'])
    if find_rew_cat(unparsed_data)[0] == 'Object':
        data['rew_cat'] = data['rew_cat'].str.replace('Object', '1')
        data['rew_cat'] = data['rew_cat'].str.replace('Animal', '-1')
    elif find_rew_cat(unparsed_data)[0] == 'Animal':
        data['rew_cat'] = data['rew_cat'].str.replace('Object', '-1')
        data['rew_cat'] = data['rew_cat'].str.replace('Animal', '1')
    
    data.insert(loc=0, column='Age', value=get_demographics(unparsed_data)[0])
    data.insert(loc=0, column='Sex', value=get_demographics(unparsed_data)[1])
    data.insert(loc=0, column='Rew_Subgroup', value=[find_rew_cat(unparsed_data)[0]] * len(data))
    data.insert(loc=0, column='UserID', value=[get_ID(unparsed_data)] * len(data))  
    
    match_data = match_data_create(unparsed_data)
    df_regression_part = data.merge(match_data, left_on='word', right_on='word',how='left')
    df_regression_part = df_regression_part.drop(columns=['responses','trial_id','index'])
    
    df_regression_part = df_regression_part.rename(columns={"rew_cat_name":"Rew_Subgroup", "rew_cat":"Reward_Category", 
                                              "category":"Category", "phase":"Phase", "word":"Stim", "type":"Stim_Type",
                                              "button_pressed":"Certainty", "match_rt":"Match_RT", "match_corr":"Match_Correct", 
                                              "rt":"Memory_RT", "correct":"Memory_Correct"})
    return df_regression_part

def concat_dfs(matched_files, filterby, img_or_word):
    for file in range(len(matched_files)):
       part_data = matched_files[file]
       df_summary_part,df_trials_part = create_summary_df(part_data, filterby, img_or_word)
       df_regression_part = create_regression_df(part_data, img_or_word)
       if file==0:
           df_summary = df_summary_part.copy()
           df_trials = df_trials_part.copy()
           df_regression = df_regression_part.copy()
       if file>0:
           df_summary = pd.concat([df_summary,df_summary_part])
           df_trials = pd.concat([df_trials,df_trials_part])  
           df_regression = pd.concat([df_regression,df_regression_part])  
    return df_summary, df_trials, df_regression
    

def remove_low_DP(df_summary, df_trials, df_regression, DP_cutoff):
    '''Exclusion E2: Below chance performance in memory test.
    Participant is excluded if overall dprime in memory test is equal to or below zero.'''
    DP = df_summary.loc[df_summary['Condition'].isin(['DP Overall'])]
    reject = DP['UserID'].loc[DP['Value']<=DP_cutoff]
    reset_reject = reject.reset_index()
    for ids in range(len(reset_reject)):
        rejectID = reset_reject['UserID'][ids]
        print('dprime score below chance in memory task, exclude:',rejectID)
        df_summary = df_summary[~df_summary.UserID.str.contains(rejectID)]
        df_trials = df_trials[~df_trials.UserID.str.contains(rejectID)]
        df_regression = df_regression[~df_regression.UserID.str.contains(rejectID)]
    return df_summary, df_trials, df_regression, reject

def outlier_treatment(datacolumn):
     sorted(datacolumn)
     Q1,Q3 = np.percentile(datacolumn , [25,75])
     IQR = Q3 - Q1
     lower_range = Q1 - (1.5 * IQR)
     upper_range = Q3 + (1.5 * IQR)
     return lower_range, upper_range

def remove_outlier_RT(df_summary, df_trials, df_regression):
    '''Exclusion E3: Outliers in reaction times in memory test.
    Defined as outlier if data point is greater than 1.5 times the interquartile range'''
    RT = df_summary.loc[df_summary['Condition'].isin(['Memory Test RT'])]
    lowerbound,upperbound = outlier_treatment(RT.Value)
    reject = RT['UserID'].loc[(RT.Value < lowerbound) | (RT.Value > upperbound)]
    reset_reject = reject.reset_index()
    for ids in range(len(reset_reject)):
        rejectID = reset_reject['UserID'][ids]
        print('Anomolous reaction time in memory task, exclude:',rejectID)
        df_summary = df_summary[~df_summary.UserID.str.contains(rejectID)]
        df_trials = df_trials[~df_trials.UserID.str.contains(rejectID)]
        df_regression = df_regression[~df_regression.UserID.str.contains(rejectID)]
    return df_summary, df_trials, df_regression, reject

def preproc(matched_files, DP_cutoff=0, filterby='None',img_or_word='img'):
    """
    Args
    ----
    matched_files : dict 
        output of match_files function (participant data)
    
    DP_cutoff : int
        reject participants with overall dprime score below DP_cutoff (default = 0 as chance)
        
    filterby : str
        'None' analyse all memory data (includes memory certainty responses: maybe, likely, definitely)
        'High' analyse data where participants answered with high certainty (includes: likely, definitely)
        'Highest' analyse data where participants answered with highest certainty (incldues: definitely) 
        
    Returns
    -------
    df_summary : pandas DataFrame 
        summary data by participant (all information including sex, age, bonus recieved, survey answers etc.)
    df_trials : pandas DataFrame 
        data by participant (trial relevant information for analysis (ANOVA, t-tests etc.))
    df_regression : pandas DataFrame 
        trial by trial data (relevant information trial by trial coded (Regression and Bayesian analysis)
    """
    df_summary,df_trials,df_regression = concat_dfs(matched_files,'None',img_or_word)
    df_summary,df_trials,df_regression,rejectID2=remove_low_DP(df_summary,df_trials,df_regression,DP_cutoff)
    df_summary,df_trials,df_regression,rejectID3=remove_outlier_RT(df_summary,df_trials,df_regression)
    rejectIDs = rejectID2.append(rejectID3)
    if filterby == 'None':
        return df_summary,df_trials,df_regression
    elif filterby != 'None':
        df_summary, df_trials, df_regression = concat_dfs(matched_files,filterby,img_or_word)
        rejectIDs = rejectIDs.reset_index()
        for ids in range(len(rejectIDs)):
            rejectID = rejectIDs['UserID'][ids]
            df_summary = df_summary[~df_summary.UserID.str.contains(rejectID)]
            df_trials = df_trials[~df_trials.UserID.str.contains(rejectID)]
            df_regression = df_regression[~df_regression.UserID.str.contains(rejectID)]
        return df_summary, df_trials, df_regression
    return df_summary, df_trials, df_regression
   
def grouped_memory_certainty(df_all, rew_cat, phase):
    '''
    Args
    ----
    df_all : pandas DataFrame 
        Dataframe of all trial data (output of preproc function)
        
    rew_cat : str
        '1' for high reward category
        '-1' for low reward category
        
    phase : str or int
        1 for phase 1
        2 for phase 2
        3 for phase 3
        'New' for new items
        
    Returns
    -------
    df : pandas DataFrame 
        Reponse to memory test by certainty grouped by participant UserID
    '''
    df_all = df_all.replace('Rec_Memory', 'New')
    df_all = df_all.loc[df_all['Certainty'].isin(['0','1','2','3','4','5'])]
    df_ph = df_all.loc[df_all['Phase'].isin([phase])]
    df = df_ph.loc[df_ph['Reward_Category'].isin([rew_cat])]
    
    df_count = df.groupby('UserID')['Certainty'].value_counts().to_frame()
    df_count = df_count.rename(columns={"Certainty": "Count"}).reset_index()

    df_count['Phase'] = phase
    df_count['Reward_Category'] = rew_cat
    tot = df_count.groupby('UserID')['Count'].sum().to_frame()
    tot = tot.rename(columns={"Count": "Total_Count"}).reset_index()
    df_out = df_count.merge(tot)
    df_out['Proportion'] = df_out['Count']/df_out['Total_Count']
    return df_out
    
def grouped_memory_certainty_df(df_regression):
    ph1_hr = grouped_memory_certainty(df_regression, rew_cat = '1', phase = 1)
    ph1_lr = grouped_memory_certainty(df_regression, rew_cat = '-1', phase = 1)
    ph2_hr = grouped_memory_certainty(df_regression, rew_cat = '1', phase = 2)
    ph2_lr = grouped_memory_certainty(df_regression, rew_cat = '-1', phase = 2)
    ph3_hr = grouped_memory_certainty(df_regression, rew_cat = '1', phase = 3)
    ph3_lr = grouped_memory_certainty(df_regression, rew_cat = '-1', phase = 3)
    new_hr = grouped_memory_certainty(df_regression, rew_cat = '1', phase = 'New')
    new_lr = grouped_memory_certainty(df_regression, rew_cat = '-1', phase = 'New')
    df_out = pd.concat([ph1_hr, ph1_lr, ph2_hr, ph2_lr, ph3_hr, ph3_lr, new_hr, new_lr])
    return df_out

def summary_stats(df_summary):
    print('Matching Task: Accuracy', np.mean(df_summary.loc[df_summary['Condition'].isin(['Overall Match Accuracy'])]['Value']),u"\u00B1", 
          stdev(df_summary.loc[df_summary['Condition'].isin(['Overall Match Accuracy'])]['Value']))
    print('Matching Task: Reaction time', np.mean(df_summary.loc[df_summary['Condition'].isin(['Overall Match RT'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['Overall Match RT'])]['Value']))
    print('Memory Test: Corrected Recognition', np.mean(df_summary.loc[df_summary['Condition'].isin(['CR Overall'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['CR Overall'])]['Value']))
    print('Memory Test: dprime', np.mean(df_summary.loc[df_summary['Condition'].isin(['DP Overall'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['DP Overall'])]['Value']))
    print('Memory Test: HR', np.mean(df_summary.loc[df_summary['Condition'].isin(['HR Overall'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['HR Overall'])]['Value']))
    print('Memory Test: FA', np.mean(df_summary.loc[df_summary['Condition'].isin(['FA Overall'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['FA Overall'])]['Value']))
    print('Memory Test: Reaction time', np.mean(df_summary.loc[df_summary['Condition'].isin(['Memory Test RT'])]['Value']),u"\u00B1",
          stdev(df_summary.loc[df_summary['Condition'].isin(['Memory Test RT'])]['Value']))

 
exp = '1b'
x1b = df_files(exp)
df_summary, df_trials, df_regression = preproc(x1b, DP_cutoff=0, filterby='None', img_or_word='img')
rew_counts = df_summary.loc[df_summary['Condition'].isin(['Rewarded Category'])].Value
print('Check conditions are counter-balanced:', rew_counts.value_counts())
sex = df_summary.loc[df_summary['Condition'].isin(['Sex'])].Value
print('Sex breakdown:', sex.value_counts())
print('Summary Statistics:'+' Exp'+exp)
summary_stats(df_summary)

'''
# Make required folders
maindir = 'Exp'+exp+'_CleanData/'
if not os.path.exists(maindir):
    os.mkdir(maindir)
outdir = maindir+'/Main/'
if not os.path.exists(outdir):
    os.mkdir(outdir)
outdir_supp = maindir+'/Supp/'
if not os.path.exists(outdir_supp):
    os.mkdir(outdir_supp)
    
# Save required dfs
df_trials.to_csv(os.path.join(outdir,'x'+exp+'_Anova.csv'))
df_regression.to_csv(os.path.join(outdir,'x'+exp+'_Regression.csv'))
df_summary.to_csv(os.path.join(outdir_supp,'x'+exp+'.csv'))
df_certainty =  grouped_memory_certainty_df(df_regression)
df_certainty.to_csv(os.path.join(outdir_supp,'x'+exp+'_Certainty.csv'))
'''
'''
df_summary_high, df_trials_high, df_regression = preproc(x1a, DP_cutoff=0, filterby='High', img_or_word='img')
# Save required dfs
df_trials_high.to_csv(os.path.join(outdir,'x'+exp+'_High_Anova.csv'))
df_summary_high.to_csv(os.path.join(outdir_supp,'x'+exp+'_High.csv'))
'''
