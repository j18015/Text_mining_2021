# from apiclient.discovery import build
import secrets
from googleapiclient.discovery import build
import pandas as pd
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from wordcloud import WordCloud
import MeCab
import re
from matplotlib import pyplot as plt
import json

with open('secret.json') as f:
    secret=json.load(f)

DEVELOPER_KEY = secret['KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

FONT_PATH = "/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

def video_search(youtube, q='自動化', max_results=10):
    response = youtube.search().list(
        q=q, 
        part='id,snippet',
        order='viewCount', 
        type='video',
        maxResults=max_results
        ).execute()

    items_id = []
    items = response['items']
    for item in items:
        item_id = {}
        item_id['video_id'] = item['id']['videoId']
        item_id['channel_id'] = item['snippet']['channelId']
        items_id.append(item_id)

    df_video = pd.DataFrame(items_id)
    return df_video

def get_results(df_video, threshould=5000):
    channel_ids = df_video['channel_id'].unique().tolist()
    subscriber_list = youtube.channels().list(
        id=','.join(channel_ids),
        part='statistics',
        fields='items(id, statistics(subscriberCount))'
        ).execute()

    subscribers = []
    for item in subscriber_list['items']:
        subscriber = {}
        if len(item['statistics']) > 0:
            subscriber['channel_id'] = item['id']
            subscriber['subscriber_count'] = int(item['statistics']['subscriberCount'])
        else:
            subscriber['channel_id'] = item['id']
        subscribers.append(subscriber)


    df_subscribers = pd.DataFrame(subscribers)

    df = pd.merge(left=df_video, right=df_subscribers, on='channel_id')
    df_extracted = df[df['subscriber_count'] > threshould]

    video_ids = df_extracted['video_id'].tolist()
    videos_list = youtube.videos().list(
        id=','.join(video_ids),
        part='snippet, statistics',
        fields='items(id, snippet(title), statistics(viewCount))'
        ).execute()

    videos_info = []
    items = videos_list['items']
    for item in items:
        video_info = {}
        video_info['video_id'] = item['id']
        video_info['title'] = item['snippet']['title']
        video_info['view_count'] = item['statistics']['viewCount']
        videos_info.append(video_info)

    df_videos_info = pd.DataFrame(videos_info)
    results = pd.merge(left=df_extracted, right=df_videos_info, on='video_id')
    results = results.loc[:,['video_id', 'title', 'view_count', 'subscriber_count', 'channel_id']]
    return results

def get_dl_txt(videoid):
    transcript_list = YouTubeTranscriptApi.list_transcripts(videoid)

    transcript = transcript_list.find_generated_transcript(['ja'])

    dl_text_list = []

    for dl_text in transcript.fetch():
        dl_text_list.append(dl_text['text']) 

    dl_text_list = ''.join(dl_text_list)

    return dl_text_list

def get_word_str(text):
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    parsed = mecab.parse(text)
    lines = parsed.split('\n')
    lines = lines[0:-2]
    word_list = []

    for line in lines:
        tmp = re.split('\t|,', line)
        #print(tmp)
        # 名詞のみ対象
        if tmp[1] in ["名詞"]:
            # さらに絞り込み
            if tmp[2] in ["一般", "固有名詞"]:
                word_list.append(tmp[0])
 
    return " " . join(word_list)

def get_wordcloud(word_list):
    # 形態素解析結果取得
    word_str = get_word_str(text)
    wc = WordCloud(font_path=FONT_PATH, max_font_size=200,background_color="white", prefer_horizontal=1,width=800,height=400).generate(word_str)
    return wc


def display_wordcoud(word_cloud):
    dw = plt.imshow(word_cloud)
    dw = plt.axis('off')
    #st.pyplot()
    return dw


st.title('YouTube分析アプリ')

st.sidebar.write('## クエリと閾値の設定')
st.sidebar.write('### クエリの入力')
query = st.sidebar.text_input('検索クエリを入力してください', 'Python 自動化')

st.sidebar.write('### 閾値の設定')
#threshould = st.sidebar.slider('登録者数の閾値', 1000, 10000, 5000)
threshould = st.sidebar.number_input('登録者数を入力してください', 10000, 50000, 25000, step=10000)

st.write('### 選択中のパラメータ')
st.markdown(f"""
- 検索クエリ：{query}
- 登録者数の閾値：{threshould}
""")


df_video = video_search(youtube, q=query, max_results=30)
results = get_results(df_video, threshould=threshould)


st.write('### 分析結果', results)
st.write('### 動画再生')
video_id = st.text_input('動画IDを入力してください')
url = f'https://youtube.com/watch?v={video_id}'

video_field = st.empty()
video_field.write('こちらに動画が表示されます')

if st.button('ビデオ表示'):
    if len(video_id) > 0:
        try:
            video_field.video(url)
        except:
            st.error('おっと！何かエラーが起きているようです！')

if st.button('字幕取得'):
    if len(video_id) > 0:
        try:
            text = get_dl_txt(video_id)
            st.write('字幕がダウンロードできました！')
            if len(text) > 0:
                word_list = get_word_str(text)
                #st.write(word_list)
                word_cloud = get_wordcloud(word_list)
                #if len(word_cloud) > 0:
                st.write('ワードクラウドが生成できました')
                #if st.button('ワードクラウド表示'):
                #display_wordcoud(word_cloud)
                plt.axis("off")
                plt.imshow(word_cloud)
                st.pyplot()
        except:
            st.error('おっと！何かエラーが起きているようです！')

