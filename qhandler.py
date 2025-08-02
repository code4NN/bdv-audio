import streamlit as st
from sheet_db import get_user_lecture


def query_handler(app):

    query_dict = st.query_params
    source = query_dict.get("src", 'blank')

    if source == 'm':
        userid = query_dict.get('user', 'blank')
        lecid = query_dict.get('id', 'blank')

        if userid == 'blank':
            app.additional_info = {'has_error':True,'error':'missing user id'}
        elif lecid == 'blank':
            app.additional_info = {'has_error':True,'error':'missing lecture id'}
        else:
            user_lecturedb = get_user_lecture()
            user_info = user_lecturedb['users'].get(userid, None)
            lecture_info = user_lecturedb['lectures'].get(lecid, None)

            if not user_info:
                app.additional_info = {'has_error':True,'error':'user account no longer exist'}
            elif not lecture_info:
                app.additional_info = {'has_error':True,'error':'could not find lecture'}
            else:
                app.lecture_info = {'id':lecid,**lecture_info}
                app.user_info = {'id':userid,**user_info}
                app.additional_info = {'src':source}
    
    else:
        app.additional_info = {'has_error':True,'error':'missing source'}