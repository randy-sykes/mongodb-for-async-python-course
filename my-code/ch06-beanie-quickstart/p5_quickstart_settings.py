import asyncio
import datetime
from typing import Optional

import beanie
import motor.motor_asyncio
import pydantic


# Goal of this step:
# Connect to MongoDB with Beanie
# We'll evolve this into beanie in the next step.

async def main():
    await init_connection("beanie_quickstart")
    await create_a_user()
    await insert_multiple_users()
    await find_some_users()

    print("Done.")


async def init_connection(db_name: str):
    conn_str = f"mongodb://localhost:27017/{db_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str)

    await beanie.init_beanie(database=client[db_name], document_models=[User])

    print(f"Connected to {db_name}.")


async def find_some_users():

    # All at once
    users: list[User] = await User\
        .find(User.location.country == 'USA')\
        .find(User.name == 'Danie')\
        .sort(-User.name)\
        .limit(5)\
        .to_list()
    user_query = User.find(User.location.country == 'USA').sort(User.name)
    print('\n'.join([f"{u.name}, {u.location.country}" for u in users]))
    async for u in user_query:
        u.password_hash = 'a'
        await u.save()

    print("Upgraded security for all USA users.")


async def create_a_user():
    user_count = await User.count()
    if user_count > 0:
        print(f"Already have {user_count:,} users!")
        return
    print("Creating new user...")
    # Make sure you set up the DB connection before this line
    loc = Location(city="Austin", state="TX", country="USA")
    user = User(name="Randy", email="rjsykes28@outlook.com", location=loc)
    print(user)

    await user.save()
    print(f'User after save: {user}')


async def insert_multiple_users():
    user_count = await User.count()
    if user_count > 3:
        print(f"Already have {user_count:,} users!")
        return

    print("Creating a set of users...")
    # Make sure you set up the DB connection before this line
    u1 = User(name="Fred", email="Fred@outlook.com", location=Location(city="Bob", state="TX", country="USA"))
    u2 = User(name="Bob", email="Bob@outlook.com", location=Location(city="Fred", state="TX", country="USA"))
    u3 = User(name="Danie", email="dkasting-sykes@outlook.com", location=Location(city="Austin", state="TX", country="USA"))

    await User.insert_many([u1, u2, u3] )

    print('Inserted multiple users objects.')


class Location(pydantic.BaseModel):
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]


class User(beanie.Document):
    name: str
    email: str
    password_hash: Optional[str]

    created_date: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    last_login: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    location: Location = pydantic.Field(default_factory=Location)

    class Settings:
        name = "users"
        indexes = [
            "location.country"
        ]



if __name__ == '__main__':
    asyncio.run(main())

