import streamlit as st
import os

def query_handler(app):
    
    query_dict = st.query_params
    
    user = query_dict.get('user','blank')
    lecture_id = query_dict.get('id', 'blank')
    sindhu = query_dict.get('sindhu', 'blank')
    
    if lecture_id == 'blank' or sindhu == 'blank':
        st.warning("the url is incorrect")
        st.stop()
    
    # get the lecture info dict and push user etc info to a sheet
    lecture_info = {
        'user':user,
    }
    # 'user':'',
    # "sindhu":'',
    
    # 'server':'',
    # 'lecture_index': '',
    # 'lecture_filename_extension':''
    # 'lecture_name':'',
    # "lecture_id":''
    app.lecture_info= lecture_info
    
    app.query_is_handled = True
    
            
def download_lecture(root_dir, lec_index,extension, server):
    
    filename = f"{lec_index}.{extension}"
    
    available_file_raw = os.listdir(root_dir)
    available_files = [i.split("^")[1] for i in available_file_raw]    
    file_exists = filename in available_files
    
    if server =='yt':
        pass
        
    if not file_exists:
        MAX_LECTURE_STORE = 10
        
        
            
        
        
        
        