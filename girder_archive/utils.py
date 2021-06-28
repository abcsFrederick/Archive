from collections import namedtuple
from typing import Any

import json
import unicodedata

class Parser(object):
    @staticmethod
    def str_to_obj(string: str):
        parsed_string = Parser.format_string(string)
        return json.loads(parsed_string, object_hook=lambda kwargs: namedtuple('item', kwargs.keys())(*kwargs.values()))

    @staticmethod
    def str_to_dict(string: str):
        parsed_string = Parser.format_string(string)
        return json.loads(parsed_string)

    @staticmethod
    def dict_to_obj(dictinary: dict):
        parsed_string = Parser.format_string(json.dumps(dictinary).replace('"$', '"'))
        return json.loads(parsed_string, object_hook=lambda kwargs: namedtuple('item', kwargs.keys())(*kwargs.values()))

    @staticmethod
    def dict_to_str(dictinary: dict):
        return Parser.__unpack_obj(dictinary, indent=4)
        # return json.dumps(dictinary, indent=4, sort_keys=True)

    @staticmethod
    def obj_to_str(obj: Any):
        return Parser.__unpack_obj(obj, indent=4)

    @staticmethod
    def obj_to_dict(obj: Any):
        if type(obj) is list:
            return [Parser.__unpack(item) for item in obj]
        else:
            return Parser.__unpack(obj)

    @staticmethod
    def format_string(string):
        return unicodedata.normalize(
                'NFKD',
                string
            ).encode(
                'ascii',
                'ignore'
            )

    @staticmethod
    def is_namedtuple(x):
        _type = type(x)
        bases = _type.__bases__
        if len(bases) != 1 or bases[0] != tuple:
            return False
        fields = getattr(_type, '_fields', None)
        if not isinstance(fields, tuple):
            return False
        return all(type(i)==str for i in fields)

    @staticmethod
    def is_list(obj):
        return isinstance(obj, list)

    @staticmethod
    def __unpack_obj(obj, indent: int = 2, depth: int = 1):
        spaces = indent*" "
        if isinstance(obj, list):
            block= "["
            for index in range(0, len(obj)):
                value = obj[index]
                if isinstance(value, tuple):
                    block+="\n{}{}".format(depth*spaces, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, list):
                    block+="\n{}{}".format(depth*spaces, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, dict):
                    block+="\n{}{}".format(depth*spaces, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, int):
                    block+="\n{}{}".format(depth*spaces, value)
                else:
                    block+="\n{}\'{}\'".format(depth*spaces, value)
                if (index+1) < len(obj):
                    block+=","
            block+= "\n{}{}".format((depth-1)*spaces,"]")
        elif isinstance(obj, tuple):
            block= "{"
            for index in range(0, len(obj)):
                key = obj._fields[index]
                value = obj[index]
                if isinstance(value, tuple):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, list):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, dict):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, int):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, value)
                else:
                    block+="\n{}\'{}\': \'{}\'".format(depth*spaces, key, value)
                if (index+1) < len(obj):
                    block+=","
            block+= "\n{}{}".format((depth-1)*spaces,"}")
        elif isinstance(obj, dict):
            block= "{"
            index = 0
            for key, value in obj.items():
                if isinstance(value, tuple):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, list):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, dict):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, Parser.__unpack_obj(value, indent, depth+1))
                elif isinstance(value, int):
                    block+="\n{}\'{}\': {}".format(depth*spaces, key, value)
                else:
                    block+="\n{}\'{}\': \'{}\'".format(depth*spaces, key, value)
                if (index+1) < len(obj):
                    block+=","
                index+=1
            block+= "\n{}{}".format((depth-1)*spaces,"}")
        return block

    @staticmethod
    def __unpack(obj):
        if isinstance(obj, dict):
            return {key: Parser.__unpack(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [Parser.__unpack(value) for value in obj]
        elif Parser.is_namedtuple(obj):
            return {key: Parser.__unpack(value) for key, value in obj._asdict().items()}
        elif isinstance(obj, tuple):
            return tuple(Parser.__unpack(value) for value in obj)
        else:
            return obj
