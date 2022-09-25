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
