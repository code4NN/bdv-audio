import streamlit as st

from qhandler import query_handler, download_lecture


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
            'lecture_index': '',
            'lecture_filename_extension':'',
            'lecture_name':'',
            "lecture_id":''
                }
        
        
        
    def home(self):
        st.title("Welcome ")
        
        lecinfo = self.lecture_info
        root_dir  = f"./{lecinfo['sindhu']}/"
        lec_index = lecinfo['lecture_index']
        lec_suffix = lecinfo['lecture_filename_extension']
        server = lecinfo['server']
        
        download_lecture(root_dir, lec_index,lec_suffix,server)
    
        
    def run(self):
        self.home()

if 'mainapp'  not in st.session_state:
    st.session_state['mainapp'] = mainapp()
# ---------------------------------------------------------------------
mainapp = st.session_state['mainapp']
st.set_page_config(**mainapp.page_config)


if not mainapp.query_is_handled:
    mainapp.page_map['active'] = query_handler(mainapp)
    mainapp.query_is_handled = True

mainapp.run()