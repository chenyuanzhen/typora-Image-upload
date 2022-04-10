import main
import re


def replace(match):
    # print(match.group("path"))
    return "(h)"


# if __name__ == '__main__':
#     # [!\[.*\](].*[)]
#     # path = re.sub(, "http://s", "![file](a.jpg)")
#     # r!\[.*\]\((.*)\)
#     line = "![image-20220127213400616](image-20220127213400616.png)![asb](ssss.png)"
#     paths = re.findall(r"!\[.*\]\((.*)\)", line)
#     for path in paths:
#         print(path)
#         line = line.replace(path, "https://s")
#
#     print(line)
#
#
