import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import pytz, datetime


def get_user_lecture():
    if 'google_sheet_connection' not in st.session_state:
            credentials_info = st.secrets['service_account']
            SCOPE = [
            # "https://spreadsheets.google.com/feeds",
            # "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
            ]
            
            gc = (gspread
                .authorize(ServiceAccountCredentials
                            .from_json_keyfile_dict(credentials_info,
                                                    SCOPE)
                            )
                )
            
            sheet_id = '1M_vma6TihnAh_UTRNhA29Uh886YZ7bx3oQvBP5jUfIs'
            workbook = gc.open_by_key(sheet_id)
            st.session_state['google_sheet_connection'] = workbook
    
    workbook = st.session_state['google_sheet_connection'].worksheet('users')
    # return workbook.batch_get(['users','lectures'])
    user_array, lecture_array = workbook.batch_get(['users','lectures'])
    
    userdict = pd.DataFrame(user_array[1:],columns=user_array[0]).set_index('id').to_dict(orient='index')
    lecturedict = pd.DataFrame(lecture_array[1:],columns=lecture_array[0]).set_index('id').to_dict(orient='index')
    return {"users":userdict,"lectures":lecturedict}

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