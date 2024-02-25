from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON  # Import specific JSON type for SQLite


Base = declarative_base()

class List(Base):
    __tablename__ = 'lists'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    sources = Column(SQLiteJSON)
    elements = Column(SQLiteJSON)

class Chore(Base):
    __tablename__ = 'chores'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    repeat_after = Column(Integer)  # Seconds
    labels = Column(SQLiteJSON)
    project_id = Column(Integer)
    time = Column(Integer)
    list_id = Column(Integer, ForeignKey('lists.id'))
    parent_chore_id = Column(Integer, ForeignKey('chores.id'))
    lists = Column(SQLiteJSON)
    child_chores = Column(SQLiteJSON)

class DB:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

# Example usage
db = DB('sqlite:///example.db')
session = db.get_session()

# Note: When adding or retrieving `children_chores`, ensure to serialize/deserialize the JSON appropriately.

test_chore = Chore(name='TestChore', frequency='daily', time=10)
session.add(test_chore)
session.commit()

# get all chores
chores = session.query(Chore).all()
print(chores)
pass

from inputs.amazon import load_prior_results
amazon_list = []
with open('amazon.json', 'r') as f:
    for i, line in enumerate(f):
        # i used for debug counter
        try:
            amazon_list.append(eval(line))
        except Exception as e:
            print(f'Error: {e}')
            print(f'Line: {line}')
            continue

#amazon_list = List(name='amazon', location='amazon.json', elements=amazon_list)
#session.add(amazon_list)
#session.commit()

# Print all amazon items, sorted by transaction_date (if available) and then by amount
amazon_from_sql = session.query(List).filter_by(name='amazon').all()[0]
# sort
sorted_amazon = sorted(amazon_from_sql.elements, key=lambda x: (dict(x).get('transaction_date', ''), dict(x).get('amount', 0)))
for element in sorted_amazon:
    print(f'{element.get("transaction_date", "No date")} | OrderID: {element["orderID"]}\nAmount: {element["amount"]}\nItems: {element["items"]}')