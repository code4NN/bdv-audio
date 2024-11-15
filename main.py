import streamlit as st

from qhandler import query_handler, download_play_lecture


class mainapp:
    def __init__(self):
        
        
        self.page_config = {'page_title': "",
                            'page_icon':'☔',
                            'layout':'wide'}
        
        # application level information
        self.query_is_handled = False
        self.lecture_info = {
            'user':'',
            "sindhu":'',
            
            'server':'',
            'lecture_name':'',
            'lec_encrypt_id':'',
            "lec_download_id":''
                }
        
        
        
    def home(self):
        st.title("Welcome ")
        
        lecinfo = self.lecture_info
        root_dir  = f"./{lecinfo['sindhu']}"
        
        lecture_name = lecinfo['lecture_name']
        lec_encrypt_id = lecinfo['lec_entrypt_id']
        lec_id = lecinfo['lec_download_id']
        server = lecinfo['server']
        
        download_play_lecture(root_dir,lecture_name,
                         lec_encrypt_id,lec_id,
                         server)
        
        
    
        
    def run(self):
        self.home()

if 'mainapp'  not in st.session_state:
    st.session_state['mainapp'] = mainapp()
# ---------------------------------------------------------------------
mainapp = st.session_state['mainapp']
st.set_page_config(**mainapp.page_config)


if not mainapp.query_is_handled:
    query_handler(mainapp)
    mainapp.query_is_handled = True

mainapp.run()