import requests
import websocket
from threading import Thread
import time
import json
import Tools
import io
from PIL import Image
url = "wss://changjiang.yuketang.cn/wsapp/"
websoUrl = "wss://changjiang.yuketang.cn/wsapp/"
global qrQueryData
qrQueryData = json.dumps({"op": "requestlogin", "role": "web",
                         "version": 1.4, "type": "qrcode", "from": "web"})


def sendSignData(wait: int = 60):
    global qrQueryData
    while 1:
        print("Sending... ")
        wb.send(qrQueryData)
        for i in range(wait, 0, -1):
            print(f"\rwating... {Tools.color(str(i), 'green')}",  end="")
            time.sleep(1)


def showQRCode(qrc: bytes):
    bt = io.BytesIO(qrc)
    img = Image.open(bt)
    img.show()


def getQRCode(url):
    qrc = requests.get(url).content
    return qrc


def onclose(wb):
    print(wb)


def onopen(wb):
    print("onopen")


def onmessage(wb, msg):
    print("\nonmessage")
    data = json.loads(msg)
    match data["op"]:
        case "requestlogin":
            qrc = getQRCode(data["ticket"])
            if len(qrc) > 1:
                showQRCode(qrc)
            else:
                print("No QRCode Found")
        case "loginsuccess":
            pass
    print("二维码时效:", data["expire_seconds"])
    print(msg)


def onerror(wb, msg):
    print("error")
    print(msg)


wb = websocket.WebSocketApp(
    url, on_open=onopen, on_message=onmessage, on_close=onclose, on_error=onerror)
Thread(target=wb.run_forever, daemon=True).start()

# def takeshit():
#     print(1)
#     time.sleep(5)
# Thread(target=takeshit, daemon=True).start()
# wb.run_forever()


# from PIL import Image, ImageOps
# import PIL
# import io
# import pyzbar.pyzbar as pyzbar
# import qrcode
# import qrcode_terminal
# import os
# os.system("")

# img = Image.open(r"C:\Users\moiiii\Desktop\tmp\RainClassroomAssitant\tmp\test0.png")
# # t = pyzbar.decode(img)

# # qr = qrcode.QRCode()
# # qr.add_data(t)
# # qr.make(fit=True)
# # res = qr.make_image()
# # res.save("qrc.png")


# white_block = '\033[0;37;47m  '
# black_block = '\033[0;37;40m  '
# new_line = '\033[0m\n'

# def terminalOutPut(qr:qrcode.QRCode):
#     output = white_block*(qr.modules_count+2) + new_line
#     for mn in qr.modules:
#         output += white_block
#         for m in mn:
#             if m:
#                 output += black_block
#             else:
#                 output += white_block
#         output += white_block + new_line
#     output += white_block*(qr.modules_count+2) + new_line
#     return output
#     # res.get_image()
# # open(r"C:\Users\moiiii\Desktop\tmp\RainClassroomAssitant\tmp\test0.png", "rb").read()
# # print(res.get_image())
# # print(Image.open(r"C:\Users\moiiii\Desktop\tmp\RainClassroomAssitant\tmp\test1.png"))


# if __name__ == "__main__":
#     # pass
#     print(terminalOutPut(qr))
