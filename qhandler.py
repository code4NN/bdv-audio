import streamlit as st
import os
import pytz
import datetime
import pandas as pd

from custom_module.mega.mega.mega import Mega
import gdown

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import subprocess
import io
# import ffmpeg

def query_handler(app):
    
    query_dict = st.query_params
    
    user = query_dict.get('user','blank')
    lecture_encrypt_id = query_dict.get('id', 'blank')
    sindhu = query_dict.get('sindhu', 'blank')
    
    
    if lecture_encrypt_id == 'blank' or sindhu == 'blank' :
        st.warning("the url is incorrect; absent id or sindhu")
        st.stop()
    
    # get the lecture info dict and push user etc info to a sheet
    if sindhu =='vani':
        configdf = pd.read_excel('config_file.xlsx', sheet_name='vani')
        
        file_exists = configdf.query(f"encrypt_id=='{lecture_encrypt_id}'").shape[0] > 0
        
        if not file_exists:
            st.warning("the url is incorrect; file not found")
            st.stop()
        
        lectureinfo = (configdf.query(f"encrypt_id=='{lecture_encrypt_id}'")
                       .reset_index(drop=True)
                       .to_dict(orient='index')[0])
        lectureinfo = {
            'user':user,
            'sindhu':sindhu,
            
            'server':lectureinfo['server_type'],
            'lecture_name': lectureinfo['display_name'],
            'lec_encrypt_id': lecture_encrypt_id,
            'lec_download_id': lectureinfo['file_id']
        }
                        
    elif sindhu =='spvani':
        configdf = pd.read_excel('config_file.xlsx', sheet_name='spvani')
        
        file_exists = configdf.query(f"encrypt_id=='{lecture_encrypt_id}'").shape[0] > 0
        if not file_exists:
            st.warning("the url is incorrect; file not found")
            st.stop()
        
        lectureinfo = (configdf.query(f"encrypt_id=='{lecture_encrypt_id}'")
                       .reset_index(drop=True)
                       .to_dict(orient='index')[0])
        lectureinfo = {
            'user':user,
            'sindhu':sindhu,
            
            'server': 'mega',
            'lecture_name': lectureinfo['full_name'],
            'lec_encrypt_id': lecture_encrypt_id,
            'lec_download_id': lectureinfo['server_id']
        }
    
    else:
        st.warning("the url is incorrect; sindhu is incorrect")
        st.stop()
    app.lecture_info= lectureinfo
    
    # for sharing of clips
    start_time = query_dict.get('ss','no')
    duration = query_dict.get('dur','no')
    clip_name = query_dict.get('name','no')
    # st.write([i=='no' for i in [start_time,duration,clip_name]])
    if sum([i=='no' for i in [start_time,duration,clip_name]])==0:
        # valid clip URL
        start_time = int(start_time)
        duration = int(duration)
        app.clip_info_dict = {
            "start_time":start_time,
            "duration":duration,
            "clip_name":clip_name
        }
        app.page_is_sharedclip = True
    
            
def bring_lecture_by_id(root_dir,lec_encrypt_id,lec_id, server):
    # root_dir,lec_encrypt_id,lec_id,server)
    
    filename = f"{lec_encrypt_id}.mp3"
    
    available_file_raw = os.listdir(root_dir)
    available_files = [i.split("^")[1] for i in available_file_raw]    
    file_exists = filename in available_files
    
    if server =='yt':
        pass
        
    if not file_exists:
        MAX_LECTURE_STORE = 10
        
        sorted_available_files = sorted(available_file_raw,
                                        key=lambda x: int(x.split("^")[0]),
                                        reverse=True)
        for one_file in sorted_available_files[MAX_LECTURE_STORE:]:
            os.remove(f"{root_dir}/{one_file}")
        
        msgbox = st.empty()
        download_url = ''
        url = ''
        india_timezone = pytz.timezone('Asia/Kolkata')
        file_prefix = (datetime.datetime.now(india_timezone)
                    .strftime("%d%H%M%S"))
        filename = f"{file_prefix}^{filename}"
        
        if server =='mega':
            download_url = f"https://mega.co.nz/#!{lec_id}"
            with msgbox.container():
                st.markdown(f"downloading from mega ")
                st.caption("This may take a while please wait ...")
                mega_connection = Mega()
                mega_connection.download_url(download_url,
                                                root_dir,
                                                dest_filename=filename)
                st.success("completed")
            msgbox.empty()
        
        elif server =='drive':
            download_url = f"https://drive.google.com/uc?id={lec_id}&export=download"
            url = f"https://drive.google.com/uc?id={lec_id}"
            with msgbox.container():
                st.markdown(f"downloading from drive ")
                st.caption("This may take a while please wait ...")
                gdown.download(url, f"{root_dir}/{filename}", quiet=False, fuzzy=True)
                st.success("done")
            msgbox.empty()
        
    else:
        # change the filename so that it points to actual file
        existing_file = [i for i in available_file_raw if i.split("^")[1] == filename]
        filename = existing_file[0]
        download_url = ''
        url = ''
        
        # define the download urls etc
        if server =='mega':
            download_url = download_url = f"https://mega.co.nz/#!{lec_id}"
        
        elif server =='drive':
            download_url = f"https://drive.google.com/uc?id={lec_id}&export=download"
            url = f"https://drive.google.com/file/d/{lec_id}/view"
        
    return (f"{root_dir}/{filename}",download_url,url)
        
        
