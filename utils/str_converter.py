import re


def remove_whitespace(s):
    return s.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")


def convertMMtoInches(mm):
    return round(mm * 0.0393701, 1)


def convertGramtoPound(gram):
    return round(gram * 0.00220462, 1)


def extractFloatFromStr(str):
    values = re.findall(r"[-+]?(?:\d*\.*\d+)", str)
    return float(values[0])


def extract_digit_list_from_str(text):
    values = re.findall(r"[-+]?(?:\d*)", text)
    rets = [int(x) for x in values if x.isdigit()]

    return rets


def extract_digit_from_str(text):
    values = re.findall(r"[-+]?(?:\d*)", text)
    text = "".join(values)

    if len(text) < 1:
        return None
    else:
        return int(text)


def extract_between(text, sub1, sub2):
    idx1 = text.index(sub1)
    idx2 = text.index(sub2)

    res = ""
    for idx in range(idx1 + len(sub1), idx2):
        res = res + text[idx]

    return res


def is_float_regex(self, value):
    return bool(re.match(r"^[-+]?[0-9]*\.?[0-9]+$", value))
