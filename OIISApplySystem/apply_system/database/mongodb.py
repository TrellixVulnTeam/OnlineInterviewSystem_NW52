# coding=utf-8
# author: Lan_zhijiang
# description: mongodb操作器
# date: 2022/4/9

import pymongo
import sys


class MongoDBManipulator:

    def __init__(self, addr, port, user, pw):

        self.database_names_list = []
        self.collection_names_list = {}

        self.server = pymongo.MongoClient(
            host=addr, port=port,
            username=user, password=pw, authSource="admin"
        )
        self.get_database_names_list()

    def add_database(self, db_name):

        """
        添加数据库
        :param db_name: 数据库名
        :return: bool
        """
        print("MongoDB: try add database-%s " % db_name)
        try:
            self.server[db_name]
        except:
            return False
        else:
            self.get_database_names_list()
            return True

    def add_collection(self, db_name, coll_name):

        """
        创建集合
        :param coll_name: 集合名称
        :param db_name: 该集合要插入到的数据库
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            print("MongoDB: add coll-%s into db-%s failed" % (coll_name, db_name))
            return False
        else:
            self.get_collection_names_list(db_name)
            print("MongoDB: add coll-%s into db-%s successfully" % (coll_name, db_name))
            return True

    def delete_collection(self, db_name, coll_name):

        """
        删除集合
        :param db_name: 集合所在的数据库名
        :param coll_name: 要删除的集合名
        :return: bool
        """
        try:
            db = self.server[db_name]
            db[coll_name].drop()
        except:
            print("MongoDB: delete coll-%s from db-%s failed" % (coll_name, db_name))
            return False
        else:
            self.get_collection_names_list(db_name)
            print("MongoDB: delete coll-%s from db-%s successfully" % (coll_name, db_name))
            return True

    def get_database_names_list(self):

        """
        获取所有数据库名称
        :return: list
        """
        self.database_names_list = self.server.list_database_names()
        print("MongoDB: database_names_list has been updated")
        return self.database_names_list

    def get_collection_names_list(self, db_name):

        """
        获取某个数据库中所有集合名称
        :param db_name: 数据库名称
        :return:
        """
        db = self.server[db_name]

        self.collection_names_list[db_name] = db.list_collection_names()
        print("MongoDB: collection_names_list has been updated")
        return self.collection_names_list[db_name]

    def is_database_exist(self, name, update=False):

        """
        判断某个数据库是否存在
        :param name: 数据表名称
        :param update: 是否更新
        :return: bool
        """
        if update or self.database_names_list is None:
            self.get_database_names_list()

        if name in self.database_names_list:
            print("MongoDB: database-%s" % name + " exist")
            return True
        else:
            print("MongoDB: db_exist?: second time search start")
            self.get_database_names_list()
            if name in self.database_names_list:
                print("MongoDB: db-%s exist" % name)
                return True
            else:
                print("MongoDB: db-%s does not exist" % name)
                return False

    def is_collection_exist(self, db_name, coll_name, update=False):

        """
        判断某个集合是否存在
        :param db_name: 数据库名称
        :param coll_name: 要查询的集合的名称
        :param update: 是否更新
        :return:
        """
        if update or self.collection_names_list is None:
            self.get_collection_names_list(db_name)

        try:
            if coll_name in self.collection_names_list[db_name]:
                print("MongoDB: collection-%s" % coll_name + " exist")
                return True
        finally:
            print("MongoDB: coll_exist?: second time search start")
            self.get_collection_names_list(db_name)
            if coll_name in self.collection_names_list[db_name]:
                print("MongoDB: collection-%s exist" % coll_name)
                return True
            else:
                print("MongoDB: collection-%s does not exist" % coll_name)
                return False

    def add_one_document(self, db_name, coll_name, docu):

        """
        添加单个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param docu: 要插入的文档内容 dict
        :return: False or class
        """
        try:
            db = self.server[db_name]
        except:
            print("MongoDB: no database named " + db_name + " or something else wrong")
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                print("MongoDB: no collection named " + coll_name + " or something else wrong")
                return False
            else:
                try:
                    result = coll.insert_one(docu)
                except:
                    print("MongoDB: add one document failed")
                    return False
                else:
                    print("MongoDB: add one document successfully")
                    return result

    def add_many_documents(self, db_name, coll_name, docu_s):

        """
        添加多个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param docu_s: 要插入的文档内容 list[dict, dict]
        :return: False or class
        """
        try:
            db = self.server[db_name]
        except:
            print("MongoDB: no database named " + db_name + " or something else wrong")
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                print("MongoDB: no collection named " + coll_name + " or something else wrong")
                return False
            else:
                try:
                    result = coll.insert_many(docu_s)
                except:
                    print("MongoDB: add many document fail")
                    return False
                else:
                    print("MongoDB: add many document success")
                    return result

    def get_document(self, db_name, coll_name, query=None, mode=0):

        """
        获取某集合中的数据
        :type query: dict
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 查找关键词，不指定则返回全部数据
        :param mode: 查找模式 0: 全部 1: key 2: key的值
        :return: False/dict
        """
        try:
            print("MongoDB: try to get document from " + db_name + "/" + coll_name)
        except TypeError:
            coll_name = ""
        if query is None:
            query = {}
        if type(query) is dict:
            try:
                db = self.server[db_name]
                coll = db[coll_name]
            except:
                print("MongoDB: get one document: something wrong")
                return False
            else:
                try:
                    if mode == 0:
                        result = coll.find()
                    elif mode == 1:
                        result = coll.find(query)
                    elif mode == 2:
                        result = coll.find({}, query)
                    else:
                        print("MongoDB: mode error!")
                        return False
                except:
                    print("MongoDB: get document failed")
                    return False
                else:
                    return list(result)
        else:
            print("MongoDB: get one document: param query must be a dict")
            return False

    def parse_document_result(self, documents, targets, debug=True):

        """
        解析搜索到的文档结果(返回包含targets中任一一个的document)
        :param documents: 查找结果
        :param targets: 查找目标
        :param debug: 是否输出哪些keys没有被找到
        :type documents: list
        :type target: list
        :return:
        """
        print("MongoDB: parsing the documents, targets: " + str(targets))
        result = []
        found_targets = []
        can_not_find_targets = []
        for target in targets:
            for document in documents:
                if target in document:
                    result.append(document)
                    found_targets.append(target)
            if target not in found_targets:
                can_not_find_targets.append(target)

        if can_not_find_targets:
            print("MongoDB: parse_result: can't find these targets in your documents: %s" % can_not_find_targets)

        return result

    def generate_finding_query(self, mode, keys, values=None, mode2_mode=None):

        """
        根据模式生成查询的query
        :type keys: list
        :type values: list
        :param mode: query生成模式 1：关键词 2：要的字段
        :param mode2_mode: 模式2的模式：1：要的字段 0:不要的字段
        :param keys: 字段
        :param values: 字段对应的关键词
        :return: dict
        """
        print("MongoDB: query generate start")
        query = {}
        if mode == 1:
            for index in range(0, len(keys)):
                query[keys[index]] = values[index]
        elif mode == 2:
            if mode2_mode == 1:
                for i in keys:
                    query[i] = 1
            elif mode2_mode == 0:
                for i in keys:
                    query[i] = 0
            else:
                print("MongoDB: generate finding query: if you choose mode 2, you have to fill mode2_mode correctly")
                return False
        else:
            print("MongoDB: generate finding query: unknown mode")
            query = False
        return query

    def update_many_documents(self, db_name, coll_name, query, values):

        """
        更新记录（文档）（多个）
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 查找条件 {}
        :param values: 要修改的值（只要是一条以内的都可以） {"key": "value"}
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            print("MongoDB: update_many_document: something went wrong")
            return False
        else:
            values = {"$set": values}
            try:
                result = coll.update_many(query, values)
            except:
                print("MongoDB: update many document fail")
                return False
            else:
                print("MongoDB: update document success. Update count: "
                                    + str(result.modified_count))
                return result

    def delete_many_documents(self, db_name, coll_name, query):

        """
        删除多个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 删除条件
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            print("MongoDB: delete_many_document: something went wrong")
            return False
        else:
            try:
                result = coll.delete_many(query)
            except:
                print("MongoDB: delete many document fail")
                return False
            else:
                print("MongoDB: delete document success. Update count: "
                                    + str(result.deleted_count))
                return result


