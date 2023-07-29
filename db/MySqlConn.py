# -*- coding: UTF-8 -*-
"""
1. When executing SQL with parameters, please use the SQL statement to specify the list of conditions that need to be input, and then use tuple/list for condition batching
2. In the format SQL, there is no need to use quotation marks to specify the data type, the system will automatically identify it according to the input parameters
3. There is no need to use the conversion function in the input value, the system will handle it automatically
"""

import pymysql
from pymysqlpool.pooled_db import PooledDB
# from dbutils.pooled_db import PooledDB
from config import config


class Mysql(object):
    """
     The MYSQL database object is responsible for generating database connections, and the connection in this class uses
     the connection pool to obtain the connection object:
     conn = Mysql.getConn()
    Release the connection object; conn.close() or del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self):
        self._conn = Mysql.__getConn()
        self._cursor = self._conn.cursor(pymysql.cursors.DictCursor)

    @staticmethod
    def __getConn():
        """
        @summary: Static method, take out the connection from the connection pool
        @return MySQLdb.connection
        """
        if Mysql.__pool is None:
            __pool = PooledDB(
                              # creator=pymysql,
                              max_connections=60,
                              # set_session=["set global time_zone = '+8:00'", "set time_zone = '+8:00'"],  # 开始会话前执行的命令列表。
                              ping=0,  # ping MySQL服务端，检查是否服务可用。
                              host=config["MYSQL"]["DBHOST"],
                              port=config["MYSQL"]["DBPORT"],
                              user=config["MYSQL"]["DBUSER"],
                              password=config["MYSQL"]["DBPWD"],
                              database=config["MYSQL"]["DBNAME"],
                              charset=config["MYSQL"]["DBCHAR"])

        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: Execute the query and fetch all result sets
        @param sql: query SQL, if there is a query condition, please only specify the condition list, and pass the condition value using the parameter [param]
        @param param: optional parameter, conditional list value (tuple/list)
        @return: result list (dictionary object)/boolean query result set
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False

        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self, sql, value=None):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql, value)
        return self.__getInsertId()

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        print(result)
        return result[0]["id"]

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()
