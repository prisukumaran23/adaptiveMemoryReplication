#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Last edited: 15/01/2022 @Priyanka Sukumaran
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

script_location = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_location)

pd.options.mode.chained_assignment = None  # default='warn'

sns.set_theme()
matplotlib.rc('figure', figsize=(8, 5))

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
    data = unparsed_data[["stim_eng","responses","type","response",
                             "rt","category","trial_id","correct", "phase"]]
    age = re.sub("[^\d\.]", "", data.iloc[2,1])
    sex = re.sub(r'[^\w]', '', data.iloc[3,1])
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

def find_rew_cat(data):
    ''' Returns the category which was rewarded higher for given participant  '''
    rew = data.loc[data['trial_id'].isin(['prolificID'])]
    rew_reset = rew.reset_index()
    high_rew = []
    low_rew = []
    if rew_reset['condition'][0] != rew_reset['condition'][1]:
        print(rew_reset['condition'][0],rew_reset['condition'][1],get_ID(data))
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

def calc_bonus(data):
    high_rew,low_rew,subgroup = find_rew_cat(data)
    match_data = data.loc[data['trial_id'].isin(['match'])]
    match_data = match_data.loc[match_data['phase'].isin(['Phase 1','Phase 2'])]
    if exp == '2a' or exp == '3':
        conditioned_match_data = match_data.loc[match_data['phase'].isin(['Phase 2'])]  # phase 2 is the conditioning phase in experiment 2a
    elif exp == '2b':
        conditioned_match_data = match_data.loc[match_data['phase'].isin(['Phase 1'])]  # phase 1 is the conditioning phase in experiment 2b
    else:         
        raise Exception('Experiment not found.')
    high_rew_match = conditioned_match_data.loc[conditioned_match_data['category'].isin([high_rew])]
    low_rew_match = conditioned_match_data.loc[conditioned_match_data['category'].isin([low_rew])]
    high_rew_match_count = high_rew_match['correct'].value_counts()
    low_rew_match_count = low_rew_match['correct'].value_counts()
    bonus = 0
    if high_rew_match_count[1] > 26:
        bonus += 5
    if low_rew_match_count[1] > 26:
        bonus += 0.25
    return bonus

def calc_match_acc(data):
    '''Accuracy was calculated based on correct matching within the given time (600ms). 
    Null responses (took more than 600ms to respond) were counted as incorrect.'''
    high_rew,low_rew,subgroup = find_rew_cat(data)
    match_data = data.loc[data['trial_id'].isin(['match'])]
    match_data = match_data.loc[match_data['phase'].isin(['Phase 1','Phase 2'])]
    match_count = match_data['correct'].value_counts()
    match_RT = np.mean(match_data[match_data['rt'].notna()]['rt'])
    
    ph1_match_data = match_data.loc[match_data['phase'].isin(['Phase 1'])]
    ph2_match_data = match_data.loc[match_data['phase'].isin(['Phase 2'])] 
    
    ph1_high = ph1_match_data.loc[ph1_match_data['category'].isin([high_rew])]
    ph1_low = ph1_match_data.loc[ph1_match_data['category'].isin([low_rew])]
    ph2_high = ph2_match_data.loc[ph2_match_data['category'].isin([high_rew])]
    ph2_low = ph2_match_data.loc[ph2_match_data['category'].isin([low_rew])]
    
    ph1_high_MA = ph1_high['correct'].value_counts()[1]
    ph1_low_MA = ph1_low['correct'].value_counts()[1]
    ph2_high_MA = ph2_high['correct'].value_counts()[1]
    ph2_low_MA = ph2_low['correct'].value_counts()[1]
        
    ph1_high_RT =  np.mean(ph1_high[ph1_high['rt'].notna()]['rt'])
    ph1_low_RT = np.mean(ph1_low[ph1_low['rt'].notna()]['rt'])
    ph2_high_RT = np.mean(ph2_high[ph2_high['rt'].notna()]['rt'])
    ph2_low_RT = np.mean(ph2_low[ph2_low['rt'].notna()]['rt'])
    out = [ph1_high_MA/30, ph1_low_MA/30, ph2_high_MA/30, ph2_low_MA/30,
           ph1_high_RT, ph1_low_RT, ph2_high_RT, ph2_low_RT, 
           match_count[1]/120, match_RT]
    return out
    
