from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from config.config import Config
from cryptography.hazmat.backends import default_backend
import os
from loguru import logger
class RsaHelper():
    _private_key=None
    _public_key=None

    @staticmethod
    def init_key_file():
        if Config._rsa_encrypt:
            if os.path.exists(os.path.join(Config.get_keys_path(), 'private_key.pem')) and \
                os.path.exists(os.path.join(Config.get_keys_path(), 'public_key.pem')):
                #公钥私钥文件已经存在
                RsaHelper._private_key,RsaHelper._public_key=RsaHelper.load_keys()
                logger.info("公钥私钥文件已经存在")
                return
            
            # 生成RSA密钥对
            RsaHelper._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            RsaHelper._public_key = RsaHelper._private_key.public_key()
            # 序列化私钥
            private_pem = RsaHelper._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            # 序列化公钥
            public_pem = RsaHelper._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            # 将私钥保存到文件
            with open(os.path.join(Config.get_keys_path(), 'private_key.pem'), "wb") as private_file:
                private_file.write(private_pem)

            # 将公钥保存到文件
            with open(os.path.join(Config.get_keys_path(), 'public_key.pem'), "wb") as public_file:
                public_file.write(public_pem)
            logger.info("无公钥私钥文件，已生成并保存公钥私钥文件")

    
    @staticmethod
    def load_keys():
        if Config._rsa_encrypt:
            with open(os.path.join(Config.get_keys_path(), 'private_key.pem'), "rb") as private_file:
                private_pem = private_file.read()
                private_key = serialization.load_pem_private_key(
                    private_pem,
                    password=None,
                    backend=default_backend()
                )

            with open(os.path.join(Config.get_keys_path(), 'public_key.pem'), "rb") as public_file:
                public_pem = public_file.read()
                public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )

            print("Keys have been loaded from 'private_key.pem' and 'public_key.pem'")
            return private_key, public_key
        return None,None
    
    @staticmethod
    # 使用公钥加密消息
    def encrypt_message(public_key, message):
        """使用公钥加密消息

        Args:
            public_key (_type_): 公钥
            message (_type_): 需要加密的信息

        Returns:
            _type_: 加密后的信息
        """
        if Config._rsa_encrypt:
            encrypted_message = public_key.encrypt(
                message.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted_message
        else:
            return message
    
    @staticmethod
    # 使用私钥解密消息
    def decrypt_message(private_key, encrypted_message):
        """使用私钥解密消息

        Args:
            private_key (_type_): 私钥
            encrypted_message (_type_): 需要解密的消息

        Returns:
            _type_: 解密后的信息
        """
        if Config._rsa_encrypt:
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_message.decode('utf-8')
        else:
            return encrypted_message