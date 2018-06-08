# -*- coding:utf-8 -*-

from __future__ import unicode_literals
import os,sys,time,re
from prettytable import PrettyTable
from mysqlcon import mysqlhelper
reload(sys)
sys.setdefaultencoding('utf8')

'''
统计信息：
1. 处理的客户总数，客户各种类型的数量
2. 记录有文档输出的事件总数，不同的数据库处理事件总数
3. 不同类型事件总数

新建归档目录和事件子目录
1. 判断该客户是否存在，否则新建
2. 新建该客户下的事件目录

保存至mysql中
将每一个客户事件记录保存至mysql数据库
设计表结构
id 客户名称 客户类型 事件发起时间 数据库类型 数据库载体 事件类别 事件简述
'''

class Statistical_customer_information():
    def __init__(self,path):
        self.path = path
        self.dba_user = raw_input('请输入姓名[yt\hjx\wyp]: ')

    def count_customer(self):
        "获取该路径下的所有目录，该目录的命名规则为“类型_客户名称”，且该目录下只有目录，可以不用判断"
        self.c_list = os.listdir(self.path)
        #print self.c_list
        # 客户总数
        self.c_num = len(self.c_list)
        return  self.c_num

    def get_customer(self):
        self.customer_list = []
        for i in self.c_list:
            self.customer_list.append(i.split('_')[1])
        return self.customer_list

    def count_case(self):
        """
        记录的事件总数
        """
        self.case_list = []
        self.client_case_list = []
        for client in self.c_list:
            #print client
            cpath = os.path.join(self.path,client)
            for i in os.listdir(cpath):
                self.client_case_list.append(client+'_'+i)
                #print self.client_case_list
                self.case_list.append(i)
        return len(self.case_list)

    def count(self,info,col):
        a_list = []
        a_dict = {}
        for i in info:
            try:
                a_list.append(i.split('_')[col])
            except IndexError:
                print i
        a_set = set(a_list)
        for i in a_set:
            num = a_list.count(i)
            a_dict[i] = num
        return  a_dict

    def count_customer_type(self):
        """有文档输出的事件总数"""
        return self.count(self.c_list,0)

    def count_day(self):
        """每日输出事件总数"""
        return self.count(self.case_list,0)

    def count_database(self):
        """有文档输出的事件总数"""
        return self.count(self.case_list,1)

    def count_case_info(self):
        """
        统计具体的数据库平台，自建还是云产品
        """
        return self.count(self.case_list, 2)

    def count_trouble_type(self):
        """
        统计不同的事件类型
        """
        return self.count(self.case_list, 3)

    def format_print(self,a,b,c):
        """将字典c以从大到小排序，并将结果以表格的方式打印"""
        x = PrettyTable([a, b])
        x.padding_width = 1
        for k, v in sorted(c.items(), key=lambda x: x[1], reverse=True):
            x.add_row([k, v])
        return x

    def choose(self,new_dict):
        key = 0
        str = '\n'
        for k,v in new_dict.iteritems():
            str = str + k + ' : ' + v + '\n'
        while True:
            if key in new_dict.keys():
                value = new_dict[key]
                break
            else:
                key= raw_input(
                    """请选择:{0}""".format(str)
                )
        return new_dict[key]





    def ana(self):
        now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        count_customer = self.count_customer()
        print("【有文档输出de事件统计】")
        print("1. 至 {0} 处理的客户总数 : {1}".format(now,count_customer))
        print self.format_print("客户类型", "数量",self.count_customer_type())
        print
        print("2. 有文档输出的事件总数 : {}\n".format(self.count_case()))

        case_day = self.count_day()
        case_day_sorted = sorted(case_day.items(), key=lambda x: x[1], reverse=True)
        for k,v in case_day_sorted:
            print("3. 每日文档最多输出事件统计：{} {}\n".format(k,v))
            break

        print("4. 数据库类型统计结果：")
        print self.format_print("数据库类型", "数量", self.count_database())

        print("5. 事件类型统计结果：")
        print self.format_print("事件类型", "数量", self.count_trouble_type())
        #print c.client_case_list




    def insert(self):
        now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        count_customer = self.count_customer()
        customer_list = self.get_customer()

        customer = raw_input("输入客户名称 : ")
        cus_type_dict = {'1':'免费版','2':'白金版','3':'大师版','4':'MSP'}
        ctype = self.choose(cus_type_dict)
        ctype_customer = '{0}_{1}'.format(ctype, customer)
        cpath = os.path.join(self.path, ctype_customer)
        print cpath
        print self.path
        if customer not in customer_list:
            # 新建目录ctype_customer，新建readme.md
            os.mkdir(cpath)
        else:
            print '【{}】该客户已存在'.format(customer)

        # 新建case事件记录 事件发起时间_数据库类型_数据库载体_事件类别_事件简述
        # #例如：2017-11-21_Redis_云Redis_产品咨询_产品推荐info
        case_database_type_dict = {
            '1': 'MySQL',
            '2': 'Redis',
            '3': 'MSSQL',
            '4': 'Mongodb',
            '5': 'Oracle',
            '6': 'PGSQL',
            '7': 'Hybirdb',
            '8': 'DRDS',
            '9': 'MyCat'
        }
        case_database_carrier_dict = {
            '1': 'RDS For MySQL',
            '2': 'RDS For MSSQL',
            '3': 'RDS For PGSQL',
            '4': '云Redis',
            '5': '云Mongodb',
            '6': 'ECS自建MySQL',
            '7': 'ECS自建Oracle',
            '8': 'ECS自建MSSQL',
            '9': 'ECS自建Redis',
            '10': 'ECS自建Mongodb',
            '11': 'IDC自建MySQL',
            '12': 'IDC自建Redis'
        }
        case_event_type_dict = {
            '1': '产品咨询',
            '2': '语法故障',
            '3': 'CPU故障',
            '4': '内存故障',
            '5': 'IO故障',
            '6': '磁盘故障',
            '7': '主从故障',
            '8': '锁故障',
            '9': '连接故障',
            '10': '密码破解',
            '11': '数据丢失',
            '12': '安装配置',
            '13': '备份恢复',
            '14': '架构设计',
            '15': 'SQL优化',
            '16': '迁移实施',
            '17': '数据库升级',
            '18': 'SQL追踪',
            '19': '数据库宕机',
            '20': '非数据库故障'
        }

        case_start_time = raw_input('事件发起时间【举例：2018-01-01】:')
        print '*数据库类型*'
        case_database_type = self.choose(case_database_type_dict)
        print '*数据库载体*'
        case_database_carrier = self.choose(case_database_carrier_dict)
        print '*事件类别*'
        case_event_type = self.choose(case_event_type_dict)
        case_event_info = raw_input('事件简述: ')

        case_info = '{0}_{1}_{2}_{3}_{4}'.format(case_start_time, case_database_type, case_database_carrier,
                                                 case_event_type, case_event_info)
        case_path = os.path.join(cpath, case_info)
        print case_path
        os.mkdir(case_path)


    def insert_mysql(self):
        """
        连接数据库，插入某个dba的事件记录，以覆盖的形式，即每次同步都是全量
        :return:
        """
        url, port, username, password, dbname = ("10.200.6.239", 3306, 'python', '(Uploo00king)', 'dba')
        mysql = mysqlhelper(url,port,username,password,dbname)
        dba = self.dba_user
        sql0 = """show tables;"""
        table_tuple = mysql.queryRow(sql0)
        # 如果表不存在则新建
        if table_tuple is None or 'technical_archiving' not in table_tuple:
            sql1 = """create table technical_archiving(
      id int primary key auto_increment,
      company varchar(50) not null comment '客户名称',
      company_type varchar(50) not null comment '客户类型',
      event_start_time datetime not null comment '事件发起时间',
      case_database_type varchar(50) not null comment '数据库类型',
      case_database_carrier varchar(50) not null comment '数据库载体',
      case_event_type varchar(50) not null comment '事件类别',
      case_event_info varchar(50) not null comment '事件简述',
      dba varchar(50) not null comment 'DBA',
      update_time timestamp not null default CURRENT_TIMESTAMP comment '更新时间')
      charset utf8
      comment '事件归档表';"""
            mysql.query(sql1)

        # 覆盖该用户的所有事件记录
        ## 先删除
        sql2 = """
        delete from technical_archiving where dba = '{0}';
        """.format(dba)
        mysql.query(sql2)
        mysql.commit()

        ## 后添加
        self.count_customer()
        self.count_case()
        for client_case in self.client_case_list:
            #print client_case
            client_case_each_list = client_case.split('_')
            company = client_case_each_list[1]
            company_type = client_case_each_list[0]
            event_start_time = client_case_each_list[2]
            case_database_type = client_case_each_list[3]
            case_database_carrier = client_case_each_list[4]
            case_event_type  = client_case_each_list[5]
            case_event_info = client_case_each_list[6]
            sql3 = """
            insert into  technical_archiving values (null,'{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}',now());
            """.format(company,company_type,event_start_time,case_database_type,case_database_carrier,case_event_type,case_event_info,dba)
            mysql.query(sql3)
        mysql.commit()

    def ana_high(self):
        url, port, username, password, dbname = ("10.200.6.239", 3306, 'python', '(Uploo00king)', 'dba')
        mysql = mysqlhelper(url,port,username,password,dbname)
        dba = self.dba_user
        # 1. 指定时间范围内的事件数统计
        start_time = raw_input('统计的起始时间【2017-01-01】: ')
        end_time = raw_input('统计的结束时间【2017-09-01】: ')
        re_date = r"^\d{4}-\d{2}-\d{2}$"
        while True:
            if re.match(re_date,start_time) and re.match(re_date,end_time):
                break
            else:
                print "Error:时间格式输入错误，请重新输入"
                start_time = raw_input('统计的起始时间【2017-01-01】: ')
                end_time = raw_input('统计的结束时间【2017-09-01】: ')

        sql = """select count(*) from technical_archiving where dba = '{0}' and 
        event_start_time BETWEEN '{1}' and '{2}' ;""".format(dba,start_time,end_time)
        count_case = mysql.queryRow(sql)[0]

        print("1. 从 {0} 至 {1} 处理的事件总数 : {2}".format(start_time,end_time,count_case))






if __name__ == "__main__":
    # 客户case存放路径
    path = 'C:\\Users\\rgwei\\Desktop\\公司格式文档\\客户支持\\解决方案\\CLIENT\\客户事件归档'
    c = Statistical_customer_information(path)
    while True:
        if input == 'f':
            c.ana()
            break
        elif input == 'i':
            c.insert()
            break
        elif input == 'fi':
            c.ana()
            c.insert()
            break
        else:
            input = raw_input('保持归档分析的好习惯，棒棒哒^.^~  小主，你现在选【f 基础分析】还是【i 新增】呢？(f/i): ')

    while True:
        input2 = raw_input('是否继续【新增】呢？(y/n): ')
        if input2 == 'n':
            break
        else:
            c.insert()
    input3 = raw_input('是否需要同步至数据库【sync】呢？(y/n): ')
    if input3 == 'y' :
        c.insert_mysql()
        input4 = raw_input('现在可以做高级分析，是否开始(y/n):')
        if input4 == 'y':
            c.ana_high()




