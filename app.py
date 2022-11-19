from pydoc import doc
import uvicorn
import random
from fastapi import FastAPI, HTTPException

from typing import Optional

from sqlmodel import Field, SQLModel, create_engine,Session,select

app = FastAPI()


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: Optional[int] = None

url = "postgresql://user:password@localhost:5432/db"

engine = create_engine(url, echo=True)

SQLModel.metadata.create_all(engine)

def create_name(table, n):
    Obtained_Names = []
    for i in range(n):
        first = random.randint(0, len(table)-1)
        last = random.randint(0, len(table)-1)
        if table[first] + " " + table[last] not in Obtained_Names and table[first] != table[last]:
            Obtained_Names.append(table[first] + " " + table[last])
    return Obtained_Names
def create_heroes():
    num_heroes = 200
    Sel_TableHeros = ["Spider", "Man", "Arrow", "Green", "Big", "Bat", "Dive", "Boy", "Iron", "Rust", "Dead", "Pool"]
    Sel_TableSecretName = ["Dave", "Will", "Tommy", "Mat", "Henry", "Jake", "Smith", "Grant", "Sharp", "Pedro", "Marco", "Peter"]
    SuperHeroNames = create_name(Sel_TableHeros, num_heroes)
    SecretNames = create_name(Sel_TableSecretName, num_heroes)

    # hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    # hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    # hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    with Session(engine) as session:  # 
        for i in range(len(SuperHeroNames)):
            session.add(Hero(name=SuperHeroNames[i], secret_name=SecretNames[i], age=random.randint(1, 100)))
        # session.add(hero_1)  # 
        # session.add(hero_2)
        # session.add(hero_3)

        session.commit()
class HeroUpdate(SQLModel):
    name: Optional[str] = None
    secret_name: Optional[str] = None
    age: Optional[int] = None

@app.post("/heros")
def create_hero(hero:HeroCreate):
    with Session(engine) as session:
        db_hero = Hero.from_orm(hero)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero

@app.post("/create_test_data")
def create_test_data():
    create_heroes()
    return {"Result": "Ok"}

@app.delete("/heros/{hero_id}")
def delete_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        session.delete(hero)
        session.commit()
        return {"Deleted": True}

@app.delete("/heros")
def delete_all_hero():
    statement = select(Hero)
    with Session(engine) as session:
        results = session.exec(statement)
        results_all = results.all()
        for i in range(0,len(results_all)):
            session.delete(results_all[i])
        session.commit()
        return {"Deleted": True}


@app.get("/heros/{hero_id}")
def read_hero(hero_id):
    with Session(engine) as session:
        statement = select(Hero).where(Hero.id == hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero has not found")
        results = session.exec(statement)
        hero = results.first()
        return hero
@app.get("/heros")
def read_heros_age(age:int|None=None):
    if age is not None:
        statement = select(Hero).where(Hero.age >= age)
    else:
        statement = select(Hero)
    with Session(engine) as session:
        results = session.exec(statement)
        Allheros = results.all()
        return Allheros
@app.patch("/heros/{hero_id}")
def update_hero(hero_id:int, hero_new: HeroUpdate):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero has not found")
        hero_data = hero_new.dict(exclude_unset=True)
        for key, value in hero_data.items():
            setattr(hero, key, value)
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)