import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import motor.motor_asyncio
from report import make_report
from get_data_from_resource import get_processed_data, get_processed_data_db


connection_string = (
    'mongodb://' +
    os.environ['MONGODB_USERNAME'] + ':' +
    os.environ['MONGODB_PASSWORD'] + '@' +
    os.environ['MONGODB_HOSTNAME'] + ':27017/')

client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
db = client.scrapperdb
report_collection = db.reports
data_collection = db.data


async def daily_task():
    old_data = await get_processed_data_db(data_collection)
    new_data = await get_processed_data()
    document = {
        "datetime": datetime.now(),
        "data": new_data
    }
    result = await data_collection.insert_one(document)
    print(result.inserted_id)

    if not old_data:
        print("Initial load")
        return

    report, (fixes, breakdowns) = make_report(new_data, old_data)
    await report_collection.insert_one(report)
    print(report)


async def main(scheduler: AsyncIOScheduler):
    try:
        scheduler.start()
        while True:
            await asyncio.sleep(1)
    except:
        scheduler.shutdown()
        print('Scheduler stopped')

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_task, 'interval', seconds=60)
    try:
        asyncio.run(main(scheduler))
    except KeyboardInterrupt:
        print('Bye!')
