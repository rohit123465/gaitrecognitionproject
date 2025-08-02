from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for the model
Base = declarative_base()

# Define the 'User' model 
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Create SQLite database 
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create the table in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
