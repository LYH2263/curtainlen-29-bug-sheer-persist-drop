import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(window_id, fabric_id, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(window_id,fabric_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (window_id, fabric_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def list_runs(limit=50, window_id=None):
    sql = ("SELECT r.*, w.name window_name, f.name fabric_name FROM calc_runs r "
           "LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id ")
    params = []
    if window_id is not None:
        sql += "WHERE r.window_id=? "
        params.append(window_id)
    sql += "ORDER BY r.id DESC LIMIT ?"
    params.append(limit)
    c = connect()
    try:
        rows = c.execute(sql, params).fetchall()
        from app.services.sheer_persist import list_summary_view

        out = []
        for row in rows:
            d = dict(row)
            raw = json.loads(d.pop("result_json"))
            d["result"] = list_summary_view(raw)
            out.append(d)
        return out
    finally:
        c.close()
