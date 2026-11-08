"""按备注搜索。"""


def fetch_by_note(conn, note):
    """note 来自查询框。"""
    sql = "SELECT id, note FROM ledger_entry WHERE note LIKE '%{}%'".format(note)
    return conn.execute(sql).fetchall()
