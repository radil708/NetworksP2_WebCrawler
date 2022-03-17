import socket
import ssl
from simple_socket_package.helper_functions import send_message_display_helper

DEFAULT_TIMEOUT_VAL_SEC = 20
# Variable for making display messages neat
SINGLE_LINE_DIVIDER = "------------------------------------------------------"

'''
    This class is an ssl socket that will connect with the project servers.
        It can send messages, receive messages and will display information
        depending on whether the user wants it to or not. It has default values
        as it is specialized for HW2, but changing the parameters will make it
        flexible enough for project reuse. The information is helpful for 
        debugging but assignment requirements don't want them.
'''
class mySimpleSocketObj:
    def __init__(self, host_in, port_in, timeout_sec=DEFAULT_TIMEOUT_VAL_SEC,
                 display_success_msg=True, display_errors=True, ssl_protocol="TLS"):
        '''
        This will create a wrapped ssl socket that will connect to a host and port passed in the
            args.
        :param host_in: The server as a string. This program will automatically convert it
                            to the IP address. By default it is "project2.5700.network".
        :param port_in: The port the socket will connect to as an int. By default it is
                            the HTTP port 443.
        :param timeout_sec: The time in sec as an int. Will dictate how long the socket will wait
                                for a response. By default it is 20 sec
        :param display_success_msg: A boolean, if true it will display success messages, else
                                        it will not display any success messages. It is true by defualt.
        :param display_errors: A boolean, if true it will display any errors messages, else
                                the program will exit without any messages. It is true by default.
        :param ssl_protocol: The protocol to use as a String. Valid options are:
                                'TLS' , 'TLSv1' , 'TLSv1.1', or 'TLSv1.2'
        '''

        host_ip = socket.gethostbyname(host_in)

        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.settimeout(timeout_sec)

        # TLS is default value
        if ssl_protocol == "TLS":
            #protocol for HW2
            self.socket = ssl.wrap_socket(my_socket)
        elif ssl_protocol == "TLSv1":
            # protocol used for HW1
            self.socket = ssl.wrap_socket(my_socket, ssl_version=ssl.PROTOCOL_TLSv1)
        elif ssl_protocol == "TLSv1.1":
            self.socket = ssl.wrap_socket(my_socket, ssl_version=ssl.PROTOCOL_TLSv1_1)
        elif ssl_protocol == "TLSv1.2":
            self.socket = ssl.wrap_socket(my_socket, ssl_version=ssl.PROTOCOL_TLSv1_2)
        else:
            if display_errors:
                raise ValueError("ERROR: ssl_protocol can only be one of the following:\n"
                                 "'TLS' , 'TLSv1' , 'TLSv1.1', or 'TLSv1.2' ")
            else:
                exit(1)

        self.assigned_ssl_protocol = ssl_protocol
        self.assigned_host = host_in
        self.assigned_port = port_in
        self.assigned_displays = display_success_msg

        try:
            self.socket.connect((host_ip, port_in))
            if display_success_msg:
                print(f"Socket Successfully Connected to:\nHost: {host_in}\nIP: {host_ip}\nPort: {port_in}\n"
                      + SINGLE_LINE_DIVIDER + "\n")
        except:
            if display_errors:
                raise RuntimeError(f"ERROR:\n\tSocket Failed to connect to Host: {host_in}, IP: {host_ip} at Port: {port_in}\n")
            else:
                exit(1)

    def send_msg(self, msg_send: str,encoding_schema="", display_sent=True) -> None:
        '''
        A message as a string will be encoded according to input
            then sent to the server.
        :param msg_send: The message to send as a string
        :param encoding_schema: The encoding type i.e. utf-8, ascii.. etc as a String
        :param display_sent: A boolean that will display the message sent as a String
                                formatted to show newline characters. True by default.
        :return: Void.
        '''

        if display_sent == True:
            print("SENDING:")
            print(send_message_display_helper(msg_send)+ SINGLE_LINE_DIVIDER + "\n")

        if encoding_schema == "":
            send_out_bytes = msg_send.encode()
        else:
            send_out_bytes = msg_send.encode(encoding_schema)

        self.socket.send(send_out_bytes)

    def rcv_msg(self,byte_limit=2048,end_char="\n",decoding_schema="",
                display_byte_received=True, display_rcvd_msg=False,
                display_error_msg=True) -> str:
        '''
        This will receive a message from the server and decode it to a string.
            the decoded string will be returned.
        :param byte_limit: The amount of bytes that can be received at any one time
                                as an int. It is 2048 by default.
        :param end_char: The character that announces the end of the message.
        :param decoding_schema: The decoding schema as a string. utf-8. ascii etc...
        :param display_byte_received: A boolean, it will display byte received info.
                                        It is true by default.
        :param display_rcvd_msg: This will display the completely received
                                    and formatted message if true. It is false
                                    by default.
        :return: The complete response from the server as a String.
        '''
        full_response = ""

        total_bytes_received = 0

        empty_counter = 0

        if display_byte_received == True:
            print("RECEIVING:")

        while True:
            received = self.socket.recv(byte_limit)
            total_bytes_received += len(received)

            if display_byte_received == True:
                print(f"Received {len(received)} bytes")

            if decoding_schema == "":
                decoded_buffer = received.decode()
            else:
                decoded_buffer = received.decode(decoding_schema)

            full_response += decoded_buffer

            if (empty_counter) > 4:
                if display_error_msg == False:
                    exit(1)
                else:
                    raise RuntimeError("ERROR: Received only empty bytes,\n"
                                       "Check message sent to server!")

            if len(decoded_buffer) == 0:
                empty_counter +=1

            if len(decoded_buffer) > 0 and decoded_buffer[-1] == end_char:
                break

        if display_byte_received == True and display_rcvd_msg == True:
            print(f"Total bytes received = {total_bytes_received}\n\n" + "RECEIVED MESSAGE: ")
            print(send_message_display_helper(full_response))
            print(SINGLE_LINE_DIVIDER + "\n")
        elif display_byte_received == True and display_rcvd_msg == False:
            print(f"Total bytes received = {total_bytes_received}\n" + SINGLE_LINE_DIVIDER + "\n")
        elif display_byte_received == False and display_rcvd_msg == True:
            print("RECEIVED MESSAGE: " + send_message_display_helper(full_response) + "\n" + SINGLE_LINE_DIVIDER + "\n")

        return full_response

    def close_connection(self, display_closing_msg = True):
        '''
        This will close the socket connection.
        :param display_closing_msg: A boolean. It will display connection closed
            message if true. It will not display anything otherwise.
        :return: void
        '''
        if display_closing_msg == True:
            print("\nSocket connection closed\nEXITING PROGRAM\n" + SINGLE_LINE_DIVIDER)

        self.socket.close()