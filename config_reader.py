# coding=utf-8

import ConfigParser
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ConfigReader(object):
    """
    读取配置文件
    """
    dbconfig = None
    viewconfigs = None

    @classmethod
    def db_cfgreader(cls, dbtype):
        parser = ConfigParser.ConfigParser()
        file_path = os.path.join(os.path.dirname(__file__) + '/ini/config.ini')
        if parser.read(file_path) == []:
            print 'Fatal Error: conf file {} not exitst'.format(file_path)
            exit(1)

        type = dbtype
        cls.dbconfig = {
            'type': type,
            'host': parser.get(type, 'host'),
            'port':parser.getint(type, 'port'),
            'user':parser.get(type, 'user'),
            'passwd':parser.get(type, 'passwd'),
            'schema':parser.get(type, 'schema'),
            'maxreadcount':parser.getint(type, 'maxreadcount'),
            'maxusage':parser.getint(type, 'maxusage'),
            'mincached':parser.getint(type, 'mincached'),
            'maxcached':parser.getint(type, 'maxcached'),
            'charset': parser.get(type, 'charset'),
            'thread':parser.getint(type, 'thread'),
            'processor':parser.getint(type, 'processor')
        }
        return cls.dbconfig

    @classmethod
    def view_cfgreader(cls, view_name):
        parser = ConfigParser.ConfigParser()
        file_path = os.path.join(os.path.dirname(__file__) + '/ini/{}.ini'.format(view_name))
        if parser.read(file_path) == []:
            print 'Fatal Error: config file {} not exists'.format(file_path)
            sys.exit(1)

        columns = parser.get('columns', 'columns')
        index = parser.get('columns', 'index')
        fields = []
        for field_name in columns.split(','):
            field = {
                'field_name': field_name,
                'cn_name': parser.get(field_name, 'cn_name'),
                'required': parser.getint(field_name, 'required'),
                'field_type': parser.get(field_name, 'field_type'),
                'max_length': parser.getint(field_name, 'max_length'),
                'uniqueness': parser.getint(field_name, 'uniqueness'),
                'allowed_value': parser.get(field_name, 'allowed_value')
            }
            fields.append(field)

        viewconfig = {
            'view_name': view_name,
            'columns': columns,
            'index': index,
            'fields': fields
        }
        return viewconfig

    @classmethod
    def views_cfgreader(cls, views):
        cls.viewconfigs = []
        for view in views:
            viewconfig = cls.view_cfgreader(view)
            cls.viewconfigs.append(viewconfig)
        return cls.viewconfigs

    @staticmethod
    def is_value_allowed(value, allowed_value):
        if allowed_value == 'all':
            return True
        else:
            return str(value) in allowed_value.decode('utf-8').split(',')


if __name__ == "__main__":
    fc = ConfigReader.view_cfgreader('opt_recipe')
    for field in fc['fields']:
        print field['allowed_value']
