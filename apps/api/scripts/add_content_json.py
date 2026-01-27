from sqlalchemy import create_engine, text
import os

# DB is in CWD if running from apps/api
DB_PATH = "sql_app.db"

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    try:
        with engine.connect() as conn:
            # Check if column exists (pragmatic way for SQLite)
            result = conn.execute(text("PRAGMA table_info(page_contents)"))
            columns = [row[1] for row in result]
            
            if "content_json" not in columns:
                print("Adding 'content_json' column to 'page_contents' table...")
                conn.execute(text("ALTER TABLE page_contents ADD COLUMN content_json VARCHAR"))
                conn.commit()
                print("Migration successful: Added content_json column.")
            else:
                print("Migration skipped: 'content_json' column already exists.")

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_db()
