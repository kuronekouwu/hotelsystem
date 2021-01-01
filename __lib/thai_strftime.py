# Thai date and time string formatter
# Formatting directives similar to datetime.strftime()
# by @bact, to be included in PyThaiNLP 2.0
#
# จัดรูปแบบข้อความวันที่และเวลา แบบเดียวกับ datetime.strftime()
# โดยจะใช้ชื่อเดือนเป็นภาษาไทย และปีเป็นพุทธศักราช
# (ไม่รองรับปีก่อน พ.ศ. 2484 - ก่อนการเปลี่ยนวันปีใหม่ไทย)
#
# Will use Thai names and Thai Buddhist era for these directives:
# - %a abbreviated weekday name
# - %A full weekday name
# - %b abbreviated month name
# - %B full month name
# - %y year without century
# - %Y year with century
# - %c date and time representation
# - %v short date representation (undocumented directive, please avoid)
#
# Other directives will be passed to datetime.strftime()
#
# See Python document for strftime:
# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
#
# Note 1:
# The Thai Buddhist Era (BE) year is simply converted from AD by adding 543.
# This is certainly not accurate for years before 1941 AD,
# due to the change in Thai New Year's Day.
#
# Note 2:
# This meant to be an interrim solution, since Python standard's locale module
# (which relied on C's strftime()) does not support "th" or "th_TH" locale yet.
# If supported, we can just locale.setlocale(locale.LC_TIME, "th_TH") and
# then use native datetime.strftime().
#
# Gist:
# https://gist.github.com/bact/b8afe49cb1ae62913e6c1e899dcddbdb
# Colab:
# https://colab.research.google.com/drive/1V9a3bvXRx6TqE9TPvRWM4h3ZzWE70kDw

import datetime

_TH_ABBR_WEEKDAYS = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]
_TH_FULL_WEEKDAYS = [
    "วันจันทร์",
    "วันอังคาร",
    "วันพุธ",
    "วันพฤหัสบดี",
    "วันศุกร์",
    "วันเสาร์",
    "วันอาทิตย์",
]

_TH_ABBR_MONTHS = [
    "ม.ค.",
    "ก.พ.",
    "มี.ค.",
    "เม.ย.",
    "พ.ค.",
    "มิ.ย.",
    "ก.ค.",
    "ส.ค.",
    "ก.ย.",
    "ต.ค.",
    "พ.ย.",
    "ธ.ค.",
]
_TH_FULL_MONTHS = [
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
]

_HA_TH_DIGITS = str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙")


# Conversion support for thai_strftime()
def _thai_strftime(datetime, fmt_c):
    text = ""
    if fmt_c == "a":  # abbreviated weekday
        text = _TH_ABBR_WEEKDAYS[datetime.weekday()]
    elif fmt_c == "A":  # full weekday
        text = _TH_FULL_WEEKDAYS[datetime.weekday()]
    elif fmt_c == "b":  # abbreviated month
        text = _TH_ABBR_MONTHS[datetime.month - 1]
    elif fmt_c == "B":  # full month
        text = _TH_FULL_MONTHS[datetime.month - 1]
    elif fmt_c == "y":  #  # year without century
        text = str(datetime.year + 543)[2:4]
    elif fmt_c == "Y":  # year with century
        text = str(datetime.year + 543)
    elif fmt_c == "c":
        # Wed  6 Oct 01:40:00 1976
        # พ   6 ต.ค. 01:40:00 2519  <-- left-aligned weekday, right-aligned day
        text = "{:<2} {:>2} {} {} {}".format(
            _TH_ABBR_WEEKDAYS[datetime.weekday()],
            datetime.day,
            _TH_ABBR_MONTHS[datetime.month - 1],
            datetime.strftime("%H:%M:%S"),
            datetime.year + 543,
        )
    elif fmt_c == "v":  # undocumented format: ' 6-Oct-1976'
        text = "{:>2}-{}-{}".format(
            datetime.day, _TH_ABBR_MONTHS[datetime.month - 1], datetime.year + 543
        )
    else:  # matched with nothing
        text = datetime.strftime("%{}".format(fmt_c))

    return text


def thai_strftime(datetime, fmt, thaidigit=False):
    """
    Thai date and time string formatter

    Formatting directives similar to datetime.strftime()

    Note:
    The Thai Buddhist Era (BE) year is simply converted from AD by adding 543.
    This is certainly not accurate for years before 1941 AD,
    due to the change in Thai New Year's Day.

    :return: Date and time spelled out in text, with month in Thai name and year in Thai Buddhist era.
    """
    thaidate_parts = []

    i = 0
    fmt_len = len(fmt)
    while i < fmt_len:
        text = ""
        if fmt[i] == "%":
            j = i + 1
            if j < fmt_len:
                fmt_c = fmt[j]
                if fmt_c in "aAbByYcv":  # weekday/month names, years: to be localized
                    text = _thai_strftime(datetime, fmt_c)
                elif fmt_c == "-":  # no padding day or month
                    k = j + 1
                    if k < fmt_len:
                        fmt_c_nopad = fmt[k]
                        if fmt_c_nopad in "aAbByYcv":  # check if requires localization
                            text = _thai_strftime(datetime, fmt_c_nopad)
                        else:
                            text = datetime.strftime("%-{}".format(fmt_c_nopad))
                        i = i + 1  # consume char after "-"
                    else:
                        text = "-"
                elif fmt_c:
                    text = datetime.strftime("%{}".format(fmt_c))

                i = i + 1  # consume char after "%"
            else:
                text = "%"
        else:
            text = fmt[i]

        thaidate_parts.append(text)
        i = i + 1

    thaidate_text = "".join(thaidate_parts)

    if thaidigit:
        thaidate_text = thaidate_text.translate(_HA_TH_DIGITS)

    return thaidate_text