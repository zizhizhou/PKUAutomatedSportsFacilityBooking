# coding: utf-8



class ModuleConf(object):
    WEEK_MENU={
        "1":'星期一',
        "2":'星期二',
        "3":'星期三',
        "4":'星期四',
        "5":'星期五',
        "6":'星期六',
        "7":'星期日'      
    }
    
    #支付方式:
    PAY_MENU={
        "0":'不自动支付',
        "1":'校园卡自动支付',
        "2":'微信支付',
        "3":'支付宝支付'
    }
    
    GYM_MENU={
        "0":{"name":"邱德拔体育馆羽毛球场",
             "url":'https://epe.pku.edu.cn/venue/venue-reservation/60',
             "short":"邱德拔"},
        "1":{"name":"五四体育中心羽毛球馆",
             "url":'https://epe.pku.edu.cn/venue/venue-reservation/86',
             "short":"五四"}
    }  

    FIELD_MENU={
            "1":{
                "id": 1,
                "text": "1号场地",
            },
            "2":{
                "id": 2,
                "text": "2号场地",
            },
            "3":{
                "id": 3,
                "text": "3号场地",
            },
            "4":{
                "id": 4,
                "text": "4号场地",
            },
            "5":{
                "id": 5,
                "text": "5号场地",
            },
            "6":{
                "id": 6,
                "text": "6号场地",
            },
            "7":{
                "id": 7,
                "text": "7号场地",
            },
            "8":{
                "id": 8,
                "text": "8号场地",
            },
            "9":{
                "id": 9,
                "text": "9号场地",
            },
            "10":{
                "id": 10,
                "text": "10号场地",
            },
            "11":{
                "id": 11,
                "text": "11号场地",
            },
            "12":{
                "id": 12,
                "text": "12号场地",
            }        
    }

    TIME_MENU={
        "06:50":{
            "id": 0,
            "text": "06:50-07:50",
        },
        "08:00":{
            "id": 1,
            "text": "08:00-09:00",
        },
        "09:00":{
            "id": 2,
            "text": "09:00-10:00",
        },
        "10:00":{
            "id": 3,
            "text": "10:00-11:00",
        },
        "11:00":{
            "id": 4,
            "text": "11:00-12:00",
        },
        "12:00":{
            "id": 5,
            "text": "12:00-13:00",
        },
        "13:00":{
            "id": 6,
            "text": "13:00-14:00",
        },
        "14:00":{
            "id": 7,
            "text": "14:00-15:00",
        },
        "15:00":{
            "id": 8,
            "text": "15:00-16:00",
        },
        "16:00":{
            "id": 9,
            "text": "16:00-17:00",
        },
        "17:00":{
            "id": 10,
            "text": "17:00-18:00",
        },
        "18:00":{
            "id": 11,
            "text": "18:00-19:00",
        },
        "19:00":{
            "id": 12,
            "text": "19:00-20:00",
        },
        "20:00":{
            "id": 13,
            "text": "20:00-21:00",
        },
        "21:00":{
            "id": 14,
            "text": "21:00-22:00",
        },
        "22:00":{
            "id": 15,
            "text": "22:00-23:00",
        }
        }
    @staticmethod
    def get_enum_name(enum, value):
        """
        根据Enum的value查询name
        :param enum: 枚举
        :param value: 枚举值
        :return: 枚举名或None
        """
        for e in enum:
            if e.value == value:
                return e.name
        return None

    @staticmethod
    def get_enum_item(enum, value):
        """
        根据Enum的value查询name
        :param enum: 枚举
        :param value: 枚举值
        :return: 枚举项
        """
        for e in enum:
            if e.value == value:
                return e
        return None

    @staticmethod
    def get_dictenum_key(dictenum, value):
        """
        根据Enum dict的value查询key
        :param dictenum: 枚举字典
        :param value: 枚举类（字典值）的值
        :return: 字典键或None
        """
        for k, v in dictenum.items():
            if v.value == value:
                return k
        return None
