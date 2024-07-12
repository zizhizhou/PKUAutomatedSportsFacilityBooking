
import re,ast
class Command():


    @staticmethod
    def hex18_to_decimal(hex18):
        # 定义18进制数的字符集
        hex18_chars = '0123456789ABCDEFGH'
        
        # 确保输入是两位数的字符串
        if type(hex18)==int:
            hex18_str=str(hex18)
        else:
            hex18_str=hex18
        if len(hex18_str) == 1:
            # 提取个位字符
            unit_char = hex18_str[0]
        elif len(hex18_str) == 2:
            unit_char = hex18_str[1]
        else:
            raise ValueError("输入必须是两位数的18进制数字符串")
        
        
        # 将字符转换为十进制数
        if unit_char in hex18_chars:
            decimal_value = hex18_chars.index(unit_char)
        else:
            raise ValueError("输入包含无效的18进制字符")
        
        return str(decimal_value)
    @staticmethod
    def parse_command(input_str:str):
        try:
            # 使用正则表达式匹配命令和参数部分
            command_match = re.match(r'^(/[\w_/]+)', input_str)
            if not command_match:
                raise ValueError("Invalid input format")
            
            command = command_match.group(1)

            # 提取参数部分
            params_str = input_str[len(command):].strip()

            # 定义匹配参数的正则表达式
            pattern = r'--([a-zA-Z]+)=(\[.*?\]|\S+)'
            
            # 使用正则表达式找到所有匹配项
            matches = re.findall(pattern, params_str)
            
            # 构建字典
            params_dict = {}
            for key, value in matches:
                # 尝试将字符串解析为列表
                # 如果解析结果是列表，则返回列表
                try:
                    parsed_value = ast.literal_eval(value)
                    if not isinstance(parsed_value, list):
                        parsed_value=value
                except (ValueError, SyntaxError):
                    parsed_value = value
                params_dict[key] = parsed_value

            return command, params_dict
        except ValueError:
            return None,None
    @staticmethod
    def comp_command(cmd:str,param:dict):
        # 使用正则表达式匹配命令和参数部分
        result_string = f"{cmd}"
        
        # 遍历字典并格式化每个键值对
        if param!=None:
            for key, value in param.items():
                if isinstance(value, list):
                    value_str = str(value)
                else:
                    value_str = str(value)
                result_string += f" --{key}={value_str}"
        return result_string