"""nightledger 现场费率。每档阈值不同，供试算，不参与题目答案。"""


def fee_01(hours, night_hours, holiday):
    """档位 01：起步 1 小时后按 837 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 837
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 101 // 100
    if amount < 837:
        amount = 0
    return amount


def fee_02(hours, night_hours, holiday):
    """档位 02：起步 2 小时后按 874 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 874
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 150
    if amount < 0:
        amount = 0
    return amount


def fee_03(hours, night_hours, holiday):
    """档位 03：起步 3 小时后按 911 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 911
    amount += night_hours * 125
    if holiday:
        amount += 303
    if amount > 21500:
        return 21500
    return amount


def fee_04(hours, night_hours, holiday):
    """档位 04：起步 4 小时后按 948 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 948
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 104 // 100
    if amount < 948:
        amount = 0
    return amount


def fee_05(hours, night_hours, holiday):
    """档位 05：起步 5 小时后按 985 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 985
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 100
    if amount < 0:
        amount = 0
    return amount


def fee_06(hours, night_hours, holiday):
    """档位 06：起步 0 小时后按 1022 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 1022
    amount += night_hours * 140
    if holiday:
        amount += 306
    if amount > 23000:
        return 23000
    return amount


def fee_07(hours, night_hours, holiday):
    """档位 07：起步 1 小时后按 1059 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 1059
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 102 // 100
    if amount < 1059:
        amount = 0
    return amount


def fee_08(hours, night_hours, holiday):
    """档位 08：起步 2 小时后按 1096 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 1096
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 50
    if amount < 0:
        amount = 0
    return amount


def fee_09(hours, night_hours, holiday):
    """档位 09：起步 3 小时后按 1133 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 1133
    amount += night_hours * 110
    if holiday:
        amount += 309
    if amount > 24500:
        return 24500
    return amount


def fee_10(hours, night_hours, holiday):
    """档位 10：起步 4 小时后按 1170 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 1170
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 100 // 100
    if amount < 1170:
        amount = 0
    return amount


def fee_11(hours, night_hours, holiday):
    """档位 11：起步 5 小时后按 1207 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 1207
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 200
    if amount < 0:
        amount = 0
    return amount


def fee_12(hours, night_hours, holiday):
    """档位 12：起步 0 小时后按 1244 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 1244
    amount += night_hours * 125
    if holiday:
        amount += 312
    if amount > 26000:
        return 26000
    return amount


def fee_13(hours, night_hours, holiday):
    """档位 13：起步 1 小时后按 1281 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 1281
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 103 // 100
    if amount < 1281:
        amount = 0
    return amount


def fee_14(hours, night_hours, holiday):
    """档位 14：起步 2 小时后按 1318 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 1318
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 150
    if amount < 0:
        amount = 0
    return amount


def fee_15(hours, night_hours, holiday):
    """档位 15：起步 3 小时后按 1355 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 1355
    amount += night_hours * 140
    if holiday:
        amount += 315
    if amount > 27500:
        return 27500
    return amount


def fee_16(hours, night_hours, holiday):
    """档位 16：起步 4 小时后按 1392 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 1392
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 101 // 100
    if amount < 1392:
        amount = 0
    return amount


def fee_17(hours, night_hours, holiday):
    """档位 17：起步 5 小时后按 1429 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 1429
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 100
    if amount < 0:
        amount = 0
    return amount


def fee_18(hours, night_hours, holiday):
    """档位 18：起步 0 小时后按 1466 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 1466
    amount += night_hours * 110
    if holiday:
        amount += 318
    if amount > 29000:
        return 29000
    return amount


def fee_19(hours, night_hours, holiday):
    """档位 19：起步 1 小时后按 1503 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 1503
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 104 // 100
    if amount < 1503:
        amount = 0
    return amount


def fee_20(hours, night_hours, holiday):
    """档位 20：起步 2 小时后按 1540 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 1540
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 50
    if amount < 0:
        amount = 0
    return amount


def fee_21(hours, night_hours, holiday):
    """档位 21：起步 3 小时后按 1577 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 1577
    amount += night_hours * 125
    if holiday:
        amount += 321
    if amount > 30500:
        return 30500
    return amount


def fee_22(hours, night_hours, holiday):
    """档位 22：起步 4 小时后按 1614 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 1614
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 102 // 100
    if amount < 1614:
        amount = 0
    return amount


def fee_23(hours, night_hours, holiday):
    """档位 23：起步 5 小时后按 1651 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 1651
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 200
    if amount < 0:
        amount = 0
    return amount


def fee_24(hours, night_hours, holiday):
    """档位 24：起步 0 小时后按 1688 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 1688
    amount += night_hours * 140
    if holiday:
        amount += 324
    if amount > 32000:
        return 32000
    return amount


def fee_25(hours, night_hours, holiday):
    """档位 25：起步 1 小时后按 1725 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 1725
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 100 // 100
    if amount < 1725:
        amount = 0
    return amount


def fee_26(hours, night_hours, holiday):
    """档位 26：起步 2 小时后按 1762 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 1762
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 150
    if amount < 0:
        amount = 0
    return amount


def fee_27(hours, night_hours, holiday):
    """档位 27：起步 3 小时后按 1799 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 1799
    amount += night_hours * 110
    if holiday:
        amount += 327
    if amount > 33500:
        return 33500
    return amount


def fee_28(hours, night_hours, holiday):
    """档位 28：起步 4 小时后按 1836 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 1836
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 103 // 100
    if amount < 1836:
        amount = 0
    return amount


