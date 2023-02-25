import asyncio
from aiohttp import ClientSession


async def main():
    async with ClientSession() as session:
        response = await session.post(
            "http://127.0.0.1:111/ads/",
            json={
                "id": 1,
                "title": "Крутое объявление",
                "description": "Крутое описание",
                "owner": "Василий",
            },
        )
        print(response.status)
        print(await response.json())

        response = await session.post(
            "http://127.0.0.1:111/ads/",
            json={
                "id": 1,
                "title": "Крутое объявление",
                "description": "Крутое описание",
                "owner": "Василий",
            },
        )
        print(response.status)
        print(await response.json())

        response = await session.get("http://127.0.0.1:111/ads/1/")
        print(response.status)
        print(await response.json())

        response = await session.patch("http://127.0.0.1:111/ads/1/", json={"id": 5})
        print(response.status)
        print(await response.json())

        response = await session.get("http://127.0.0.1:111/ads/5/")
        print(response.status)
        print(await response.json())

        response = await session.delete("http://127.0.0.1:111/ads/5/")
        print(response.status)
        print(await response.json())

        response = await session.get("http://127.0.0.1:111/ads/5/")
        print(response.status)
        print(await response.json())

    async with ClientSession() as session:
        response = await session.post(
            "http://127.0.0.1:111/ads/",
            json={
                "id": "gfjhfgjg",
                "title": "8",
                "description": "Крутое описание",
                "owner": "Василий",
            },
        )
        print(response.status)
        print(await response.json())


asyncio.run(main())
