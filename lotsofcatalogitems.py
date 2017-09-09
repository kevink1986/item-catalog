from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(
    name="Kevin Kriek",
    email="kevinkriek@gmail.com",
    picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()


item1 = Item(user_id=1, name="Shoes", description="Nike soccer shoes",
             price="$99.99", category=category1)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Ball", description="Adidas soccer ball",
             price="$5.50", category=category1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="T-shirt", description="Puma soccer shirt",
             price="$79.99", category=category1)

session.add(item3)
session.commit()


# Menu for UrbanBurger
category2 = Category(user_id=1, name="Tennis")

session.add(category1)
session.commit()


item1 = Item(user_id=2, name="Racket", description="Head tennis racket",
             price="$299.99", category=category2)

session.add(item1)
session.commit()

item2 = Item(user_id=2, name="Shorts", description="Robyn tennis short",
             price="$10.99", category=category2)

session.add(item2)
session.commit()


print "added catalog items!"
