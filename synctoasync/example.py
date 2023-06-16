import httpx
import asyncio
from rich import print

async def get_data(client, url):
    resp = await client.get(url)
    return resp.json()['name']

async def main():
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(1, 150):
            tasks.append(get_data(client, f"https://rickandmortyapi.com/api/character/{i}"))

        characters = await asyncio.gather(*tasks)
        for c in characters:
            print(c)

asyncio.run(main())