# -*- coding: utf-8 -*-
import json
import os


def check_information(_dict, n, num, s):
    """
    检查并修复
    :param _dict:
    :param n: 总圣遗物数
    :param num: 每个圣遗物组件个数
    :param s: 每个圣遗物组件名称组成的字符串
    :return: dict(), {str:[,,]}:
    """
    initialized = {}  # _dict被初始化的信息
    # {key1:{key2:value2, ...}, ...}
    # 检查key1
    _list = [str(x) for x in range(n)]
    __dict = _dict.copy()
    for key_ in __dict:
        if key_ in _list:
            _list.remove(key_)
        else:
            _dict.pop(key_)
            continue
        # 检查key2
        templist = []
        list_ = s.split(',')
        d = _dict[key_]
        dd = d.copy()
        for _key in dd:
            if _key in list_:
                list_.remove(_key)
            else:
                d.pop(_key)
                continue
            # 检查value2
            if _key == 's1':
                if isinstance(d[_key], int) and 1 < d[_key] < 5:
                    pass
                else:
                    d[_key] = 2
                    templist.append(_key)
            elif 'cb' in _key:
                if isinstance(d[_key], bool):
                    pass
                else:
                    d[_key] = False
                    templist.append(_key)
            elif 's' in _key:
                if isinstance(d[_key], int) and 0 <= d[_key] < 4:
                    pass
                else:
                    d[_key] = 0
                    templist.append(_key)
        # 添加不存在的key2
        for l in list_:
            if l == 's1':
                d[l] = 2
            elif 'cb' in l:
                d[l] = False
            elif 's' in l:
                d[l] = 0
            templist.append(l)
        if len(templist) == 0:
            continue
        initialized[key_] = templist
    # 添加不存在的key1
    for l in _list:
        _dict[l] = create_precise_(s)
        initialized[l] = s.split(',')

    return _dict, initialized


def _create_precise(n, s):
    """
    创建总
    :param n:圣遗物数
    :param s:每个圣遗物组件名称组成的字符串
    :return: dict()
    """
    _dict = {}
    for i in range(n):
        _dict[str(i)] = create_precise_(s)
    return _dict


def create_precise_(s):
    """
    创建分
    :param s: 每个圣遗物组件名称组成的字符串
    :return: dict()
    """
    dict_ = {}
    for j in s.split(','):
        if j == 's1':
            dict_[j] = 2
        elif 's' in j:
            dict_[j] = 0
        else:
            dict_[j] = False
    return dict_


def check_and_specialize(_name, _level, _place, _main_attr, _attrs):
    """
    检验并将元素变为指定值
    :param _name:
    :param _level:
    :param _place:
    :param _main_attr:
    :param _attrs:
    :return:
    """
    name = {'角斗士的终幕礼': '0', '流浪大地的乐团': '1', '昔日宗室之仪': '2', '染血的骑士道': '3',
            '被怜爱的少女': '4', '翠绿之影': '5', '悠古的磐岩': '6', '逆飞的流星': '7', '平息雷鸣的尊者': '8',
            '如雷的盛怒': '9', '渡过烈火的贤人': '10', '炽烈的炎之魔女': '11', '冰风迷途的勇士': '12',
            '沉沦之心': '13', '千岩牢固': '14', '苍白之火': '15', '追忆之注连': '16', '绝缘之旗印': '17',
            '华馆梦醒形骸记': '18', '海染砗磲': '19', '辰砂往生录': '20', '来歆余响': '21', '深林的记忆': '22',
            '饰金之梦': '23', '沙上楼阁史话': '24', '乐园遗落之花': '25', '水仙之梦': '26', '花海甘露之光': '27'}
    place = {'生之花': '2', '死之羽': '2', '时之沙': '3', '空之杯': '3', '理之冠': '3'}

    # 排除等级不为0的圣遗物
    if _level != '+0':
        return False
    tempdict = {}
    try:
        for _attr in _attrs:
            a, b = _attr.split('+')
            tempdict[a] = b
        return name[_name], place[_place], _main_attr, tempdict
    except:
        return ['识别错误,请重试！！']


