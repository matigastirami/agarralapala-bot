from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.config.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
db_session = sessionmaker(autoflush=False, bind=engine)
