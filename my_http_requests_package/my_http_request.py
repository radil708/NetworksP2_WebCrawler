from simple_socket_package.mySimpleSocket import *
from html_parser_package.myHTMLParsers import HTMLResponseHelper, HTMLHeadParser
from helper_functions_p2 import get_first_line, post_first_line

class myHTTPRequestObj:
    def __init__(self, socket_in : mySimpleSocketObj):
        #set up all parsers
        self.responseParser = HTMLResponseHelper()
        self.statusParser = HTMLHeadParser()

        # set up socket and get save socket info for easy reference
        self.current_socket = socket_in
        self.socket_ssl_protocol = (self.current_socket).assigned_ssl_protocol
        self.socket_host = (self.current_socket).assigned_host
        self.socket_port = (self.current_socket).assigned_port
        self.host_header = "Host: " + self.socket_host + "\r\n"
        self.socket_display_bool = self.current_socket.assigned_displays

        self.current_csrftoken = None
        self.current_session_id = None

    def set_csrftoken(self, token_in : str):
        self.current_csrftoken = token_in

    def set_session_id(self,sess_id_in : str):
        self.current_session_id = sess_id_in

    def post_request(self, resource : str, payload_in : dict, show_sent = False, show_resp = False, encoding_in =""):
        payload_str = ""

        # translate the dictionary into a string payload
        for key,value in payload_in.items():
            payload_str += key + "=" + value + "&"

        # processing payload to add end char and removing extra &
        payload_str = payload_str.rstrip("&")
        payload_str += "\r\n"

        payload_len = len(payload_str)

        start_line = post_first_line(resource)
        optional_header_lines = self.host_header + "Connection: keep-alive" + "\r\n"
        optional_header_lines += "Content-Type: application/x-www-form-urlencoded" + "\r\n"
        optional_header_lines += "Content-Length: " + str(payload_len) + "\r\n"
        optional_header_lines += "Cache-Control: max-age=0" + "\r\n"
        optional_header_lines += "Cookie:csrftoken=" + self.current_csrftoken + "\r\n\r\n"

        full_request = start_line + optional_header_lines + payload_str + "\n"

        if show_sent == True:
            print("SENDING POST REQUEST: ")
            print(send_message_display_helper(full_request))

        connection_flag = False

        while connection_flag == False:
            try:
                self.current_socket.send_msg(msg_send=full_request, encoding_schema=encoding_in,display_sent=False)
                post_response = self.current_socket.rcv_msg(decoding_schema=encoding_in,display_byte_received=False,
                                                            display_rcvd_msg=show_resp)
                connection_flag = True
            # If connection drops for any reason, close current then open a new one as many times as needed
            except ConnectionAbortedError:
                self.current_socket.close_connection(display_closing_msg=self.socket_display_bool)
                self.current_socket = None
                self.current_socket = mySimpleSocketObj(host_in=self.socket_host, port_in=self.socket_port,
                                                        ssl_protocol=self.socket_ssl_protocol,
                                                        display_success_msg=self.socket_display_bool)
                continue
            # If the server responds with empty response close connection and then open a new one as many times as neede
            except RuntimeError:
                self.current_socket.close_connection(display_closing_msg=self.socket_display_bool)
                self.current_socket = None
                self.current_socket = mySimpleSocketObj(host_in=self.socket_host, port_in=self.socket_port,
                                                        ssl_protocol=self.socket_ssl_protocol,
                                                        display_success_msg=self.socket_display_bool)
                continue

            post_head = self.responseParser.get_HTML_response_head(post_response)
            self.statusParser.fill_self_data(post_head)

            # if I receive these status codes, resend message until I get the OK, because server will
            # intentionally send these even if name and password are correct!
            if self.statusParser.give_status_code() == "403" or self.statusParser.give_status_code() == "503":
                continue
            else:
                break

        return post_response


    def get_request(self, resource, show_sent=False, show_rcd_byte=False, show_rcd_resp=False, encoding_schema=""):
        msg = get_first_line(resource) + self.host_header
        msg += "Connection: keep-alive" + "\r\n"

        if self.current_csrftoken != None and self.current_session_id != None:
            msg += "Cookie: csrftoken=" + self.current_csrftoken + "; sessionid=" +\
                   self.current_session_id + "\r\n\n"
        else:
            raise RuntimeError("ERROR: csrftoken or session id missing, please set them before calling get")

        if show_sent == True:
            print("SENDING GET REQUEST: \n" + msg)

        connection_flag = False

        while connection_flag == False:
            try:
                (self.current_socket).send_msg(msg_send=msg,encoding_schema=encoding_schema,display_sent=show_sent)
                get_response = self.current_socket.rcv_msg(decoding_schema=encoding_schema,
                                                           display_byte_received=show_rcd_byte,
                                                           display_rcvd_msg=show_rcd_resp)
                connection_flag = True
            # If connection drops for any reason, close current then open a new one as many times as needed
            except ConnectionAbortedError:
                self.current_socket.close_connection(display_closing_msg=self.socket_display_bool)
                self.current_socket = None
                self.current_socket = mySimpleSocketObj(host_in=self.socket_host, port_in=self.socket_port,
                                                        ssl_protocol=self.socket_ssl_protocol,
                                                        display_success_msg=self.socket_display_bool)
                continue
            # If the server responds with empty response close connection and then open a new one as many times as neede
            except RuntimeError:
                self.current_socket.close_connection(display_closing_msg=self.socket_display_bool)
                self.current_socket = None
                self.current_socket = mySimpleSocketObj(host_in=self.socket_host, port_in=self.socket_port,
                                                        ssl_protocol=self.socket_ssl_protocol,
                                                        display_success_msg=self.socket_display_bool)
                continue

        return get_response

    def close_http_connection(self):
        self.current_socket.close_connection()





