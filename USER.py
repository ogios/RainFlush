from threading import Thread
from PIL import Image
import io
import os
import json
import time
import requests
import Tools
import websocket

# global websoUrl
# global qrQueryData
# global loginUrl
# websoUrl = "wss://changjiang.yuketang.cn/wsapp/"
# qrQueryData = json.dumps({"op": "requestlogin", "role": "web",
#                          "version": 1.4, "type": "qrcode", "from": "web"})
# loginUrl = "https://changjiang.yuketang.cn/pc/web_login"

PATH = os.path.dirname(__file__)+"/usercookies/"
print("Cookie保存路径:", PATH)
if not os.path.isdir(PATH):
    os.mkdir(PATH)
    print("cookie Directory not found, Created one.")


def showQRCode(qrc: bytes):
    bt = io.BytesIO(qrc)
    img = Image.open(bt)
    img.show()


def getQRCode(url: str):
    qrc = requests.get(url).content
    return qrc


class User:
    def __init__(self, uid=None) -> None:
        self.URL_websocket = "wss://changjiang.yuketang.cn/wsapp/"
        self.qrQueryData = json.dumps({"op": "requestlogin", "role": "web",
                                       "version": 1.4, "type": "qrcode", "from": "web"})
        self.URL_login = "https://changjiang.yuketang.cn/pc/web_login"
        self.URL_getUserInfo = "https://changjiang.yuketang.cn/v/course_meta/user_info"
        self.flushQR = False
        self.isLogin = False
        self.wb = None
        self.UserID = None
        self.Auth = None
        self.isSigned = False
        self.cookies = None

        self.cookieHeaders = {
            "Referer": "https://changjiang.yuketang.cn/web?next=/v2/web/index&type=3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        self.uid = uid
        self.fileName = ''
        if uid:
            self.setfileName()
        else:
            print(Tools.color("未传入学号，开始请求", "red"))

    def setfileName(self):
        self.fileName = PATH+str(self.uid)+".json"

    def getCookie(self):
        print("正在获取cookie...")
        if not self.cookies:
            print("未找到Cookie")
            if os.path.exists(self.fileName):
                try:
                    js: dict = json.loads(open(self.fileName, "r").read())
                    if ("csrftoken" in js.keys()) & ("sessionid" in js.keys()):
                        self.cookies = requests.utils.cookiejar_from_dict(
                            js)
                        print("从json读取内容")
                        self.isLogin = True

                except Exception as e:
                    pass
        if not self.isLogin:
            self.login()
        while not self.isLogin:
            time.sleep(1)
        return self.cookies

    def saveCookie(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.cookies.get_dict()))

    def sendSignData(self, wait: int = 60):
        '''
        发送qrcode请求
        '''
        while 1:
            if self.isLogin:
                return
            if self.flushQR == False:
                time.sleep(1)
                continue
            print("Sending... ")
            self.wb.send(self.qrQueryData)  # type: ignore
            for i in range(wait, 0, -1):
                if self.isLogin:
                    return
                print(f"\rwating... {Tools.color(str(i), 'green')}",  end="")
                time.sleep(1)

    def postCookie(self):
        '''
        通过用户id和Auth链接获取cookie
        '''
        data = {
            "UserID": self.UserID,
            "Auth": self.Auth,
        }
        res = requests.post(self.URL_login, headers=self.cookieHeaders,
                            data=json.dumps(data))
#         print(res.text)
        print(Tools.color("Cookies:", "green"), res.cookies)
        self.cookies = res.cookies
        if (self.cookies.get("csrftoken") != None) & (self.cookies.get("sessionid") != None):
            self.isLogin = True
            self.wb.close()
            # cookies = json.dumps(res.cookies.get_dict())
            if self.getUserInfo():
                self.saveCookie()
                print("Cookie已保存")
        else:
            print(Tools.color("本次Cookie获取失败，等待重试", "red"))

    def getUserInfo(self):
        '''
        获取用户学号以便保存
        '''
        try:
            res = requests.get(self.URL_getUserInfo,
                               headers=self.cookieHeaders, cookies=self.cookies)
            js = res.json()
            if js["success"]:
                self.uid = res.json()["data"]["user_profile"]["school_number"]
                self.setfileName()
                return True
            else:
                raise Exception
        except:
            print("用户信息获取失败，cookie无法保存")
            return False

    def login(self):
        '''
        登录总方法。创建websocket连接
        '''
        def onclose(wb):
            print("closed")

        def onopen(wb):
            print("onopen")
            self.flushQR = True

        def onmessage(wb, msg):
            '''
            接收消息，获取qrcode时展示，获取登陆成功的消息时请求cookie
            '''
            print("\nonmessage")
            data = json.loads(msg)
            match data["op"]:
                case "requestlogin":
                    qrc = getQRCode(data["ticket"])
                    if len(qrc) > 1:
                        showQRCode(qrc)
                    else:
                        print(Tools.color("No QRCode Found", "red"))
                case "loginsuccess":
                    self.Auth = data["Auth"]
                    self.UserID = data["UserID"]
                    print(Tools.color("Auth:", "green"), self.Auth)
                    print(Tools.color("UserID:", "green"), self.UserID)
                    self.postCookie()
                case _:
                    print(Tools.color("未知错误", "red"))
                    print(msg)
            print("\n二维码时效:", time.strftime("%m-%d %H:%M:%S",
                  time.localtime(time.time()+int(data["expire_seconds"]))))
            print(msg)

        def onerror(wb, msg):
            print("error")
            print(msg)
        self.wb = websocket.WebSocketApp(
            self.URL_websocket, on_open=onopen, on_message=onmessage, on_close=onclose, on_error=onerror)
        Thread(target=self.wb.run_forever, daemon=True).start()
        Thread(target=self.sendSignData(60), daemon=True).start()


if __name__ == "__main__":
    us = User("20338209150460")
    cookie = us.getCookie()
    print(cookie)