def get_phase(data):
    match_data = data.loc[data['trial_id'].isin(['match'])]
    ph1_match_data = match_data.loc[match_data['phase'].isin(['Phase 1'])]
    ph1_keys = ph1_match_data['stim_eng'].reset_index()
    ph2_match_data = match_data.loc[match_data['phase'].isin(['Phase 2'])]
    ph2_keys = ph2_match_data['stim_eng'].reset_index()
    return ph1_keys, ph2_keys

def get_survey(data):
    surveys = data.loc[data['trial_type'].isin(['survey-text'])]
    surveys = surveys.loc[surveys['trial_index']>200]['responses']
    surveys = surveys.reset_index()
    if exp == '2a' or exp == '2b':
        out = surveys.responses[0],surveys.responses[1]
    elif exp == '3' :
        out = surveys.responses[0],surveys.responses[0]
    return out

def filter_highcert(memory_data, filterby):
    if filterby == 'High':
        memory_data = memory_data[memory_data['response'].isin(['0','12','60','72'])]
    elif filterby == 'Highest':
        memory_data = memory_data[memory_data['response'].isin(['0','72'])]
    elif filterby == 'None':
        memory_data = memory_data
    return memory_data

def calc_mem_RT(memory_data):
    memory_data = memory_data.loc[memory_data['trial_id'].isin(['rec_memory'])]
    RT = np.mean(memory_data['rt'])
    return RT

def calc_CR_ph(old_imgs,memory_data):
    hits = old_imgs.loc[old_imgs['correct'].isin(['1'])]['correct'].count()/len(old_imgs)
    new_imgs = memory_data.loc[memory_data['type'].isin(['new_img'])]
    fa = new_imgs.loc[new_imgs['correct'].isin(['0'])]['correct'].count()/len(new_imgs) #common fa rate
    CR = hits-fa  
    return CR

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
  