def store_log_sheet(lecinfo_dict,hit_type):
    
    if 'google_sheet_connection' not in st.session_state:
        sheet_id = st.secrets['database']['logger_sheet_id']
        credentials_info = st.secrets['service_account']
        SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
        ]
        
        gc = (gspread
            .authorize(ServiceAccountCredentials
                        .from_json_keyfile_dict(credentials_info,
                                                SCOPE)
                        )
            )
        
        workbook = gc.open_by_key(sheet_id)
        st.session_state['google_sheet_connection'] = workbook
    
    india_timezone = pytz.timezone('Asia/Kolkata')
    timestamp = (datetime.datetime.now(india_timezone)
                .strftime("%Y-%m-%d %H:%M:%S"))
    
    if hit_type =='hearnow':
        upload_array_final = [[
            timestamp,
            lecinfo_dict['server'],
            lecinfo_dict['sindhu'],
            lecinfo_dict['lec_encrypt_id'],
            lecinfo_dict['lecture_name'],
            lecinfo_dict['user']
        ]]
        
        
        workbook = st.session_state['google_sheet_connection']
        (workbook
        .worksheet('url_hits')
        .append_rows(values=upload_array_final,
                    value_input_option='USER_ENTERED',
                    table_range='A:F'))
    
    elif hit_type =="clip":
        upload_array_final = [[
            timestamp,
            lecinfo_dict['server'],
            lecinfo_dict['sindhu'],
            lecinfo_dict['lec_encrypt_id'],
            lecinfo_dict['lecture_name'],
            lecinfo_dict['clip_url'],
            lecinfo_dict['clip_name'],
            lecinfo_dict['clip_duration'],
            lecinfo_dict['clip_maker']
        ]]
        
        
        workbook = st.session_state['google_sheet_connection']
        (workbook
        .worksheet('clip_hits')
        .append_rows(values=upload_array_final,
                    value_input_option='USER_ENTERED',
                    table_range='A:I'))
    
    elif hit_type =="shared_clip":
        upload_array_final = [[
            timestamp,
            lecinfo_dict['server'],
            lecinfo_dict['sindhu'],
            lecinfo_dict['lec_encrypt_id'],
            lecinfo_dict['lecture_name'],
            lecinfo_dict['clip_url'],
            lecinfo_dict['clip_name'],
            lecinfo_dict['clip_duration'],
            lecinfo_dict['clip_maker']
        ]]
        
        
        workbook = st.session_state['google_sheet_connection']
        (workbook
        .worksheet('shared_clip_hits')
        .append_rows(values=upload_array_final,
                    value_input_option='USER_ENTERED',
                    table_range='A:I'))
    

def clip_audio_to_memory(input_file_path, start_time, duration):
    output_buffer = io.BytesIO()

    # Construct the ffmpeg command
    command = [
        'ffmpeg',
        '-i', input_file_path,         # Input file
        '-ss', str(start_time),   # Start time
        '-t', str(duration),      # Duration
        '-f', 'mp3',              # Output format
        '-'
    ]
    
    # Run the command and capture stdout
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    output_buffer.write(process.stdout)
    output_buffer.seek(0)  # Reset buffer position to the start
    
    return output_buffer    
        
        
        