import io
import json
import math
import time
from alive_progress import alive_bar
import cv2
import requests
import requests.utils
import Tools


def getDuration(url):
    '''
    根据视频id获取视频长度(单位: 秒)
    '''
    video = cv2.VideoCapture(url)
    for i in range(3):
        if video.isOpened():
            framerate = video.get(5)
            framecount = video.get(7)
            duration = int(math.ceil(framecount/framerate))
            return duration
        else:
            time.sleep(2)
    return False


class run:
    def __init__(self, cookies: requests.cookies.RequestsCookieJar):
        self.REPLACE = " -replace- "
        self.REPLACE_CLASSROOMID = " -classroom-id- "
        self.URL_getCourse = "https://henutdxl.yuketang.cn/v2/api/web/courses/list?identity=2"
        # self.URL_getCuts = "https://henutdxl.yuketang.cn/v2/api/web/logs/learn/" + \
        #     self.REPLACE+"?actype=-1&page=0&offset=20"
        self.URL_getVideo = "https://henutdxl.yuketang.cn/c27/online_courseware/xty/kls/pub_news/"+self.REPLACE+"/"
        self.URL_getDone = "https://henutdxl.yuketang.cn/mooc-api/v1/lms/learn/course/pub_new_pro"
        self.URL_getVideoInfo = "https://henutdxl.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/" + \
            self.REPLACE_CLASSROOMID+"/"+self.REPLACE+"/"
        self.URL_getVideoUrl = "https://henutdxl.yuketang.cn/api/open/audiovideo/playurl"
        self.URL_heartBeat = "https://henutdxl.yuketang.cn/video-log/heartbeat/"
        # self.CourseUrl = CourseUrl
        # self.FinishUrl = FinishUrl
        self.cookies = cookies
        self.Courses = []
        # self.cuts = []
        self.classroom_id = None
        self.videos = []
        # self.reads = []
        self.done = []
        self.undonevideos = []
        # self.undonereads = []

        self.CourseHeaders = {
            'university-id': '0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'x-client': 'web',
            'x-csrftoken': cookies["csrftoken"],
            'xt-agent': 'web',
            'xtbz': 'ykt'
        }
        self.FinishHeaders = {
            'classroom-id': None,
            'Content-Type': 'application/json;charset=utf-8',
            'university-id': None,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
            'uv-id': None,
            'X-CSRFToken': cookies['csrftoken'],
            'Xt-Agent': 'web',
            'xtbz': 'ykt'
        }
        print(cookies)
        # self.getCourses()

    def getCourses(self):
        '''
        获取所有科目。变量保存在self.Courses
        '''
        res = requests.get(self.URL_getCourse,
                           headers=self.CourseHeaders, cookies=self.cookies)
        js = res.json()
        if js["errmsg"] == "Success":
            for i in js["data"]["list"]:
                self.Courses += [{
                    "classroom_id": i["classroom_id"],
                    "uv":i["course"]["university_id"],
                    "name":i["course"]["name"],
                }]
            return True
        else:
            print(Tools.color("请求课程失败 - 未知错误", "red"))
            print(res.text)
            return False

    def chooseCourse(self):
        '''
        人为挑选科目，输入前面的序号挑选。
        把选中科目的科目id保存至self.classroom_id
        '''
        print("选择课程:")
        for i in range(len(self.Courses)):
            print(f"{i}. {self.Courses[i]}")
        while 1:
            choose = input(">>> ")
            try:
                course = self.Courses[int(choose)]
                print(course["name"])
                self.classroom_id = course["classroom_id"]
                self.URL_getVideoInfo = self.URL_getVideoInfo.replace(
                    self.REPLACE_CLASSROOMID, str(self.classroom_id))
                self.FinishHeaders["classroom-id"] = str(
                    course["classroom_id"])
                self.FinishHeaders["university-id"] = str(course["uv"])
                self.FinishHeaders["uv"] = str(course["uv"])
                break
            except Exception as e:
                print(e)
                print("输入错误")

    # def getCuts(self):
    #     '''
    #     获取学习日志的所有分段，各分段里都可能包含着视频测试等内容
    #     '''
    #     # url = f"https://henutdxl.yuketang.cn/v2/api/web/logs/learn/{self.classroom_id}?actype=-1&page=0&offset=20"
    #     url = self.URL_getCuts.replace(self.REPLACE, str(self.classroom_id))
    #     res = requests.get(url, headers=self.FinishHeaders,
    #                        cookies=self.cookies)
    #     js = res.json()
    #     if js["errmsg"] == "Success":
    #         for i in js["data"]["activities"]:
    #             if (i["type"] == 17) | (i["type"] == "17"):
    #                 self.videos += [{"title": i["title"],
    #                                  "id":i["content"]["leaf_id"]}]
    #                 print("共 1 个视频")
    #             self.cuts += [i["courseware_id"]]
    #         print(Tools.color("学习日志分段:", "green"), self.cuts)
    #         return True
    #     else:
    #         print(js)
    #         return False

    # def _getVideo(self, courses):
    #     '''
    #     getVideo的内置方法。用于用于从课程中提取视频类。
    #     将视频项的标题和id返回
    #     '''
    #     videos = []
    #     reads = []
    #     # print(courses)
    #     if courses["data"]:
    #         contents = courses["data"]["content_info"]
    #         if isinstance(contents, list):
    #             for a in contents:
    #                 sections = a["section_list"]
    #                 for b in sections:
    #                     for c in b["leaf_list"]:
    #                         if c["leaf_type"] == 0:
    #                             videos += [{"title": c["title"], "id":c["id"]}]
    #                         elif c["leaf_type"] == 3:
    #                             reads += [{"title": c["title"], "id":c["id"]}]
    #     print(f"{len(videos)} 个视频")
    #     print(f"{len(reads)} 个图文")
    #     return (videos, reads)
    def _getVideo(self, media):
        video = []
        for a in media["data"]["course_chapter"]:
            for b in a["section_leaf_list"]:
                if "leaf_list" in b.keys():
                    for c in b["leaf_list"]:
                        if c["leaf_type"] == 0:
                            video += [c]
        return video

    def getVideo(self):
        '''
        对每个学习日志的分段获取视频
        '''
        url = f"https://henutdxl.yuketang.cn/mooc-api/v1/lms/learn/course/chapter?cid={self.FinishHeaders['classroom-id']}&sign=9xrFKjkicWA&term=latest&uv_id=3357"
        res = requests.get(url, headers=self.FinishHeaders,
                           cookies=self.cookies)
        js = res.json()
        if js["success"]:
            self.videos += self._getVideo(js)
        else:
            print(js)
            return False
        if len(self.videos) > 0:
            return True
        else:
            return False

    def getDone(self):
        '''
        获取所有已完成内容
        '''
        url = f"https://henutdxl.yuketang.cn/mooc-api/v1/lms/learn/course/schedule?cid={self.FinishHeaders['classroom-id']}&sign=9xrFKjkicWA&term=latest&uv_id=3357"
        res = requests.get(url, headers=self.FinishHeaders,
                           cookies=self.cookies)
        self.done = res.json()
        if self.done["success"]:
            return True
        else:
            return False

    def getUndone(self):
        '''
        获取已完成内容并根据结果提取出未完成的视频
        '''

        self.getDone()
        if self.done:
            totalDone = self.done["data"]["leaf_schedules"]
            undone = []
            for i in self.videos:
                try:
                    if totalDone[str(i["id"])] == 1:
                        pass
                    else:
                        undone += [i]
                except:
                    undone += [i]
            print(f"{len(undone)} 个未完成")
            self.undonevideos += undone
            return True
        else:
            return False

    def getVideoInfo(self, video):
        '''
        获取单个视频信息
        '''
        id_ = video["id"]
        url = self.URL_getVideoInfo.replace(self.REPLACE, str(id_))
        res = requests.get(url, headers=self.FinishHeaders,
                           cookies=self.cookies)
        return res.json()

    def getReadyData(self, leaf_data):
        dic = {
            "c": leaf_data["course_id"],
            "cards_id": "",
            "cc": leaf_data["content_info"]["media"]["ccid"],
            "classroomid": leaf_data["classroom_id"],
            "cp": 4,
            "d": leaf_data["content_info"]["media"]["duration"],
            "et": "loadeddata",
            "fp": 0,
            "i": 5,
            "lob": "cloud4",
            "n": "ali-cdn.xuetangx.com",
            "p": "web",
            "pg": f"{leaf_data['id']}_n0ga",
            "skuid": leaf_data["sku_id"],
            "slide": 0,
            "sp": 1,
            "sq": 45,
            "t": "video",
            "tp": 0,
            "ts": str(int(time.time()*1000)-200),
            "u": leaf_data["user_id"],
            "uip": "",
            "v": leaf_data["id"],
            "v_url": ""
        }
        return dic

    def getHeartData(self, leaf_data, count):
        '''
        获取心跳信息
        '''
        dic = {
            "c": leaf_data["course_id"],
            "cards_id": "",
            "cc": leaf_data["content_info"]["media"]["ccid"],
            "classroomid": leaf_data["classroom_id"],
            "cp": count,
            "d": leaf_data["content_info"]["media"]["duration"],
            "et": "heartbeat",
            "fp": 0,
            "i": 5,
            "lob": "ykt",
            "n": "ali-cdn.xuetangx.com",
            "p": "web",
            "pg": f"{leaf_data['id']}_n0ga",
            "skuid": leaf_data["sku_id"],
            "slide": 0,
            "sp": 1,
            "sq": 45,
            "t": "video",
            "tp": 0,
            "ts": str(int(time.time()*1000)-200),
            "u": leaf_data["user_id"],
            "uip": "",
            "v": leaf_data["id"],
            "v_url": ""
        }
        return dic

    def getFinalData(self, leaf_data):
        '''
        获取视频结束信息
        '''
        final = {
            "c": leaf_data["course_id"],
            "cards_id": "",
            "cc": leaf_data["content_info"]["media"]["ccid"],
            "classroomid": leaf_data["classroom_id"],
            "cp": 0,
            "d": leaf_data["content_info"]["media"]["duration"],
            "et": "videoend",
            "fp": 0,
            "i": 5,
            "lob": "ykt",
            "n": "ali-cdn.xuetangx.com",
            "p": "web",
            "pg": f"{leaf_data['id']}_n0ga",
            "skuid": leaf_data["sku_id"],
            "slide": 0,
            "sp": 1,
            "sq": 50,
            "t": "video",
            "tp": 0,
            "ts": str(int(time.time()*1000)),
            "u": leaf_data["user_id"],
            "uip": "",
            "v": leaf_data["id"],
            "v_url": ""
        }
        return final

    def sendHeartBeat(self, test_data):
        '''
        三次发送心跳信息的机会，都报错返回False
        '''
        url = self.URL_heartBeat
        for i in range(3):
            try:
                res = requests.post(
                    url, headers=self.FinishHeaders, cookies=self.cookies, data=json.dumps(test_data))
                return res
            except Exception as e:
                pass
            time.sleep(2)
        return False

    def getVideoUrl(self, leaf_data):
        '''
        根据视频ccid获取视频链接
        '''
        ccid = leaf_data["content_info"]["media"]["ccid"]
        url = self.URL_getVideoUrl
        param = {
            "video_id": ccid,
            "provider": "cc",
            "file_type": "1",
            "is_single": "0",
            "domain": "changjiang.yuketang.cn",
        }
        res = requests.get(url, params=param,
                           headers=self.FinishHeaders, cookies=self.cookies)
        js = res.json()
        try:
            if js["success"]:
                sources = js["data"]["playurl"]["sources"]
                for i in sources.keys():
                    if "quality" in i:
                        return sources[i][0]
                return False
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def heartBeat(self, leaf_data):
        '''
        发送心跳内容
        '''
        # url = "https://henutdxl.yuketang.cn/video-log/heartbeat/"
        # print(leaf_data)
        url = self.URL_heartBeat
        test_data = {
            "heart_data": []
        }
        count = 0
        videourl = self.getVideoUrl(leaf_data)
        if videourl:
            duration = getDuration(videourl)
        else:
            raise Exception("No Video Length Found")
        print("Video length:", duration)
        test_data["heart_data"] += [self.getReadyData(leaf_data)]
        with alive_bar(duration) as bar:
            for i in range(1, int(duration/5)+1):

                count += 5
                test_data["heart_data"] += [
                    self.getHeartData(leaf_data, count)]

                if len(test_data["heart_data"]) >= 5:
                    print("Send")
                    # for i in range(3):
                    #     try:
                    #         res = requests.post(
                    #             url, headers=self.FinishHeaders, cookies=self.cookies, data=json.dumps(test_data))
                    #         break
                    #     except Exception as e:
                    #         print(Tools.color("请求失败", "red"))
                    res = self.sendHeartBeat(test_data)
                    if (res != False) & (res.text != "{}"):
                        print(Tools.color("请求失败", "red"))
                        print(res.text)

                    test_data["heart_data"] = []
                    print("Pending... takes about 5s")
                    time.sleep(5)
                bar(5)
            else:
                test_data["heart_data"] += [self.getFinalData(leaf_data)]
                # res = requests.post(url, headers=self.FinishHeaders,
                #                     cookies=self.cookies, data=json.dumps(test_data))
                res = self.sendHeartBeat(test_data)
                if (res != False) & (res.text != "{}"):
                    print(Tools.color("请求失败", "red"))
                    print(res.text)
                bar(duration-count)
        print("done")

    # def _readContent(self, leaf_data):
    #     '''
    #     访问图文项，完成阅读任务
    #     '''
    #     content_id = leaf_data["id"]
    #     classroom_id = leaf_data["classroom_id"]
    #     sku_id = leaf_data["sku_id"]
    #     url = f"https://henutdxl.yuketang.cn/mooc-api/v1/lms/learn/user_article_finish/{content_id}/?cid={classroom_id}&sid={sku_id}"
    #     res = requests.get(url, headers=self.FinishHeaders,
    #                        cookies=self.cookies)
    #     return res

    # def readContent(self):
    #     '''
    #     完成所有图文任务
    #     '''
    #     for i in self.undonereads:
    #         leaf_info = self.getVideoInfo(i)
    #         res = self._readContent(leaf_info["data"])
    #         if res.json()["success"]:
    #             print(i["title"], "- Finished")
    #         else:
    #             print(res.json())
    #             print(i["title"], "- Error")

    def flush(self, video):
        '''
        刷单个课
        '''
        leaf_info = self.getVideoInfo(video)
        # print(leaf_info)
        if leaf_info["success"]:
            leaf_data = leaf_info["data"]
            self.heartBeat(leaf_data)
            return True
        else:
            print(leaf_info)
            return False

    def flushALL(self):
        '''
        刷undone中的全部课程
        '''
        for i in self.undonevideos:
            print("Start - "+i["name"])
            flushed = self.flush(i)
            if not flushed:
                print(i["name"], Tools.color("未成功", "red"))
                continue
            print("\nWait for 3s")
            time.sleep(3)


if __name__ == "__main__":
    dic = {
        "sessionid": "xbk7wjllfmffs4whoxhb9fjim892ejem",
        "csrftoken": "MasSiCAhTeunIeTidssZ5tDADkAQ1958",
    }
    mission = run(requests.utils.cookiejar_from_dict(dic))
    print(mission.cookies)
