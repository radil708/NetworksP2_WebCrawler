
def send_message_display_helper(str_in : str) -> str:
    '''
    Helper function to mySimpleSocketObj.send_msg()
        that will help in formatting messages sent over so the user
        can see special characters like "\n", "\r\", and "\r\n\r\n".
        Existence of different combinations of characters in the string
        may be formatted incorrectly.
    :param str_in: a string to be formatted. The only special characters that
        should exist in the string are "\n", "\r\n\r\n", and "\n\n\n". Errors
        may occur if other combinations exist like \n\n or \r or \r\r\r\r.
    :return: a formatted string.
    '''
    new_string = ""
    replaced_alpha = str_in.replace("\r\n", "\\r\\n\r\n")
    prev = replaced_alpha[0]
    new_string += prev
    for i in range(1,len(replaced_alpha)):
        current = replaced_alpha[i]

        if prev != "\r" and current == "\n":
            new_string += "\\n\n"
        else:
            new_string += current
        prev = replaced_alpha[i]

    return new_string