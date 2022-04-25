from html.parser import HTMLParser


VISITED_SITES = ["/", "/fakebook", "/fakebook/",'/accounts/login/',"/accounts/logout/"]
TO_VISIT = []
SECRET_FLAGS = []


class LinkHTMLParserObj(HTMLParser):
    '''
    A subclass of the HTMLParser super class. Its purpose is to find
        links for website to crawl from an html doc string.
    '''

    def handle_starttag(self, tag, attrs):
        '''
        An ovveride of the superclass method.
        Any time a website that has not been visited is encountered, the site is added
        to the TO_VISIT list. This will automatically be called for each start tag after
         calling the .feed(<html document>) method
        :param tag: a string representation of any start tag in an html document
        :param attrs: a string representation of the value associated with a tag
        :return: Void / None
        '''
        if tag == "a":
            if attrs[0][1][0] != "/":
                return
            elif (attrs[0][1] not in VISITED_SITES) and (attrs[0][1] not in TO_VISIT):
                TO_VISIT.append(attrs[0][1])
        else:
            return

class secretFlagParserObj(HTMLParser):
    '''
    A subclass of the HTMLParser super class. Its purpose is to find
        secret flags placed in a given html doc string
    '''

    def reset_flag(self):
        '''
        Helper method to set the found_flag attr to false
        :return:
        '''
        self.found_flag = False

    def handle_starttag(self, tag: str, attrs) -> None:
        '''
        An ovveride of the superclass method.
        Any time a secret flag is encountered, found flag is set to tru.
        This will automatically be called for each start tag after calling the .feed(<html document>) method
        :param tag: a string representation of any start tag in an html document
        :param attrs: a string representation of the value associated with a tag
        :return: Void / None
        '''
        if tag == "h2":
            for t1,t2 in attrs:
                if t1 == "class" and t2 == "secret_flag":
                    self.found_flag = True

    def handle_data(self, data: str) -> None:
        '''
        Any time the found_flag is true, the data must contain the secret flag. It will add the secret flag
        to the SECRET_FLAGS list and then set the found_flag back to false.
        This will automatically be called for each data after calling the .feed(<html document>) method
        :param data: a string representation of any data in an html document
        :return: Void / None
        '''
        if self.found_flag == True:
            if data[6:] not in SECRET_FLAGS:
                # print secret flag
                #print(data[6:])
                # data is "FLAG: asdsd.. so slice to only keep flag value
                SECRET_FLAGS.append(data[6:])
        self.found_flag = False




class HTMLResponseHelper:
    '''
    This class is meant to cleave the server responses into the head and payload.
    '''

    def get_HTML_response_head(self,str_in : str, display : bool = False,
                               display_formatted: bool= False, delimiter : str = "\r\n\r\n") -> str:
        '''
        Splits the server response and returns only the NON-PAYLOAD i.e. head section.
        :param str_in: The server response as a string
        :param display: A boolean, if true it will print out / display the head
        :param display_formatted: A boolean. If display is true and this is true
            then the display will format the string to show the CRLF and newline characters.
        :param delimiter: The delimiting character that is used to cleave the server response
            into two. By default it is 2 CRLF i. "\r\n\r\n"
        :return: a string representation (unformatted) of the the head.
        '''

        head =  str_in.split(delimiter)[0]

        if display == True and display_formatted == True:
            print(self.string_display_formatter(head))
        elif display == True and display_formatted == False:
            print(head)

        return head

    def get_HTML_response_body(self, str_in : str, display: bool = False,
                               display_formatted: bool = False, delimiter : str = "\r\n\r\n") -> str:
        '''
        Splits the server response and returns ONLY the PAYLOAD section.
        :param str_in: The server response as a string
        :param display:  A boolean, if true it will print out / display the payload
        :param display_formatted:  A boolean. If display is true and this is true
            then the display will format the string to show the CRLF and newline characters.
        :param delimiter: The delimiting character that is used to cleave the server response
            into two. By default it is 2 CRLF i. "\r\n\r\n"
        :return: a string representation (unformatted) of the payload
        '''

        body = str_in.split(delimiter)[1]

        if display == True and display_formatted == True:
            print(self.string_display_formatter(body))
        elif display == True and display_formatted == False:
            print(body)

        return body


    def string_display_formatter(self,str_in):
        '''
            Helper function to HTMLResponseHelper
                that will help in formatting messages sent over so the user
                can see special characters like "\n", "\r\", and "\r\n\r\n".
                Existence of different combinations of characters in the string
                may be formatted incorrectly.
            :param str_in: a string to be formatted. The only special characters that
                should exist in the string are "\n", and "\r\n". Errors
                may occur if other combinations exist like \n\n or \r or \r\r\r\r.
            :return: a formatted string.
            '''
        new_string = ""
        replaced_alpha = str_in.replace("\r\n", "\\r\\n\r\n")
        prev = replaced_alpha[0]
        new_string += prev
        for i in range(1, len(replaced_alpha)):
            current = replaced_alpha[i]

            if prev != "\r" and current == "\n":
                new_string += "\\n\n"
            else:
                new_string += current
            prev = replaced_alpha[i]

        return new_string

class HTMLHeadParser():
    '''
    A helper class used to obtain the headers, values, and status codes of a server response/head.
    '''

    def __init__(self):
        self.my_map = None

    def fill_self_data(self, str_in):
        '''
        Used to get header, values, and status codes of a server response head i.e. the return value of
            HTMLResponseHelper.get_HTML_response_head(<server response>). Stores the headers, values
            and status code in a dictionary of self.my_map
        :param str_in: Only the non-payload portion of the server response. i.e. the return value of
            HTMLResponseHelper.get_HTML_response_head(<server response>).
        :return: None.
        '''
        head_list = str_in.split("\r\n")

        first_line = head_list.pop(0)
        first_line_as_list = first_line.split(" ")
        self.my_map = {}
        self.my_map["status_code"] = first_line_as_list[1]
        self.my_map["status_msg"] = first_line_as_list[2]

        for each in head_list:
            temp = each.split(":")
            header = temp[0].strip()
            value = temp[1].strip()
            self.my_map[header] = value


    def display_map(self):
        if self.my_map == None:
            raise RuntimeError("No Map exists, please call fill_self_data method")
        else:
            for key,value in self.my_map.items():
                print(f"{key} : {value}")

    def give_status_code(self):
        '''
        Returns the status code of a parsed server response head. i.e. call this after calling
        HTMLHeadParserObject.fill_self_data.
        :return: The status code a string.
        '''
        if self.my_map == None:
            raise RuntimeError("No Map exists, please call fill_self_data method")
        else:
            return self.my_map["status_code"]


