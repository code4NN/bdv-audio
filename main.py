import pandas as pd
import streamlit as st

# for handling cover image of audio
import eyed3
from io import BytesIO
from PIL import Image

# for sharing link via whatsapp
from urllib.parse import quote_plus

# helper functions
from qhandler import query_handler, bring_lecture_by_id
from qhandler import store_log_sheet
from qhandler import clip_audio_to_memory
from qhandler import bringme2top
from qhandler import valid_start_end_time


class mainapp:
    def __init__(self):
        
        self.page_config = {'page_title': "VANI",
                            'page_icon':'💊',
                            'layout':'wide'}
        
        # shared clip view related
        self.page_is_sharedclip = False
        self.clip_info_dict = {
            "start_time":None,
            "duration":None,
            "clip_name":''
        }
        # flag to ensure cut only once
        self.clip_is_ready = False
        # clipped audio output
        self.clip_audio_buffer_shared = None
        
        
        # clip related variables
        # flag whether to show clip tools
        self.clip_mode_active = False
        self.clipped_audio_buffer = None
        # Trigger to clip audio
        self.clip_green_signal ={'state':False}
        
        # application level information
        self.query_is_handled = False
        
        # flags to save log at url hit
        self.log_saved_hit_normal = False
        self.log_saved_hit_hear_clip = False
        
        # which lecture is being opened
        self.lecture_info = {
            'user':'',
            "sindhu":'',
            
            'server':'',
            'lecture_name':'',
            'lec_encrypt_id':'',
            "lec_download_id":''
                }
        
    def home(self):
        
        st.title(":gray[Welcome to Barasana Dhaam Audio services]")
        st.markdown("")
        st.markdown("")
        
        lecinfo = self.lecture_info
        root_dir  = f"./{lecinfo['sindhu']}"
        
        lecture_name = lecinfo['lecture_name']
        lec_encrypt_id = lecinfo['lec_encrypt_id']
        lec_id = lecinfo['lec_download_id']
        server = lecinfo['server']
        
        lec_response = bring_lecture_by_id(root_dir,
                                            lec_encrypt_id,lec_id,
                                            server)
        
        
        file_path, download_url, play_url = lec_response
        # get meta data of audio
        eye_file = eyed3.load(file_path)
        file_duration_secs = eye_file.info.time_secs
        file_duration_mins = int(file_duration_secs//60)
        
        
        st.markdown(f"## :rainbow[{lecture_name}]")

        # items to show in default mode
        if not self.clip_mode_active:
            
            # show album photo
            if eye_file.tag and eye_file.tag.images:
                cover_image = Image.open(BytesIO(eye_file.tag.images[0].image_data))
                st.image(cover_image)
            else:
                # have sample images stored which we can show based on which lecture is there...
                pass
            
            st.markdown("")
            st.markdown("")
            foward_min = st.number_input("forward (in min)",
                                            step=1,min_value=0,
                                            value=0)
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.audio(file_path,format="audio/wav",
                        start_time=foward_min*60,
                        autoplay=True)
            st.markdown("")
            st.markdown("")
            st.divider()
            
            st.download_button("Direct Download",
                               data=file_path,
                               file_name=f"{lecture_name}.mp3",
                                mime="audio/mpeg"
                               )
            
            if server =='mega':
                st.markdown(f"[download from mega]({download_url})")
            
            elif server =='drive':
                st.markdown(f"[download from drive]({download_url})")
                st.markdown("")
                st.markdown(f"[play on drive]({play_url})")
        
        def toggle_clipmode():
            self.clip_mode_active = not self.clip_mode_active
            self.page_config.__setitem__("page_icon","✂️")
            bringme2top()
        
        st.divider()
        st.button("Make a clip ✂️" if not self.clip_mode_active else "Return to home page",
                  on_click=toggle_clipmode,
                  type='primary' if self.clip_mode_active else 'secondary'
                  )
        
        if not self.log_saved_hit_normal:
            store_log_sheet(lecinfo,'hearnow')
            self.log_saved_hit_normal = True
            
        if self.clip_mode_active:
            # show tools to clip the audio
            
            st.divider()
            left,middle,right = st.columns(3)
            st.markdown(
                """
                <style>
                [data-testid="stNumberInputStepUp"] {
                 display: none;
                }
                [data-testid="stNumberInputStepDown"] {
                 display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
                )
            
            def convert_time_to_int(time_seconds):
                minute_,seconds_ = divmod(int(time_seconds),60)
                # st.write(time_seconds)
                # st.write(minute_,seconds_,f"{minute_}{seconds_}")
                return int(f"{minute_}{seconds_:02}")
            with left:
                with st.popover("Time format guide"):
                    st.markdown("* last 2 digit of integer are considered as seconds. and remaining(if any) as minutes")
                    st.dataframe(pd.DataFrame([
                              [1,"1 s"],
                              [16,"16 s"],
                              [108,"1 min 8 s"],
                              [1600,"16 min 0 s"]
                              ],columns=['input','inferred time']),
                             hide_index=True)
            with middle:
                start_time_input = st.number_input("choose start time",
                                                   min_value=0,
                                                   max_value=convert_time_to_int(file_duration_secs),
                                                   step=1,
                                                   value=0
                                                   )
                start_is_valid, msg, start_time_seconds = valid_start_end_time(start_time_input)
                st.markdown(msg)
                
            with right:
                end_time_input = st.number_input("choose end time",
                                                   step=1,
                                                   value=0,
                                                   min_value=0
                                                #    min_value=convert_time_to_int(start_time_seconds),
                                                #    value=convert_time_to_int(min(file_duration_secs,start_time_seconds+60)),
                                                   )
                end_is_valid, msg, end_time_seconds = valid_start_end_time(end_time_input)
                st.markdown(msg)
            
            st.divider()
            
            # validate the input time window
            if end_time_seconds < start_time_seconds:
                st.error("End time should be greater than start time")

            elif end_time_seconds - start_time_seconds < 10:
                st.error("Minimum duration of clip should be 10 seconds")
                st.caption(f"Selection option is {end_time_seconds - start_time_seconds} s")
            
            elif not start_is_valid:
                st.error("Some gadbad in start time")
            elif not end_is_valid:
                st.error("Some gadbad in end time")
            
            else:
                
                st.markdown("#### :orange[Clip Preview]")
                
                st.markdown(f"##### :gray[Duration of clip: {divmod(end_time_seconds - start_time_seconds,60)[0]}min and {divmod(end_time_seconds - start_time_seconds,60)[1]} s]")
                st.caption("Play to begin and it will stop when clip duration is completed")
                
                st.audio(file_path,format="audio/wav",
                         start_time=start_time_seconds,
                         end_time=end_time_seconds,
                         autoplay=False)
                st.divider()
                left,right = st.columns([2,1])
                clip_name = left.text_input("Name the clip",
                                max_chars=100,
                                value= f"myclip").strip().replace("  "," ").replace(" ","_").lower()
                
                if not clip_name:
                    st.warning("enter name please")
                    st.stop()
                clip_name = f"{clip_name.replace('.mp3','')}.mp3"
                
                
                right.markdown("")
                right.markdown("")
                right.button("Clip ✂️ the audio",
                        on_click=lambda :self.clip_green_signal.__setitem__('state',True)
                             )
                
                # create the url to the clip
                root_link = st.secrets['database']['site_url']
                share_url = [
                    f"user={lecinfo['user']}",
                    f"sindhu={lecinfo['sindhu']}",
                    f"id={lecinfo['lec_encrypt_id']}",
                    f"ss={start_time_seconds}",
                    f"dur={end_time_seconds-start_time_seconds}",
                    f"name={clip_name.replace('.mp3','')}"
                    ]
                share_url = f"{root_link}{'&'.join(share_url)}"
                
                if self.clip_green_signal['state']:
                    # turn it off
                    self.clip_green_signal.__setitem__('state',False)
                    with st.spinner("audio clipping in progress"):
                        self.clipped_audio_buffer = clip_audio_to_memory(
                            input_file_path=file_path,
                            start_time=start_time_seconds,
                            duration=end_time_seconds-start_time_seconds
                        )
                        
                        # store the log
                        store_log_sheet(
                            {**lecinfo,
                             "clip_url":share_url,
                             "clip_name":clip_name.replace(".mp3",''),
                             "clip_duration":end_time_seconds-start_time_seconds,
                             "clip_maker":lecinfo['user']
                             },
                            'clip'
                            )
                    st.balloons()
                
                if self.clipped_audio_buffer:
                    st.audio(self.clipped_audio_buffer,
                             format="audio/mp3",
                             autoplay=True)
                    st.divider()
                    st.download_button(
                            label="Download Clipped Audio",
                            data=self.clipped_audio_buffer,
                            file_name=clip_name,
                            mime="audio/mpeg"
                        )
                    
                    # sharing the clip
                    st.divider()
                    st.markdown(":gray[Share the nectar !!]")
                    
                    share_msg = "\n".join(["Hare Krishna Pr",
                                 "I found this amazing clip",
                                 f"from the lecture: *{lecture_name}*",
                                 "Please hear this drop of nectar",
                                 "",
                                 f"title: *{clip_name.replace('.mp3','')}*",
                                 f"link to hear: {share_url}",
                                 "",
                                 "Let me know how you found it!!"])
                    st.markdown(f"[Share on Whatsapp](http://wa.me?text={quote_plus(share_msg)})")
      
      
                    
    def play_shared_clip(self):
        
        st.title(":gray[Welcome to BDV audio services]")
        lecinfo = self.lecture_info
        clipinfo = self.clip_info_dict
        root_dir  = f"./{lecinfo['sindhu']}"
        
        lecture_name = lecinfo['lecture_name']
        lec_encrypt_id = lecinfo['lec_encrypt_id']
        lec_id = lecinfo['lec_download_id']
        server = lecinfo['server']
        
        lec_response = bring_lecture_by_id(root_dir,
                                            lec_encrypt_id,lec_id,
                                            server)
        file_path, _, _ = lec_response
        
        # create the sharable URL
        root_link = st.secrets['database']['site_url']
        share_url = [
            f"user={lecinfo['user']}",
            f"sindhu={lecinfo['sindhu']}",
            f"id={lecinfo['lec_encrypt_id']}",
            f"ss={clipinfo['start_time']}",
            f"dur={clipinfo['duration']}",
            f"name={clipinfo['clip_name'].replace('.mp3','')}"
            ]
        share_url = f"{root_link}{'&'.join(share_url)}"
        
        if not self.clip_is_ready:
            self.clip_is_ready = True
            with st.spinner("audio clipping in progress"):
                        self.clip_audio_buffer_shared = clip_audio_to_memory(
                            input_file_path=file_path,
                            start_time=clipinfo['start_time'],
                            duration=clipinfo['duration']
                        )
                        store_log_sheet(
                            {**lecinfo,
                             "clip_url":share_url,
                             "clip_name":clipinfo['clip_name'].replace(".mp3",''),
                             "clip_duration":clipinfo['duration'],
                             "clip_maker":lecinfo['user']
                             },
                            'shared_clip'
                            )
        
        # ------------
        st.markdown(f"## :rainbow[{clipinfo['clip_name'][:-4]}]")
        st.caption(f" :gray[from lecture] :blue[{lecture_name}]")
        
        st.audio(self.clip_audio_buffer_shared,
                format="audio/mp3",
                autoplay=True)
        st.divider()
        
        
        left,right = st.columns(2)
        with left:
            st.download_button(
                    label="Download Clipped Audio",
                    data=self.clip_audio_buffer_shared,
                    file_name=clipinfo['clip_name'],
                    mime="audio/mpeg"
                )
            st.markdown("")
            st.markdown("")
            st.markdown("")
            def gotomain():
                self.page_is_sharedclip = False
            
            st.button("Hear full lecture",
                  on_click=gotomain)
        
        
        with right:
            st.markdown("### :orange[share the nectar]")
            share_msg = "\n".join(["Hare Krishna Pr",
                            "I found this amazing clip",
                            f"from the lecture: *{lecture_name}*",
                            "Please hear this drop of nectar",
                            "",
                            f"title: *{clipinfo['clip_name'].replace('.mp3','')}*",
                            f"link to hear: {share_url}",
                            "",
                            "Let me know how you found it!!"])
            st.markdown(f"### [Share on Whatsapp](http://wa.me?text={quote_plus(share_msg)})")
                

        
    
    def run(self):
        if not self.page_is_sharedclip:
            self.home() 
        else:
            self.play_shared_clip()





# ---------------------------------------------------------------------
if 'mainapp'  not in st.session_state:
    st.session_state['mainapp'] = mainapp()
mainapp = st.session_state['mainapp']
st.set_page_config(**mainapp.page_config)

st.markdown(
            """
            <style>
            [data-testid="baseButton-header"] {
                visibility: hidden;
            }
            [data-testid="stHeader"] {
            background-color: #365069;
            color: white;
            }
            footer {
            background-color: #365069;
            color: white;
            }
            a[href="https://streamlit.io/cloud"] {
            display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
)



if not mainapp.query_is_handled:
    query_handler(mainapp)
    mainapp.query_is_handled = True

mainapp.run()