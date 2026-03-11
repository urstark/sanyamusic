# -----------------------------------------------
# 🔸 SanyaMusic Project
# 🔹 Developed & Maintained by: Stark (https://github.com/urstark)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by urstark
# -----------------------------------------------
from SANYAMUSIC.utils.mongo import db

filters = db.filters["filters"] 

# Cache for chat filters
FILTERS_CACHE = {}

async def add_filter_db(chat_id: int, filter_name: str, content: str, text: str, data_type: int):
   filter_data = await filters.find_one({'chat_id': chat_id})

   if filter_data is None:
      _id = await filters.count_documents({}) + 1
      new_filters = [
         {
            'filter_name': filter_name,
            'content': content,
            'text': text,
            'data_type': data_type
         }
      ]
      await filters.insert_one({'_id': _id, 'chat_id': chat_id, 'filters': new_filters})
      if len(FILTERS_CACHE) > 1000:
          FILTERS_CACHE.clear()
      FILTERS_CACHE[chat_id] = new_filters
   
   else:
         FILTERS_NAME = await get_filters_list(chat_id)
         if filter_name not in FILTERS_NAME:
            new_filter = {
               'filter_name': filter_name,
               'content': content,
               'text': text,
               'data_type': data_type
            }
            await filters.update_one({'chat_id': chat_id}, {'$addToSet': {'filters': new_filter}}, upsert=True)
            if chat_id in FILTERS_CACHE:
               FILTERS_CACHE[chat_id].append(new_filter)
         else:
            await filters.update_one(
               {'chat_id': chat_id, 'filters.filter_name': filter_name},
               {'$set': {
                  'filters.$.content': content,
                  'filters.$.text': text,
                  'filters.$.data_type': data_type
               }}
            )
            if chat_id in FILTERS_CACHE:
               for f in FILTERS_CACHE[chat_id]:
                  if f['filter_name'] == filter_name:
                     f['content'] = content
                     f['text'] = text
                     f['data_type'] = data_type
                     break

async def stop_db(chat_id: int, filter_name:str):
   await filters.update_one({'chat_id': chat_id}, {'$pull': {'filters': {'filter_name': filter_name}}})
   if chat_id in FILTERS_CACHE:
      FILTERS_CACHE[chat_id] = [f for f in FILTERS_CACHE[chat_id] if f['filter_name'] != filter_name]

async def stop_all_db(chat_id: int):
   await filters.update_one({'chat_id': chat_id}, {'$set': {'filters': []}}, upsert=True)
   FILTERS_CACHE[chat_id] = []
   
async def get_filter(chat_id: int, filter_name: str):
   if chat_id not in FILTERS_CACHE:
       data = await filters.find_one({'chat_id': chat_id})
       if data:
           if len(FILTERS_CACHE) > 1000:
               FILTERS_CACHE.clear()
           FILTERS_CACHE[chat_id] = data['filters']
       else:
           return None

   for f in FILTERS_CACHE[chat_id]:
      if f['filter_name'] == filter_name:
         return filter_name, f['content'], f['text'], f['data_type']
   return None

async def get_filters_list(chat_id: int):
   if chat_id not in FILTERS_CACHE:
       data = await filters.find_one({'chat_id': chat_id})
       if data:
           if len(FILTERS_CACHE) > 1000:
               FILTERS_CACHE.clear()
           FILTERS_CACHE[chat_id] = data['filters']
       else:
           return []

   return [f['filter_name'] for f in FILTERS_CACHE[chat_id]]