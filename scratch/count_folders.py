import sys
import os
sys.path.append(os.path.abspath('.'))

from app import create_app
from models import db

app = create_app()
with app.app_context():
    print("Database tables:")
    for table_name in db.metadata.tables.keys():
        print(f" - {table_name}")
