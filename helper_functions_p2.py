import sys

def getArgs():
    '''
    Get the arguments passed
    :return: a list that omits the first argument(program name)
    '''
    l1 = sys.argv
    return l1[1:]

def get_first_line(str_in):
    return "GET " + str_in + " HTTP/1.1\r\n"

def post_first_line(str_in):
    return "POST " + str_in + " HTTP/1.1\r\n"

def get_cookie(str_in, display=False):
    list_head = str_in.split("\r\n")
    target_line = ""

    for each in list_head:
        if "Set-Cookie: csrftoken=" in each:
            target_line = each
            break
        else:
            continue

    if target_line == "":
        raise RuntimeError("There was no 'Set-Cookie' in the response headers")
    if ";" not in target_line:
        raise RuntimeError("no delimiting token ';' UNABLE to PARSE")

    target_line_list = target_line.split(";")
    final_target = target_line_list[0]
    final_target = final_target.lstrip("Set-Cookie: csrftoken=")

    if display == True:
        print("Cookie: " + final_target)

    return final_target

def get_session_id(str_in, display = False):
    list_head = str_in.split("\r\n")
    target_line = ""

    for each in list_head:
        if "Set-Cookie: sessionid=" in each:
            target_line = each
            break
        else:
            continue

    if target_line == "":
        raise RuntimeError("There was no 'Set-Cookie: sessionid' in the response headers")


    target_line_list = target_line.split(";")
    final_target = target_line_list[0]
    final_target = final_target.lstrip("Set-Cookie: sessionid=")

    if display == True:
        print("Session id: " + final_target)

    return final_target