def check_statify(_name, _place, _main_attr, _attrs):
    """
    检查圣遗物是否符合条件
    :param _name:
    :param _place:
    :param _main_attr:
    :param _attrs:
    :return: tips(str)
    """
    attr = {'暴击率': '1', '暴击伤害': '2', '元素精通': '3', '元素充能效率': '4', '攻击力': '5', '生命值': '5',
            '防御力': '5'}
    name = {'0': '攻击力', '1': False, '2': False, '3': False, '4': False, '5': False, '6': False, '7': False,
            '8': False, '9': False, '10': False, '11': False, '12': False, '13': False, '14': '生命值', '15': False,
            '16': '攻击力', '17': False, '18': '防御力', '19': False, '20': '攻击力', '21': '攻击力', '22': False,
            '23': False, '24': False, '25': False, '26': False, '27': '生命值'}
    temp = ['攻击力', '生命值', '防御力']
    relic1 = {'2.7%': 0, '3.1%': 1, '3.5%': 2, '3.9%': 3}
    relic2 = {'5.4%': 0, '6.2%': 1, '7.0%': 2, '7.8%': 3}
    relic3 = {'16': 0, '19': 1, '21': 2, '23': 3}
    relic4 = {'4.5%': 0, '5.2%': 1, '5.8%': 2, '6.5%': 3}
    relic5_12 = {'4.1%': 0, '4.7%': 1, '5.3%': 2, '5.8%': 3}
    relic5_3 = {'5.1%': 0, '5.8%': 1, '6.6%': 2, '7.3%': 3}

    # print(os.listdir('../'))
    # 读取条件
    with open('./info.json', 'r') as f:
        info = json.loads(f.read())
    info = info[_name]
    # print(info)

    # 是否符合(cb3)
    if info['cb3']:
        if '暴击率' in _attrs and '暴击伤害' in _attrs:
            return '建议锁定cb3'

    # 是否符合(cb1)
    if info['cb1']:
        if _main_attr in temp and _place == '3':
            if name[_name]:
                if name[_name] != _main_attr:
                    return '建议不锁定cb1'

    # 保留有效词条
    # 保留暴击，暴伤，精通，充能，%攻，%生，%防
    for k, v in _attrs.copy().items():
        if k != '元素精通' and '%' not in v:
            _attrs.pop(k)
    # [部位3的主词条算有效词条，攻生防不共存且(主词条不为攻生防)攻 > 生 > 防，(主词条为攻生防)主词条优先，
    # 防御与精通共存时，有效词条个数减1]
    validlist = list(_attrs.keys())
    flag = False
    if _place == '3':
        flag = True
    if flag and _main_attr in temp:
        for valid in validlist:
            if valid in temp:
                validlist.remove(valid)
        validlist.append(_main_attr)
    elif flag and _main_attr not in temp:
        if '攻击力' in validlist:
            if '生命值' in validlist:
                validlist.remove('生命值')
            if '防御力' in validlist:
                validlist.remove('防御力')
        elif '生命值' in validlist:
            if '防御力' in validlist:
                validlist.remove('防御力')
        validlist.append(_main_attr)
    lenn = len(validlist)
    if '防御力' in validlist and '元素精通' in validlist:
        lenn -= 1
    validdict = {}
    if flag:
        for valid in validlist[:-1]:
            validdict[valid] = _attrs[valid]
    else:
        for valid in validlist:
            validdict[valid] = _attrs[valid]
    # print(validdict, lenn)

    # 是否符合最少词条数条件(s1)
    if lenn < info['s1']:
        return '建议不锁定s1'

    # 是否符合(cb2)
    if lenn == 3 and info['cb2']:
        for _attr in validlist.copy():
            if _attr == '攻击力' or _attr == '生命值':
                validlist.remove(_attr)
            elif _attr == '元素精通':
                validlist.remove(_attr)
            elif _attr == '元素充能效率':
                validlist.remove(_attr)
        if len(validlist) == 0:
            return '建议不锁定cb2'

    # 是否符合最小副词条条件(s2[1~5], s3[1~5])
    for k, v in validdict.items():
        if k in temp:
            if k == '攻击力' or k == '生命值':
                if relic5_12[v] < info['s' + _place + attr[k]]:
                    return '建议不锁定s'
            else:
                if relic5_3[v] < info['s' + _place + attr[k]]:
                    return '建议不锁定s'
        else:
            if eval('relic' + attr[k] + '[v]') < info['s' + _place + attr[k]]:
                return '建议不锁定s'
    return '建议锁定'
