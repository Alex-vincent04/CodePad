from datetime import datetime
from app.models.db import get_db
from app.models.schemas import CodeHistory

async def save_version(task_id: str, code: str, username: str, html: str = None, css: str = None, js: str = None):
    """Saves a new version of code to the code_history collection."""
    db = get_db()
    
    # Optional: check if the new code is different from the last saved version to avoid duplicates
    last_version = await db.code_history.find_one(
        {"task_id": task_id},
        sort=[("timestamp", -1)]
    )
    
    is_duplicate = False
    if last_version:
        if last_version.get("code") == code and \
           last_version.get("html") == html and \
           last_version.get("css") == css and \
           last_version.get("js") == js:
            is_duplicate = True
            
    if is_duplicate:
        print(f"[DEBUG] Skipping save - code is identical to last version for task_id: {task_id}")
        return # No change, don't save duplicate
    
    print(f"[DEBUG] Creating CodeHistory entry - task_id: {task_id}, username: {username}")
    
    # Use current local time instead of UTC
    from datetime import datetime as dt
    current_time = dt.now()
    
    history_entry = CodeHistory(
        task_id=task_id,
        code=code,
        html=html,
        css=css,
        js=js,
        timestamp=current_time,
        username=username
    )
    
    result = await db.code_history.insert_one(history_entry.dict())
    print(f"[DEBUG] CodeHistory inserted with ID: {result.inserted_id}, timestamp: {current_time}")
