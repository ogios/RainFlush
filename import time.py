# import json

# res = json.loads("{}")
# print(res)

st = "f"
print(st.replace("f", 1))

# import time
# from alive_progress import alive_bar

# duration = 226
# count = 0
# tmp = []
# with alive_bar(duration) as bar:
#     for i in range(1, int(duration/5)+1):
#         count += 5
#         tmp += [1]
#         if len(tmp) >= 7:
#             print("send")
#             tmp = []
#             print("Pending...")
#             time.sleep(5)
#         # print(i)
#         bar(5)
#     bar(duration-count)
# print("done.")
