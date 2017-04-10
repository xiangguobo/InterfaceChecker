****
1、安装python2.7
并且用到python的几个模块，mysql-connector, mysql-python, pymssql, cx_Oracle，请自行安装

2、修改ini下面的config.ini配置文件
根据数据库类型修改对应的参数，其中重点要注意maxreadcount，别设置太大了把HIS数据库给搞崩了

3、命令行的用法（有数据库类型和视图名称列表两个参数）：

E:\xianggb_dev\InterfaceChecker>python __main__.py -h
usage: __main__.py [-h] [-v] [-t [mysql|oracle]] [view_list [view_list ...]]

interface check command tool (for ipharmacare3.0/3.2 dp interface)

positional arguments:
  view_list          the view(s) to be checked

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -t [mysql|oracle]  the view database type, can be mysql or oracle(default is
                     oracle)

E:\xianggb_dev\InterfaceChecker>python __main__.py -t mysql base_product opt_recipe
2017-03-19 02:04:33 view base_product check start...
Warning: view base_product field [content_spec] type VAR_STRING not match with config DOUBLE
Warning: view base_product field [count_unit] type VAR_STRING not match with config DOUBLE
Warning: view base_product field [antibacterial] type VAR_STRING not match with config LONG
Warning: view base_product field [essential_drug] type VAR_STRING not match with config LONG
Error: view base_product field [producer_id] must have data, but have 103 rows no this field data
Error: view base_product field [producter_name] must have data, but have 103 rows no this field data
Error: view base_product field [specification] must have data, but have 615 rows no this field data
Error: view base_product field [preparation] must have data, but have 103 rows no this field data
Error: view base_product field [antibacterial] must have data, but have 210 rows no this field data
Error: view base_product field [essential_drug] must have data, but have 194 rows no this field data
Error: view base_product field [drug_id] is config unique but actually have duplicate values
2017-03-19 02:04:33 view base_product check result finish... result is Fail
2017-03-19 02:04:33 view opt_recipe check start...
Warning: view opt_recipe field [recipe_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe field [check_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe field [prep_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe field [despensing_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe field [fee_taken_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe field [recipe_fee_total] type VAR_STRING not match with config DOUBLE
Warning: view opt_recipe field [last_modify_time] type VAR_STRING not match with config DATETIME
Error: view opt_recipe field [hospital_diag_code] must have data, but have 1000 rows no this field data
Error: view opt_recipe field [icd_code] must have data, but have 1000 rows no this field data
Error: view opt_recipe field [hospital_diag_name] must have data, but have 2 rows no this field data
Error: view opt_recipe field [recipe_status] must have data, but have 1000 rows no this field data
Error: view opt_recipe field [recipe_category] must have data, but have 1000 rows no this field data
Error: view opt_recipe field [recipe_doc_title] must have data, but have 167 rows no this field data
Error: view opt_recipe field [herb_packet_count] must have data, but have 918 rows no this field data
Error: in view opt_recipe, 1000 rows len([recipe_time]) > config length 0
Error: in view opt_recipe, 1000 rows len([last_modify_time]) > config length 0
Error: view opt_recipe field [recipe_id] is config unique but actually have duplicate values
Error: view opt_recipe field [recipe_no] is config unique but actually have duplicate values
2017-03-19 02:04:35 view opt_recipe check result finish... result is Fail

E:\xianggb_dev\InterfaceChecker>python __main__.py -t oracle opt_recipe_drug
2017-03-19 02:05:00 view opt_recipe_drug check start...
Warning: view opt_recipe_drug field [start_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe_drug field [end_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe_drug field [approval_time] type VAR_STRING not match with config DATETIME
Warning: view opt_recipe_drug field [skin_test_flag] type VAR_STRING not match with config LONG
Warning: view opt_recipe_drug field [cancel_flag] type DOUBLE not match with config LONG
Error: view opt_recipe_drug field [producer_id] must have data, but have 99 rows no this field data
Error: view opt_recipe_drug field [drug_using_freq] must have data, but have 32 rows no this field data
Error: view opt_recipe_drug field [preparation_name] must have data, but have 44 rows no this field data
Error: view opt_recipe_drug field [recipe_item_id] is config unique but actually have duplicate values
2017-03-19 02:05:51 view opt_recipe_drug check result finish... result is Fail

E:\xianggb_dev\InterfaceChecker>
