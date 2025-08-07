import pandas as pd
import streamlit as st

# for handling cover image of audio
import eyed3
from io import BytesIO
from PIL import Image

# for sharing link via whatsapp
from urllib.parse import quote_plus

# helper functions
from qhandler import query_handler
from audio_handler import bring_lecture_by_id, clip_audio_to_memory, valid_start_end_time
from sheet_db import get_user_lecture
from sheet_db import log_hearing_traffic

from streamlit.components.v1 import html as myHTML


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


class mainapp:
    def __init__(self):

        self.page_config = {'page_title': "VANI",
                            'page_icon': '💊',
                            'layout': 'wide'}

        # clipped audio output
        self.clip_audio_buffer_shared = None

        # clip related variables
        # flag whether to show clip tools
        self.clip_mode_active = False
        self.clipped_audio_buffer = None

        # Trigger to clip audio
        self.clip_green_signal = {'state': False}

        # application level information
        self.query_is_handled = False

        # flags to save log at url hit
        self.log_saved_traffic_lecture = False
        self.log_saved_traffic_clip = False

        # which lecture is being opened
        self.additional_info = {}
        self.lecture_info = {}
        self.user_info = {}
        
        # shared clip view related
        self.page_is_sharedclip = False
        self.clip_info = {
            # "start_time": None,
            # "duration": None,
            # "clip_name": ''
        }

    def home(self):

        st.title(
            f":gray[Welcome] :rainbow[{self.user_info.get('display name')}]")
        st.markdown("")
        st.markdown("")

        if self.additional_info['has_error']:
            st.error(self.additional_info["error"])
            return

        lecinfo = self.lecture_info
        userinfo = self.user_info
        root_dir = f"./{self.additional_info['src']}"

        lecture_name = lecinfo['title']
        speaker = lecinfo['speaker']
        server = lecinfo['cloud']
        lec_id = lecinfo['cloud_id']
        lec_encrypt_id = lecinfo['id']
        
        st.markdown(f"## :rainbow[{lecture_name}]")
        st.caption(f"speaker: {speaker}")

        lec_response = bring_lecture_by_id(root_dir,
                                           lec_id,
                                           server,
                                           lec_encrypt_id)

        file_path, download_url, play_url = lec_response

        # get meta data of audio
        eye_file = eyed3.load(file_path)
        file_duration_secs = eye_file.info.time_secs

        # items to show in default mode
        if not self.clip_mode_active:

            # show album photo
            if eye_file.tag and eye_file.tag.images:
                cover_image = Image.open(
                    BytesIO(eye_file.tag.images[0].image_data))
                st.image(cover_image)
            else:
                # have sample images stored which we can show based on which lecture is there...
                pass

            st.markdown("")
            st.markdown("")
            foward_min = st.number_input("forward (in min)",
                                         step=1, min_value=0,
                                         value=int(self.additional_info['start_minute']))
            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.audio(file_path, format="audio/wav",
                     start_time=foward_min*60,
                     autoplay=True)
            st.markdown("")
            st.markdown("")
            st.divider()

            if server == 'mega':
                st.markdown(f"[download from mega]({download_url})")

            elif server == 'gdrive':
                st.markdown(f"[download from drive]({download_url})")
                st.markdown("")
                st.markdown(f"[play on drive]({play_url})")
        # ==================================================================

        def toggle_clipmode():
            self.clip_mode_active = not self.clip_mode_active
            self.page_config.__setitem__("page_icon", "✂️")
            bringme2top()

        st.divider()
        st.button("Make a clip ✂️" if not self.clip_mode_active else "Return to home page",
                  on_click=toggle_clipmode,
                  type='primary' if self.clip_mode_active else 'secondary'
                  )
        
        if len(self.clip_info.keys())>0:
            def go_to_clip():
                self.page_is_sharedclip = True
            st.button("Hear the Shared Clip",
                            on_click=go_to_clip)

        # ==================================================================
        if self.clip_mode_active:
            # show tools to clip the audio

            st.divider()
            left, middle, right = st.columns(3)
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
                minute_, seconds_ = divmod(int(time_seconds), 60)
                # st.write(time_seconds)
                # st.write(minute_,seconds_,f"{minute_}{seconds_}")
                return int(f"{minute_}{seconds_:02}")

            with left:
                with st.popover("Time format guide"):
                    st.markdown(
                        "* last 2 digit of integer are considered as seconds. and remaining(if any) as minutes")
                    st.dataframe(pd.DataFrame([
                        [1, "1 s"],
                        [16, "16 s"],
                        [108, "1 min 8 s"],
                        [1600, "16 min 0 s"]
                    ], columns=['input', 'inferred time']),
                        hide_index=True)
            with middle:
                start_time_input = st.number_input("choose start time",
                                                   min_value=0,
                                                   max_value=convert_time_to_int(
                                                       file_duration_secs),
                                                   step=1,
                                                   value=0
                                                   )
                start_is_valid, msg, start_time_seconds = valid_start_end_time(
                    start_time_input)
                st.markdown(msg)

            with right:
                end_time_input = st.number_input("choose end time",
                                                 step=1,
                                                 value=0,
                                                 min_value=0
                                                 #    min_value=convert_time_to_int(start_time_seconds),
                                                 #    value=convert_time_to_int(min(file_duration_secs,start_time_seconds+60)),
                                                 )
                end_is_valid, msg, end_time_seconds = valid_start_end_time(
                    end_time_input)
                st.markdown(msg)

            st.divider()

            # validate the input time window
            if end_time_seconds < start_time_seconds:
                st.error("End time should be greater than start time")

            elif end_time_seconds - start_time_seconds < 10:
                st.error("Minimum duration of clip should be 10 seconds")
                st.caption(
                    f"Selection option is {end_time_seconds - start_time_seconds} s")

            elif not start_is_valid:
                st.error("Some gadbad in start time")
            elif not end_is_valid:
                st.error("Some gadbad in end time")

            else:

                st.markdown("#### :orange[Clip Preview]")

                st.markdown(
                    f"##### :gray[Duration of clip: {divmod(end_time_seconds - start_time_seconds,60)[0]}min and {divmod(end_time_seconds - start_time_seconds,60)[1]} s]")
                st.caption(
                    "Play to begin and it will stop when clip duration is completed")

                st.audio(file_path, format="audio/wav",
                         start_time=start_time_seconds,
                         end_time=end_time_seconds,
                         autoplay=False)
                st.divider()
                left, right = st.columns([2, 1])
                clip_name = left.text_input("Name the clip",
                                            max_chars=100,
                                            value=f"myclip").strip().replace("  ", " ").replace(" ", "_").lower()

                if not clip_name:
                    st.warning("enter name please")
                    st.stop()
                clip_name = f"{clip_name.replace('.mp3','')}.mp3"

                right.markdown("")
                right.markdown("")
                right.button("Clip ✂️ the audio",
                             on_click=lambda: self.clip_green_signal.__setitem__(
                                 'state', True)
                             )
                
                # create the url to the clip
                root_link = st.secrets['info']['site_url']
                share_url = [
                    f"src=clip",
                    f"osrc={self.additional_info['src']}",
                    f"id={lec_encrypt_id}",
                    f"creator={userinfo['id']}",
                    f"ss={start_time_seconds}",
                    f"dur={end_time_seconds-start_time_seconds}",
                    f"name={clip_name.replace('.mp3','')}"
                ]
                share_url = f"{root_link}?{'&'.join(share_url)}"

                if self.clip_green_signal['state']:
                    # turn it off
                    self.clip_green_signal.__setitem__('state', False)
                    with st.spinner("audio clipping in progress"):
                        self.clipped_audio_buffer = clip_audio_to_memory(
                            input_file_path=file_path,
                            start_time=start_time_seconds,
                            duration=end_time_seconds-start_time_seconds
                        )

                        # store the log
                        # store_log_sheet(
                        #     {**lecinfo,
                        #      "clip_url": share_url,
                        #      "clip_name": clip_name.replace(".mp3", ''),
                        #      "clip_duration": end_time_seconds-start_time_seconds,
                        #      "clip_maker": lecinfo['user']
                        #      },
                        #     'clip'
                        # )
                    st.balloons()
                    if not self.log_saved_traffic_clip:
                        try:
                            log_hearing_traffic({
                                'hit_type':'clipped',
                                'source':server,
                                'source_id':lec_encrypt_id,
                                'clipper_id':userinfo['id'],
                                'clip_name':clip_name,
                                'start_seconds': start_time_seconds,
                                'duration':end_time_seconds-start_time_seconds,
                            })
                            self.log_saved_traffic_clip=True
                        except Exception as e:
                            st.error(e)

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
                                           f"by: *{speaker}*",
                                           "Please hear this drop of nectar",
                                           "",
                                           f"title: *{clip_name.replace('.mp3','')}*",
                                           f"link to hear: {share_url}",
                                           "",
                                           "Let me know how you found it!!"])
                    st.markdown(
                        f"[Share on Whatsapp](http://wa.me?text={quote_plus(share_msg)})")
        # ==================================================================
        if not self.log_saved_traffic_lecture:
            try:
                log_hearing_traffic({
                    'hit_type':"lecture",
                    'source':server,
                    'source_id':lec_encrypt_id,
                    'user_id':userinfo['id'],
                    'is_clip':'no',
                    'clip_name':'',
                    # 'start_seconds': userinfo['start_time'],
                    # 'duration':clipper_info['duration'],
                    # 'clip_name':clipper_info['clip_name']
                })
                self.log_saved_traffic_lecture=True
            except Exception as e:
                pass
    def play_shared_clip(self):
        
        st.title(
            f":gray[Hare Krishna]")
        st.markdown("")
        st.markdown("")

        if self.additional_info['has_error']:
            st.error(self.additional_info["error"])
            return

        lecinfo = self.lecture_info
        clipper_info = self.user_info
        clip_info = self.clip_info
        root_dir = f"./{self.additional_info['src']}"

        lecture_name = lecinfo['title']
        speaker = lecinfo['speaker']
        server = lecinfo['cloud']
        lec_id = lecinfo['cloud_id']
        lec_encrypt_id = lecinfo['id']
        
        st.markdown(f"## :gray[clip:] :green[{clip_info['clip_name']}]")
        st.caption(f"created by: {clipper_info['display name']}")
        
        st.markdown(f"## :gray[from the lecture] :rainbow[{lecture_name}]")
        st.caption(f"speaker: {speaker}")
        

        lec_response = bring_lecture_by_id(root_dir,
                                           lec_id,
                                           server,
                                           lec_encrypt_id)

        file_path, download_url, play_url = lec_response
        

        with st.spinner("audio clipping in progress"):
            self.clip_audio_buffer_shared = clip_audio_to_memory(
                input_file_path=file_path,
                start_time=clip_info['start_time'],
                duration=clip_info['duration']
            )
            
        st.audio(self.clip_audio_buffer_shared,
                 format="audio/mp3",
                 autoplay=True)
        st.divider()

        left, right = st.columns(2)
        with left:
            st.download_button(
                label="Download Clipped Audio",
                data=self.clip_audio_buffer_shared,
                file_name=f"{clip_info['clip_name']}.mp3",
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
            root_link = st.secrets['info']['site_url']
            share_url = [
                f"src=clip",
                f"osrc={self.additional_info['src']}",
                f"id={lec_encrypt_id}",
                f"creator={clipper_info['id']}",
                f"ss={clip_info['start_time']}",
                f"dur={clip_info['duration']}",
                f"name={clip_info['clip_name']}"
            ]
            share_url = f"{root_link}?{'&'.join(share_url)}"
            share_msg = "\n".join(["Hare Krishna Pr",
                                           "I found this amazing clip",
                                           f"from the lecture: *{lecture_name}*",
                                           f"by: *{speaker}*",
                                           "Please hear this drop of nectar",
                                           "",
                                           f"title: *{clip_info['clip_name']}*",
                                           f"link to hear: {share_url}",
                                           "",
                                           "Let me know how you found it!!"])
            st.markdown(
                f"[Share on Whatsapp](http://wa.me?text={quote_plus(share_msg)})")

        # =====================
        if not self.log_saved_traffic_lecture:
            try:
                log_hearing_traffic({
                    'hit_type':'lecture',
                    'source':server,
                    'source_id':lec_encrypt_id,
                    'user_id':clipper_info['id'],
                    'is_clip':'yes',
                    'clip_name':clip_info['clip_name'],
                    # 'start_seconds': userinfo['start_time'],
                    # 'duration':clipper_info['duration'],
                    # 'clip_name':clipper_info['clip_name']
                })
                self.log_saved_traffic_lecture=True
            except Exception as e:
                st.error(e)
            

    def run(self):
        if  self.page_is_sharedclip:
            self.play_shared_clip()
        else:
            self.home()


# ---------------------------------------------------------------------
if 'mainapp' not in st.session_state:
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
            ._profilePreview_gzau3_63 {
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
# st.secrets['service_account']
# st.write(get_user_lecture())
