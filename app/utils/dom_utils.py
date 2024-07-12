class DomUtils:

    @staticmethod
    def tag_value(tag_item, tag_name, attname="", default=None):
        """
        解析XML标签值
        """
        tagNames = tag_item.getElementsByTagName(tag_name)
        if tagNames:
            if attname:
                attvalue = tagNames[0].getAttribute(attname)
                if attvalue:
                    return attvalue
            else:
                firstChild = tagNames[0].firstChild
                if firstChild:
                    return firstChild.data
        return default

    @staticmethod
    def add_node(doc, parent, name, value=None):
        """
        添加一个DOM节点
        """
        node = doc.createElement(name)
        parent.appendChild(node)
        if value is not None:
            text = doc.createTextNode(str(value))
            node.appendChild(text)
        return node


    #@staticmethod
    #def get_Elements(tag_item, tag_name, attname="", default=None):
        # """`
        # 解析XML标签值
        # """
        # tagNames = tag_item.getElementsByTagName(tag_name)
        # for option_id in selected_item.findall('.//OptionId'):
        #     print(option_id.text)
        # if tagNames:
        #     if attname:
        #         attvalue = tagNames[0].getAttribute(attname)
        #         if attvalue:
        #             return attvalue
        #     else:
        #         firstChild = tagNames[0].firstChild
        #         if firstChild:
        #             return firstChild.data
        # return default
    
    @staticmethod
    def tag_value_list(tag_item, tag_name, attname="", default=None):
        """
        解析XML标签值
        """
        tagNames = tag_item.getElementsByTagName(tag_name)
        if tagNames:
            if attname:
                attvalue_list=[]
                for tagName in tagNames:
                    attvalue_list.append(tagName.getAttribute(attname))
                if attvalue_list:
                    return attvalue_list
            else:
                data_list=[]
                for tagName in tagNames:
                    data_list.append(tagName.firstChild.data)
                if data_list:
                    return data_list
        return default

