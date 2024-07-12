import json
from config.config import Config
from app.utils import  ExceptionUtils
from app.helper.thread_helper import ThreadHelper
from web.appoint_cmd import Appoint_Cmd
from web.other_cmd import Other_Cmd
from web.account_cmd import Account_Cmd
from app.utils.command import Command
class WebAction:
    _actions = {}
    event_commands = {}
    text_commands={}

    def __init__(self):
        # WEB请求响应
        self._actions = {

            "logout": self.__logout,
            "update_config": self.__update_config,
            "get_users": self.get_users,


        }
        self.appoint=Appoint_Cmd()
        self.other=Other_Cmd()
        self.account=Account_Cmd()
        # 远程命令响应
        self._default=self.other.default
        WebAction.text_commands={
            "/Default":{"func": self._default, "desc": "缺省回复"},
            "/Add_Personal_Info":{"func": self.account.add_personal_info, "desc": "添加个人信息"},
            "/Edit_Personal_Info":{"func": self.account.view_personal_info, "desc": "添加个人信息"},
            "/Delete_Personal_Info":{"func": self.account.delete_personal_info, "desc": "注销个人信息"},
            "/Help_Personal_Info":{"func": self.account.help_personal_info, "desc": "个人信息帮助"},
            
            "/Add_Appoint": {"func": self.appoint.add_appoint, "desc": "添加预约"},
            "/Edit_Appoint": {"func": self.appoint.edit_appoint, "desc": "编辑预约"},    
            "/View_Appoint": {"func": self.appoint.view_appoint, "desc": "查看所有预约信息"},   
            "/Delete_Appoint": {"func": self.appoint.delete_appoint, "desc": "删除预约"},
            "/Help_Appoint": {"func": self.appoint.help_appoint, "desc": "预约帮助"},        
        }
        WebAction.event_commands = {

            "/Edit_Personal_Info":{"func": self.account.view_personal_info, "desc": "添加个人信息"},

            "/Default":{"func": self._default, "desc": "缺省回复"},
            "/Subscribe":{"func": self.other.help, "desc": "缺省回复"},
            "/Add_Personal_Info":{"func": self.account.add_personal_info, "desc": "添加个人信息"},
            "/Delete_Personal_Info":{"func": self.account.delete_personal_info, "desc": "注销个人信息"},
            "/Help_Personal_Info":{"func": self.account.help_personal_info, "desc": "个人信息帮助"},   

            "/Add_Week_Appoint/Week": {"func": self.appoint.week_appoint, "desc": "编辑周常预约周几"},
            "/Add_Week_Appoint/Field": {"func": self.appoint.field_appoint, "desc": "编辑周常预约场地"},
            "/Add_Week_Appoint/Gym": {"func": self.appoint.gym_appoint, "desc": "编辑周常预约场馆"},
            "/Add_Week_Appoint/Time": {"func": self.appoint.time_appoint, "desc": "编辑周常预约时间"},
            "/Add_Week_Appoint/Confirm": {"func": self.appoint.confirm_appoint, "desc": "确认周常预约"},
            "/Add_Week_Appoint/Submit": {"func": self.appoint.submit_appoint, "desc": "提交周常预约"},
            "/Add_Date_Appoint/Date": {"func": self.appoint.date_appoint, "desc": "编辑日期预约"},


            "/View_Appoint/All": {"func": self.appoint.view_appoint_all, "desc": "查看所有预约信息"},
            "/View_Appoint/Day": {"func": self.appoint.view_appoint_day, "desc": "查看某日预约信息"},
            "/Help_Appoint": {"func": self.appoint.help_appoint, "desc": "预约帮助"},

            "/Edit_Appoint": {"func": self.appoint.edit_appoint, "desc": "编辑预约"},  
            "/Delete_Appoint": {"func": self.appoint.delete_appoint, "desc": "删除预约"},

            "/Help": {"func": self.other.help, "desc": "查看帮助"},
            "/Privacy": {"func": self.other.privacy, "desc": "查看隐私政策"},
            "/Feedback": {"func": self.other.feedback, "desc": "使用反馈"}
        }
        



    @staticmethod
    def __logout():
        """
        注销
        """
        #logout_user()
        return {"code": 0}

    def __update_config(self, data):
        """
        更新配置信息
        """
        cfg = Config.get_config()
        cfgs = dict(data).items()
        # 仅测试不保存
        config_test = False
        # 修改配置
        for key, value in cfgs:
            if key == "test" and value:
                config_test = True
                continue
            # 生效配置
            cfg = self.set_config_value(cfg, key, value)

        # 保存配置
        if not config_test:
            Config.save_config(cfg)

        return {"code": 0}


    @staticmethod
    def get_users():
        """
        查询所有用户
        """
        # user_list = ProUser().get_users()
        # Users = []
        # for user in user_list:
        #     pris = str(user.PRIS).split(",")
        #     Users.append({"id": user.ID, "name": user.NAME, "pris": pris})
        # return {"code": 0, "result": Users}
    




    
    def handle_message_job(self, msg,  user_id=None, response_code=None):
        """
        处理消息事件
        """
        if not msg:
            return

        # 触发MessageIncoming事件
        # EventManager().send_event(EventType.MessageIncoming, {
        #     "channel": in_from.value,
        #     "user_id": user_id,
        #     "user_name": user_name,
        #     "message": msg

        # })

        # 系统内置命令
        cmd,param_dict=Command.parse_command(msg)
        if len(param_dict)!=0:
            if param_dict.get("Wechat"):
                command = WebAction.text_commands.get(cmd)
            else:
                command = WebAction.event_commands.get(cmd)
        else:
            command = WebAction.event_commands.get(cmd)            
        if command:
            # 启动服务
            ThreadHelper().start_thread(command.get("func"), ( user_id,param_dict,response_code))
            # 消息回应
            return
        else:
            ThreadHelper().start_thread(self._default, ( user_id,))
            return


