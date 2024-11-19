import streamlit as st
import os,sys
import pytz
import datetime
import pandas as pd
import zipfile

from custom_module.mega.mega.mega import Mega
import gdown

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import subprocess
import io
# import ffmpeg

from streamlit.components.v1 import html as myHTML

def query_handler(app):
    
    query_dict = st.query_params
    
    user = query_dict.get('user','blank')
    lecture_encrypt_id = query_dict.get('id', 'blank')
    sindhu = query_dict.get('sindhu', 'blank')
    
    
    if lecture_encrypt_id == 'blank' or sindhu == 'blank' :
        st.markdown("### :rainbow[BDV audio services]")
        st.image("https://i.ytimg.com/vi/sIzVWf21J1g/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLA30SYKGDSfqO9blTj0xPX9WWQq9Q")
        st.markdown("* the app works in conjunction with the vani syllabus on notion")
        st.markdown("* and to provide audio player and trimmer for VANI syllabus and SP-sindhu lectures ")
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
        
        download_url = ''
        url = ''
        india_timezone = pytz.timezone('Asia/Kolkata')
        file_prefix = (datetime.datetime.now(india_timezone)
                    .strftime("%d%H%M%S"))
        filename = f"{file_prefix}^{filename}"
        
        msgbox = st.empty()
        if server =='mega':
            download_url = f"https://mega.co.nz/#!{lec_id}"
            with st.spinner("downloading from mega..."):
                msgbox.caption("may take sometime please wait...")
                mega_connection = Mega()
                mega_connection.download_url(download_url,
                                                root_dir,
                                                dest_filename=filename)
                msgbox.success("...done")
            msgbox.empty()
        
        elif server =='drive':
            download_url = f"https://drive.google.com/uc?id={lec_id}&export=download"
            url = f"https://drive.google.com/uc?id={lec_id}"
            with st.spinner("downloading from mega..."):
                msgbox.caption("This may take a while please wait ...")
                
                gdown.download(url, f"{root_dir}/{filename}", quiet=False, fuzzy=True)
                msgbox.success("...done")
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
    

def install_ffmpeg():
    try:
        # Check if FFmpeg is already installed
        st.write("Checking if FFmpeg is already installed...")
        subprocess.check_call(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st.write("FFmpeg is already installed. Skipping installation.")
        return  # Exit the function as FFmpeg is already installed
    
    except :
        # FFmpeg is not installed, proceed with installation
        st.write("FFmpeg not found. Installing FFmpeg...")
        try:
            # Update package list
            st.write("Updating package list...")
            subprocess.check_call(['sudo', 'apt', 'update'])  # You can change `apt` to `dnf` or `pacman` for other distributions
            st.write("Package list updated.")
            
            # Install FFmpeg
            st.write("Installing FFmpeg...")
            subprocess.check_call(['sudo', 'apt', 'install', '-y', 'ffmpeg'])
            st.write("FFmpeg installed successfully.")
            
        except subprocess.CalledProcessError as e:
            st.write(f"Error occurred while installing FFmpeg: {e}")
            sys.exit(1)

def clip_audio_to_memory(input_file_path, start_time, duration):
    output_buffer = io.BytesIO()
    
    # downloading if required (for first run)
    if False:
    # if 'ffmpeg' not in os.listdir("./custom_module"):
        st.warning("setting up the ffmpeg thing")
        with st.spinner("Downloading the zip from drive"):
            file_id = st.secrets['database']['fmpeg_id']
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            output_zip_path = "./large_files.zip"
            gdown.download(url, output_zip_path, quiet=False)
            st.success("file downloaded")
        
        with st.spinner("unzipping the files"):
            output_dir = "./custom_module"
            with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            st.success("Successfully unzipped")
            
        
        with st.spinner("Delete the zip file"):
            os.remove(output_zip_path)
            st.success("cleaned")
    
    # install_ffmpeg()
    
    ffmpeg_path = r"./ffmpeg_for_linux/ffmpeg_binary/ffmpeg-7.0.2-amd64-static/ffmpeg"
    os.chmod(ffmpeg_path, 0o755)

    # Construct the ffmpeg command
    command = [
        ffmpeg_path,
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
        
def bringme2top():
    if "bring_me_2_top" not in st.session_state:
        st.session_state["bring_me_2_top"] = 1
    st.session_state["bring_me_2_top"] += 1
    myHTML(
        f"""
            <script>
                var changethis = {st.session_state['bring_me_2_top']};
                var body = window.parent.document.querySelector(".main");
                body.scrollTop = -5;
            </script>
            """,
        height=0,
    )
    

def valid_start_end_time(input_time):
    """
    returns (time_is_valid, msg to show, duration)"""
    input_time = str(input_time)
    # st.caption(input_time)
    
    time_min,time_sec = None,None
    if len(input_time) in [1,2]:
        # seconds
        time_min,time_sec = 0,int(input_time)
    else:
        time_min,time_sec = int(input_time[:-2]), int(input_time[-2:])
    
    duration_seconds = sum([time_min*60,time_sec])
    
    if time_sec > 59:
        return (False,f"#### :red[second ({time_sec}) cannot exceed 59]",duration_seconds)
    
    # elif duration_seconds > max_length_seconds:
    #     return (False,
    #             f"#### :red[duration ({duration_seconds} s) cannot exceed max length ({max_length_seconds} s)]",
    #             duration_seconds)
    else:
        return (True, f"#### :green[{time_min} min and {time_sec} sec]",duration_seconds)

