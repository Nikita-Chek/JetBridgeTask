# Task
Finding out how much money McDonalds might be losing due to broken ice cream machines in the US

### Aim
Scripts will calculate the report daily and display the total amount lost in revenue.
### Instruments
1. Python
2. MongoDB
3. docker-compose

### Asamptions

Note: All information and conclusions are based on assumptions from available sources.

According to the official website of McDonald’s, it serves more than 25 million customers every day in the U.S in 14,000 restaurants (https://corporate.mcdonalds.com/corpmcd/en-us/our-stories/article/ourstories.adding-260000-jobs.html). So, there is about 1,785 visitors in each McDonalds per day.

There is no relevant data on what percentage of customers order an ice cream, but in the same article it is mentioned that soft serve ice cream is used in more than 60% of its dessert menu. So, the assumption will be that about 50% of customers order a dessert of some description.

That means 892 customers might order dessert in one restraint per day, 535 of them might order an ice cream. The average price of an ice cream vanilla cone is $1. Sundaes price is $1.29. McFlurry Small is $1.7, Medium $2.39 (https://cakesprices.com/mcdonalds-ice-cream/). Meaning that average price of an ice cream is $1.6. Therefore, the revenue per one McDonalds per day for ice creams is 856 \$.

## Solution


```python
import aiohttp
import asyncio
```

#### Getting data from internet source and db


```python
import aiohttp

URL = 'https://mcbroken2.nyc3.digitaloceanspaces.com/markers.json'


async def get_data_from_url(URL: str) -> dict:
    """
    Get data from URL and return it as dict
    Args:
        URL (str): url of the resource

    Raises:
        Exception: If the response status is not 200

    Returns:
        dict: Response data
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            if resp.status != 200:
                raise Exception('API is not responding')
            result = await resp.json()
            return result


async def get_processed_data() -> tuple[dict]:
    """
    Process data from URL and return it as tuple of dicts.
    Flatten the data, process the coordinates,
    filter countries and active shops,
    sort by coordinates

    Returns:
        tuple[dict]: Tuple of dicts with processed data
    """
    result = await get_data_from_url(URL)
    result = result['features']
    for i, value in enumerate(result):
        result[i] = value['properties'] | value['geometry']
        result[i]['coordinates'] = tuple(
            float(coord) for coord in result[i]['coordinates']
        )
    result = filter(
        lambda row:
            row['country'] == 'USA' and
            row['is_active'] == True,
        result)
    result = sorted(result, key=lambda row: row['coordinates'])
    return tuple(result)


async def get_processed_data_db(data_collection) -> tuple[dict]:
    """
    Get data from database and return it as tuple of dicts.
    Transforms coordinates from list to tuple of floats.

    Args:
        data_collection: mongo database collection

    Returns:
        tuple[dict]: processed data
    """
    cursor = data_collection.find({}).sort("datetime", -1).limit(1)
    old_data = await cursor.to_list(length=1)
    if not old_data:
        return tuple()
    old_data = old_data[0]['data']
    for i, value in enumerate(old_data):
        old_data[i]['coordinates'] = tuple(
            float(coord) for coord in value['coordinates']
        )
    return tuple(old_data)
```


```python
result_old = await get_processed_data()
```


```python
result_new = await get_processed_data()
```

#### Compare result by number of working machines

In order to compare breakdowns in different periods, you can compare each point to each point.

$n^2$

But it is better to sort the two arrays, and go through them (taking into account that some points may have no similar ones in the other array). 

Sorting $ n\ log(n) $ + while loop $ n $ = $n\ log(n)$


```python
def compare_results_by_broken_index(new_data: list | tuple,
                                    old_data: list | tuple) -> tuple[tuple]:
    """
    Compare two lists of dictionaries by the index of the broken ice cream
    machine. Results should be sorted by coordinates.

    Args:
        new_data (list | tuple): Sorted by coordinates list of new results
        old_data (list | tuple): Sorted by coordinates list of old results

    Returns:
        tuple[tuple]: (
            mcdonalds with fixed ice cream machines,
            mcdonalds with broken ice cream machines
            )
    """
    old_len, new_len = len(old_data), len(new_data)
    i, j = 0, 0
    started_working, stoped_working = [], []
    while (i < new_len) and (j < old_len):
        if new_data[i]['coordinates'] == old_data[j]['coordinates']:
            if new_data[i]['is_broken'] and (not old_data[j]['is_broken']):
                stoped_working.append(new_data[i])
            if (not new_data[i]['is_broken']) and old_data[j]['is_broken']:
                started_working.append(new_data[i])
            i += 1
            j += 1
        elif new_data[i]['coordinates'] > old_data[j]['coordinates']:
            j += 1
        else:
            i += 1
    return tuple(started_working), tuple(stoped_working)
```


```python
compare_results_by_broken_index(result_new, result_old);
```

#### Make daily reports


```python
import datetime

RESTAURANT_CLIENTS_PER_DAY = 1785
DISERT_ORDER_PERSENT = 0.5
ICE_CREAM_ORDER_PERSENT = 0.6
ICE_CREAM_PRICE = 1.6
ICE_CREAM_REVENUE_PER_DAY = (
    RESTAURANT_CLIENTS_PER_DAY *
    DISERT_ORDER_PERSENT *
    ICE_CREAM_ORDER_PERSENT *
    ICE_CREAM_PRICE
)


def make_report(new_data: tuple,
                old_data: tuple) -> dict:
    """
    Makes report by compare new and old data,
    evaluate revenue and broken ice cream machines

    Args:
        new_data (tuple): new data
        old_data (tuple): old data

    Returns:
        dict: report
    """
    broken_machines = sum(map(lambda row: row['is_broken'],
                              new_data))
    fixes, breakdowns = compare_results_by_broken_index(new_data, old_data)
    report = {
        "datetime": datetime.datetime.now(),
        "broken_machines": broken_machines,
        "clients_count_per_day": RESTAURANT_CLIENTS_PER_DAY,
        "currency": "USD",
        "ice_cream_revenue_per_day": ICE_CREAM_REVENUE_PER_DAY,
        "overall_losses": broken_machines * ICE_CREAM_REVENUE_PER_DAY,
        "machine_fixed": len(fixes),
        "machine_breakdown": len(breakdowns),
    }
    return report, (fixes, breakdowns)

```


```python
report, (_, _) = make_report(result_new, result_old)
```

#### Scheduler


```python
import asyncio
from datetime import datetime
import os
import motor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
```

##### Seting up db connection


```python
connection_string = (
    'mongodb://' +
    os.environ['MONGODB_USERNAME'] + ':' +
    os.environ['MONGODB_PASSWORD'] + '@' +
    os.environ['MONGODB_HOSTNAME'] + ':27017/')
client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
db = client.scrapperdb
report_collection = db.reports
data_collection = db.data
```

##### Define daily Task Process

It takes data from sources, if there is no data in the database, then it initializes. Otherwise, there is a comparison of the previous day and the current day.

For simplicity, for now, I just output the results to the console. For more serious implementations, you can use for example Airflow.


```python
async def daily_task():
    old_data = await get_processed_data_db(data_collection)
    new_data = await get_processed_data()
    document = {
        "datetime": datetime.now(),
        "data": new_data
    }
    result = await data_collection.insert_one(document)

    if not old_data:
        print("Initial load")
        return

    report, (fixes, breakdowns) = make_report(new_data, old_data)
    await report_collection.insert_one(report)
    print(report)
```

##### Running main file

We can take a minute, not a day, for the test.


```python

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

```

### Result

You can look at the records in the database, through <b>mongosh</b>.

<img src="pict\Screenshot 2022-09-25 193056.png" width=400 height=400 />

Or via docker-compose console.log

<img src="pict\Screenshot 2022-09-25 193601.png" width=1000 height=60 />

You can run this solution on your own by downloading the repository and running docker-compose.
