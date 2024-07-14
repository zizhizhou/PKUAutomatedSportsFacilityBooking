from flask import Flask, request, json, render_template, make_response, session, send_from_directory, send_file, \
    redirect, Response
import datetime,os
from werkzeug.middleware.proxy_fix import ProxyFix
from loguru import logger
from config.config import Config
from web.WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.dom.minidom
from app.utils import DomUtils,ExceptionUtils
from app.client.wechat import WeChat
import traceback
from web.action import WebAction
from app.utils.command import Command
# Flask App
App = Flask(__name__)
App.wsgi_app = ProxyFix(App.wsgi_app)
App.config['JSON_AS_ASCII'] = False
App.config['JSON_SORT_KEYS'] = False
App.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
App.config['SESSION_REFRESH_EACH_REQUEST'] = False
App.secret_key = os.urandom(24)
App.permanent_session_lifetime = datetime.timedelta(days=30)
WX=WeChat()


@App.route('/wechat', methods=['GET', 'POST'])
def wechat():   
    sToken = Config._token
    sEncodingAESKey = Config._encodingAESKey
    sCorpID = Config._corpid
    if not sToken or not sEncodingAESKey or not sCorpID:
        return
    wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
    sVerifyMsgSig = request.args.get("msg_signature")
    sVerifyTimeStamp = request.args.get("timestamp")
    sVerifyNonce = request.args.get("nonce")

    if request.method == 'GET':
        if not sVerifyMsgSig and not sVerifyTimeStamp and not sVerifyNonce:
            return "NAStool微信交互服务正常！<br>微信回调配置步聚：<br>1、在微信企业应用接收消息设置页面生成Token和EncodingAESKey并填入设置->消息通知->微信对应项，打开微信交互开关。<br>2、保存并重启本工具，保存并重启本工具，保存并重启本工具。<br>3、在微信企业应用接收消息设置页面输入此地址：http(s)://IP:PORT/wechat（IP、PORT替换为本工具的外网访问地址及端口，需要有公网IP并做好端口转发，最好有域名）。"
        sVerifyEchoStr = request.args.get("echostr")
        logger.info("收到微信验证请求: echostr= %s" % sVerifyEchoStr)
        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
        if ret != 0:
            logger.error("微信请求验证失败 VerifyURL ret: %s" % str(ret))
        # 验证URL成功，将sEchoStr返回给企业号
        return sEchoStr
    else:
        #return
        try:
            sReqData = request.data
            #logger.debug("收到微信请求：%s" % str(sReqData))
            ret, sMsg = wxcpt.DecryptMsg(sReqData, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce)
            if ret != 0:
                logger.error("解密微信消息失败 DecryptMsg ret = %s" % str(ret))
                return make_response("ok", 200)
            # 解析XML报文
            """
            1、消息格式：
            <xml>
               <ToUserName><![CDATA[toUser]]></ToUserName>
               <FromUserName><![CDATA[fromUser]]></FromUserName> 
               <CreateTime>1348831860</CreateTime>
               <MsgType><![CDATA[text]]></MsgType>
               <Content><![CDATA[this is a test]]></Content>
               <MsgId>1234567890123456</MsgId>
               <AgentID>1</AgentID>
            </xml>
            2、事件格式：
            <xml>
                <ToUserName><![CDATA[toUser]]></ToUserName>
                <FromUserName><![CDATA[UserID]]></FromUserName>
                <CreateTime>1348831860</CreateTime>
                <MsgType><![CDATA[event]]></MsgType>
                <Event><![CDATA[subscribe]]></Event>
                <AgentID>1</AgentID>
            </xml>            
            """
            dom_tree = xml.dom.minidom.parseString(sMsg.decode('UTF-8'))
            root_node = dom_tree.documentElement
            # 消息类型
            msg_type = DomUtils.tag_value(root_node, "MsgType")
            # Event event事件只有click才有效,enter_agent无效
            event = DomUtils.tag_value(root_node, "Event")
            # 用户ID
            user_id = DomUtils.tag_value(root_node, "FromUserName")
            # 没的消息类型和用户ID的消息不要
            if not msg_type or not user_id:
                logger.info("收到微信心跳报文...")
                return make_response("ok", 200)
            # 解析消息内容
            content = ""
            input_cmd=""
            response_code=None
            web_action=WebAction()
            if msg_type == "event" or msg_type =="text":
                logger.info(f"收到微信请求：userid={user_id}, msg_type={msg_type}")
                content = DomUtils.tag_value(root_node, "Content", default="")
                if msg_type == "text":
                    # 文本消息
                    if content:
                        input_cmd=content
                        command_key,param_dict=Command.parse_command(content)
                        if command_key in WebAction.text_commands.keys():
                            param_dict["Wechat"]=True
                        else:
                            command_key="/Default"
                        input_cmd=Command.comp_command(command_key,param_dict)

                elif msg_type == "event":
                    event_key = DomUtils.tag_value(root_node, "EventKey")
                    if event=="subscribe":#新增用户
                        input_cmd="/Subscribe"
                    elif event=="click":#用户点击菜单
                        if event_key:
                            input_cmd=event_key
                    elif event=="template_card_event":                   
                        command_key,param_dict=Command.parse_command(event_key)
                        question_key = DomUtils.tag_value(root_node, "QuestionKey", default="")
                        response_code= DomUtils.tag_value(root_node, "ResponseCode", default="")
                        #tagNames = root_node.getElementsByTagName("OptionId")
                                        
                        if command_key in ['/Add_Week_Appoint/Gym','/Add_Week_Appoint/Time']:
                            # 处理多项选择消息
                            option_ids= DomUtils.tag_value_list(root_node, "OptionId", default="") 
                            #for i in range(len(option_ids)):
                                #option_ids[i]=Command.hex18_to_decimal(option_ids[i])
                            input_cmd=event_key+f" --{question_key}={option_ids}"

                        elif command_key in ['/Add_Week_Appoint/Field','/View_Appoint/Day']:
                            # 处理单项选择消息

                            option_id= DomUtils.tag_value(root_node, "OptionId", default="")
                            input_cmd=event_key+f" --{question_key}={option_id}" 
                  
                        elif command_key=='/Add_Week_Appoint':
                            # 处理消息内容
                            option_ids= DomUtils.tag_value_list(root_node, "OptionId", default="") 
                            #for i in range(len(option_ids)):
                            #    option_ids[i]=WebAction.hex18_to_decimal(option_ids[i])
                            input_cmd=Command.comp_command("/Add_Week_Appoint/Confirm",param_dict)+f" --{question_key}={option_ids}"
                                            
                        elif command_key in ['/Add_Week_Appoint/Submit','/View_Appoint/All','/Delete_Appoint','/Edit_Appoint']:
                            # 处理没有或自带参数的消息内容
                            option_ids= DomUtils.tag_value_list(root_node, "OptionId", default="") 
                            input_cmd=event_key

                        
                web_action.handle_message_job(msg=input_cmd,
                            user_id=user_id,
                            response_code=response_code) 
                
            return make_response(content, 200)
        
        except Exception as err:
            ExceptionUtils.exception_traceback(err)
            logger.error("微信消息处理发生错误：%s - %s" % (str(err), traceback.format_exc()))
            return make_response("ok", 200)
