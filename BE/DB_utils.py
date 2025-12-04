from dotenv import load_dotenv,find_dotenv
import os
import pprint
from datetime import datetime as dt, timedelta
from pymongo.mongo_client import MongoClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
load_dotenv(find_dotenv('BE/.env'))
password = os.environ.get("MONGODB_PWD")
uri = f'mongodb+srv://phuochuunguyen2009_db_user:{password}@cluster0.nptsvtz.mongodb.net/?appName=Cluster0'

client = MongoClient(uri)
DB = client.FocusDB
FC = DB.focus_scores
GO = DB.goals
US = DB.users
def get_goals(payload):
    userid = payload.userid
    query = [
        {"$match":{
            "userId":userid
        }},
        {"$set":{
            "status": {
                "$cond" : {
                    "if":{
                        "$and": [
                            {"$lt": ['$deadline', '$$NOW']},
                            {'$eq': ['$status','In Progress']}
                        ]
                    },
                    "then":"Overdue",
                    "else":"$status"
                    
                }
            }
        }},
        {"$set": {"_id": {"$toString":"$_id"}}}
    ]
    res = GO.aggregate(query)
    return list(res)
def create_goal(payload):
    userid = payload.userid
    title = payload.title
    desc = payload.desc
    date = payload.deadline
    date_split = date.split("-")
    date = dt(int(date_split[0]),int(date_split[1]),int(date_split[2]))
    GO.insert_one({
        "title":title,
        "description":desc,
        "deadline":date,
        "current_progress":0,
        'status': 'In Progress',
        'userId' :userid
    })
def edit_goal_progress(payload):
    new_progress = payload.new_progress
    _id = ObjectId(payload.id)
    query = {"$set": {"current_progress":new_progress}}
    
    if new_progress == 100:
        query = {"$set": {"current_progress": new_progress, "status": "Completed"}}
    
    GO.update_one({"_id":_id},query)    
def delete_goal(payload):
    _id = ObjectId(payload.id)
    GO.delete_one({"_id":_id})
def create_timestamp(payload):
    userid = payload.userid
    focus_score = payload.avgfocus_score
    data = {
        'userId':userid,
        "focus_score": focus_score,
        "timestamp": dt.now()
    }
    FC.insert_one(data)
def find_timestamp_today(payload):
    userid = payload.userid
    now = dt.now()
    start = dt(now.year,now.month,now.day)
    query = [
        {
            "$match": {
                "userId":userid,
                "timestamp":{"$gte":start,"$lte":now}
            }
        },
        {
            "$group": {
                "_id": {"hour": {"$hour":"$timestamp"}},
                "avg_focus": {"$avg":"$focus_score"}
            }
        },
        {"$sort": {"_id.hour":1}}
    ]
    res = FC.aggregate(query)
    return list(res)
def find_timestamp_this_month(payload):
    userid = payload.userid
    now = dt.now()
    start = dt(now.year,now.month,1)
    query = [
        {"$match":{
            "userId":userid,
            "timestamp": {"$gte":start, "$lte":now}    
        }},
        {"$group": {
            "_id": {"day": {"$dayOfMonth":"$timestamp"}},
            "avg_focus": {"$avg":"$focus_score"}
        }},
        {"$sort": {"_id.day":1}}
    ]
    res = FC.aggregate(query)
    return list(res)
def find_timestamp_this_year(payload):
    userid = payload.userid
    now = dt.now()
    start = dt(now.year,1,1)
    query = [
        {"$match":{
            "userId":userid,
            "timestamp": {"$gte":start,"$lte":now}
        }},
        {"$group":{
            "_id": {"month": {"$month":"$timestamp"}},
            "avg_focus": {"$avg": "$focus_score"}
        }},
        {"$sort":{"_id.month":1}}
    ]
    res = FC.aggregate(query)
    return list(res)
def find_timestamp_this_week(payload):
    userid = payload.userid
    now = dt.now()
    weekday = now.weekday()
    start = dt(now.year, now.month, now.day) - timedelta(days=weekday)

    # End of week (Sunday 23:59:59)
    end = start + timedelta(days=7)

    query = [
        {"$match": {
            "userId": userid,
            "timestamp": {"$gte": start, "$lt": end}
        }},
        {"$group": {
            "_id": {
                "year": {"$year": "$timestamp"},
                "month": {"$month": "$timestamp"},
                "day": {"$dayOfMonth": "$timestamp"}
            },
            "avg_focus": {"$avg": "$focus_score"}
        }},
        {"$sort": {
            "_id.year": 1,
            "_id.month": 1,
            "_id.day": 1
        }}
    ]
    res = FC.aggregate(query)
    return list(res)



# userid = "692f03cf6f92de6a879a0528"

# # how many weeks of data you want to generate
# WEEKS = 4

# # list to store generated test documents
# docs = []

# now = datetime.now()

# for week in range(WEEKS):
#     for day in range(7):
#         # timestamp going backwards week by week
#         ts = now - timedelta(weeks=week, days=day)

#         # generate random focus score (0–100)
#         focus = random.randint(60, 95)

#         doc = {
#             "userId": userid,
#             "focus_score": focus,
#             "timestamp": ts
#         }

#         docs.append(doc)

# # print first 5 generated docs
# FC.insert_many(docs)
# for d in docs[:5]:
#     print(d)

# print(f"\nTotal documents generated: {len(docs)}")
