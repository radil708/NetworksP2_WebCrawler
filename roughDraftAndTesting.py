from simple_socket_package.mySimpleSocket import *
from project_constants import *
from html_parser_package.myHTMLParsers import *
from helper_functions_p2 import *

HOST_LINE = "Host: " + HW2_HOST_NAME + "\r\n"
COOKIE = None

TO_PARSE = []

def main():
    # Set up helper objects
    response_parser = HTMLResponseHelper()
    link_finder = LinkHTMLParserObj()
    csrftoken_finder = tokenFinder()
    status_parser = HTMLHeadParser()
    secret_flag_finder = secretFlagParserObj()

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #Connect to network
    socket_1 = mySimpleSocketObj(host_in=HW2_HOST_NAME, port_in=HW2_PORT,ssl_protocol="TLS")

    # Send initial get request to homepage "/"
    home_get_request = get_first_line("/") + HOST_LINE + "\n"
    socket_1.send_msg(home_get_request)

    # Get server response
    received_total = socket_1.rcv_msg(display_rcvd_msg=False,display_byte_received=True)
    received_body = response_parser.get_HTML_response_body(received_total,display=False,display_formatted=False)
    # Add any website that is not already in visited list
    link_finder.feed(received_body)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # GET login request, to get csrftoken
    socket_1.send_msg(get_first_line('/accounts/login/') + HOST_LINE + "\n")
    get_login_response = socket_1.rcv_msg(display_rcvd_msg=True)
    get_login_head = response_parser.get_HTML_response_head(get_login_response,display=True, display_formatted=True)
    cookie_1 = get_cookie(get_login_head,display=False)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    while True:
        #POST login request using scrftoken obtained from GET request, to get a new cookie and sessionid
        #TODO On final submission, username and password should use sys args
        init_post_body = "username=" + USERNAME + "&password=" + PASSWORD + "&csrfmiddlewaretoken=" + cookie_1 + \
                         "&next=%2Ffakebook%2F" + "\r\n\n"
        body_len = len(init_post_body)
        init_post_head = post_first_line('/accounts/login/') + HOST_LINE
        init_post_head += "Connection: keep-alive" + "\r\n"
        init_post_head += "Content-Type: application/x-www-form-urlencoded" + "\r\n"
        init_post_head += "Content-Length: " + str(body_len) + "\r\n"
        init_post_head += "Cache-Control: max-age=0" + "\r\n"
        init_post_head += "Cookie:csrftoken=" + cookie_1 + "\r\n\r\n"
        init_post_full = init_post_head + init_post_body

        socket_1.send_msg(init_post_full, display_sent=True)
        post_response = socket_1.rcv_msg(display_rcvd_msg=False)
        post_r_head = response_parser.get_HTML_response_head(post_response)
        status_parser.fill_self_data(post_r_head)

        if status_parser.give_status_code() == "403":
            #TODO delete
            print("403 Forbidden error")
            continue
        elif status_parser.give_status_code() == "503":
            print("503 Service Unavailable")
        else:
            break



    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # get request to get all links from homepage
    post_response_head = response_parser.get_HTML_response_head(post_response, display=True, display_formatted=True)

    cookie_2 = get_cookie(post_response_head, display=True)

    try:
        session_id_1 = get_session_id(post_response_head,display=True)
    except RuntimeError:
        print("incorrect password/username")
        exit(1)

    get_request_2 = get_first_line("/fakebook/") + HOST_LINE + "Cookie: csrftoken=" + cookie_2 + "; sessionid=" \
                    + session_id_1 + "\r\n\n"

    socket_1.send_msg(get_request_2,display_sent=True)
    homepage_html = socket_1.rcv_msg(display_rcvd_msg=True)

    homepage_html_head = response_parser.get_HTML_response_head(homepage_html)


    session_id_2 = get_session_id(homepage_html_head)


    homepage_html_body = response_parser.get_HTML_response_body(homepage_html)
    link_finder.feed(homepage_html_body)
    print(TO_VISIT)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #test checking link

    while len(SECRET_FLAGS) < 5 and len(TO_VISIT) > 0:
        URI = TO_VISIT.pop(0)
        VISITED_SITES.append(URI)
        get_request_3 = get_first_line(URI) + HOST_LINE
        get_request_3 += "Connection: keep-alive" + "\r\n"
        get_request_3 += "Cookie: csrftoken=" + cookie_2 + "; sessionid=" + session_id_2 + "\r\n\n"

        try: #if connection drops
            socket_1.send_msg(get_request_3, display_sent=False)
        except ConnectionAbortedError:
            print("DROPPED")
            socket_1.close_connection()
            socket_1 = mySimpleSocketObj(host_in=HW2_HOST_NAME, port_in=HW2_PORT, ssl_protocol="TLS")
            socket_1.send_msg(get_request_3, display_sent=False)
            #TODO DELETE LINE BELOW
            #response_3 = socket_1.rcv_msg(display_rcvd_msg=False, display_byte_received=False)

        # SERVER no response??
        try: # how can this lead to an error?
            response_3 = socket_1.rcv_msg(display_rcvd_msg=False, display_byte_received=False)
        except RuntimeError:
            print(f"REQUEST SENT: {get_request_3}\n")
            socket_1.close_connection()
            socket_1 = mySimpleSocketObj(host_in=HW2_HOST_NAME, port_in=HW2_PORT, ssl_protocol="TLS")
            socket_1.send_msg(get_request_3, display_sent=False)
            response_3 = socket_1.rcv_msg(display_rcvd_msg=False, display_byte_received=False)
            #continue

        # Try except here

        # They put in duds for responses where HTML is not formed correctly or is just empty
        try:
            response_3_body = response_parser.get_HTML_response_body(response_3)
        except IndexError:
            #TODO delete
            print(f"could not parse body, this is a dud {URI}")
            print(send_message_display_helper(response_3))
            continue

        response_3_head = response_parser.get_HTML_response_head(response_3)



        status_parser.fill_self_data(response_3_head)
        if status_parser.give_status_code() == "200":
            if len(TO_PARSE) < 100:
                TO_PARSE.append(response_3_body)
                link_finder.feed(response_3_body)
            else:
                while len(TO_PARSE) > 0:
                    popped_body = TO_PARSE.pop(0)
                    secret_flag_finder.reset_flag()
                    secret_flag_finder.feed(popped_body)
        elif status_parser.give_status_code() == "302":
            status_parser.display_map()
        elif status_parser.give_status_code() == "503":
            #TODO delete
            print("503 HIT")
            print(URI)
            VISITED_SITES.remove(URI)
            TO_VISIT.append(URI)
            continue
        else:
            print(status_parser.give_status_code())
            print(f"{len(TO_VISIT)} sites left to search")
            print(f"{len(VISITED_SITES)} already visited")
            if (len(SECRET_FLAGS) > 0):
                print(f"flags found so far {len(SECRET_FLAGS)}\nSECRET FLAGS: {SECRET_FLAGS}")
            continue
            #print(f"VISITED:{VISITED_SITES}\nTO VISIT: {TO_VISIT}")


    print("done")
    print(f"{len(TO_VISIT)} sites left to search")
    print(f"{len(VISITED_SITES)} already visited")
    print(SECRET_FLAGS)

    #print(received.split("\r\n\r\n")[1])
    socket_1.close_connection()
    #with open("home_data_test.txt", "r") as t1:
    #    words = t1.readlines()
    #print(words)
main()