

def check_len_constraint(check_string: str, max_len: int) -> bool:
    """ util function to check if the length is as per passed constraint or not
    :param check_string:
    :type check_string:
    :param max_len:
    :type max_len:
    :return:
    :rtype:
    """
    return True if len(check_string) <= max_len else False

