#coding=utf-8

import time
import pymysql



class  MyMySQL:

    def __init__(self, host, port, user, pwd, db, charset):
        self.host= host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.charset = charset

    def select(self,sql):
        # 耗时计时开始
        start = time.perf_counter()
        # 建立数据库连接
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            connect_timeout=1000,
            charset=self.charset
            )
        # 获取游标
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 执行sql语句
        rows = cursor.execute(sql)
        data_list = cursor.fetchmany(rows)
        # 关闭游标
        cursor.close()

        # 关闭连接
        conn.close()
        # 统计耗时
        stop = time.perf_counter()
        elapse = str(stop - start)[:6]
        print('>>> select  elapse %s s, sql=%s' % (elapse, sql) )
        if data_list is not None and len(data_list) == 0:
            if isinstance(data_list, tuple):
                data_list = []
        return data_list

    def insert(self, sql):
        # 建立数据库连接
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            connect_timeout=100,
            charset=self.charset
        )
        # 获取游标
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 执行sql语句
        ret = cursor.execute(sql)
        conn.commit()
        # 关闭游标
        cursor.close()

        # 关闭连接
        conn.close()

        return ret

    def update(self, sql):
        # 建立数据库连接
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            connect_timeout=100,
            charset=self.charset
        )
        # 获取游标
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 执行sql语句
        ret = cursor.execute(sql)
        conn.commit()
        # 关闭游标
        cursor.close()

        # 关闭连接
        conn.close()

        return ret

    def execute(self, sql, data):
        # 建立数据库连接
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            connect_timeout=100,
            charset=self.charset
        )
        # 获取游标
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 执行sql语句
        ret = cursor.execute(sql, data)
        conn.commit()
        # 关闭游标
        cursor.close()

        # 关闭连接
        conn.close()

        return ret


    def executemany(self, sql, data):
        # 建立数据库连接
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pwd,
            db=self.db,
            connect_timeout=100,
            charset=self.charset
        )
        # 获取游标
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 执行sql语句
        ret = cursor.executemany(sql, data)
        conn.commit()
        # 关闭游标
        cursor.close()

        # 关闭连接
        conn.close()

        return ret

    def insert_table(self, tablename, params):
        """插入数据库

            args：
                tablename  ：表名字
                key        ：属性键
                value      ：属性值
        """
        key_list = []
        value_list = []
        for tmp_key, tmp_value in params.items():
            if tmp_value is None:
                tmp_value = ''
            key_list.append(tmp_key)
            if isinstance(tmp_value, str):
                value_list.append("\'" + tmp_value + "\'")
            else:
                value_list.append(str(tmp_value))
        attrs_sql = '('+','.join(key_list)+')'
        values_sql = ' values('+','.join(value_list)+')'
        sql = 'insert into %s' % tablename
        sql = sql + attrs_sql + values_sql
        return self.insert(sql)

    def insert_table_list(self, tablename, mysql_list):
        """插入数据库

            args：
                tablename  ：表名字
                key        ：属性键
                value      ：属性值
        """
        params = mysql_list[0]
        key = []
        for tmpkey, tmpvalue in params.items():
            key.append(tmpkey)
        attrs_sql = '('+','.join(key)+')'
        values_sql = ''
        for i in range(len(mysql_list)):
            values_sql += '('
            times = 0
            for tmpvalue in mysql_list[i].values():
                if isinstance(tmpvalue, str):
                    if times==0:
                        values_sql += "\'" + tmpvalue + "\'"
                    else:
                        values_sql += ",\'" + tmpvalue + "\'"
                else:
                    if times == 0:
                        values_sql += tmpvalue
                    else:
                        values_sql += ','+tmpvalue
                times = times + 1
            if i == len(mysql_list)-1:
                values_sql += ')'
            else:
                values_sql += '),'

        sql = 'insert into %s'%tablename
        sql = sql + attrs_sql +' values '+ values_sql
        return self.insert(sql)

    def update_table(self, tablename, attrs_dict, cond_dict):
        """更新数据

            args：
                tablename  ：表名字
                attrs_dict  ：更新属性键值对字典
                cond_dict  ：更新条件字典

            example：
                params = {"name" : "caixinglong", "age" : "38"}
                cond_dict = {"name" : "liuqiao", "age" : "18"}
                mydb.update(table, params, cond_dict)

        """
        attrs_list = []
        consql = ' '
        for tmp_key, tmp_value in attrs_dict.items():
            if tmp_value is None:
                tmp_value = ''
            if isinstance(tmp_value, str):
                attrs_list.append(f"`{tmp_key}`='{tmp_value}'")
            else:
                attrs_list.append(f"`{tmp_key}`={tmp_value}")
        attrs_sql = ",".join(attrs_list)
        if cond_dict!='':
            for key, value in cond_dict.items():
                if isinstance(value, int):
                    consql = consql + "`" + key + "`" + '=' + str(value) + ' and '
                else:
                    consql = consql + "`" + key + "`" + '="' + str(value) + '" and '
        consql = consql + ' 1=1 '
        sql = "UPDATE %s SET %s where%s" % (tablename, attrs_sql, consql)
        return self.update(sql)


if __name__ == '__main__':
    host = 'localhost'
    port = 3306
    user = 'user'
    pwd = 'password'
    db = 'database'
    charset = 'utf8'

    my_mysql = MyMySQL(host, port, user, pwd, db, charset)

    sql = "select * from record"
    json = my_mysql.select(sql)
    print(json)


    sql = "update record set succeed_count='%s' where id=1" % (1000)
    ret = my_mysql.update(sql)
    print(ret)
