# coding=utf-8
from DBUtils.PooledDB import PooledDB
from mysql.connector import FieldType
import MySQLdb
import pymssql
import cx_Oracle
from config_reader import ConfigReader
import sys
import os

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class Database(object):
    config = None
    conn = None
    pool = None
    dbtype = None

    def __init__(self, dbtype):
        try:
            self.config = ConfigReader.db_cfgreader(dbtype)
            config = self.config
            self.dbtype = dbtype

            if dbtype == 'mysql': # mysql
                self.pool = PooledDB(
                    creator=MySQLdb,
                    maxusage=config['maxusage'],
                    mincached=config['mincached'],
                    maxcached=config['maxcached'],
                    db=config['schema'],
                    host=config['host'],
                    user=config['user'],
                    passwd=config['passwd'],
                    charset=config['charset'],
                    port=config['port'])
            elif dbtype == 'mssql': # sql server
                self.pool = PooledDB(
                    creator=pymssql,
                    maxusage=config['maxusage'],
                    mincached=config['mincached'],
                    maxcached=config['maxcached'],
                    database=config['schema'],
                    host=config['host'],
                    user=config['user'],
                    password=config['passwd'],
                    charset=config['charset'],
                    port=config['port'])
            elif dbtype == 'oracle': #oracle
                self.pool = PooledDB(
                        creator=cx_Oracle,
                        maxusage=config['maxusage'],
                        mincached=config['mincached'],
                        maxcached=config['maxcached'],
                        user=config['user'],
                        password=config['passwd'],
                        dsn="%s:%s/%s" % (config['host'], config['port'], config['schema']))

            self.conn = self.pool.connection()

        except Exception, e:
            print '[Fatal Error from Database.__init__]:', e
            sys.exit(1)

    def execute_sql(self, sql_str):
        result = []
        if self.conn is None:
            return None
        sql = sql_str.lower()

        cur = self.conn.cursor()

        try:
            cur.execute(sql)
            descr = cur.description

            # # 将res中的字段名统一转换为小写
            # for res in cur.fetchall():
            #     res_low = {}
            #     for item in res.items():
            #         res_low[item[0].lower()] = item[1]
            #     result.append(res_low)

            # 将res中的字段名统一转换为小写，并将结果的行值类型从tuple改为dict返回
            for row in cur.fetchall():
                dictrow = {}
                for i in range(len(row)):
                    data = row[i]
                    if type(data).__name__=='str':
                        data = Database.convert_to_utf8(data)
                    dictrow[descr[i][0].lower()] = data
                result.append(dictrow)

        except Exception, e:
            print '[Fatal Error from Database.execSQL]', e
            sys.exit(1)
        finally:
            cur.close()

        return result, descr

    def get_view_data_set(self, view_name):

        # 如果数据量太大的话，会导致查询数据的时候，系统卡死，所以根据配置文件中的行数限制，重新组装sql
        if self.dbtype=='mysql':
            sql = 'select * from {} limit {}'.format(view_name, self.config['maxreadcount'])
        elif self.dbtype=='oracle':
            sql = 'select * from {} where rownum < {}'.format(view_name, self.config['maxreadcount'])
        elif self.dbtype=='mssql':
            sql = 'select top {} * from {}'.format(self.config['maxreadcount'], view_name)


        dataset, descr = self.execute_sql(sql)
        return dataset, descr

    @staticmethod
    def convert_to_utf8(str):
        if type(str).__name__ != "unicode":
            return unicode(str, "utf-8")
        else:
            return str
    @staticmethod
    def convert_to_gb2312(str):
        if isinstance(str, unicode):
            print str.encode('gb2312')
        else:
            print str.decode('utf-8').encode('gb2312')

    oracle_field_map = {
        cx_Oracle.STRING: 'VAR_STRING',
        cx_Oracle.FIXED_CHAR: 'VAR_STRING',
        cx_Oracle.TIMESTAMP: 'TIMESTAMP',
        cx_Oracle.NUMBER: 'DOUBLE',
        cx_Oracle.DATETIME: 'DATETIME'
    }

    def fieldmap(self, field_type_section):
        if self.dbtype == 'mysql':
            return FieldType.get_info(field_type_section)
        elif self.dbtype == 'oracle':
            return self.oracle_field_map[field_type_section]
        else:
            raise Exception('Database.fieldmap(): param {} not support'.format(field_type_section))

    def is_string(self, field_type_section):
            return self.fieldmap(field_type_section) in ('VAR_STRING', 'STRING', 'VARCHAR')

    def is_unique_field(self, view_name, field_name):
        return self.is_fields_index_effective(view_name, field_name)

    def is_fields_index_effective(self, view_name, index_fields):
        # 如果数据量太大的话，会导致查询数据的时候，系统卡死，所以根据配置文件中的行数限制组装sql
        if self.dbtype=='mysql':
            sql = 'select count(1) cnt from (select count(1) c from %s group by %s limit %d) t where t.c>1' % (
                view_name, index_fields, self.config['maxreadcount'])
        elif self.dbtype=='oracle':
            sql = 'select count(1) cnt from (select count(1) c from %s where rownum < %d group by %s) t where t.c>1' %(
                view_name, self.config['maxreadcount'], index_fields)
        elif self.dbtype=='mssql':
            sql = 'select count(1) cnt from (select top %d count(1) c from %s group by %s) t where t.c>1' %(
                self.config['maxreadcount'], view_name, index_fields)

        ds, none = self.execute_sql(sql)
        return ds[0]['cnt'] == 0


if __name__ == "__main__":
    db = Database('mssql')
    re = db.get_view_data_set('his_patient')
    print re
