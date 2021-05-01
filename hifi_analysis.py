import pandas as pd
import numpy as np
import itertools
from bs4 import BeautifulSoup
import requests
from requests import get
import time
from random import seed
from random import random
from random import randint
import re
import sys


#Scraping web page for data and appendig it to a list
url = 'https://www.hifiengine.com/database/hifi_database.php?model_type=amp&make=Sony&mdl='
amps = []
count = 1

while count <= 12 :
    new_count = 0
    if count == 1 :
        first_page = 'https://www.hifiengine.com/database/hifi_database.php?model_type=amp&make=Sony&mdl='
        response = get(first_page)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        amp_data = html_soup.find_all('div', class_="mod-data")

        if amp_data != [] :
            amps.extend(amp_data)
            value = random()
            scaled_value = 1 + (value * (9 - 5))
            time.sleep(scaled_value)
    elif count != 1:
        url = 'https://www.hifiengine.com/database/hifi_database.php?model_type=amp&make=Sony&mdl=' + '&page=' + str((count-1)*20)
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        amp_data = html_soup.find_all('div', class_="mod-data")

        if amp_data != [] :
            amps.extend(amp_data)
            value = random()
            scaled_value = 1 + (value * (9 - 5))
            time.sleep(scaled_value)

        else :
            break

    count += 1

#define initial column names
c0 = "Name"
c1 = "Power Output"
c2 = "Frequency Response"
c3 = "Distortion"
c4 = "Signal to Noise Ratio"
c5 = "Dimensions"
c6 = "Weight"

#create dataframe
df = pd.DataFrame(columns=['name','power_output','frequency_response','distortion','signal_to_noise_ratio','dimensions','weight'])

#fill dataframe with data from scraped html bits
for item in amps :

    name = item.find("a").get_text()
    power = item.find("b", text=c1).find_parent("div").get_text().replace(c1,'')
    freq_res = item.find("b", text=c2).find_parent("div").get_text().replace(c2,'')
    dist = item.find("b", text=c3).find_parent("div").get_text().replace(c3,'')
    stn_ratio = item.find("b", text=c4).find_parent("div").get_text().replace(c4,'')
    dimens = item.find("b", text=c5).find_parent("div").get_text().replace(c5,'')
    weight = item.find("b", text=c6).find_parent("div").get_text().replace(c6,'')


    df = df.append({'name': name, 'power_output': power,'frequency_response': freq_res,'distortion': dist,'signal_to_noise_ratio': stn_ratio,'dimensions': dimens,'weight': weight},ignore_index=True)


def get_inches(el):
    list1=el.split('-')
    v1 = float(list1[0])
    list2 = list1[1].split('/')
    v2 = float(list2[0])
    v3 = float(list2[1])
    v = (v1 + (v2/v3))*25.4
    return v


#weight data processing
def weight_conversion(input_w) :
    if input_w != '':
        input_s = str(input_w)
        if 'lb' in input_s :
            input_s = input_s[:-3]
            ret = float(input_s)/2.2
        else :
            input_s = input_s[:-3]
            ret = float(input_s)
    else :
        ret = np.nan
    return ret

# extract min and max tresholds from 'frequency_response' data
def hz_strip(inp) :
    if inp == '' :
        ret = np.nan
    else :
        ret = float(inp[:-2])
    return ret

def khz_strip(inp) :
    if inp == '' or inp is None:
        ret = np.nan
    else :
        ret = float(inp[:-3])*1000
    return ret

def percent_strip(inp):
    if inp == '':
        ret = np.nan
    else:
        ret = float(inp[:-1])
    return ret


# separate 'dimensions' data to three different columns
def separate_dim_x(row):
    if row['dimensions'] == '' :
        ret = np.nan
    else :
        ret1 = row['dimensions'].replace('  ',' x ').split('x')
        ret = ret1[0].strip()
        if '"' in row['dimensions'] :
            ret = get_inches(ret)
        else :
            ret = float(ret)
    return ret

def separate_dim_y(row):
    if row['dimensions'] == '':
        ret = np.nan
    else :
        ret1 = row['dimensions'].replace('  ',' x ').split('x')
        ret = ret1[1].strip()
        if '"' in row['dimensions'] :
            ret = get_inches(ret)
        else :
            ret = float(ret)
    return ret

def separate_dim_z(row):
    if row['dimensions'] == '' :
        ret = np.nan
    else :
        ret1 = row['dimensions'].replace('  ',' x ').split('x')
        ret = ret1[2].strip()

        if '"' in row['dimensions'] :
            ret = ret[:-1]
            ret = ret.strip()
            ret = get_inches(ret)
        else :
            ret = float(ret[:-2])
    return ret

