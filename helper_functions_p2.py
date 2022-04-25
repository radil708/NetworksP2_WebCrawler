import sys


def getArgs() -> list:
    '''
    Get the arguments passed
    :return: a list that omits the first argument(program name)
    '''
    l1 = sys.argv
    return l1[1:]


def get_first_line(str_in: str) -> str:
    '''
    Create a string that is the start/first line in a GET request
    :param str_in: The resource/URI to send the request to
    :return: a string in the format "GET /someResource HTTP/1.1\r\n"
    '''
    return "GET " + str_in + " HTTP/1.1\r\n"


def post_first_line(str_in: str) -> str:
    '''
    Create a string that is the start/first line in a GET request
    :param str_in: The resource/URI to send the request to
    :return: a string in the format "POST /someResource HTTP/1.1\r\n"
    '''
    return "POST " + str_in + " HTTP/1.1\r\n"


def get_cookie(str_in: str, display: bool = False) -> str:
    '''
    Parses the response of a server. Looks for a cookie/csrftoken and returns it.
    :param str_in: The response from a request to the server as a string
    :param display: A boolean, if true it will display the cookie parsed from the
        response.
    :return: a string representation of the cookie/csrftoken
    '''
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


def get_session_id(str_in: str, display: bool = False) -> str:
    '''
    Parses the response from the server and obtains a cookie/session id.
    :param str_in: The response from a request to the server as a string
    :param display: A boolean, if true it will display the cookie parsed from the
        response.
    :return: s tring representation of the session id / cookie
    '''
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
