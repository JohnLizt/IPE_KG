# -*- coding: utf-8 -*-
from py2neo import Graph, Node, Relationship, NodeMatcher


# 版本说明：Py2neo v4
class Neo4j_Handle():
    graph = None
    matcher = None

    def __init__(self):
        print("Neo4j Init ...")

    def connectDB(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", ".neo4j0"))
        self.matcher = NodeMatcher(self.graph)

    # 实体查询，用于命名实体识别：品牌+车系+车型
    def matchEntityItem(self, value):
        answer = self.graph.run("MATCH (entity1) WHERE entity1.name = \"" + value + "\" RETURN entity1").data()
        return answer

    # 实体查询
    def getEntityRelationbyEntity(self, value):
        # 查询实体：不考虑实体类型，只考虑关系方向
        answer = self.graph.run(
            "MATCH (entity1) - [rel] -> (entity2)  WHERE entity1.name = \"" + value + "\" RETURN entity1,rel,entity2").data()
        # if(len(answer) == 0):
        # #查询实体：不考虑关系方向
        # answer = self.graph.run("MATCH (entity1) - [rel] - (entity2)  WHERE entity1.name = \"" + value + "\" RETURN entity1,rel,entity2").data()
        print(answer)
        return answer

    # 关系查询:实体1
    def findRelationByEntity1(self, entity1):
        # 基于品牌查询
        answer = self.graph.run("MATCH (n1:Bank {name:\"" + entity1 + "\"})- [rel] -> (n2) RETURN n1,rel,n2").data()
        # 基于车系查询，注意此处额外的空格
        if (len(answer) == 0):
            answer = self.graph.run(
                "MATCH (n1:Serise {name:\"" + entity1 + " \"})- [rel] - (n2) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体2
    def findRelationByEntity2(self, entity1):
        # 基于品牌
        answer = self.graph.run("MATCH (n1)<- [rel] - (n2:Bank {name:\"" + entity1 + "\"}) RETURN n1,rel,n2").data()
        if (len(answer) == 0):
            # 基于车系
            answer = self.graph.run(
                "MATCH (n1) - [rel] - (n2:Serise {name:\"" + entity1 + " \"}) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体1+关系
    def findOtherEntities(self, entity, relation):
        answer = self.graph.run(
            "MATCH (n1:Bank {name:\"" + entity + "\"})- [rel:Subtype {type:\"" + relation + "\"}] -> (n2) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：关系+实体2
    def findOtherEntities2(self, entity, relation):
        print("findOtherEntities2==")
        print(entity, relation)
        answer = self.graph.run(
            "MATCH (n1)- [rel:RELATION {type:\"" + relation + "\"}] -> (n2:Bank {name:\"" + entity + "\"}) RETURN n1,rel,n2").data()
        if (len(answer) == 0):
            answer = self.graph.run(
                "MATCH (n1)- [rel:RELATION {type:\"" + relation + "\"}] -> (n2:Serise {name:\"" + entity + " \"}) RETURN n1,rel,n2").data()
        return answer

    # 关系查询：实体1+实体2(注意Entity2的空格）
    def findRelationByEntities(self, entity1, entity2):
        answer = self.graph.run("MATCH (n1 {name:\"" + entity1 + "\"})- [rel] -> (n2 {name:\"" + entity2 + "\"}) "
                                                                                                           "RETURN n1,rel,n2").data()
        return answer

    # 查询数据库中是否有对应的实体-关系匹配
    def findEntityRelation(self, entity1, entity2, relation):
        answer = self.graph.run(
            "MATCH (n1 {name:\"" + entity1 + "\"})- [rel {type:\"" + relation + "\"}] -> (n2{name:\"" + entity2 + "\"}) RETURN n1,rel,n2").data()
        return answer

    # 新建实体
    def createEntity(self, entityName, entityTag, entityRelease, entityLink):
        answer = []
        try:
            if entityTag == "IPE_l0":
                answer = self.graph.run(
                    "CREATE (n1:" + entityTag + "{name:\"" + entityName + "\", released:\"" + entityRelease + "\", link:\"" + entityLink + "\"}) RETURN n1").data()
            elif entityTag == "IPE_l1" or entityTag == "IPE_l2":
                answer = self.graph.run(
                    "CREATE (n1:" + entityTag + "{name:\"" + entityName + "\", released:\"" + entityRelease + "\"}) RETURN n1").data()
            else:
                answer = self.graph.run(
                    "CREATE (n1:" + entityTag + "{name:\"" + entityName + "\"}) RETURN n1").data()
        finally:
            return answer

    # 删除实体
    def deleteEntity(self, entityName):
        try:
            self.graph.run("MATCH (n {name:\"" + entityName + "\"}) DETACH DELETE n")
            return True
        except:
            return False

    # 创建两个已存在实体间的关系
    def createRel(self, entity1, entity2, relation):
        try:
            cypher = "MATCH (n1 {name:\"" + entity1 + "\"}) MATCH (n2 {name:\"" + entity2 + "\"}) CREATE (n1)-[:" + relation + "]->(n2)"
            print(cypher)
            self.graph.run(
                "MATCH (n1 {name:\"" + entity1 + "\"}) MATCH (n2 {name:\"" + entity2 + "\"}) CREATE (n1)-[:" + relation + "]->(n2)")
            return True
        except:
            return False

    # 删除两个实体间的关系
    def deleteRel(self, entity1, entity2):
        try:
            self.graph.run("MATCH (n1 {name:\"" + entity1 + "\"}) - [r] - (n2 {name:\"" + entity2 + "\"}) DELETE r")
            return True
        except:
            return False
