"""一次性迁移：todos 表新增 status 列，并按废弃的 completed 回填。

幂等设计：PRAGMA 判断列是否已存在，重复执行安全。
用法：cd backend && .venv/Scripts/python scripts/migrate_todo_status.py
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "app.db")

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
cols = [row[1] for row in cur.execute("PRAGMA table_info(todos)").fetchall()]

if "status" in cols:
    print("status column already exists, skip ALTER")
else:
    cur.execute("ALTER TABLE todos ADD COLUMN status VARCHAR(10) NOT NULL DEFAULT 'todo'")
    print("added status column")

# 按 completed 回填（幂等：只改仍为默认值的行）
cur.execute("UPDATE todos SET status = 'done' WHERE completed = 1 AND status = 'todo'")
print("backfilled:", cur.rowcount, "rows -> done")

con.commit()
print("cols now:", [row[1] for row in cur.execute("PRAGMA table_info(todos)").fetchall()])
con.close()
