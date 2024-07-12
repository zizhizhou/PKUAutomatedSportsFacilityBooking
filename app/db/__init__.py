import os
#import log
from config.config import Config
from .main_db import MainDb
from .main_db import DbPersist
from loguru import logger
#from .media_db import MediaDb
#from alembic.config import Config as AlembicConfig
#from alembic.command import upgrade as alembic_upgrade


def init_db():
    """
    初始化数据库
    """
    logger.info('开始初始化数据库...')
    #log.console('开始初始化数据库...')
    #MediaDb().init_db()
    MainDb().init_db()
    logger.info('数据库初始化完成')

    #log.console('数据库初始化完成')


def init_data():
    """
    初始化数据
    """
    logger.info('开始初始化数据...')
    if Config._local_sql:#则读本地数据库
        MainDb().init_data()
        logger.info('数据初始化完成')


def update_db():
    """
    更新数据库
    """
    #db_location = os.path.normpath(os.path.join("./config", 'user.db'))
    #script_location = os.path.normpath(os.path.join(Config().get_root_path(), 'scripts'))
    logger.info('开始更新数据库...')
    try:
        #alembic_cfg = AlembicConfig()
        #alembic_cfg.set_main_option('script_location', script_location)
        #alembic_cfg.set_main_option('sqlalchemy.url', f"sqlite:///{db_location}")
        #alembic_upgrade(alembic_cfg, 'head')
        logger.info('数据库更新完成')
    except Exception as e:
        logger.info(f'数据库更新失败：{e}')
