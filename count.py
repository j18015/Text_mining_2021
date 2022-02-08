#MeCabで分割
import MeCab
m = MeCab.Tagger ("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
#m = MeCab.Tagger()
#TXT_NAME = '[Japanese] 【小５　算数】　　小５－１　　整数と小数① [DownSub.com]'
TXT_NAME = 'toaru_math_high2'
FONT_PATH = "/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf"

# テキストファイル読み込み
read_text = open(TXT_NAME + ".txt", encoding="utf8").read() 

node = m.parseToNode(read_text)
#print(node)
words=[]

while node:
    word = node.surface
    hinshi = node.feature.split(",")[0]
    bunrui = node.feature.split(",")[1]
    if hinshi == "名詞":
      #if bunrui in ["普通名詞", "固有名詞"]:
      words.append(node.surface)
    node = node.next

#print(words)

'''
while node:
    hinshi = node.feature.split(",")[0]
    #bunrui = node.feature.split(",")[1]
    if hinshi == "名詞" :
      rigin = node.feature.split(",")[6]
      words.append(node.surface)
      print(words)
    node = node.next

while node:
    hinshibunrui = node.feature.split(",")[4]
    if hinshibunrui == "名詞-固有名詞-一般":
        origin = node.feature.split(",")[0]
        words.append(node.surface)
    node = node.next

#print(words)
#print(origin)
'''
#単語の数カウント
import collections
c = collections.Counter(words)
print(c.most_common(20))
#print(c)

import seaborn as sns
#sns.set(font="/usr/share/fonts/truetype/fonts-japanese-mincho.ttf")#自分が使える日本語フォントを探して入れる
#sns.set(font="usr/share/fonts/truetype/fonts-japanese-gothic.ttf")#自分が使える日本語フォントを探して入れる
#sns.set(font='IPAexGothic')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import japanize_matplotlib
#plt.rcParams["font.family"] = "IPAexGothic"
japanize_matplotlib.japanize()

# 日本語フォント
fp = FontProperties(fname='/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf') 
 
#sns.set(context="talk")
fig = plt.subplots(figsize=(10, 10))
 
sns.countplot(y=words,order=[i[0] for i in c.most_common(20)])