def create_summary_df(data, filterby):
    ''' filterby: 'None', High' or 'Highest' '''
    ID = get_ID(data)
    high_rew,low_rew,subgroup = find_rew_cat(data)
    memory_data = data.loc[data['trial_id'].isin(['rec_memory'])]
    memory_data = memory_data[memory_data['response'].notna()]    #remove nan in response
    memory_data = filter_highcert(memory_data,filterby)
    
    percent_correct = memory_data['correct'].value_counts()[1]/len(memory_data) 
    high_memory = memory_data.loc[memory_data['category'].isin([high_rew+'s'])]
    low_memory = memory_data.loc[memory_data['category'].isin([low_rew+'s'])]
    ph1_keys,ph2_keys =  get_phase(data)
    
    ph1_high = ph1_keys.merge(high_memory, left_on='stim_eng', right_on='stim_eng',how='inner')
    ph1_low = ph1_keys.merge(low_memory, left_on='stim_eng', right_on='stim_eng',how='inner')
    ph2_high = ph2_keys.merge(high_memory, left_on='stim_eng', right_on='stim_eng',how='inner')
    ph2_low = ph2_keys.merge(low_memory, left_on='stim_eng', right_on='stim_eng',how='inner')
    
    data_summary = [[ID,'Overall PC', percent_correct],
                    [ID, 'Age', get_demographics(data)[0]],
                    [ID, 'Sex', get_demographics(data)[1]],
                    [ID, 'Bonus', calc_bonus(data)],
                    [ID, 'Overall Match Accuracy', calc_match_acc(data)[8]],
                    [ID, 'Overall Match RT', calc_match_acc(data)[9]],

                    [ID, 'CR Overall', calc_CR(memory_data)],
                    [ID, 'HR Overall', calc_HR_FA(memory_data)[0]],
                    [ID, 'FA Overall', calc_HR_FA(memory_data)[1]],
                    [ID, 'CR Overall High Reward', calc_CR(high_memory)],
                    [ID, 'CR Overall Low Reward', calc_CR(low_memory)],
                    [ID, 'CR Ph1 High Reward', calc_CR_ph(ph1_high,high_memory)],
                    [ID, 'CR Ph1 Low Reward', calc_CR_ph(ph1_low,low_memory)],
                    [ID, 'CR Ph2 High Reward', calc_CR_ph(ph2_high,high_memory)],
                    [ID, 'CR Ph2 Low Reward', calc_CR_ph(ph2_low,low_memory)],
                    
                    [ID, 'DP Overall', calc_DP(memory_data)],
                    [ID, 'DP Overall High Reward', calc_DP(high_memory)],
                    [ID, 'DP Overall Low Reward', calc_DP(low_memory)],
                    [ID, 'DP Ph1 High Reward', calc_DP_ph(ph1_high,high_memory)],
                    [ID, 'DP Ph1 Low Reward', calc_DP_ph(ph1_low,low_memory)],
                    [ID, 'DP Ph2 High Reward', calc_DP_ph(ph2_high,high_memory)],
                    [ID, 'DP Ph2 Low Reward', calc_DP_ph(ph2_low,low_memory)],
                    
                    #[ID, 'PHQ Score', get_phq(data)[0]],
                    #[ID, 'PHQ Attention Check', get_phq(data)[1]],
                    
                    [ID, 'Memory Test RT', calc_mem_RT(memory_data)],
                    [ID, 'Rewarded Category', high_rew],
                    [ID, 'End Survey', get_survey(data)[0]]]
                    #[ID, 'End Survey2', get_survey(data)[1]]]
    
    data_trials = [[ID, subgroup, high_rew, 'Ph1', 'High Reward', 
                    calc_CR_ph(ph1_high,high_memory), calc_DP_ph(ph1_high,high_memory),
                    calc_match_acc(data)[0], calc_match_acc(data)[4], calc_RB_ph(ph1_high,high_memory),
                    calc_HR_FA_ph(ph1_high,high_memory)[0],calc_HR_FA_ph(ph1_high,high_memory)[1]],
                   [ID, subgroup, low_rew, 'Ph1', 'Low Reward', 
                    calc_CR_ph(ph1_low,low_memory), calc_DP_ph(ph1_low,low_memory),
                    calc_match_acc(data)[1], calc_match_acc(data)[5],calc_RB_ph(ph1_low,low_memory),
                    calc_HR_FA_ph(ph1_low,low_memory)[0],calc_HR_FA_ph(ph1_low,low_memory)[1]],
                   [ID, subgroup, high_rew, 'Ph2', 'High Reward', 
                    calc_CR_ph(ph2_high,high_memory), calc_DP_ph(ph2_high,high_memory),
                    calc_match_acc(data)[2], calc_match_acc(data)[6],calc_RB_ph(ph2_high,high_memory),
                    calc_HR_FA_ph(ph2_high,high_memory)[0],calc_HR_FA_ph(ph2_high,high_memory)[1]],
                   [ID, subgroup, low_rew, 'Ph2', 'Low Reward', 
                    calc_CR_ph(ph2_low,low_memory), calc_DP_ph(ph2_low,low_memory),
                    calc_match_acc(data)[3], calc_match_acc(data)[7],calc_RB_ph(ph2_low,low_memory),
                    calc_HR_FA_ph(ph2_low,low_memory)[0],calc_HR_FA_ph(ph2_low,low_memory)[1]]]
    
    df_summary_part = pd.DataFrame(data_summary, columns = ['UserID','Condition','Value'])
    df_trials_part = pd.DataFrame(data_trials, columns = ['UserID','Rew_Subgroup','Category','Phase','Reward_Category','CR','DP','MA','RT','RB','HR','FA'])
    
    return df_summary_part, df_trials_part

def match_data_create(data):
    match_data = data[["trial_id","phase","rt","stim_eng","correct"]]
    match_data = match_data.loc[match_data["phase"].isin(['Phase 1','Phase 2'])] 
    match_data = match_data.loc[match_data["trial_id"].isin(['match'])] 
    match_data = match_data.rename({'rt': 'match_rt'}, axis='columns') # rename column correct to match word
    match_data = match_data.rename({'correct': 'match_corr'}, axis='columns') # rename column correct to match word
    match_data = match_data.drop(columns=['phase','trial_id'])
    return match_data

