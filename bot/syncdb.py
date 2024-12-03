import ast
from bson import ObjectId

from config import redis_db
from config import mongo_db

def push_item(item_id):
    if item_id in redis_db.keys():
        item_data = ast.literal_eval(redis_db.get(item_id))
    else:
        print('Wrong item ID')
        return

    send_data = {
        'category_id': ObjectId(), 
        'title': item_data['title'],
        'description': item_data['description'],
        'condition': item_data['condition'], 
        'address': item_data['address'],
        'cost': item_data['cost'],
        'status': item_data['status'],
        'seller_id': ObjectId()
    }
    
    try:
        mongo_db.item.insert_one(send_data)
    except:
        print(f'Unable to push item {item_id}')

def push_ad(ad_id):
    if ad_id in redis_db.keys():
        ad_data = ast.literal_eval(redis_db.get(ad_id))
    else:
        print('Wrong ad ID')
        return
    
    send_data = {
    }

    '''
    try:
        mongo_db.ad.insert_one(send_data)
    except:
        print(f'Unable to push item {ad_id}')
    '''