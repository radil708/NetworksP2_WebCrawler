from html.parser import HTMLParser


VISITED_SITES = ["/", "/fakebook", "/fakebook/",'/accounts/login/',"/accounts/logout/"]
TO_VISIT = []
SECRET_FLAGS = []


class LinkHTMLParserObj(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if attrs[0][1][0] != "/":
                return
            elif (attrs[0][1] not in VISITED_SITES) and (attrs[0][1] not in TO_VISIT):
                TO_VISIT.append(attrs[0][1])
        else:
            return

class secretFlagParserObj(HTMLParser):

    def reset_flag(self):
        self.found_flag = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "h2":
            for t1,t2 in attrs:
                if t1 == "class" and t2 == "secret_flag":
                    self.found_flag = True

    def handle_data(self, data: str) -> None:
        if self.found_flag == True:
            if data[6:] not in SECRET_FLAGS:
                # print secret flag
                #print(data[6:])
                # data is "FLAG: asdsd.. so slice to only keep flag value
                SECRET_FLAGS.append(data[6:])
        self.found_flag = False




class HTMLResponseHelper:
    def __init__(self):
        self.info = "This is am HTMLResponseHelper object"

    def get_HTML_response_head(self,str_in, display = False, display_formatted = False):

        head =  str_in.split("\r\n\r\n")[0]

        if display == True and display_formatted == True:
            print(self.string_display_formatter(head))
        elif display == True and display_formatted == False:
            print(head)

        return head

    def get_HTML_response_body(self, str_in, display = False, display_formatted = False):

        body = str_in.split("\r\n\r\n")[1]

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
    def __init__(self):
        self.info = "This is an HTML Head Parser Object"
        self.my_map = None

    def fill_self_data(self, str_in):
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
        if self.my_map == None:
            raise RuntimeError("No Map exists, please call fill_self_data method")
        else:
            return self.my_map["status_code"]


