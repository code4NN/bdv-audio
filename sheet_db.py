import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import pytz, datetime


def get_user_lecture():
    if 'google_sheet_connection' not in st.session_state:
            credentials_info = st.secrets['service_account']
            SCOPE = [
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
    

def log_hearing_traffic(payload):
    
    if 'google_sheet_connection' not in st.session_state:
            credentials_info = st.secrets['service_account']
            SCOPE = [
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
    

    india_timezone = pytz.timezone('Asia/Kolkata')
    timestamp = (datetime.datetime.now(india_timezone)
                .strftime("%Y-%m-%d %H:%M:%S"))
    
    hit_type = payload['hit_type']
    
    if hit_type =='lecture':
        upload_array_final = [[
            timestamp,
            payload['source'],
            payload['source_id'],
            payload['user_id'],
            payload['is_clip'],
            payload['clip_name']
        ]]
        
        worksheet = st.session_state['google_sheet_connection'].worksheet('hearing_traffic')
        (worksheet
        .append_rows(values=upload_array_final,
                    value_input_option='USER_ENTERED',
                    table_range='A:F'))
    
    
    elif hit_type =="clipped":
        upload_array_final = [[
            timestamp,
            payload['source'],
            payload['source_id'],
            payload['clipper_id'],
            payload['start_seconds'],
            payload['duration'],
            payload['clip_name']
        ]]
        
        worksheet = st.session_state['google_sheet_connection'].worksheet('clipping_traffic')
        (worksheet
        .append_rows(values=upload_array_final,
                    value_input_option='USER_ENTERED',
                    table_range='A:G'))