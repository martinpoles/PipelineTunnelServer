import os
import time
import shutil
from config import NAS_STORAGE, TEMPLATE_PATH
from logger import logger

def create_project_folder(project_id):
    """
    Crea la cartella progetto sul NAS copiando il template.
    Blocca operazione se NAS non disponibile.
    """

    project_path = os.path.join(NAS_STORAGE, project_id)

    # 🔥 sicurezza: verifica NAS prima di tutto
    if not check_nas():
        raise Exception("[NAS] NAS non disponibile, operazione bloccata")

    # crea progetto se non esiste
    if not os.path.exists(project_path):
        print(f"[NAS] Creating project folder: {project_id}")
        logger.info(f"[NAS] Creating project folder: {project_id}")
        shutil.copytree(TEMPLATE_PATH, project_path)
    else:
        print(f"[NAS] Project already exists: {project_id}")
        logger.info(f"[NAS] Project already exists: {project_id}")

    return project_path

def check_nas(retries=3, delay=1):
    print("\n[NAS] Checking availability...")
    logger.info("\n[NAS] Checking availability...")

    for attempt in range(1, retries + 1):
        try:
            # test reale di accesso
            os.listdir(NAS_STORAGE)

            print("[NAS] OK - NAS disponibile ✔\n")
            logger.info("[NAS] OK - NAS disponibile ✔\n")
            return True

        except Exception as e:
            print(f"[NAS][WARN] Tentativo {attempt}/{retries} fallito: {e}")
            logger.info(f"[NAS][WARN] Tentativo {attempt}/{retries} fallito: {e}")
            time.sleep(delay)

    print(f"[NAS][ERROR] NAS non raggiungibile: {NAS_STORAGE}\n")
    logger.info(f"[NAS][ERROR] NAS non raggiungibile: {NAS_STORAGE}\n")
    return False
