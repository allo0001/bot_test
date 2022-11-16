from datetime import datetime

from sqlalchemy import Column, String, create_engine, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DB_PATH = 'sqlite:///db.db'


def create_eng():
    return create_engine(DB_PATH)


def create_session():
    Session = sessionmaker(bind=create_eng())
    return Session()


engine = create_eng()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    id_tel = Column(String)
    role = Column(Integer, default=0)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, id_tel):
        self.name = name
        self.id_tel = id_tel

    def __repr__(self):
        return f'<User({self.name},{self.id_tel})>'


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    alias = Column(String)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    expense = relationship('Expense', back_populates='categories')

    def __init__(self, name, alias):
        self.name = name
        self.alias = alias

    def __repr__(self):
        return f'<Category({self.name},({self.alias}))>'

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    category = Column(Integer, ForeignKey('categories.id'))
    amount = Column(Integer)
    user = Column(Integer, ForeignKey('users.id'))
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    categories = relationship('Category', back_populates='expense')

    def __init__(self, user, name, category, amount):
        self.name = name
        self.category = category.id
        self.amount = amount
        self.user = user

    def __repr__(self):
        return f'<Expense({self.name})>'


def user_verification(id_tel: str):
    session = create_session()
    usr = session.query(User).filter(User.id_tel == id_tel).first()
    if usr:
        if usr.role:
            return usr
        else:
            return True
    else:
        usr = User(name=id_tel, id_tel=id_tel)
        session.add(usr)
        session.commit()
        return False


def insert(obj):
    session = create_session()
    session.add(obj)
    session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    session = create_session()

    # cat1 = session.query(Category).filter(Category.name == 'cat1').first()
    # cat2 = session.query(Category).filter(Category.name == 'cat2').first()
    #
    #
    # exp1 = Expense(name='категория №1', category=cat1)
    # exp2 = Expense(name='категория №2', category=cat2)
    #
    # session.add_all([exp1, exp2])
    # session.commit()

    print(session.query(Expense).all()[0].categories)

