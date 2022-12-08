# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from toolkit.pre_load import neo4jconn
from django.http import JsonResponse
import os

import json
relationCountDict = {}
filePath = os.path.abspath(os.path.join(os.getcwd(),"."))

with open(filePath+"/toolkit/relationStaticResult.txt","r") as fr:
	for line in fr:
		relationNameCount = line.split(",")
		relationName = relationNameCount[0][2:-1]
		relationCount = relationNameCount[1][1:-2]
		relationCountDict[relationName] = int(relationCount)
def sortDict(relationDict):
	for i in range( len(relationDict) ):
		relationName = relationDict[i]['rel']['type']
		relationCount = relationCountDict.get(relationName)
		if(relationCount is None ):
			relationCount = 0
		relationDict[i]['relationCount'] = relationCount

	relationDict = sorted(relationDict,key = lambda item:item['relationCount'],reverse = True)

	return relationDict

#实体查询
def search_entity(request):
	ctx = {}
	#根据传入的实体名称搜索出关系
	if(request.GET):
		entity = request.GET['user_text']
		#连接数据库
		db = neo4jconn
		db.connectDB()
		entityRelation = db.getEntityRelationbyEntity(entity)
		if len(entityRelation) == 0:
			#若数据库中无法找到该实体，则返回数据库中无该实体
			ctx= {'title' : '<h2>数据库中暂未添加该实体</h1>'}
			return render(request,'entity.html',{'ctx':json.dumps(ctx,ensure_ascii=False)})
		else:
			#返回查询结果
			#将查询结果按照"关系出现次数"的统计结果进行排序
			entityRelation = sortDict(entityRelation)
			relJsonData = json.loads(json.dumps(entityRelation, ensure_ascii=False))
			for i in range(len(entityRelation)):
				relJsonData[i]['rel'] = entityRelation[i]["rel"].__class__.__name__
			return render(request,'entity.html',{'entityRelation':json.dumps(relJsonData)})

	#需要进行类型转换
	return render(request,"entity.html",{'ctx':ctx})

# 实体及关系管理
def search_relation(request):
	ctx = {}
	if(request.GET):
		db = neo4jconn
		# 处理实体管理请求
		if len(request.GET) == 5:

			entityName = str.strip(request.GET['entityName'])
			entityTag = str.strip(request.GET['entityTag'])
			entityRelease = str.strip(request.GET['entityRelease'])
			entityLink = str.strip(request.GET['entityLink'])
			operation = str.strip(request.GET['entityOperation'])

			# 新建实体
			if operation == "createEntity":
				if not entityName or not entityTag:
					ctx = {'title': '新建实体失败：请填写实体名称和类型'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				if not entityRelease:
					entityRelease = "null"
				if not entityLink:
					entityLink = "null"
				answer = db.matchEntityItem(entityName)
				if len(answer) != 0:
					ctx = {'title': '新建实体失败：同名实体已存在'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				createResult = db.createEntity(entityName, entityTag, entityRelease, entityLink)
				if (len(createResult) == 0):
					ctx = {'title': '新建实体失败'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				else:
					ctx = {'title': '新建实体成功'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})

			# 删除实体
			if operation == "deleteEntity":
				if not entityName:
					ctx = {'title': '删除实体失败：请填写实体名称'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				answer = db.matchEntityItem(entityName)
				if len(answer) == 0:
					ctx = {'title': '删除实体失败：实体不存在'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				deleteResult = db.deleteEntity(entityName)
				if not deleteResult:
					ctx = {'title': '删除实体失败'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				else:
					ctx = {'title': '删除实体成功'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})


		# 处理关系管理请求
		if len(request.GET) == 4:
			entity1_text = str.strip(request.GET['entity1_text'])
			operation = str.strip(request.GET['relOperation'])
			entity2_text = str.strip(request.GET['entity2_text'])
			relation = str.strip(request.GET['relType'])

			if not entity1_text or not entity2_text:
				ctx = {'title': '请填写实体名称'}
				return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
			entity1 = db.matchEntityItem(entity1_text)
			entity2 = db.matchEntityItem(entity2_text)
			if not entity1 or not entity2:
				ctx = {'title': '实体不存在'}
				return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
			if operation == "createRel":
				answer = db.findEntityRelation(entity1_text, entity2_text, relation)
				if len(answer) > 0:
					ctx = {'title': '关系创建失败：关系已存在'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				db.deleteRel(entity1_text,entity2_text)
				createRes = db.createRel(entity1_text, entity2_text, relation)
				opposite = {"包含": "属于", "属于": "包含", "关联": "关联"}
				createRes = createRes and db.createRel(entity2_text,entity1_text, opposite[relation])
				if createRes is True:
					ctx = {'title': '关系创建成功'}
				else:
					ctx = {'title': '关系创建成功'}
			if operation == "deleteRel":
				answer = db.findEntityRelation(entity1_text, entity2_text, relation)
				if len(answer) == 0:
					ctx = {'title': '关系删除失败：关系不存在'}
					return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
				delRes = db.deleteRel(entity1_text, entity2_text)
				if delRes is True:
					ctx = {'title': '关系删除成功'}
				else:
					ctx = {'title': '关系删除失败'}
			return render(request, 'relation.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})

	return render(request, 'relation.html', {'ctx':ctx})