def create_regression_df(unparsed_data):
    data = unparsed_data[["stim_eng","responses","type","response",
                             "rt","category","trial_id","correct", "phase"]]

    data = data.loc[data['phase'].isin(['Rec_Memory'])] # remove other trial data
    data = data.loc[data['trial_id'].isin(['rec_memory'])] # remove feedblack slide data
    data_new_imgs = data.loc[data['type'].isin(['new_img'])] 

    ph1_keys,ph2_keys = get_phase(unparsed_data)
    data_ph1 = ph1_keys.merge(data, left_on='stim_eng', right_on='stim_eng',how='inner')
    data_ph1.phase=1
    data_ph2 = ph2_keys.merge(data, left_on='stim_eng', right_on='stim_eng',how='inner')  
    data_ph2.phase=2
    data = data_ph1.append(data_ph2)
    data = data.append(data_new_imgs)
    
    data.insert(loc=0, column='rew_cat', value=data['category'])
    if find_rew_cat(unparsed_data)[0] == 'Object':
        data['rew_cat'] = data['rew_cat'].str.replace('Objects', '1')
        data['rew_cat'] = data['rew_cat'].str.replace('Animals', '-1')
    elif find_rew_cat(unparsed_data)[0] == 'Animal':
        data['rew_cat'] = data['rew_cat'].str.replace('Objects', '-1')
        data['rew_cat'] = data['rew_cat'].str.replace('Animals', '1')
    
    data.insert(loc=0, column='Age', value=get_demographics(unparsed_data)[0])
    data.insert(loc=0, column='Sex', value=get_demographics(unparsed_data)[1])
    data.insert(loc=0, column='Rew_Subgroup', value=[find_rew_cat(unparsed_data)[0]] * len(data))
    data.insert(loc=0, column='UserID', value=[get_ID(unparsed_data)] * len(data))  
    
    match_data = match_data_create(unparsed_data)
    df_regression_part = data.merge(match_data, left_on='stim_eng', right_on='stim_eng',how='left')
    df_regression_part = df_regression_part.drop(columns=['responses','trial_id','index'])
    
    df_regression_part = df_regression_part.rename(columns={"rew_cat_name":"Rew_Subgroup", "rew_cat":"Reward_Category", 
                                              "category":"Category", "phase":"Phase", "stim_eng":"Stim", "type":"Stim_Type",
                                              "response":"Certainty", "match_rt":"Match_RT", "match_corr":"Match_Correct", 
                                              "rt":"Memory_RT", "correct":"Memory_Correct"})
    return df_regression_part

def concat_dfs(matched_files, filterby):
    for file in range(len(matched_files)):
       part_data = matched_files[file]
       df_summary_part,df_trials_part = create_summary_df(part_data, filterby)
       df_regression_part = create_regression_df(part_data)
       if file==0:
           df_summary = df_summary_part.copy()
           df_trials = df_trials_part.copy()
           df_regression = df_regression_part.copy()
       if file>0:
           df_summary = pd.concat([df_summary,df_summary_part])
           df_trials = pd.concat([df_trials,df_trials_part])  
           df_regression = pd.concat([df_regression,df_regression_part])  
    return df_summary, df_trials, df_regression

def remove_low_MA(df_summary, df_trials, df_regression, MA_cutoff):
    '''Exclusion E1: Below chance performance in matching test.
    Participant is excluded if overall matching accuracy in matching task below chance (taken as 60%).'''
    MA = df_summary.loc[df_summary['Condition'].isin(['Overall Match Accuracy'])]
    reject = MA['UserID'].loc[MA['Value']<=MA_cutoff]
    reset_reject = reject.reset_index()
    for ids in range(len(reset_reject)):
        rejectID = reset_reject['UserID'][ids]
        print('Matching accuracy below chance in matching task, exclude:',rejectID)
        df_summary = df_summary[~df_summary.UserID.str.contains(rejectID)]
        df_trials = df_trials[~df_trials.UserID.str.contains(rejectID)]
        df_regression = df_regression[~df_regression.UserID.str.contains(rejectID)]
    return df_summary, df_trials, df_regression, reject    

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

