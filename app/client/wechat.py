import json
import threading
from datetime import datetime

from app.client._base import _IMessageClient
from app.utils.http_utils import RequestUtils
from app.utils.exception_utils import ExceptionUtils
from config.config import Config
import time
lock = threading.Lock()


class WeChat(_IMessageClient):
    task_id = 0
    schema = "wechat"

    _instance = None
    _access_token = None
    _expires_in = None
    _access_token_time = None
    _default_proxy = False
    _default_proxy_url = ''
    _client_config = {}
    _corpid = None
    _corpsecret = None
    _agent_id = None
    _interactive = False

    _send_msg_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s"
    _token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s"

    def __init__(self):
        return

        
        self.init_config()

    def init_config(self):
        if Config._wechat_notice:
            WeChat._corpid = Config._corpid
            WeChat._corpsecret = Config._corpserect
            WeChat._agent_id = Config._agentid
            WeChat._default_proxy = Config._proxy
            if WeChat._default_proxy:
                if isinstance(WeChat._default_proxy, bool) and WeChat.is_string_and_not_empty(WeChat._default_proxy_url):
                    WeChat._send_msg_url = f"{WeChat._default_proxy_url}/cgi-bin/message/send?access_token=%s"
                    WeChat._token_url = f"{WeChat._default_proxy_url}/cgi-bin/gettoken?corpid=%s&corpsecret=%s"
                else:
                    WeChat._send_msg_url = f"{WeChat._default_proxy}/cgi-bin/message/send?access_token=%s"
                    WeChat._token_url = f"{WeChat._default_proxy}/cgi-bin/gettoken?corpid=%s&corpsecret=%s"
            if WeChat._corpid and WeChat._corpsecret and WeChat._agent_id:
                self.__get_access_token()
    
    @staticmethod   
    def get_task_id():
        return time.time()

        

    @classmethod
    def match(cls, ctype):
        return True if ctype == cls.schema else False

    def __get_access_token(self, force=False):
        """
        获取微信Token
        :return： 微信Token
        """
        if Config._wechat_notice:
            token_flag = True
            if not WeChat._access_token:
                token_flag = False
            else:
                if (datetime.now() - WeChat._access_token_time).seconds >= WeChat._expires_in:
                    token_flag = False

            if not token_flag or force:
                if not WeChat._corpid or not WeChat._corpsecret:
                    return None
                try:
                    token_url = WeChat._token_url % (WeChat._corpid, WeChat._corpsecret)
                    res = RequestUtils().get_res(token_url)
                    if res:
                        ret_json = res.json()
                        if ret_json.get('errcode') == 0:
                            WeChat._access_token = ret_json.get('access_token')
                            WeChat._expires_in = ret_json.get('expires_in')
                            WeChat._access_token_time = datetime.now()
                except Exception as e:
                    ExceptionUtils.exception_traceback(e)
                    return None
            return WeChat._access_token

    def __send_message(self, title, text, user_id=None, url=None):
        """
        发送文本消息
        :param title: 消息标题
        :param text: 消息内容
        :param user_id: 消息发送对象的ID，为空则发给所有人
        :param url: 点击消息跳转URL
        :return: 发送状态，错误信息
        """
        if Config._wechat_notice:
            if not self.__get_access_token():
                return False, "参数未配置或配置不正确"
            message_url = WeChat._send_msg_url % self.__get_access_token()
            if text:
                conent = "%s\n%s" % (title, text.replace("\n\n", "\n"))
            else:
                conent = title
            if url:
                conent = f"{conent}\n\n<a href='{url}'>查看详情</a>"
            if not user_id:
                user_id = "@all"
            req_json = {
                "touser": user_id,
                "msgtype": "text",
                "agentid": WeChat._agent_id,
                "text": {
                    "content": conent
                },
                "safe": 0,
                "enable_id_trans": 0,
                "enable_duplicate_check": 0
            }
            return self.__post_request(message_url, req_json)

    def direct_send_message(self,content,send_url=None):
        """直接发送信息

        Args:
            content (_type_): _description_
            user_id (_type_): _description_
        """

        if Config._wechat_notice:
            if not self.__get_access_token():
                return False, "参数未配置或配置不正确"
            if send_url==None:
                message_url = WeChat._send_msg_url % self.__get_access_token()
            else:
                message_url=send_url
            return self.__post_request(message_url, content)

    def __send_image_message(self, title, text, image_url, url, user_id=None):
        """
        发送图文消息
        :param title: 消息标题
        :param text: 消息内容
        :param image_url: 图片地址
        :param url: 点击消息跳转URL
        :param user_id: 消息发送对象的ID，为空则发给所有人
        :return: 发送状态，错误信息
        """
        if Config._wechat_notice:
            if not self.__get_access_token():
                return False, "获取微信access_token失败，请检查参数配置"
            message_url = WeChat._send_msg_url % self.__get_access_token()
            if text:
                text = text.replace("\n\n", "\n")
            if not user_id:
                user_id = "@all"
            req_json = {
                "touser": user_id,
                "msgtype": "news",
                "agentid": WeChat._agent_id,
                "news": {
                    "articles": [
                        {
                            "title": title,
                            "description": text,
                            "picurl": image_url,
                            "url": url
                        }
                    ]
                }
            }
            return self.__post_request(message_url, req_json)

    def send_msg(self, title, text="", image="", url="", user_id=None):
        """
        微信消息发送入口，支持文本、图片、链接跳转、指定发送对象
        :param title: 消息标题
        :param text: 消息内容
        :param image: 图片地址
        :param url: 点击消息跳转URL
        :param user_id: 消息发送对象的ID，为空则发给所有人
        :return: 发送状态，错误信息
        """
        if Config._wechat_notice:
            if not title and not text:
                return False, "标题和内容不能同时为空"
            if image:
                ret_code, ret_msg = self.__send_image_message(title, text, image, url, user_id)
            else:
                ret_code, ret_msg = self.__send_message(title, text, user_id, url)
            return ret_code, ret_msg

    # def get_user_id_list(self):
    #     req_json = {
    #         "limit": 10000
    #     }
    #     msg_url="https://qyapi.weixin.qq.com/cgi-bin/department/simplelist?access_token=%s&id=2" %self.__get_access_token()
    #     self.__get_request(message_url=msg_url)

    def send_list_msg(self, medias: list, c="", title="", **kwargs):
        """
        发送列表类消息
        """
        if Config._wechat_notice:
            if not self.__get_access_token():
                return False, "参数未配置或配置不正确"
            if not isinstance(medias, list):
                return False, "数据错误"
            message_url = WeChat._send_msg_url % self.__get_access_token()
            if not user_id:
                user_id = "@all"
            articles = []
            index = 1
            for media in medias:
                if media.get_vote_string():
                    title = f"{index}. {media.get_title_string()}\n{media.get_type_string()}，{media.get_vote_string()}"
                else:
                    title = f"{index}. {media.get_title_string()}\n{media.get_type_string()}"
                articles.append({
                    "title": title,
                    "description": "",
                    "picurl": media.get_message_image() if index == 1 else media.get_poster_image(),
                    "url": media.get_detail_url()
                })
                index += 1
            req_json = {
                "touser": user_id,
                "msgtype": "news",
                "agentid": WeChat._agent_id,
                "news": {
                    "articles": articles
                }
            }
            return self.__post_request(message_url, req_json)

    # def __get_request(self, message_url):
    #     """
    #     向微信发送请求
    #     """
    #     headers = {'content-type': 'application/json'}
    #     try:
    #         res = RequestUtils(headers=headers).get(message_url)
    #         if res and res.status_code == 200:
    #             ret_json = res.json()
    #             if ret_json.get('errcode') == 0:
    #                 return True, ret_json.get('errmsg')
    #             else:
    #                 if ret_json.get('errcode') == 42001:
    #                     self.__get_access_token(force=True)
    #                 return False, ret_json.get('errmsg')
    #         elif res is not None:
    #             return False, f"错误码：{res.status_code}，错误原因：{res.reason}"
    #         else:
    #             return False, "未获取到返回信息"
    #     except Exception as err:
    #         ExceptionUtils.exception_traceback(err)
    #         return False, str(err)


    def set_menu(self):
        if Config._wechat_notice:
            req_json={
                "button":[
                    {    
                        "name":"我的",
                        "sub_button":[
                            {
                                "type":"click",
                                "name":"添加个人信息",
                                "key":"/Add_Personal_Info"
                            },
                            {
                                "type":"click",
                                "name":"查看&编辑个人信息",
                                "key":"/Edit_Personal_Info"
                            },
                            {
                                "type":"click",
                                "name":"注销个人信息",
                                "key":"/Delete_Personal_Info"
                            },
                            {
                                "type":"click",
                                "name":"个人信息帮助",
                                "key":"/Help_Personal_Info"
                            }
                        ]
                    },
                    {
                        "name":"预约",
                        "sub_button":[

                            {
                                "type":"click",
                                "name":"周常预约",
                                "key":"/Add_Week_Appoint/Week"
                            },
                            {
                                "type":"click",
                                "name":"指定日期预约",
                                "key":"/Edit_Date_Appoint/Date"
                            },
                            {
                                "type":"click",
                                "name":"查看&编辑预约",
                                "key":"/View_Appoint/All"
                            },
                            {
                                "type":"click",
                                "name":"预约帮助",
                                "key":"/Help_Appoint"
                            }
                        ]
                    },
                    {
                        "name":"其他",
                        "sub_button":[
                            {
                                "type":"click",
                                "name":"使用帮助",
                                "key":"/Help"
                            },
                            {
                                "type":"click",
                                "name":"隐私政策",
                                "key":"/Privacy"
                            },
                            {
                                "type":"click",
                                "name":"使用反馈",
                                "key":"/Feedback"
                            },
                        ]
                    }
                ]
                }
            send_url=f"{WeChat._default_proxy}/cgi-bin/menu/create?access_token=%s&agentid={WeChat._agent_id}" %self.__get_access_token()
            self.direct_send_message(req_json,send_url)
            pass


    def __post_request(self, message_url, req_json):
        if Config._wechat_notice:
            """
            向微信发送请求
            """
            headers = {'content-type': 'application/json'}
            try:
                res = RequestUtils(headers=headers).post(message_url,
                                                        data=json.dumps(req_json, ensure_ascii=False).encode('utf-8'))
                if res and res.status_code == 200:
                    ret_json = res.json()
                    if ret_json.get('errcode') == 0:
                        return True, ret_json.get('errmsg')
                    else:
                        if ret_json.get('errcode') == 42001:
                            self.__get_access_token(force=True)
                        return False, ret_json.get('errmsg')
                elif res is not None:
                    return False, f"错误码：{res.status_code}，错误原因：{res.reason}"
                else:
                    return False, "未获取到返回信息"
            except Exception as err:
                ExceptionUtils.exception_traceback(err)
                return False, str(err)    
        
    @staticmethod
    def is_string_and_not_empty(word):
        """
        判断是否是字符串并且字符串是否为空
        """
        if isinstance(word, str) and word.strip():
            return True
        else:
            return False