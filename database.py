from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:123456@localhost/caretaker')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
