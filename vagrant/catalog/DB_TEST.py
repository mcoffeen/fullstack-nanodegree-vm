from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from db_setup import Collection, Disc, Base, User

engine = create_engine('sqlite:///discgolfcollections.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

discs = session.query(Disc).order_by(asc(Disc.discType))
collections = session.query(Collection)
users = session.query(User)

#delete all discs
#----------------
#session.query(Disc).delete()
#session.query(Collection).delete()
#session.query(User).delete()
#session.commit()

for i in users:
    print i.name

for collection in collections:
    colName = "%s created by User #%s" % (collection.name, collection.user_id)
    print "=" * len(colName)
    print colName
    print "=" * len(colName)

for disc in discs:
    title = "Item #%s - %s - %s - %s - %sg" % (disc.id,
        disc.discType, disc.mfr, disc.name, disc.weight)
    print "-" * len(title)
    print title
    print "-" * len(title)
