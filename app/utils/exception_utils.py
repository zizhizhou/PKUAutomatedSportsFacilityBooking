# -*- coding: utf-8 -*-
import traceback,sys

class OtherError(RuntimeError):#其他异常
    def __init__(self, arg=None):
        self.args = arg
class ConfigError(OtherError):#设置异常
    pass
class LoginError(OtherError):#登录异常
    pass
class AppointError(OtherError):#预约异常
    pass
class SoldError(OtherError):#全部售出异常
    pass
class VerifyError(OtherError):#验证码异常
    pass
class PayError(OtherError):#支付异常
    pass
class WeChatError(OtherError):#微信通知异常
    pass
class NetWorkError(OtherError):#网络异常
    pass
class Successful(OtherError):#成功异常
    pass


class ExceptionUtils:
    @classmethod
    def exception_traceback(cls, e):
        print(f"\nException: {str(e)}\nCallstack:\n{traceback.format_exc()}\n")
    @classmethod
    def print_exception(cls,e:Exception):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        print(f"Exception occurred at line {line_number}: {e}")

        # 打印完整的异常堆栈信息
        traceback.print_exc()
