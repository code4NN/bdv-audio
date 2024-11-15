import streamlit as st
import os
import pytz
import datetime
import pandas as pd

from custom_module.mega.mega.mega import Mega
import gdown

import eyed3
from io import BytesIO
from PIL import Image


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
    
            
def download_play_lecture(root_dir, display_name,lec_encrypt_id,lec_id, server):
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
            url = f"https://drive.google.com/uc?id={file_id}"
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
            
            # define the download urls etc
            if server =='mega':
                download_url = download_url = f"https://mega.co.nz/#!{lec_id}"
            
            elif server =='drive':
                download_url = f"https://drive.google.com/uc?id={lec_id}&export=download"
                url = f"https://drive.google.com/file/d/{lec_id}/view"
        
        st.markdown("")
        st.markdown("")
        
        st.markdown(f"## :rainbow[{display_name}]")

        # display the image if the audio file have one
        eye_file = eyed3.load(f"{root_dir}/{filename}")
        file_duration_secs = eye_file.info.time_secs
        if eye_file.tag and eye_file.tag.images:
            cover_image = Image.open(BytesIO(eye_file.tag.images[0].image_data))
            st.image(cover_image)
        
        st.markdown("")
        st.markdown("")
        foward_min = st.number_input("forward (in min)",
                                     step=1,min_value=0,
                                     value=0)
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.audio(f"{root_dir}/{filename}",format="audio/wav",
                 start_time=foward_min*60)
        st.markdown("")
        st.markdown("")
        st.divider()
        
        if server =='mega':
            st.markdown(f"[download from mega]({download_url})")
        
        elif server =='drive':
            st.markdown(f"[download from drive]({download_url})")
            st.markdown("")
            st.markdown(f"[play on drive]({url})")
        
        
            
        
        
        
        