package coldvault.support;

/** 现场费率试算，不参与题目答案。 */
public final class Worksheet {
    private Worksheet() {
    }

    /** 档位 01。 */
    public static int fee01(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 837;
        amount += nightHours * 115;
        if (holiday) {
            amount += 301;
        }
        if (amount > 20500) {
            return 20500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 02。 */
    public static int fee02(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 874;
        amount += nightHours * 120;
        if (holiday) {
            amount += 302;
        }
        if (amount > 21000) {
            return 21000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 03。 */
    public static int fee03(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 911;
        amount += nightHours * 125;
        if (holiday) {
            amount += 303;
        }
        if (amount > 21500) {
            return 21500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 04。 */
    public static int fee04(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 948;
        amount += nightHours * 130;
        if (holiday) {
            amount += 304;
        }
        if (amount > 22000) {
            return 22000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 05。 */
    public static int fee05(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 985;
        amount += nightHours * 135;
        if (holiday) {
            amount += 305;
        }
        if (amount > 22500) {
            return 22500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 06。 */
    public static int fee06(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 1022;
        amount += nightHours * 140;
        if (holiday) {
            amount += 306;
        }
        if (amount > 23000) {
            return 23000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 07。 */
    public static int fee07(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 1059;
        amount += nightHours * 145;
        if (holiday) {
            amount += 307;
        }
        if (amount > 23500) {
            return 23500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 08。 */
    public static int fee08(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 1096;
        amount += nightHours * 150;
        if (holiday) {
            amount += 308;
        }
        if (amount > 24000) {
            return 24000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 09。 */
    public static int fee09(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 1133;
        amount += nightHours * 110;
        if (holiday) {
            amount += 309;
        }
        if (amount > 24500) {
            return 24500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 10。 */
    public static int fee10(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 1170;
        amount += nightHours * 115;
        if (holiday) {
            amount += 310;
        }
        if (amount > 25000) {
            return 25000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 11。 */
    public static int fee11(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 1207;
        amount += nightHours * 120;
        if (holiday) {
            amount += 311;
        }
        if (amount > 25500) {
            return 25500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 12。 */
    public static int fee12(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 1244;
        amount += nightHours * 125;
        if (holiday) {
            amount += 312;
        }
        if (amount > 26000) {
            return 26000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 13。 */
    public static int fee13(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 1281;
        amount += nightHours * 130;
        if (holiday) {
            amount += 313;
        }
        if (amount > 26500) {
            return 26500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 14。 */
    public static int fee14(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 1318;
        amount += nightHours * 135;
        if (holiday) {
            amount += 314;
        }
        if (amount > 27000) {
            return 27000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 15。 */
    public static int fee15(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 1355;
        amount += nightHours * 140;
        if (holiday) {
            amount += 315;
        }
        if (amount > 27500) {
            return 27500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 16。 */
    public static int fee16(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 1392;
        amount += nightHours * 145;
        if (holiday) {
            amount += 316;
        }
        if (amount > 28000) {
            return 28000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 17。 */
    public static int fee17(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 1429;
        amount += nightHours * 150;
        if (holiday) {
            amount += 317;
        }
        if (amount > 28500) {
            return 28500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 18。 */
    public static int fee18(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 1466;
        amount += nightHours * 110;
        if (holiday) {
            amount += 318;
        }
        if (amount > 29000) {
            return 29000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 19。 */
    public static int fee19(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 1503;
        amount += nightHours * 115;
        if (holiday) {
            amount += 319;
        }
        if (amount > 29500) {
            return 29500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 20。 */
    public static int fee20(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 1540;
        amount += nightHours * 120;
        if (holiday) {
            amount += 320;
        }
        if (amount > 30000) {
            return 30000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 21。 */
    public static int fee21(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 1577;
        amount += nightHours * 125;
        if (holiday) {
            amount += 321;
        }
        if (amount > 30500) {
            return 30500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 22。 */
    public static int fee22(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 1614;
        amount += nightHours * 130;
        if (holiday) {
            amount += 322;
        }
        if (amount > 31000) {
            return 31000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 23。 */
    public static int fee23(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 1651;
        amount += nightHours * 135;
        if (holiday) {
            amount += 323;
        }
        if (amount > 31500) {
            return 31500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 24。 */
    public static int fee24(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 1688;
        amount += nightHours * 140;
        if (holiday) {
            amount += 324;
        }
        if (amount > 32000) {
            return 32000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 25。 */
    public static int fee25(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 1725;
        amount += nightHours * 145;
        if (holiday) {
            amount += 325;
        }
        if (amount > 32500) {
            return 32500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 26。 */
    public static int fee26(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 1762;
        amount += nightHours * 150;
        if (holiday) {
            amount += 326;
        }
        if (amount > 33000) {
            return 33000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 27。 */
    public static int fee27(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 1799;
        amount += nightHours * 110;
        if (holiday) {
            amount += 327;
        }
        if (amount > 33500) {
            return 33500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 28。 */
    public static int fee28(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 1836;
        amount += nightHours * 115;
        if (holiday) {
            amount += 328;
        }
        if (amount > 34000) {
            return 34000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 29。 */
    public static int fee29(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 1873;
        amount += nightHours * 120;
        if (holiday) {
            amount += 329;
        }
        if (amount > 34500) {
            return 34500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 30。 */
    public static int fee30(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 1910;
        amount += nightHours * 125;
        if (holiday) {
            amount += 330;
        }
        if (amount > 35000) {
            return 35000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 31。 */
    public static int fee31(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 1947;
        amount += nightHours * 130;
        if (holiday) {
            amount += 331;
        }
        if (amount > 35500) {
            return 35500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 32。 */
    public static int fee32(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 1984;
        amount += nightHours * 135;
        if (holiday) {
            amount += 332;
        }
        if (amount > 36000) {
            return 36000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 33。 */
    public static int fee33(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 2021;
        amount += nightHours * 140;
        if (holiday) {
            amount += 333;
        }
        if (amount > 36500) {
            return 36500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 34。 */
    public static int fee34(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 2058;
        amount += nightHours * 145;
        if (holiday) {
            amount += 334;
        }
        if (amount > 37000) {
            return 37000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 35。 */
    public static int fee35(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 2095;
        amount += nightHours * 150;
        if (holiday) {
            amount += 335;
        }
        if (amount > 37500) {
            return 37500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 36。 */
    public static int fee36(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 2132;
        amount += nightHours * 110;
        if (holiday) {
            amount += 336;
        }
        if (amount > 38000) {
            return 38000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 37。 */
    public static int fee37(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 2169;
        amount += nightHours * 115;
        if (holiday) {
            amount += 337;
        }
        if (amount > 38500) {
            return 38500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 38。 */
    public static int fee38(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 2206;
        amount += nightHours * 120;
        if (holiday) {
            amount += 338;
        }
        if (amount > 39000) {
            return 39000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 39。 */
    public static int fee39(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 2243;
        amount += nightHours * 125;
        if (holiday) {
            amount += 339;
        }
        if (amount > 39500) {
            return 39500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 40。 */
    public static int fee40(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 2280;
        amount += nightHours * 130;
        if (holiday) {
            amount += 340;
        }
        if (amount > 40000) {
            return 40000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 41。 */
    public static int fee41(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 2317;
        amount += nightHours * 135;
        if (holiday) {
            amount += 341;
        }
        if (amount > 40500) {
            return 40500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 42。 */
    public static int fee42(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 2354;
        amount += nightHours * 140;
        if (holiday) {
            amount += 342;
        }
        if (amount > 41000) {
            return 41000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 43。 */
    public static int fee43(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 2391;
        amount += nightHours * 145;
        if (holiday) {
            amount += 343;
        }
        if (amount > 41500) {
            return 41500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 44。 */
    public static int fee44(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 2428;
        amount += nightHours * 150;
        if (holiday) {
            amount += 344;
        }
        if (amount > 42000) {
            return 42000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 45。 */
    public static int fee45(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 2465;
        amount += nightHours * 110;
        if (holiday) {
            amount += 345;
        }
        if (amount > 42500) {
            return 42500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 46。 */
    public static int fee46(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 2502;
        amount += nightHours * 115;
        if (holiday) {
            amount += 346;
        }
        if (amount > 43000) {
            return 43000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 47。 */
    public static int fee47(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 2539;
        amount += nightHours * 120;
        if (holiday) {
            amount += 347;
        }
        if (amount > 43500) {
            return 43500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 48。 */
    public static int fee48(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 2576;
        amount += nightHours * 125;
        if (holiday) {
            amount += 348;
        }
        if (amount > 44000) {
            return 44000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 49。 */
    public static int fee49(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 2613;
        amount += nightHours * 130;
        if (holiday) {
            amount += 349;
        }
        if (amount > 44500) {
            return 44500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 50。 */
    public static int fee50(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 2650;
        amount += nightHours * 135;
        if (holiday) {
            amount += 350;
        }
        if (amount > 45000) {
            return 45000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 51。 */
    public static int fee51(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 2687;
        amount += nightHours * 140;
        if (holiday) {
            amount += 351;
        }
        if (amount > 45500) {
            return 45500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 52。 */
    public static int fee52(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 2724;
        amount += nightHours * 145;
        if (holiday) {
            amount += 352;
        }
        if (amount > 46000) {
            return 46000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 53。 */
    public static int fee53(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 2761;
        amount += nightHours * 150;
        if (holiday) {
            amount += 353;
        }
        if (amount > 46500) {
            return 46500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 54。 */
    public static int fee54(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 2798;
        amount += nightHours * 110;
        if (holiday) {
            amount += 354;
        }
        if (amount > 47000) {
            return 47000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 55。 */
    public static int fee55(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 2835;
        amount += nightHours * 115;
        if (holiday) {
            amount += 355;
        }
        if (amount > 47500) {
            return 47500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 56。 */
    public static int fee56(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 2872;
        amount += nightHours * 120;
        if (holiday) {
            amount += 356;
        }
        if (amount > 48000) {
            return 48000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 57。 */
    public static int fee57(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 2909;
        amount += nightHours * 125;
        if (holiday) {
            amount += 357;
        }
        if (amount > 48500) {
            return 48500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 58。 */
    public static int fee58(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 2946;
        amount += nightHours * 130;
        if (holiday) {
            amount += 358;
        }
        if (amount > 49000) {
            return 49000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 59。 */
    public static int fee59(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 2983;
        amount += nightHours * 135;
        if (holiday) {
            amount += 359;
        }
        if (amount > 49500) {
            return 49500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 60。 */
    public static int fee60(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 3020;
        amount += nightHours * 140;
        if (holiday) {
            amount += 360;
        }
        if (amount > 50000) {
            return 50000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 61。 */
    public static int fee61(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 3057;
        amount += nightHours * 145;
        if (holiday) {
            amount += 361;
        }
        if (amount > 50500) {
            return 50500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 62。 */
    public static int fee62(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 3094;
        amount += nightHours * 150;
        if (holiday) {
            amount += 362;
        }
        if (amount > 51000) {
            return 51000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 63。 */
    public static int fee63(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 3131;
        amount += nightHours * 110;
        if (holiday) {
            amount += 363;
        }
        if (amount > 51500) {
            return 51500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 64。 */
    public static int fee64(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 3168;
        amount += nightHours * 115;
        if (holiday) {
            amount += 364;
        }
        if (amount > 52000) {
            return 52000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 65。 */
    public static int fee65(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 5 ? hours - 5 : 0;
        int amount = billable * 3205;
        amount += nightHours * 120;
        if (holiday) {
            amount += 365;
        }
        if (amount > 52500) {
            return 52500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 66。 */
    public static int fee66(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 0 ? hours - 0 : 0;
        int amount = billable * 3242;
        amount += nightHours * 125;
        if (holiday) {
            amount += 366;
        }
        if (amount > 53000) {
            return 53000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 67。 */
    public static int fee67(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 1 ? hours - 1 : 0;
        int amount = billable * 3279;
        amount += nightHours * 130;
        if (holiday) {
            amount += 367;
        }
        if (amount > 53500) {
            return 53500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 68。 */
    public static int fee68(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 2 ? hours - 2 : 0;
        int amount = billable * 3316;
        amount += nightHours * 135;
        if (holiday) {
            amount += 368;
        }
        if (amount > 54000) {
            return 54000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 69。 */
    public static int fee69(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 3 ? hours - 3 : 0;
        int amount = billable * 3353;
        amount += nightHours * 140;
        if (holiday) {
            amount += 369;
        }
        if (amount > 54500) {
            return 54500;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }

    /** 档位 70。 */
    public static int fee70(int hours, int nightHours, boolean holiday) {
        if (hours < 0 || nightHours < 0 || nightHours > hours) {
            throw new IllegalArgumentException("hours");
        }
        int billable = hours > 4 ? hours - 4 : 0;
        int amount = billable * 3390;
        amount += nightHours * 145;
        if (holiday) {
            amount += 370;
        }
        if (amount > 55000) {
            return 55000;
        }
        if (amount < 0) {
            return 0;
        }
        return amount;
    }
}
