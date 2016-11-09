# coding: utf-8
import re
import sys
import traceback
import collections
import time
import datetime
import hashlib
import tldextract
import langid

english_pattern = re.compile(u'[A-Za-z]+')
chinese_pattern = re.compile(u'[\u4e00-\u9fa5]+')
all_chinese_pattern = re.compile(u'^[\u4e00-\u9fa5]+$')
all_ascii_pattern = re.compile(u'^[\u0000-\u007f]+$')
japanese_pattern1 = re.compile(u'[\u3040-\u309f]+')
japanese_pattern2 = re.compile(u'[\u30a0-\u30ff]+')
japanese_pattern3 = re.compile(u'[\u4e00-\u9fbf]+')
SPLIT_PARTTERN = re.compile(u'-|·|、|与| |及|&|\+|–|\:|/|!|！|\)|\(|（|）')
EPOCH_DATETIME = datetime.datetime(1970, 1, 1, 8, 0)


def datetime2utc(dt):
    return int(time.mktime(dt.timetuple()))


def utc2datetime(t):
    return datetime.datetime.fromtimestamp(t)


def validate_datetime(dt):
    return bool(isinstance(dt, datetime.datetime) and dt >= EPOCH_DATETIME)


def fragment(l, size):
    ll = []
    n = int(len(l)/size) + bool(len(l) % size)
    for i in range(n):
        ll.append(l[i*size: (i+1)*size])
    return ll


def to_hash(*args):
    m = hashlib.md5()
    for arg in args:
        if isinstance(arg, unicode):
            arg = arg.encode('utf8')
        m.update(str(arg))
    return m.hexdigest()


def contains_english(s):
    return bool(english_pattern.search(s))


def contains_chinese(s):
    return bool(chinese_pattern.search(s))


def contains_japanese(s):
    for pattern in [japanese_pattern1, japanese_pattern2, japanese_pattern3]:
        ret = pattern.search(s)
        if ret:
            return True
    return False


def get_domain(url, is_strict=False):
    """
    get_domain('http://hi.baidu.com')
    'baidu.com'
    """
    r = tldextract.extract(url.lower())
    if is_strict:
        if r.subdomain not in ['www', '']:
            return
    return r.registered_domain.strip()


def is_chinese(*args):
    args = filter(None, args)
    text = u' '.join(args)
    if text:
        return langid.classify(text)[0] == 'zh'


def recognize_money(text):
    if not text:
        return -1  # 不明确
    unknown_string = [u'万人民币', u'万美元', u'None万美元', u'美元', u'人民币', u'asd万美元', u'新三板万人民币']
    if text in unknown_string:
        return -1
    unknown_substring = [u'未透露', u'未披露', u'不详', u'不方便透露']
    for each in unknown_substring:
        if each in text:
            return -1

    if '-' in text:
        text = sorted(text.split('-'), key=lambda t: len(t), reverse=True)[0]

    currency_value_list = [
        (u'人民币', 1),
        (u'美元', 6.45),
        (u'欧元', 7.35),
        (u'港元', 0.8354),
        (u'日元', 0.0582),
        (u'元', 1)
    ]
    text_digit_mapping_dict = {
        u'数': 3,
        u'零': 0, u'０': 0,
        u'一': 1, u'壹': 1, u'１': 1,
        u'二': 2, u'贰': 2, u'２': 2,
        u'三': 3, u'叁': 3, u'３': 3,
        u'四': 4, u'肆': 4, u'４': 4,
        u'五': 5, u'伍': 5, u'５': 5,
        u'六': 6, u'陆': 6, u'６': 6,
        u'七': 7, u'柒': 7, u'７': 7,
        u'八': 8, u'捌': 8, u'８': 8,
        u'九': 9, u'玖': 9, u'９': 9,
    }
    text_magnitude_mapping_dict = {
        u'十': 10, u'拾': 10,
        u'百': 10**2, u'佰': 10**2,
        u'千': 10**3, u'仟': 10**3,
        u'万': 10**4, u'萬': 10**4,
        u'亿': 10**8,
    }

    pos = -1
    currency_value = 0
    for currency, value in currency_value_list:
        pos = text.rfind(currency)
        if pos != -1:
            currency_value = value
            break

    if not currency_value:
        return -1

    text = text[:pos]
    number = 0.0
    fractional_count = 0
    behind_point = False
    for i in range(0, len(text)):
        if text[i].isdigit():
            number = number * 10 + int(text[i])
            if behind_point:
                fractional_count += 1
        elif text[i] in text_digit_mapping_dict:
            number = number * 10 + text_digit_mapping_dict[text[i]]
            if behind_point:
                fractional_count += 1
        elif text[i] in text_magnitude_mapping_dict:
            if i == 0 and number == 0:
                number = 1
            number *= text_magnitude_mapping_dict[text[i]]
        elif text[i] == '.':
            behind_point = True

    number /= (10 ** fractional_count)
    number *= currency_value

    if number < 100:
        number = -1

    return number


def check_datetime_valid(dt):
    unix_epoch = utc2datetime(0)
    now = datetime.datetime.now()
    if dt < unix_epoch:
        return False
    if dt > now:
        return False

    return True


def multiple_replace(string, replace_dict):
    rx = re.compile('|'.join(map(re.escape, replace_dict)))

    def one_xlat(match):
        return replace_dict[match.group(0)]
    return rx.sub(one_xlat, string)
