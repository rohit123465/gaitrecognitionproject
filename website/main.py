from gaitsignature import train_autoencoder
from gait_database import human_identification
from gait_database import get_gait_signature_from_last_person
from gait_database import get_most_recent_person_id



def results():
  file_path = "/content/drive/MyDrive/4D-Humans/website/output/walking_man_preprocessed.json"
  train_autoencoder(file_path)

  end_gait_signature=get_gait_signature_from_last_person()
  if end_gait_signature is None:
      print("Error: Gait signature is None.")
  else:
      human_identification()

