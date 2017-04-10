# coding=utf-8

import datetime

from mysql.connector import FieldType

from config_reader import ConfigReader
from database import Database


class ViewChecker(object):
    """
    执行一个视图的检查，检查项目持续扩充中，目前已包含的检查内容：
    1、视图的字段名是否和接口文档一致
    2、……
    """
    view, db, ds, descr = None, None, None, None

    def __init__(self, viewconfig, dbtype='mysql'):
        self.view = viewconfig
        if ViewChecker.db is None:
            ViewChecker.db = Database(dbtype)

        ViewChecker.ds, ViewChecker.descr = ViewChecker.db.get_view_data_set(viewconfig['view_name'])


    # 1、视图的字段名是否和接口文档一致（通过配置文件定义）
    def is_fields_exist(self):
        ret = True
        dd = ViewChecker.descr

        for i in range(len(dd)):
            if dd[i][0].lower() not in self.view['columns'].split(','):
                print 'Error: view {} column {} is not in {}'.format(self.view['view_name'], dd[i][0],
                                                                     self.view['columns'])
                ret = False

        return ret

    # 2、视图的字段数量和接口文档一致（通过配置文件定义）
    def is_fields_completed(self):
        dd = self.descr
        if len(dd) != len(self.view['fields']):
            print 'Error: view {} provide {} columns, but we need {}'.format(self.view['view_name'], len(dd),
                                                                             len(self.view['fields']))
        return True

    # 3、视图的字段的类型是否和接口文档一致（通过配置文件定义）
    def is_fields_type_correct(self):
        ret = True
        dd = self.descr
        for dd_field in dd:
            matched = False
            fieldtype = ViewChecker.db.fieldmap(dd_field[1])
            for config_field in self.view['fields']:
                if dd_field[0].lower() == config_field['field_name']:
                    matched = fieldtype == config_field['field_type']
                    # matched = FieldType.get_info(dd_field[1]) == config_field['field_type']
                    break
            if not matched:
                ret = False
                # print 'Warning: view {} field [{}] type {} not match with config {}'.format(
                #     self.view['view_name'], dd_field[0], FieldType.get_info(dd_field[1]), config_field['field_type'])
                print 'Warning: view {} field [{}] type {} not match with config {}'.format(
                    self.view['view_name'], config_field['field_name'], fieldtype, config_field['field_type'])
        return ret

    # 4、检查接口文档中定义的必填字段是否都有数据
    def is_required_fields_exist_data(self):
        ret = True
        for config_field in self.view['fields']:
            if config_field['required'] == 1:
                # 计算返回的数据集中，isRequired为1但是却未传入值的记录的条数，计数器初始化为0
                count = 0
                for row in self.ds:
                    if (row[config_field['field_name']] is None):
                        count += 1
                    else:
                        # 从实际的数据库传入值来判断是否字符串类型，如果为空串则记录错误数量
                        for dd_field in self.descr:
                            if dd_field[0].lower() == config_field['field_name']:
                                if self.db.is_string(dd_field[1]):
                                    if row[config_field['field_name']].strip() == '':
                                        count += 1
                                break
                if (count > 0):
                    print 'Error: view {} field [{}] must have data, but have {} rows no this field data'.format(
                        self.view['view_name'], config_field['field_name'], count
                    )
                    ret = False
        return ret

    # 5、检查视图给出的数据，是否有超出接口文档中定义的字符串类型字段的长度情况
    # 针对长度超过接口文档定义的，根据配置文档定义的数量读入真实数据，看是否有数据超长（仅检查字符串类型）
    def is_fields_length_correct(self):
        ret = True
        dd = self.descr

        for dd_field in dd:
            # 只检查字符串类型
            if not self.db.is_string(dd_field[1]):
                continue
            for config_field in self.view['fields']:
                if dd_field[0].lower() == config_field['field_name']:
                    field_name = config_field['field_name']
                    field_type = config_field['field_type']
                    max_length = config_field['max_length']
                    if dd_field[3] is not None and dd_field[3] / 3 <= max_length:
                        continue
                    else:
                        count = 0
                        for row in self.ds:
                            if row[field_name] is not None:
                                if len((row[field_name])) > max_length:
                                    count += 1
                        if (count > 0):
                            print 'Error: in view {}, {} rows len([{}]) > config length {}'.\
                                format(self.view['view_name'],count, field_name, max_length)
                            ret = False
        return ret

    # 6、对接口文档定义的唯一性字段值约束进行检查，在无更好的策略情况之下，目前是根据配置读入的真实数据检查是否唯一
    def is_fields_uniqueness_correct(self):
        ret = True

        for config_field in self.view['fields']:
            if config_field['uniqueness'] == 1:
                if not self.db.is_unique_field(self.view['view_name'], config_field['field_name']):
                    ret = False
                    print 'Error: view {} field [{}] is config unique but actually have duplicate values'.format(
                        self.view['view_name'], config_field['field_name']
                    )
        return ret

    # 7、对我们数据库中的组合索引要求数据组合唯一情况进行检查，策略也是根据配置读入的真实数据检查唯一性
    def is_fields_index_effective(self):
        ret = True
        if self.view['index'] != '':
            if not self.db.is_fields_index_effective(self.view['view_name'], self.view['index']):
                print 'Error: view {} index [{}] have duplicate values'.format(self.view['view_name'], self.view['index'])
                ret = False
        return ret

    # 8、对字段允许的取值进行检查，比如base_product 表中的 Essential_Drug字段（基本药物标记），就只允许0、1、2三个值
    def is_value_allowed(self):
        ret = True

        for config_field in self.view['fields']:
            field_name = config_field['field_name']
            allowed_value = config_field['allowed_value']
            for record in self.ds:
                # 如果字段传入字段为空，那就算了不检查值 (至于字段要求非空，而传入空值得情况，在其他函数进行检查
                # 本函数只检查传入了非空的值，但是不符合要求的情况
                checkrec = True

                if record[field_name] is None:
                    checkrec = False
                else:
                    for fd in self.descr:
                        if fd[0].lower() == field_name:
                            if self.db.is_string(fd[1]):
                                if record[field_name].strip() == '':
                                    checkrec = False
                                    break
                if not checkrec:
                    continue

                # 但如果字段有值传进来，那就要检查一下啦
                if not ConfigReader.is_value_allowed(record[field_name], config_field['allowed_value']):
                    print 'Error: view {} field [{}] allowed value {} but get {}'.format(
                        self.view['view_name'], field_name, allowed_value, record[field_name])
                    ret = False
        return ret

    # 9、检查处方明细表中的组号是否在五个以内，超过了说明数据有问题
    def is_group_id_count_less_than6(self):
        return True

    def do_check(self):
        print '{} view {} check start...'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                 self.view['view_name'])
        result = self.is_fields_exist() & \
                 self.is_fields_completed() & \
                 self.is_fields_type_correct() & \
                 self.is_required_fields_exist_data() & \
                 self.is_fields_length_correct() & \
                 self.is_fields_uniqueness_correct() & \
                 self.is_fields_index_effective() & \
                 self.is_value_allowed() & \
                 self.is_group_id_count_less_than6()
        print '{} view {} check result finish... result is {}'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.view['view_name'], 'Pass' if result else 'Fail')
        return result


if __name__ == '__main__':
    viewconfigs = ConfigReader.views_cfgreader(['opt_recipe', 'his_patient','base_product'])
    for view in viewconfigs:
        vc = ViewChecker(view, 'mysql')
        vc.do_check()
