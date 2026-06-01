from app.clickup import create_list_from_template
from app.nas import create_project_folder
from app.logger import logger

def run_pipeline(event):
    print(f"\n[PIPELINE] START: Event{event}")
    logger.info(f"\n[PIPELINE] START: Event{event}")
   
    create_project_folder(event)
    
    list_id = create_list_from_template(
        list_name = event,
        template_id = ""
    );

    print(f"[PIPELINE] DONE")
    logger.info(f"[PIPELINE] DONE")

