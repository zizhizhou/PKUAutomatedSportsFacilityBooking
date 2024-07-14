from app.client.wechat import WeChat
import copy
from app.conf import ModuleConf
from app.db.main_db import MainDb
from loguru import logger
from app.db.models import UserAction,Users
from app.utils.command import Command
from web.account_cmd import Account_Cmd
class Appoint_Cmd():
    def __init__(self):
        self.WX=WeChat()
        self.db=MainDb()

    @staticmethod
    def check_appoint_params(param_dict):

        try:
            
            if set(param_dict.get("Week")).issubset(set(ModuleConf.WEEK_MENU.keys())) and \
                set(param_dict.get("Gym")).issubset(set(ModuleConf.GYM_MENU.keys())) and \
                    set(param_dict.get("Field")).issubset(set(ModuleConf.FIELD_MENU.keys())) and \
                        set(param_dict.get("Time")).issubset(set(ModuleConf.TIME_MENU.keys())):
                if not param_dict.get("Status") or param_dict.get("Status")=='1' or param_dict.get("Status")=='0':
                    pass
                else:
                    return False
                return True

            else:
                return False
        except:
            return False


    def add_appoint(self,  user_id,param_dict,response_code):

        #对参数作检查
        if Appoint_Cmd.check_appoint_params(param_dict):
            param_dict["Submit"]="1"
            self.submit_appoint(user_id,param_dict,response_code=None)
        else:
            self.WX.send_msg(title="参数有误，请检查！", user_id=user_id)
        pass


    def view_appoint(self,  user_id,param_dict,response_code):
        string_list=[]

        appoint_plans = self.db.query(UserAction).filter_by(USERID=user_id).all() 
        if len(appoint_plans)==0:
            self.WX.send_msg(title="您尚无预约信息！",user_id=user_id )
            return
        string_list.append("————————————\n")
        for plan in appoint_plans:        
            string_list.append(f"【ID】：{plan.ID}\n"
                               f"【预约日期】：{ModuleConf.WEEK_MENU.get(plan.WEEKDAY)}\n"
                                f"【预约场馆】：{ModuleConf.GYM_MENU.get(plan.GYM).get('name')}\n"
                                f"【预约时段】：{plan.APPOINTTIME}\n"
                                f"【预约场地】：{plan.FIELD}\n"
                                f"【预约状态】：{plan.STATUS}\n"
                                f"————————————\n")
        send_text = "\n".join(string_list)
        self.WX.send_msg(title="【查看预约】 ",text=send_text,user_id=user_id)

    def help_appoint(self,  user_id,param_dict,response_code):
            self.WX.send_msg(title="请参阅：https://github.com/zizhizhou/PKUAutomatedSportsFacilityBooking/blob/main/README.md#22%E9%A2%84%E7%BA%A6%E7%AE%A1%E7%90%86", user_id=user_id)
            
    def week_appoint(self,user_id,param_dict,response_code):
        if not Account_Cmd.check_account(user_id):
            self.WX.send_msg(title="您尚未添加个人信息！请先在“我的—添加个人信息”中添加个人信息", user_id=user_id)
            return
        req_json= {
            "touser" : user_id,
            "msgtype" : "template_card",
            "agentid" : self.WX._agent_id,
            "template_card" : {
                "card_type" : "vote_interaction",
                "main_title" : {
                    "title" : "周常预约",
                    "desc" : "请选择您要进行编辑的日期（多选）"
                },
                "task_id": self.WX.get_task_id(),
                "checkbox": {
                    "question_key": "Week",
                    "option_list": [
                        {
                            "id": "1",
                            "text": "周一",
                            "is_checked": False
                        },
                        {
                            "id": "2",
                            "text": "周二",
                            "is_checked": False
                        },
                        {
                            "id": "3",
                            "text": "周三",
                            "is_checked": False
                        },
                        {
                            "id": "4",
                            "text": "周四",
                            "is_checked": False
                        },
                        {
                            "id": "5",
                            "text": "周五",
                            "is_checked": False
                        },
                        {
                            "id": "6",
                            "text": "周六",
                            "is_checked": False
                        },
                        {
                            "id": "7",
                            "text": "周日",
                            "is_checked": False
                        },
                    ],
                    "mode": 1
                },

                "submit_button": {
                    "text": "提交",
                    "key": "/Add_Week_Appoint/Gym"
                }
            },
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
            "replace_text":"已提交"
            }
        
        self.WX.direct_send_message(req_json,send_url=None)


    def gym_appoint(self,  user_id,param_dict,response_code):
        command=Command.comp_command("/Add_Week_Appoint/Field",param_dict)
        option_list=[]
        for gym_key,gym_value in ModuleConf.GYM_MENU.items():
            option_list.append({
                "id": gym_key,
                "text": gym_value.get("name"),
                "is_checked": False
            })
        req_json= {
                "userids" : user_id,
                "agentid" : self.WX._agent_id,
                "response_code": response_code,
                "template_card" : {
                    "card_type" : "vote_interaction",
                    "main_title" : {
                        "title" : "周常预约",
                        "desc" : "请选择场馆"
                    },
                    "checkbox": {
                        "question_key": "Gym",
                        "option_list": option_list,
                        "disable": False,
                        "mode": 0
                    },
                    "submit_button": {
                        "text": "提交",
                        "key": command
                    },
                }
            }
        
 
        send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
        self.WX.direct_send_message(req_json,send_url=send_url)



    def field_appoint(self,  user_id,param_dict,response_code):
        command=Command.comp_command("/Add_Week_Appoint/Time",param_dict)
        option_list=[]
        for field_key,field_value in ModuleConf.FIELD_MENU.items():
            if param_dict.get("Gym")=="1" and field_value.get("id")>9:#五四只有9片场地
                continue
            option_list.append({
                "id": field_key,
                "text": field_value.get("text"),
                "is_checked": False
            })
        req_json= {
                "userids" : user_id,
                "agentid" : self.WX._agent_id,
                "response_code": response_code,
                "template_card" : {
                    "card_type" : "vote_interaction",
                    "main_title" : {
                        "title" : "周常预约",
                        "desc" : "请选择您要进行编辑的场地（多选）"
                    },
                    "checkbox": {
                        "question_key": "Field",
                        "option_list": option_list,
                        "mode": 1
                    },
                    "submit_button": {
                        "text": "提交",
                        "key": command
                    },

                }
            }
        
        send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
        self.WX.direct_send_message(req_json,send_url=send_url)



    def time_appoint(self,  user_id,param_dict,response_code):
        command=Command.comp_command("/Add_Week_Appoint",param_dict)
        option_list=[]
        for time_key,time_value in ModuleConf.TIME_MENU.items():
            if param_dict.get("Gym")=="0" and time_value.get("id")<1:#邱德拔早上上午8：00才开
                continue
            option_list.append({
                "id": time_key,
                "text": time_value.get("text"),
                "is_checked": False
            })
        req_json= {
                "userids" : user_id,
                "agentid" : self.WX._agent_id,
                "response_code": response_code,
                "template_card" : {
                    "card_type" : "vote_interaction",
                    "main_title" : {
                        "title" : "周常预约",
                        "desc" : "请选择时段（最多选择两个时段）"
                    },
                    "checkbox": {
                        "question_key": "Time",
                        "option_list": option_list,
                        "disable": False,
                        "mode": 1
                    },
                    "submit_button": {
                        "text": "提交",
                        "key": command
                    },
                }
            }
        
        send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
        self.WX.direct_send_message(req_json,send_url=send_url)


    def confirm_appoint(self,  user_id,param_dict,response_code):
        cancel_dict=copy.deepcopy(param_dict)
        cancel_dict["Submit"]=0
        submmit_dict=copy.deepcopy(param_dict)
        submmit_dict["Submit"]=1
        cancel_command=Command.comp_command("/Add_Week_Appoint/Submit",cancel_dict)
        submmit_command=Command.comp_command("/Add_Week_Appoint/Submit",submmit_dict)
        for i in range(len(param_dict["Week"])):
            param_dict["Week"][i]=ModuleConf.WEEK_MENU.get(param_dict["Week"][i])
        param_dict["Gym"]=ModuleConf.GYM_MENU.get(param_dict["Gym"]).get("name")
        for i in range(len(param_dict["Field"])):
            param_dict["Field"][i]=str(param_dict["Field"][i])+"号场地"
        req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "template_card" : {
                "card_type" : "button_interaction",
                "main_title" : {
                    "title" : "周常预约",
                    "desc" : "预约信息确认"
                },

                "sub_title_text" : "以下是您本次的预约信息：",
                "horizontal_content_list" : [
                    {
                        "keyname": "预约日期",
                        "value": str(param_dict["Week"]),
                    },
                    {
                        "keyname": "预约场馆",
                        "value": str(param_dict["Gym"]),
                    },
                    {
                        "keyname": "预约场地",
                        "value": str(param_dict["Field"]),
                    },
                    {
                        "keyname": "预约时间",
                        "value": str(param_dict["Time"]),
                    }
                ],
                "button_list": [
                    {
                        "type": 0,
                        "text": "取消",
                        "style": 4,
                        "key": cancel_command
                    },
                    {
                        "type": 0,
                        "text": "确认",
                        "style": 1,
                        "key": submmit_command
                    }
                ],
            }

        }
        send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
        self.WX.direct_send_message(req_json,send_url=send_url)


    def submit_appoint(self,  user_id,param_dict,response_code):
        submit_req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "button":{
                "replace_name": "已提交"
            }
        }
        cancel_req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "button":{
                "replace_name": "已取消"
            }
        }
        if param_dict["Submit"]=="1":
            req_json=submit_req_json
            user=self.db.query(Users).filter(Users.USERID == user_id).first()
            id= 10*user.ID
            for week_day in param_dict["Week"]:
                sql_text=f"""INSERT OR REPLACE INTO "USERACTION" ( "ID","USERID", "WEEKDAY",  "GYM", "FIELD","APPOINTTIME","STATUS") VALUES (:id_val, :userid_val, :weekday_val, :gym_val, :field_val, :appointtime_val,:status_val);"""
                status=True
                if param_dict.get("Status"):
                    status=True if param_dict.get("Status")=="1" else False
                params = {
                    'id_val': id+int(week_day),
                    'userid_val': user_id,
                    'weekday_val': week_day,
                    'gym_val': param_dict['Gym'],
                    'field_val': str(param_dict['Field']),
                    'appointtime_val':str(param_dict['Time']),
                    'status_val':status
                }
                logger.info(f"用户 {user_id} 向数据库中写入信息，信息内容为:\n{sql_text}\n{params}")
                self.db.excute(sql_text,params)
                self.db.commit()
                #appoint_plans = mydb.query(UserAction).filter_by(USERID=user_id,WEEKDAY=week_day).first()
                #print(appoint_plans.ID,appoint_plans.USERID,appoint_plans.WEEKDAY,appoint_plans.GYM,appoint_plans.FIELD,appoint_plans.APPOINTTIME)
        else:
            req_json=cancel_req_json
        if response_code:
            send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
            self.WX.direct_send_message(req_json,send_url=send_url)
        else:
            string_list=[]
            for i in range(len(param_dict["Week"])):
                param_dict["Week"][i]=ModuleConf.WEEK_MENU.get(param_dict["Week"][i])
            param_dict["Gym"]=ModuleConf.GYM_MENU.get(param_dict["Gym"]).get("name")
            for i in range(len(param_dict["Field"])):
                param_dict["Field"][i]=str(param_dict["Field"][i])+"号场地"
            string_list.append(f"————————————\n"
                    f"【预约日期】：{param_dict['Week']}\n"
                    f"【预约场馆】：{param_dict['Gym']}\n"
                    f"【预约时段】：{param_dict['Time']}\n"
                    f"【预约场地】：{param_dict['Field']}\n"
                    f"【预约状态】：{param_dict['Status']}\n"
                    f"————————————\n")
            send_text = "\n".join(string_list)
            self.WX.send_msg(title=f"【周常预约】",text=send_text, user_id=user_id)            


    def view_appoint_all(self,user_id,param_dict,response_code):
        if not Account_Cmd.check_account(user_id):
            self.WX.send_msg(title="您尚未添加个人信息！请先在“我的—添加个人信息”中添加个人信息", user_id=user_id)
            return
        appoint_plans = self.db.query(UserAction).filter_by(USERID=user_id).all() 
        if len(appoint_plans)==0:
            self.WX.send_msg(title="您尚无预约信息！",user_id=user_id )
            return
        plans=[] 
        for plan in appoint_plans:
            text=f"{ModuleConf.WEEK_MENU.get(plan.WEEKDAY)},{ModuleConf.GYM_MENU.get(plan.GYM).get('name')}"
            plans.append({
                "id": plan.ID,
                "text": text,
            })
        desc=f"您有{len(appoint_plans)}条预约信息，请选择您要进行查看的预约"
        req_json= {
            "touser" : user_id,
            "msgtype" : "template_card",
            "agentid" : self.WX._agent_id,
            "template_card" : {
                "card_type" : "vote_interaction",
                "main_title" : {
                    "title" : "查看预约",
                    "desc" : desc
                },
                "task_id": self.WX.get_task_id(),
                "checkbox": {
                    "question_key": "ID",
                    "option_list": plans,
                    "mode": 0
                },
                "submit_button": {
                    "text": "提交",
                    "key": "/View_Appoint/Day"
                }
            },
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
            "replace_text":"已提交"
            }
        
        
        
        self.WX.direct_send_message(req_json,send_url=None)



    def view_appoint_day(self,user_id,param_dict,response_code):
        appoint_plan = self.db.query(UserAction).filter_by(ID=param_dict["ID"]).first() 
        command=Command.comp_command("/Edit_Appoint/Status",param_dict)
        button_list=[
                    {
                        "type": 0,
                        "text": "返回",
                        "style": 1,
                        "key": "/View_Appoint/All"
                    },
                    {
                        "type": 0,
                        "text": "编辑",
                        "style": 1,
                        "key": f"/Add_Week_Appoint/Gym --Week=['{appoint_plan.WEEKDAY}']"
                    },
                    {
                        "type": 0,
                        "text": "删除",
                        "style": 3,
                        "key": f"/Delete_Appoint --ID={appoint_plan.ID}"
                    },
                ]
        if appoint_plan.STATUS==True:
            button_list.insert(2,{"type": 0,
                        "text": "停用",
                        "style": 3,
                        "key": f"/Edit_Appoint --ID={appoint_plan.ID} --Status=0"})
        else:
            button_list.insert(2,{"type": 0,
            "text": "启用",
            "style": 2,
            "key": "/Edit_Appoint --ID={appoint_plan.ID} --Status=1"})
        req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "template_card" : {
                "card_type" : "button_interaction",
                "main_title" : {
                    "title" : "查看预约",
                    "desc" : "查看预约信息"
                },

                "sub_title_text" : "以下是您选择查看的预约信息：",
                "horizontal_content_list" : [
                    {
                        "keyname": "预约日期",
                        "value": ModuleConf.WEEK_MENU.get(appoint_plan.WEEKDAY),
                    },
                    {
                        "keyname": "预约场馆",
                        "value": ModuleConf.GYM_MENU.get(appoint_plan.GYM).get('name'),
                    },
                    {
                        "keyname": "预约场地",
                        "value": str(appoint_plan.FIELD),
                    },
                    {
                        "keyname": "预约时间",
                        "value": str(appoint_plan.APPOINTTIME),
                    },
                    {
                        "keyname": "预约状态",
                        "value": str(appoint_plan.STATUS),
                    }
                ],
                "button_list": button_list,
            }

        }
        
 
        send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
        self.WX.direct_send_message(req_json,send_url=send_url)


    def delete_appoint(self,user_id,param_dict,response_code):
        appoint_plan = self.db.query(UserAction).filter_by(ID=param_dict["ID"]).first() 
        req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "button":{
                "replace_name": "该条预约信息已删除"
            }
        }        
        self.db.delete(appoint_plan)
        if response_code:
            send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
            self.WX.direct_send_message(req_json,send_url=send_url)
        else:
            self.WX.send_msg(title=f"ID为{param_dict['ID']}的预约信息已删除", user_id=user_id)

    def edit_appoint(self,user_id,param_dict,response_code):
        appoint_plan = self.db.query(UserAction).filter_by(ID=param_dict["ID"]).first() 
        req_json={
            "userids" : user_id,
            "agentid" : self.WX._agent_id,
            "response_code": response_code,
            "button":{
                "replace_name": "已编辑"
            }
        }
        if param_dict.get("Status"):
            appoint_plan.STATUS=bool(int(param_dict.get("Status")))
        if param_dict.get("Gym"):
            appoint_plan.GYM=param_dict.get("Gym")
        if param_dict.get("Filed"):
            appoint_plan.FIELD=str(param_dict.get("Filed"))
        if param_dict.get("Time"):
            appoint_plan.TIME=str(param_dict.get("Time"))
        self.db.commit()
        
        if response_code:#如果有，说明是企业微信发的
            send_url=f"{self.WX._default_proxy}/cgi-bin/message/update_template_card?access_token={self.WX._access_token}"
            self.WX.direct_send_message(req_json,send_url=send_url)
        else:
            string_list=[]
            string_list.append(f"【ID】：{appoint_plan.ID}\n"
                    f"【预约日期】：{ModuleConf.WEEK_MENU.get(appoint_plan.WEEKDAY)}\n"
                    f"【预约场馆】：{ModuleConf.GYM_MENU.get(appoint_plan.GYM).get('name')}\n"
                    f"【预约时段】：{appoint_plan.APPOINTTIME}\n"
                    f"【预约场地】：{appoint_plan.FIELD}\n"
                    f"【预约状态】：{appoint_plan.STATUS}\n"
                    f"————————————\n")
            send_text = "\n".join(string_list)
            self.WX.send_msg(title=f"ID为{param_dict['ID']}的预约信息已修改",text=send_text, user_id=user_id)

    def date_appoint(self,user_id,param_dict,response_code):

        self.WX.send_msg(title="尚在开发，敬请期待！", user_id=user_id)
