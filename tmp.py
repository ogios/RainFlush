# -*- coding: utf-8 -*-
# version 4
# developed by zk chen
import random
import time
import requests
import re
import json

# 以下的csrftoken和sessionid需要改成自己登录后的cookie中对应的字段！！！！而且脚本需在登录雨课堂状态下使用
# 登录上雨课堂，然后按F12-->选Application-->找到雨课堂的cookies，寻找csrftoken、sessionid、university_id字段，并复制到下面两行即可
csrftoken = "MXIUQBsUBnIfSk6tJJ8ztBg29tdwSnAu"  # 需改成自己的
sessionid = "bzc2sgp9wp4q40w2lkjjgoa363tfeiap"  # 需改成自己的
university_id = "3420"  # 需改成自己的
# 按需修改域名 example:https://*****.yuketang.cn/
url_root = "https://changjiang.yuketang.cn/"
learning_rate = 4  # 学习速率 我觉得默认的这个就挺好的

# 以下字段不用改，下面的代码也不用改动
user_id = ""

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=' + university_id + '; platform_id=3',
    'x-csrftoken': csrftoken,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': university_id,
    'xtbz': 'cloud'
}

leaf_type = {
    "video": 0,
    "homework": 6,
    "exam": 5,
    "recommend": 3,
    "discussion": 4
}


def one_video_watcher(video_id, video_name, cid, user_id, classroomid, skuid):
    video_id = str(video_id)
    classroomid = str(classroomid)
    url = url_root + "video-log/heartbeat/"
    get_url = url_root + "video-log/get_video_watch_progress/?cid=" + str(
        cid) + "&user_id=" + str(user_id) + "&classroom_id=" + classroomid + "&video_type=video&vtype=rate&video_id=" + str(
        video_id) + "&snapshot=1&term=latest&uv_id=" + str(university_id) + ""
    progress = requests.get(url=get_url, headers=headers)
    if_completed = '0'
    try:
        if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
    except:
        pass
    if if_completed == '1':
        print(video_name + "已经学习完毕，跳过")
        return 1
    else:
        print(video_name + "，尚未学习，现在开始自动学习")
        time.sleep(2)

    # 默认为0（即还没开始看）
    video_frame = 0
    val = 0
    # 获取实际值（观看时长和完成率）
    try:
        res_rate = json.loads(progress.text)
        tmp_rate = res_rate["data"][video_id]["rate"]
        if tmp_rate is None:
            return 0
        val = tmp_rate
        video_frame = res_rate["data"][video_id]["watch_length"]
    except Exception as e:
        print(e.__str__())

    t = time.time()
    timstap = int(round(t * 1000))
    heart_data = []
    while float(val) <= 0.95:
        for i in range(3):
            heart_data.append(
                {
                    "i": 5,
                    "et": "loadeddata",
                    "p": "web",
                    "n": "ali-cdn.xuetangx.com",
                    "lob": "cloud4",
                    "cp": video_frame,
                    "fp": 0,
                    "tp": 0,
                    "sp": 2,
                    "ts": str(timstap),
                    "u": int(user_id),
                    "uip": "",
                    "c": cid,
                    "v": int(video_id),
                    "skuid": skuid,
                    "classroomid": classroomid,
                    "cc": video_id,
                    "d": 4976.5,
                    "pg": video_id + "_" + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', 4)),
                    "sq": i,
                    "t": "video"
                }
            )
            video_frame += learning_rate
        data = {"heart_data": heart_data}
        r = requests.post(url=url, headers=headers, json=data)
        heart_data = []
        try:
            delay_time = re.search(
                r'Expected available in(.+?)second.', r.text).group(1).strip()
            print("由于网络阻塞，万恶的雨课堂，要阻塞" + str(delay_time) + "秒")
            time.sleep(float(delay_time) + 0.5)
            print("恢复工作啦～～")
            r = requests.post(url=submit_url, headers=headers, data=data)
        except:
            pass
        try:
            progress = requests.get(url=get_url, headers=headers)
            res_rate = json.loads(progress.text)
            tmp_rate = res_rate["data"][video_id]["rate"]
            if tmp_rate is None:
                return 0
            val = str(tmp_rate)
            print("学习进度为：\t" + str(float(val) * 100) + "%/100%")
            time.sleep(2)
        except Exception as e:
            print(e.__str__())
            pass
    print("视频" + video_id + " " + video_name + "学习完成！")
    return 1


def get_videos_ids(course_name, classroom_id, course_sign):
    get_homework_ids = url_root + "mooc-api/v1/lms/learn/course/chapter?cid=" + str(
        classroom_id) + "&term=latest&uv_id=" + university_id + "&sign=" + course_sign
    homework_ids_response = requests.get(url=get_homework_ids, headers=headers)
    homework_json = json.loads(homework_ids_response.text)
    homework_dic = {}
    try:
        for i in homework_json["data"]["course_chapter"]:
            for j in i["section_leaf_list"]:
                if "leaf_list" in j:
                    for z in j["leaf_list"]:
                        if z['leaf_type'] == leaf_type["video"]:
                            homework_dic[z["id"]] = z["name"]
                else:
                    if j['leaf_type'] == leaf_type["video"]:
                        # homework_ids.append(j["id"])
                        homework_dic[j["id"]] = j["name"]
        print(course_name + "共有" + str(len(homework_dic)) + "个作业喔！")
        return homework_dic
    except:
        print("fail while getting homework_ids!!! please re-run this program!")
        raise Exception(
            "fail while getting homework_ids!!! please re-run this program!")


