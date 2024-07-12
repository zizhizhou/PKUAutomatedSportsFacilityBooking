from configparser import ConfigParser
import os,sys,shutil,ruamel.yaml
class Config():#配置类
    _config_path = None
    _config = {}
    _wechat_notice=None
    _rsa_encrypt=None
    _local_sql=None
    _browser=None
    _port=None

    _appoint_delay_day=None
    _execute_start_time=None
    _execute_finish_time=None

    _mode=None

    _token=None
    _corpid=None
    _agentid=None
    _corpserect=None
    _proxy=None
    _encodingAESKey=None   

    def __init__(self):
        pass
        #self.init_config()

    def init_data(self):
        Config._browser=self.get_config('setting').get("browser")
        Config._port=self.get_config('setting').get("port")

        Config._appoint_delay_day=self.get_config('time').get('delay_day')
        Config._execute_start_time=self.get_config('time').get('execute_start_time')
        Config._execute_finish_time=self.get_config('time').get('execute_finish_time')

        Config._mode=self.get_config('operate').get('mode')

        Config._wechat_notice=self.token=self.get_config('wechat').get('wechat_notice')
        Config._rsa_encrypt=self.token=self.get_config('wechat').get('rsa_encrypt')
        Config._local_sql=self.token=self.get_config('wechat').get('local_sql')

        Config._token=self.get_config('wechat').get('TOKEN')
        Config._corpid=self.get_config('wechat').get('CORP_ID')
        Config._agentid=self.get_config('wechat').get('AGENT_ID')
        Config._corpserect=self.get_config('wechat').get('CORP_SERECT')
        Config._proxy=self.get_config('wechat').get('PROXY')
        Config._encodingAESKey=self.get_config('wechat').get('EncodingAESKey')

    def init_config(self):
        try:
            Config._config_path=os.path.join(Config.get_root_path(),"config.yaml")
            if not os.path.exists(Config._config_path):
                os.makedirs(os.path.dirname(Config._config_path), exist_ok=True)
                cfg_tp_path = os.path.join(Config.get_inner_config_path(), "config.yaml")
                shutil.copy(cfg_tp_path, Config._config_path)
                print("【Config】config.yaml 配置文件不存在，已将配置文件模板复制到配置目录...")

            with open(Config._config_path, mode='r', encoding='utf-8') as cf:
                try:
                    # 读取配置
                    print("正在加载配置：%s" % Config._config_path)
                    Config._config = ruamel.yaml.YAML().load(cf)
                    self.init_data()
                except Exception as e:
                    print("【Config】配置文件 config.yaml 格式出现严重错误！请检查：%s" % str(e))
                    Config._config = {}
        except Exception as err:
            print("【Config】加载 config.yaml 配置出错：%s" % str(err))
            return False
        self.init_data()
    
    @staticmethod 
    def get_inner_config_path():
        return os.path.join(Config.get_root_path(), "config")
    
    @staticmethod
    def get_config_path():
        return os.path.dirname(Config._config_path) 
       
    @staticmethod
    def get_driver_path():
        return os.path.join(Config.get_root_path(), "driver")
        
    @staticmethod
    def get_root_path():
        #return os.path.dirname(os.path.realpath(__file__))
        current_file_path = os.path.realpath(__file__)  # 获取当前文件的绝对路径
        parent_directory = os.path.dirname(current_file_path)  # 获取当前文件的所在目录路径
        parent_directory = os.path.dirname(parent_directory) 
        return parent_directory
    
    @staticmethod
    def get_config(node=None):
        if not node:
            return Config._config
        return Config._config.get(node, {})

    @staticmethod
    def get_scripts_path():
        scripts_folder=os.path.join(Config.get_root_path(), "scripts")
        if not os.path.exists(scripts_folder):
            # 若文件夹不存在，则创建文件夹
            os.makedirs(scripts_folder)
        return scripts_folder

    @staticmethod
    def get_keys_path():
        keys_folder=os.path.join(Config.get_root_path(), "scripts", "keys")
        if not os.path.exists(keys_folder):
            # 若文件夹不存在，则创建文件夹
            os.makedirs(keys_folder)
        return keys_folder
    
    @staticmethod
    def get_db_path():
        db_folder=os.path.join(Config.get_root_path(), "scripts", "db")
        if not os.path.exists(db_folder):
            # 若文件夹不存在，则创建文件夹
            os.makedirs(db_folder)
        return db_folder
    
    @staticmethod
    def get_sqls_path():
        sqls_folder=os.path.join(Config.get_root_path(), "scripts", "sqls")
        if not os.path.exists(sqls_folder):
            # 若文件夹不存在，则创建文件夹
            os.makedirs(sqls_folder)
        return sqls_folder
    
    @staticmethod
    def save_config(new_cfg):
        Config._config = new_cfg
        with open(Config._config_path, mode='w', encoding='utf-8') as sf:
            yaml = ruamel.yaml.YAML()
            return yaml.dump(new_cfg, sf)