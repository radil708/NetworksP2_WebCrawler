#!/usr/bin/env python3

from my_http_requests_package.my_http_request import *
from project_constants import *
from html_parser_package.myHTMLParsers import VISITED_SITES, TO_VISIT, SECRET_FLAGS, \
    LinkHTMLParserObj, secretFlagParserObj
from helper_functions_p2 import getArgs, get_cookie, get_session_id, get_first_line

TO_PARSE = []


def main():
    list_args = getArgs()

    if len(list_args) < 2 or len(list_args) > 2:
        print("ERROR: Incorrect amount of args passed\nPlease only pass 2 args in the format <username> <password>")

    response_parser = HTMLResponseHelper()
    status_parser = HTMLHeadParser()
    htmlLinkFinderParser = LinkHTMLParserObj()
    htmlSecretFlagParser = secretFlagParserObj()
    htmlSecretFlagParser.reset_flag()

    # Create the socket and connect to server
    socket_1 = mySimpleSocketObj(host_in=HW2_HOST_NAME, port_in=HW2_PORT,ssl_protocol="TLS",display_success_msg=False)

    # GET request to get first cookie/csrftoken
    socket_1.send_msg(get_first_line('/accounts/login/') + "Host: " + HW2_HOST_NAME + "\r\n" + "\n",display_sent=False)
    get_login_response = socket_1.rcv_msg(display_rcvd_msg=False,display_byte_received=False)
    get_login_head = response_parser.get_HTML_response_head(get_login_response, display=False, display_formatted=False)
    cookie_1 = get_cookie(get_login_head, display=False)

    # Create the HTTP handler object
    HTTPHandler = myHTTPRequestObj(socket_1)
    HTTPHandler.set_csrftoken(cookie_1)

    # create post payload
    payload_post = {}
    payload_post["username"] = list_args[0]
    payload_post["password"] = list_args[1]
    payload_post["csrfmiddlewaretoken"] = cookie_1
    payload_post["next"] = "%2Ffakebook%2F"

    login_flag = False

    # post to login/ get new cookie and session id
    while login_flag == False:
        login_post_resp = HTTPHandler.post_request("/accounts/login/", payload_post, show_sent=False, show_resp=False)
        login_post_resp_head = response_parser.get_HTML_response_head(login_post_resp,display=False,display_formatted=False)
        try:
            cookie_2 = get_cookie(login_post_resp_head)
            login_flag = True
        except RuntimeError:
            continue

    # check if session id exists, if correct username or password passed it will have session id
    try:
        session_id_1 = get_session_id(login_post_resp_head)
    except RuntimeError:
        print(f"ERROR: Incorrect username: {list_args[0]} or password: {list_args[1]}", end="")
        exit(1)

    HTTPHandler.set_csrftoken(cookie_2)
    HTTPHandler.set_session_id(session_id_1)

    home_page_response = HTTPHandler.get_request(resource="/fakebook/",show_sent=False,show_rcd_resp=False)
    home_page_head = response_parser.get_HTML_response_head(home_page_response)
    home_page_payload_html = response_parser.get_HTML_response_body(home_page_response)

    session_id_2 = get_session_id(home_page_head)
    HTTPHandler.set_session_id(session_id_2)

    htmlSecretFlagParser.feed(home_page_payload_html)
    htmlLinkFinderParser.feed(home_page_payload_html)

    while len(SECRET_FLAGS) < 5 and len(TO_VISIT) > 0:
        URI = TO_VISIT.pop(0)
        current_resp = HTTPHandler.get_request(URI)

        try:
            current_resp_body = response_parser.get_HTML_response_body(current_resp)
        except IndexError:
            # links with "dud"/incomplete html doc
            VISITED_SITES.append(URI)
            continue

        current_resp_head = response_parser.get_HTML_response_head(current_resp)
        status_parser.fill_self_data(current_resp_head)

        # list of sites to visit grows way faster than htmls searched through
        # I address this by looking at 100 sites before adding more links
        # once I store 100 htmls to look through
        if status_parser.give_status_code() == "200":
            if len(TO_PARSE) < 100:
                TO_PARSE.append(current_resp_body)
                htmlLinkFinderParser.feed(current_resp_body)
                VISITED_SITES.append(URI)
            # look for secret flag on 100 htmls before adding more htmls to list of sites to crawl
            else:
                while len(TO_PARSE) > 0:
                    popped_body = TO_PARSE.pop(0)
                    htmlSecretFlagParser.reset_flag()
                    htmlSecretFlagParser.feed(popped_body)
        # For temporary server error
        elif status_parser.give_status_code() == "503":
            TO_VISIT.append(URI)
            continue
        else:
            VISITED_SITES.append(URI)
            continue

    for each in SECRET_FLAGS:
        print(each)

    HTTPHandler.close_http_connection()
    exit(0)

main()