# Split 'signal_to_noise_ratio' data to different types
def stn_process_line(row) :
    if row['signal_to_noise_ratio'] == '':
        ret = np.nan
    else:
        list1 = row['signal_to_noise_ratio'].split(',')
        for item in list1 :
            if '(line)' in item:
                ret = item.strip("dB (line)" )
                ret = int(ret)
                break
            else :
                ret = np.nan
    return ret

def stn_process_mm(row) :
    if row['signal_to_noise_ratio'] == '' :
        ret = np.nan
    else :

        list1 = row['signal_to_noise_ratio'].split(',')
        for item in list1 :
            if '(mm)' in item:
                ret = item.strip("dB (mm)" )
                ret = int(ret)
                break
            else :
                ret = np.nan
    return ret

def stn_process_mic(row) :
    if row['signal_to_noise_ratio'] == '' :
        ret = np.nan
    else:
        list1 = row['signal_to_noise_ratio'].split(',')
        for item in list1 :
            if '(mic)' in item:
                ret = item.strip("dB (mic)" )
                ret = int(ret)
                break
            else :
                ret = np.nan
    return ret

def stn_process_mc(row) :
    if row['signal_to_noise_ratio'] == '' :
        ret = np.nan
    else:
        list1 = row['signal_to_noise_ratio'].split(',')
        for item in list1 :
            if '(mc)' in item:
                ret = item.strip("dB (mc)" )
                ret = int(ret)
                break
            else :
                ret = np.nan
    return ret

#separate and extract power and impendace values from 'power_output' colums
def power_output_process(row):
    if row['power_output'] == '' :
        ret = np.nan
    elif "into" not in row['power_output'] and "W" in row['power_output'] :
        ret = row['power_output'].strip(" W (stereo)")
        ret = int(ret)

    else :
        list1 = row['power_output'].split(' into ')
        ret = list1[0].strip('W ')
        ret = int(ret)
    return ret

def power_output_impendance(row) :
    if row['power_output'] == '' :
        ret = np.nan
    elif "into" in row['power_output'] :
        list1 = row['power_output'].split(' into ')
        ret = list1[1].strip('\u2126 (stereo) ')
        ret = int(ret)
    else :
        ret = np.nan
    return ret


#add new columns to dataframe
df[['frequency_response_min', 'frequency_response_max']] = df['frequency_response'].str.split(' to ', 1, expand=True)
df['weight'] = df['weight'].apply(weight_conversion)
df['frequency_response_min'] = df['frequency_response_min'].apply(hz_strip)
df['frequency_response_max'] = df['frequency_response_max'].apply(khz_strip)
df['distortion'] = df['distortion'].apply(percent_strip)
df['dimension_x'] = df.apply(lambda row : separate_dim_x(row), axis=1)
df['dimension_y'] = df.apply(lambda row : separate_dim_y(row), axis=1)
df['dimension_z'] = df.apply(lambda row : separate_dim_z(row), axis=1)
df['signal_to_noise_ratio_line'] = df.apply(lambda row : stn_process_line(row), axis=1)
df['signal_to_noise_ratio_mm'] = df.apply(lambda row : stn_process_mm(row), axis=1)
df['signal_to_noise_ratio_mic'] = df.apply(lambda row : stn_process_mic(row), axis=1)
df['signal_to_noise_ratio_mc'] = df.apply(lambda row : stn_process_mc(row), axis=1)
df['power_output_w'] = df.apply(lambda row : power_output_process(row), axis=1)
df['impendance'] = df.apply(lambda row : power_output_impendance(row), axis=1)

#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(df['weight'])

#Amp with broadest frequency response
a = df.loc[df['frequency_response_max'] == df['frequency_response_max'].max(), 'frequency_response_min'].idxmin()
s = df.loc[a]['name']
print('Amp with broadest frequency response:',s)

#Smallest amp:
df['volume'] = df['dimension_x']*df['dimension_y']*df['dimension_z']
ats2 = df.loc[df['volume'].idxmin()]['name']
print('Smallest amp:',ats2)

#Most powerfull amp
ats4 = df.loc[df['power_output_w'].idxmax()]['name']
print('Most powerfull amp:',ats4)

#best stn Ratio (line)
ats3 = df.loc[df['signal_to_noise_ratio_line'].idxmin()]['name']
print('Amp with best Signal to Noise Ratio (line):',ats3)