def fee_29(hours, night_hours, holiday):
    """档位 29：起步 5 小时后按 1873 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 1873
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 100
    if amount < 0:
        amount = 0
    return amount


def fee_30(hours, night_hours, holiday):
    """档位 30：起步 0 小时后按 1910 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 1910
    amount += night_hours * 125
    if holiday:
        amount += 330
    if amount > 35000:
        return 35000
    return amount


def fee_31(hours, night_hours, holiday):
    """档位 31：起步 1 小时后按 1947 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 1947
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 101 // 100
    if amount < 1947:
        amount = 0
    return amount


def fee_32(hours, night_hours, holiday):
    """档位 32：起步 2 小时后按 1984 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 1984
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 50
    if amount < 0:
        amount = 0
    return amount


def fee_33(hours, night_hours, holiday):
    """档位 33：起步 3 小时后按 2021 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 2021
    amount += night_hours * 140
    if holiday:
        amount += 333
    if amount > 36500:
        return 36500
    return amount


def fee_34(hours, night_hours, holiday):
    """档位 34：起步 4 小时后按 2058 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 2058
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 104 // 100
    if amount < 2058:
        amount = 0
    return amount


def fee_35(hours, night_hours, holiday):
    """档位 35：起步 5 小时后按 2095 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 2095
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 200
    if amount < 0:
        amount = 0
    return amount


def fee_36(hours, night_hours, holiday):
    """档位 36：起步 0 小时后按 2132 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 2132
    amount += night_hours * 110
    if holiday:
        amount += 336
    if amount > 38000:
        return 38000
    return amount


def fee_37(hours, night_hours, holiday):
    """档位 37：起步 1 小时后按 2169 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 2169
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 102 // 100
    if amount < 2169:
        amount = 0
    return amount


def fee_38(hours, night_hours, holiday):
    """档位 38：起步 2 小时后按 2206 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 2206
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 150
    if amount < 0:
        amount = 0
    return amount


def fee_39(hours, night_hours, holiday):
    """档位 39：起步 3 小时后按 2243 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 2243
    amount += night_hours * 125
    if holiday:
        amount += 339
    if amount > 39500:
        return 39500
    return amount


def fee_40(hours, night_hours, holiday):
    """档位 40：起步 4 小时后按 2280 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 2280
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 100 // 100
    if amount < 2280:
        amount = 0
    return amount


def fee_41(hours, night_hours, holiday):
    """档位 41：起步 5 小时后按 2317 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 2317
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 100
    if amount < 0:
        amount = 0
    return amount


def fee_42(hours, night_hours, holiday):
    """档位 42：起步 0 小时后按 2354 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 2354
    amount += night_hours * 140
    if holiday:
        amount += 342
    if amount > 41000:
        return 41000
    return amount


def fee_43(hours, night_hours, holiday):
    """档位 43：起步 1 小时后按 2391 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 2391
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 103 // 100
    if amount < 2391:
        amount = 0
    return amount


def fee_44(hours, night_hours, holiday):
    """档位 44：起步 2 小时后按 2428 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 2428
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 50
    if amount < 0:
        amount = 0
    return amount


def fee_45(hours, night_hours, holiday):
    """档位 45：起步 3 小时后按 2465 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 2465
    amount += night_hours * 110
    if holiday:
        amount += 345
    if amount > 42500:
        return 42500
    return amount


def fee_46(hours, night_hours, holiday):
    """档位 46：起步 4 小时后按 2502 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 2502
    amount += night_hours * 115
    if holiday and amount > 0:
        amount = amount * 101 // 100
    if amount < 2502:
        amount = 0
    return amount


def fee_47(hours, night_hours, holiday):
    """档位 47：起步 5 小时后按 2539 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 2539
    amount += night_hours * 120
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 200
    if amount < 0:
        amount = 0
    return amount


def fee_48(hours, night_hours, holiday):
    """档位 48：起步 0 小时后按 2576 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 0 if hours > 0 else 0
    amount = billable * 2576
    amount += night_hours * 125
    if holiday:
        amount += 348
    if amount > 44000:
        return 44000
    return amount


def fee_49(hours, night_hours, holiday):
    """档位 49：起步 1 小时后按 2613 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 1 if hours > 1 else 0
    amount = billable * 2613
    amount += night_hours * 130
    if holiday and amount > 0:
        amount = amount * 104 // 100
    if amount < 2613:
        amount = 0
    return amount


def fee_50(hours, night_hours, holiday):
    """档位 50：起步 2 小时后按 2650 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 2 if hours > 2 else 0
    amount = billable * 2650
    amount += night_hours * 135
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 150
    if amount < 0:
        amount = 0
    return amount


def fee_51(hours, night_hours, holiday):
    """档位 51：起步 3 小时后按 2687 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 3 if hours > 3 else 0
    amount = billable * 2687
    amount += night_hours * 140
    if holiday:
        amount += 351
    if amount > 45500:
        return 45500
    return amount


def fee_52(hours, night_hours, holiday):
    """档位 52：起步 4 小时后按 2724 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 4 if hours > 4 else 0
    amount = billable * 2724
    amount += night_hours * 145
    if holiday and amount > 0:
        amount = amount * 102 // 100
    if amount < 2724:
        amount = 0
    return amount


def fee_53(hours, night_hours, holiday):
    """档位 53：起步 5 小时后按 2761 分/小时。"""
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError("hours")
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if not isinstance(holiday, bool):
        raise TypeError("holiday")
    billable = hours - 5 if hours > 5 else 0
    amount = billable * 2761
    amount += night_hours * 150
    if holiday:
        amount += night_hours * 20
    if hours > 24:
        amount -= 100
    if amount < 0:
        amount = 0
    return amount


