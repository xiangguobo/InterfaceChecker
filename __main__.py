# coding=utf-8
from view_checker import ViewChecker
from config_reader import ConfigReader
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="interface check command tool (for ipharmacare3.0/3.2 dp interface)", version='0.9')
    parser.add_argument('view_list', nargs='*',
                        help='the view(s) to be checked')
    parser.add_argument('-t', metavar='mysql|oracle',dest='dbtype', nargs='?', default='oracle',
                        help='the view database type, can be mysql or oracle(default is oracle)')
    viewlist = parser.parse_args().view_list
    dbtype = parser.parse_args().dbtype
    if len(viewlist) == 0:
        viewlist = []


    viewconfigs = ConfigReader.views_cfgreader(viewlist)
    for view in viewconfigs:
        vc = ViewChecker(view,dbtype)
        vc.do_check()