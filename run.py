from config.config import Config
from app.db import init_db, update_db, init_data
from initializer import update_config, check_config,  start_config_monitor, stop_config_monitor
from app.helper import ThreadHelper,RsaHelper
from app.book import Appoint

from app.db.models import UserAction,Users
from app.client.wechat import WeChat

from app.db.main_db import MainDb
from web.main import App
def get_run_config():
    """
    获取运行配置
    """
    _web_host = "0.0.0.0"
    _web_port = Config._port
    _ssl_cert = None
    _ssl_key = None
    _debug = False


    app_arg = dict(host=_web_host, port=_web_port, debug=_debug, threaded=True, use_reloader=False)

    return app_arg
def init_system():
    Config().init_config()
    # 数据库初始化
    init_db()
    # 数据库更新
    update_db()
    # 数据初始化
    init_data()
    RsaHelper.init_key_file()
    WX=WeChat()
    WX.init_config()
    WX.set_menu()
def start_service():
    # 启动服务
    mydb=MainDb()
    user_ids= mydb.query(Users.USERID).all()
    #ThreadHelper().start_thread(Appoint('WangLuQin').appoint_func, ())
    for user_id in user_ids:       
        ThreadHelper().start_thread(Appoint(user_id[0]).appoint_func, ())

    
    # 启动服务
    #WebAction.start_service()
    # 监听配置文件变化
    #start_config_monitor()
# 系统初始化


# 本地运行
if __name__ == '__main__':
    init_system()
    start_service()
    pass
    # Flask启动
    if Config._wechat_notice:
        App.run(**get_run_config())