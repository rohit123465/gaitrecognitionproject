from sqlalchemy import create_engine, Column, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np
from scipy.spatial.distance import cosine


Base = declarative_base()
DATABASE_URL = 'sqlite:///gait_recognition.db'

class GaitData(Base):
    __tablename__ = 'gait_data'
    gait_id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer)  # Unique ID for identified individuals
    gait_signature = Column(LargeBinary, nullable=False)


engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


# Method makes the shorter feature vector to the same length as the longer
def pad_and_flatten(gait_signature, max_length):
    gait_signature = np.array(gait_signature)
    
    # Check if the signature is 1D and reshape accordingly
    if gait_signature.ndim == 1:
        num_features = 4  
        num_frames = gait_signature.shape[0] // num_features
        gait_signature = gait_signature.reshape(num_frames, num_features)
    
    # Pad the signature to the desired max_length
    padded_signature = np.pad(gait_signature, ((0, max_length - gait_signature.shape[0]), (0, 0)), mode='constant')
    
    return padded_signature.flatten()


# Function which performs the Cosine Similarity Algorithm
def similarity_check(gait_signature_1, gait_signature_2):
    max_length = max(len(gait_signature_1), len(gait_signature_2))
    
    flattened_1 = pad_and_flatten(gait_signature_1, max_length)
    flattened_2 = pad_and_flatten(gait_signature_2, max_length)
    
    return 1 - cosine(flattened_1, flattened_2)


def insert_gait_signature(gait_signature):
    session = Session()
    try:
        existing_entries = session.query(GaitData).all()
        matching_entry = None
        highest_similarity = 0

        gait_signature_np = np.frombuffer(gait_signature, dtype=np.float32)  # Convert to NumPy array

        for entry in existing_entries:
            stored_gait_np = np.frombuffer(entry.gait_signature, dtype=np.float32)  # Convert from binary
            current_similarity = similarity_check(gait_signature_np, stored_gait_np)

            if current_similarity == 1:  # Exact match found
                print("Duplicate gait signature found. Skipping insert.")
                return entry.person_id  # Return existing person_id

            if current_similarity > highest_similarity:
                matching_entry = entry
                highest_similarity = current_similarity
        print("similarity found: ",highest_similarity)

        
        if highest_similarity > 1:
            person_id = matching_entry.person_id 
        else:
            people = {entry.person_id for entry in existing_entries}  # Set of existing person_ids
            person_id = max(people, default=0) + 1  # Assign a new person_id

        gait_signature_blob = gait_signature_np.tobytes()  # Convert back to bytes

        # Final check before inserting
        existing_gait = session.query(GaitData).filter(GaitData.gait_signature == gait_signature_blob).first()
        if existing_gait:
            print("Gait signature already exists, skipping insert.")
            return existing_gait.person_id  

        # Insert new gait signature
        new_gait = GaitData(person_id=person_id, gait_signature=gait_signature_blob)
        session.add(new_gait)
        session.commit()
        
        return person_id

    except Exception as e:
        session.rollback()
        print(f"Error inserting/updating gait signature: {e}")
        return None
    finally:
        session.close()

def get_most_recent_person_id():
    session = Session()
    try:
        # Query to get the most recent entry by sorting by gait_id in descending order
        latest_entry = session.query(GaitData).order_by(GaitData.gait_id.desc()).first()

        if latest_entry:
            return latest_entry.person_id
        else:
            print("No records found in the database.")
            return None

    except Exception as e:
        print(f"Error retrieving the most recent person_id: {e}")
        return None

    finally:
        session.close()

def get_gait_signature_from_last_person():
    session = Session()
    try:
        entry = session.query(GaitData).order_by(GaitData.person_id.desc()).first()

        if entry:
            gait_signature_np = np.frombuffer(entry.gait_signature, dtype=np.float32)
            return gait_signature_np
        else:
            print("No gait signature found in the database.")
            return None

    except Exception as e:
        print(f"Error retrieving gait signature: {e}")
        return None

    finally:
        session.close()


def human_identification():
    session = Session()
    try:
        # Get the latest person id and their gait signature
        last_entry = session.query(GaitData).order_by(GaitData.person_id.desc()).first()

        if last_entry is None:
            print("Result: No gait signature found in the database.")
            return None

        highest_person_id = last_entry.person_id  # Latest person ID
        highest_person_gait_signature = np.frombuffer(last_entry.gait_signature, dtype=np.float32)

        existing_entries = session.query(GaitData).filter(GaitData.person_id != highest_person_id).all()

        if not existing_entries:
            print("Result: No previous gait signatures available for comparison.")
            return None

        highest_similarity = 0
        identified_person_id = None

        for entry in existing_entries:
            stored_gait_np = np.frombuffer(entry.gait_signature, dtype=np.float32)  # Convert from binary
            current_similarity = similarity_check(highest_person_gait_signature, stored_gait_np)

            if current_similarity > highest_similarity:
                highest_similarity = current_similarity
                identified_person_id = entry.person_id

        if highest_similarity > 0.75:
            return "Person identified. {identified_person_id} with similarity: {highest_similarity}"

            return identified_person_id  
        else:
            return f" No matching person found. Similarity: {highest_similarity}"

            return None  # No matching person found

    except Exception as e:
        return f"Error during human identification: {e}"
        return None
    finally:
        session.close()



