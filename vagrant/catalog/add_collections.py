#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Collection, Disc, Base, User

engine = create_engine('sqlite:///discgolfcollections.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create fake user #1
u1 = User(name="Danny Disc", email="dannydisc@discgolf.com",
          picture='http://getdrawings.com/img/disc-golfer-silhouette-11.jpg')
session.add(u1)
session.commit()

# Create fake user #2
u2 = User(name="Debbie Disc", email="debbiedisc@discgolf.com",
          picture='/static/img/profile_face.png')
session.add(u2)
session.commit()

# Create Collection #1
Collection1 = Collection(name="Danny's Collection", user_id=1)
session.add(Collection1)
session.commit()

# Create Collection #2
Collection2 = Collection(name="Debbie's Collection", user_id=2)
session.add(Collection2)
session.commit()

# Add Discs to Collection #1
Disc1 = Disc(user_id=1, discType='Distance Driver', mfr='Innova',
             name='Destroyer', plastic='Star', weight=175, color='Red',
             collection_id=1)

session.add(Disc1)
session.commit()

Disc2 = Disc(user_id=1, discType='Distance Driver', mfr='Innova',
             name='Boss', plastic='Champion', weight=172, color='Tie-Dye',
             collection_id=1)

session.add(Disc2)
session.commit()

Disc3 = Disc(user_id=1, discType='Fairway Driver', mfr='Innova',
             name='Tee Bird', plastic='G-Star', weight=174, color='Yellow',
             collection_id=1)

session.add(Disc3)
session.commit()

Disc4 = Disc(user_id=1, discType='Mid-Range', mfr='Innova',
             name='Mako3', plastic='Star', weight=179, color='Green',
             collection_id=1)

session.add(Disc4)
session.commit()

Disc5 = Disc(user_id=1, discType='Mid-Range', mfr='Discraft',
             name='Buzzz', plastic='Z', weight=181, color='Pink',
             collection_id=1)

session.add(Disc5)
session.commit()

Disc6 = Disc(user_id=1, discType='Putt and Approach', mfr='Innova',
             name='Aviar', plastic='Star', weight=168, color='White',
             collection_id=1)

session.add(Disc6)
session.commit()

Disc7 = Disc(user_id=1, discType='Putt and Approach', mfr='Innova',
             name='Rhyno', plastic='Champion', weight=172, color='Orange',
             collection_id=1)

session.add(Disc7)
session.commit()

# Add Discs to Collection #2
Disc1 = Disc(user_id=2, discType='Distance Driver', mfr='Innova',
             name='Wraith', plastic='Champion', weight=171, color='Blue',
             collection_id=2)

session.add(Disc1)
session.commit()

Disc2 = Disc(user_id=2, discType='Fairway Driver', mfr='Latitude 64',
             name='River', plastic='Opto', weight=168, color='White',
             collection_id=2)

session.add(Disc2)
session.commit()

Disc3 = Disc(user_id=2, discType='Mid-Range', mfr='Innova',
             name='Shark', plastic='DX', weight=178, color='Pink',
             collection_id=2)

session.add(Disc3)
session.commit()

Disc4 = Disc(user_id=2, discType='Putt and Approach', mfr='Innova',
             name='Aviar', plastic='Star', weight=176, color='Red',
             collection_id=2)

session.add(Disc4)
session.commit()

print "Two base users created and collections added."