if __name__ == "__main__":
    # your_courses = []

    # # 首先要获取用户的个人ID，即user_id,该值在查询用户的视频进度时需要使用
    # user_id_url = url_root + "edu_admin/check_user_session/"
    # id_response = requests.get(url=user_id_url, headers=headers)
    # try:
    #     # user_id = re.search(r'"user_id":(.+?)}',
    #     #                     id_response.text).group(1).strip()
    #     user_id = "32752679"
    # except:
    #     print("也许是网路问题，获取不了user_id,请试着重新运行")
    #     raise Exception(
    #         "也许是网路问题，获取不了user_id,请试着重新运行!!! please re-run this program!")

    # # 然后要获取教室id
    # get_classroom_id = url_root + \
    #     "mooc-api/v1/lms/user/user-courses/?status=1&page=1&no_page=1&term=latest&uv_id=" + \
    #     university_id + ""
    # submit_url = url_root + \
    #     "mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id=" + university_id + ""
    # classroom_id_response = requests.get(url=get_classroom_id, headers=headers)
    # try:
    #     for ins in json.loads(classroom_id_response.text)["data"]["product_list"]:
    #         your_courses.append({
    #             "course_name": ins["course_name"],
    #             "classroom_id": ins["classroom_id"],
    #             "course_sign": ins["course_sign"],
    #             "sku_id": ins["sku_id"],
    #             "course_id": ins["course_id"]
    #         })
    # except Exception as e:
    #     print("fail while getting classroom_id!!! please re-run this program!")
    #     raise Exception(
    #         "fail while getting classroom_id!!! please re-run this program!")

    # # 显示用户提示
    # for index, value in enumerate(your_courses):
    #     print("编号：" + str(index + 1) + " 课名：" + str(value["course_name"]))

    # flag = True
    # while(flag):
    #     number = input("你想刷哪门课呢？请输入编号。输入0表示全部课程都刷一遍\n")
    #     # 输入不合法则重新输入
    #     if not (number.isdigit()) or int(number) > len(your_courses):
    #         print("输入不合法！")
    #         continue
    #     elif int(number) == 0:
    #         flag = False    # 输入合法则不需要循环
    #         # 0 表示全部刷一遍
    #         for ins in your_courses:
    #             homework_dic = get_videos_ids(
    #                 ins["course_name"], ins["classroom_id"], ins["course_sign"])
    #             for one_video in homework_dic.items():
    #                 one_video_watcher(one_video[0], one_video[1], ins["course_id"], user_id, ins["classroom_id"],
    #                                   ins["sku_id"])
    #     else:
    #         flag = False    # 输入合法则不需要循环
    #         # 指定序号的课程刷一遍
    #         number = int(number) - 1
    #         homework_dic = get_videos_ids(your_courses[number]["course_name"], your_courses[number]["classroom_id"],
    #                                       your_courses[number]["course_sign"])
    #         for one_video in homework_dic.items():
    #             one_video_watcher(one_video[0], one_video[1], your_courses[number]["course_id"], user_id,
    #                               your_courses[number]["classroom_id"],
    #                               your_courses[number]["sku_id"])
    leaf_data = {'sku_id': 5094031,
                 'is_assessed': False,
                 'locked_reason': None,
                 'course_id': 2580703,
                 'classroom_short_name': '统本大数据2001',
                 'university_id': 3420,
                 'score_deadline': 0,
                 'current_price': 0,
                 'id': 13166842,
                 'user_id': 32752679,
                 'content_info': {'status': 'post',
                                  'video_user_play': None,
                                  'expand_discuss': False,
                                  'score_evaluation': {'score_proportion': {'proportion': 0.2},
                                                       'score': 1.0,
                                                       'id': 6,
                                                       'name': '视频'},
                                  'download': [],
                                  'is_score': True,
                                  'is_discuss': False,
                                  'remark': {'remark': ''},
                                  'cover_desc': '',
                                  'cover_thumbnail': '',
                                  'media': {'ccid': '26E5D9EA229B85D69C33DC5901307461',
                                                     'cover': '',
                                                     'name': '7.2 地图上的点与线.mp4',
                                                     'duration': 0,
                                                     'type': 'video',
                                                     'size': 538003183},
                                  'cover': '',
                                           'leaf_type_id': None,
                                           'is_attachment_download': True,
                                           'context': ''},
                 'classroom_id': '11169384',
                 'leaf_type': 0,
                 'has_classend': False,
                 'upgrade_sku_status': None,
                 'price': 0,
                 'user_role': 3,
                 'class_start_time': 1661961600000,
                 'upgrade_sku_id': None,
                 'be_in_force': False,
                 'teacher': {'org_name': '浙江大学',
                             'picture': 'https://qn-next.xuetangx.com/15819238431460.jpg',
                             'name': '陈为',
                             'department_name': '计算机学院',
                             'intro': '陈为，浙江大学计算机学院教授，博导，十三五国家重点研发专项“云计算与大数据”总体组与指南组专家。研究兴趣是大数据可视分析与医疗人工智能。承担国家自然科学基金重点项目等国家项目十余项。发表国际顶级期刊和会议论文50余篇。出版教材3部（数据可视化），专著两部（可视分析；大数据），在国内外学术界和工业界形成较大影响。自2009年起在浙江大学每年主办可视化方面的研讨会或暑期学校，受众超过3000人。自2011年起在浙江大学计算机学院开始数据可视化课程，深受好评。',
                                      'job_title': '教授'},
                 'is_score': True,
                 'is_deleted': False,
                 'name': '7.2 地图上的点与线',
                 'is_locked': False,
                 'class_end_time': 1672502400000
                 }

    one_video_watcher(leaf_data["id"], '7.2 地图上的点与线.mp4', leaf_data["course_id"], leaf_data["user_id"],
                      '11169384',
                      5094031)
    print("搞定啦")
