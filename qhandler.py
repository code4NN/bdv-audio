import streamlit as st
from sheet_db import get_user_lecture


def query_handler(app):

    query_dict = st.query_params
    source = query_dict.get("src", 'blank')

    if source == 'm':
        userid = query_dict.get('user', 'blank')
        lecid = query_dict.get('id', 'blank')
        start_at = query_dict.get('begin',0)

        if userid == 'blank':
            app.additional_info = {'has_error':True,'error':'missing user id'}
        elif lecid == 'blank':
            app.additional_info = {'has_error':True,'error':'missing lecture id'}
        else:
            with st.spinner("Validating your query"):
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
                app.additional_info = {'has_error':False,'src':source,'start_minute':start_at}
    
    elif source =='clip':
        # ?src=clip&osrc=m&id=qyed&creator=rbfx&ss=0&dur=191&name=my_first_clip
        original_source = query_dict.get('osrc','blank')
        original_source_id = query_dict.get('id','blank')
        creator = query_dict.get('creator','blank')
        start_second = int(query_dict.get('ss','-1'))
        duration = int(query_dict.get('dur','-1'))
        clip_name = query_dict.get("name","unnamed")
        
        if original_source=='blank':
            app.additional_info = {'has_error':True,'error':'missing original source'}
        
        elif original_source_id == 'blank':
            app.additional_info = {'has_error':True,'error':'missing ``'}
        
        elif creator=='blank':
            app.additional_info = {'has_error':True,'error':'missing `creator`'}
            
        elif start_second==-1 or duration==-1:
            app.additional_info = {'has_error':True,'error':'missing `ss` or `dur` '}
        
        else:
            # all good
            with st.spinner("Validating your query"):
                user_lecturedb = get_user_lecture()
            # st.write(user_lecturedb)
            creator_info = user_lecturedb['users'].get(creator, None)
            lecture_info = user_lecturedb['lectures'].get(original_source_id, None)

            if not creator_info:
                app.additional_info = {'has_error':True,'error':'creator account no longer exist'}
            
            elif not lecture_info:
                app.additional_info = {'has_error':True,'error':'could not find lecture'}
            else:
                app.lecture_info = {'id':original_source_id,**lecture_info}
                app.user_info = {'id':creator,**creator_info}
                app.additional_info = {'has_error':False,'src':original_source,"start_minute":start_second//60}
                
                app.clip_info = {'start_time':start_second,
                                 'duration':duration,
                                 'clip_name':clip_name}
                app.page_is_sharedclip = True
        
        
    else:
        app.additional_info = {'has_error':True,'error':'missing src'}