def preproc(matched_files, DP_cutoff=0, MA_cutoff=0.6, filterby='None'):
    """
    Args
    ----
    matched_files : dict 
        output of match_files function (participant data)
    
    DP_cutoff : int
        reject participants with overall dprime score below DP_cutoff (default = 0 as chance)
        
    MA_cutoff : int
        reject participants with overall matching accuracy on delayed match task below MA_cutoff (default = 0.6 as chance)

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
    df_summary,df_trials,df_regression = concat_dfs(matched_files,'None')
    df_summary,df_trials,df_regression,rejectID2=remove_low_DP(df_summary,df_trials,df_regression,DP_cutoff)
    df_summary,df_trials,df_regression,rejectID3=remove_low_MA(df_summary,df_trials,df_regression,MA_cutoff)
    df_summary,df_trials,df_regression,rejectID4=remove_outlier_RT(df_summary,df_trials,df_regression)
    rejectIDs = rejectID2.append(rejectID3)
    rejectIDs = rejectIDs.append(rejectID4)
    if filterby == 'None':
        return df_summary,df_trials,df_regression
    elif filterby != 'None':
        df_summary, df_trials, df_regression = concat_dfs(matched_files,filterby)
        rejectIDs = rejectIDs.reset_index()
        for ids in range(len(rejectIDs)):
            rejectID = rejectIDs['UserID'][ids]
            df_summary = df_summary[~df_summary.UserID.str.contains(rejectID)]
            df_trials = df_trials[~df_trials.UserID.str.contains(rejectID)]
            df_regression = df_regression[~df_regression.UserID.str.contains(rejectID)]
        return df_summary, df_trials, df_regression
    return df_summary, df_trials, df_regression

def plot_memvphase(plot_data, memorytype, title,ylabel, ytick_labels, ylimtop, ylimbot):
    sns.set(font_scale=1.5)
    plot_data.insert(loc=0,column='Phase',value=plot_data['Condition'])
    plot_data.insert(loc=0,column='Reward Category',value=plot_data['Condition'])
    plot_data['Phase'] = plot_data['Phase'].str.replace(memorytype+' Ph1 High Reward','Phase 1')
    plot_data['Reward Category'] = plot_data['Reward Category'].str.replace(memorytype+' Ph1 High Reward','High Reward')
    plot_data['Phase'] = plot_data['Phase'].str.replace(memorytype+' Ph2 High Reward','Phase 2')
    plot_data['Reward Category'] = plot_data['Reward Category'].str.replace(memorytype+' Ph2 High Reward','High Reward')
    plot_data['Phase'] = plot_data['Phase'].str.replace(memorytype+' Ph1 Low Reward','Phase 1')
    plot_data['Reward Category'] = plot_data['Reward Category'].str.replace(memorytype+' Ph1 Low Reward','Low Reward')
    plot_data['Phase'] = plot_data['Phase'].str.replace(memorytype+' Ph2 Low Reward','Phase 2')
    plot_data['Reward Category'] = plot_data['Reward Category'].str.replace(memorytype+' Ph2 Low Reward','Low Reward')
    plt.title(title, size=22)         
    col = np.array([sns.color_palette("dark")[2],sns.color_palette("dark")[1],sns.color_palette("dark")[2],sns.color_palette("dark")[1]])    
    ax3 = sns.pointplot(x="Phase", y="Value", hue='Reward Category', scale = 2.5,data=plot_data,palette=col,markers="_",
                        estimator=np.mean,ci=68,capsize=.05,dodge=0.4, linestyles=["",""])
    ax3.set_ylim(top=ylimtop,bottom=ylimbot)
    for p in ax3.collections:
        for of in p.get_offsets():
            ax3.annotate(format(of[1], '.2f'),of,ha='center',va='center',size=14, 
                         weight="bold", xytext=(-28,0), textcoords='offset points')
    col_muted = np.array([sns.color_palette("muted")[2],sns.color_palette("muted")[1],
                          sns.color_palette("muted")[2],sns.color_palette("muted")[1]])    
    ax3 = sns.stripplot(x="Phase", y="Value",hue='Reward Category',data=plot_data,dodge=True,marker="o",size=9, 
                        jitter=0.2,palette=col_muted,alpha=.2)
    ax3.set(ylabel = ylabel)
    ax3.set_xticklabels(ytick_labels)
    rew_legend = mpatches.Patch(color=sns.color_palette("dark")[2], label='R+ High Reward')
    handles, labels = ax3.get_legend_handles_labels()
    unrew_legend = mpatches.Patch(color=sns.color_palette("dark")[1], label='R- Low Reward')
    plt.legend(handles=[rew_legend,unrew_legend], loc='upper right') 
    plt.show()
    return plt

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
        'New' for new items
        
    Returns
    -------
    df : pandas DataFrame 
        Reponse to memory test by certainty grouped by participant UserID
    '''
    df_all = df_all.replace('Rec_Memory', 'New')
    df_all = df_all.loc[df_all['Certainty'].isin(['0','12','24','48','60','72'])]
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
    new_hr = grouped_memory_certainty(df_regression, rew_cat = '1', phase = 'New')
    new_lr = grouped_memory_certainty(df_regression, rew_cat = '-1', phase = 'New')
    df_out = pd.concat([ph1_hr, ph1_lr, ph2_hr, ph2_lr, new_hr, new_lr])
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

def create_clean_data(exp):
    '''exp: '2a' or '2b' or '3' '''
    if exp == '2a':
        path = 'adaptiveMemoryReplication/Exp2a_RawData/' # Change to Github path
        phase_labels = ['Pre-Conditioning Phase','Conditioning Phase']
    elif exp == '2a':
        path = 'adaptiveMemoryReplication/Exp2a_RawData/' # Change to Github path
        phase_labels = ['Pre-Conditioning Phase','Conditioning Phase']
    elif exp == '3':
        path = 'adaptiveMemoryReplication/Exp3_RawData/'
        phase_labels = ['Pre-Conditioning Phase','Conditioning Phase']
    else:
        raise Exception('Experiment not found.')        
    matched_files = match_files(path)
    
    df_summary, df_trials, df_regression = preproc(matched_files, DP_cutoff=0, MA_cutoff=0.6, filterby='None')
    df_survey = df_summary.loc[df_summary['Condition'].isin(['End Survey'])]
    df_certainty =  grouped_memory_certainty_df(df_regression)
    rew_counts = df_summary.loc[df_summary['Condition'].isin(['Rewarded Category'])].Value
    print('Check conditions are counter-balanced:', rew_counts.value_counts())
    sex = df_summary.loc[df_summary['Condition'].isin(['Sex'])].Value
    print('Sex breakdown:', sex.value_counts())
    print('Summary Statistics:'+' Exp'+exp)
    summary_stats(df_summary)
    
    # Repeat analysis with only high certainty responses 
    df_summary_high, df_trials_high, df_regression = preproc(matched_files,DP_cutoff=0, MA_cutoff=0.6, filterby='High')
    print('Summary Statistics:'+' Exp'+exp+' High Certainty Memory')
    summary_stats(df_summary_high)
    
    # Make required folders
    maindir = 'Exp'+exp+'_CleanData'
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
    df_survey.to_csv(os.path.join(outdir_supp,'x'+exp+'_Survey.csv'))
    df_certainty.to_csv(os.path.join(outdir_supp,'x'+exp+'_Certainty.csv'))
    df_trials_high.to_csv(os.path.join(outdir,'x'+exp+'_High_Anova.csv'))
    df_summary_high.to_csv(os.path.join(outdir_supp,'x'+exp+'_High.csv'))
    
    # Plot main results
    plot_data = df_summary.loc[df_summary['Condition'].isin(['CR Ph1 Low Reward','CR Ph1 High Reward','CR Ph2 Low Reward','CR Ph2 High Reward'])]
    plt1 = plot_memvphase(plot_data,'CR',"Experiment "+exp+" (All Memory)","Corrected Recognition",phase_labels,1.3,-0.1)
    plt1.show()
    plot_data = df_summary.loc[df_summary['Condition'].isin(['DP Ph1 Low Reward','DP Ph1 High Reward','DP Ph2 Low Reward','DP Ph2 High Reward'])]
    plt2 = plot_memvphase(plot_data,'DP',"Experiment "+exp+" (All Memory)","dprime",phase_labels,5,0)
    plt2.show()
    plot_data = df_summary_high.loc[df_summary_high['Condition'].isin(['CR Ph1 Low Reward','CR Ph1 High Reward','CR Ph2 Low Reward','CR Ph2 High Reward'])]
    plt3 = plot_memvphase(plot_data,'CR',"Experiment "+exp+" (High Certainty)","Corrected Recognition",phase_labels,1.3,-0.1)
    plt3.show()
    plot_data = df_summary_high.loc[df_summary_high['Condition'].isin(['DP Ph1 Low Reward','DP Ph1 High Reward','DP Ph2 Low Reward','DP Ph2 High Reward'])]
    plt4 = plot_memvphase(plot_data,'DP',"Experiment "+exp+" (High Certainty)","dprime",phase_labels,5,0)
    plt4.show()
    
# Experiments with different conditioning paradigms 
exp='2a'
create_clean_data(exp)
