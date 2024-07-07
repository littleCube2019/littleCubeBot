from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

import requests
from pyquery import PyQuery as pq
import google.generativeai as genai
import os
payload = {
'from': '/bbs/Gossiping/index.html',
'yes': 'yes'
}
rs = requests.session()
res = rs.post('https://www.ptt.cc/ask/over18',data=payload)
res = rs.get('https://www.ptt.cc/bbs/Gossiping/index.html')





line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

import requests
from pyquery import PyQuery as pq
import re

api_key = 'AIzaSyBDAtzCnh-LSFqM71PpUsQgIo1YQRz9B2c'
genai.configure(api_key = api_key)
model = genai.GenerativeModel('gemini-pro')

def resHandler(m):
    BOARD = ["Gossiping","C_Chat","Baseball","Beauty","LOL"]

    if re.search("PTT", m) is not None:
        pattern = "[-]\w\w*"
        phoneRegex = re.compile(pattern)
        args = phoneRegex.findall(m)
        
        board = "Gossiping"
        goods = 20
        page = 5
        res = ""
        for arg in args:
            a = arg[2:]
            act = arg[1]
            
            if act == "h":
                return "-g 高於推文數，x表示只傳噓文，100只傳爆文/n\
                        -b 看板，預設八卦/n\
                        -p 爬多少頁/n"
            if act =="B":
                return  "[Gossiping,C_Chat,Baseball,Beauty,LOL]"
            if act == "b" and a in BOARD:
                board = a
            if act == "g":
                if len(a) != 0 and a[0] == "x":
                    goods= -1
                else:
                    goods = int(a)
            if act == "p":
                page = int(a)
                
            

        return crawler(board,goods,page)
    elif re.search("chat", m) is not None: 
        mesList = m.split()
        if len(mesList) > 1:
            return model.generate_content(mesList[1])
        else:
            return model.generate_content('假裝你接收到空白訊息，隨機回復生成文字')
    else:
        return m

def goodNum(goods):
    if goods == "":
        return 0
    if goods[0] == "爆":
        return 100
    if goods[0] == "X":
        return -1
    else:
        return int(goods)


def crawler(board, goods, page):
    res = ""


    payload = {
    'from': '/bbs/Gossiping/index.html',
    'yes': 'yes'
    }


    url = "https://www.ptt.cc/bbs/"+board+"/index.html"

    rs = requests.session()
    web = rs.post('https://www.ptt.cc/ask/over18',data=payload)
    
    for _ in range(page):
        web = rs.get(url)

        doc = pq(web.text)
        articles = doc('#main-container > div.r-list-container.action-bar-margin.bbs-screen>div').items()




        for article in articles:
        
            if article('div.title>a').text() != "" and ((goods!=-1 and goodNum(article('div.nrec > span').text()) \
                                                        >= goods) or (goods == -1 \
                                                    and goodNum(article('div.nrec > span').text()) == -1))\
            and (article('div.title>a').text())[1:3] != "公告" :
                res += "=======================================================\n"
                res += (article('div.title>a').text()) + "\n"
                res += ("https://www.ptt.cc/" + (article('div.title>a').attr("href"))) + "\n"
                res += (article('div.nrec > span').text()) + "\n"
                res += "=======================================================\n"
        
        url = "https://www.ptt.cc/" + doc("#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)").attr("href")

    return res

@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):



                line_bot_api.reply_message(
                    event.reply_token,
                   TextSendMessage(text=resHandler(event.message.text))
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
