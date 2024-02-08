"""
SQLite3-backed cache
"""
import sqlite3
from fin.datetime import CalendarDate, parseisodate

sqlite3.register_adapter(CalendarDate, str)
sqlite3.register_converter("CalendarDate", parseisodate)

from fin.api.core import HistoricalData
from fin.seq import column
from fin.seq import table
from fin.seq import expr
from fin.utils.log import console

# Historical data
CACHE_DEFAULT_DB_NAME="eod.sqlite3"

class _DB:
    def __init__(self, db_name):
        self.con = con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)

        con.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                ticker NOT NULL,
                start NOT NULL,
                end NOT NULL,
                PRIMARY KEY(ticker, start, end)
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS eod (
                ticker NOT NULL,
                date CalendarDate NOT NULL,
                open NOT NULL,
                high NOT NULL,
                low NOT NULL,
                close NOT NULL,
                adj_close NOT NULL,
                volume NOT NULL,
                PRIMARY KEY(ticker, date)
            )
        """)

    def is_range_in_cache(self, ticker, start, end):
        cur = self.con.cursor()
        try:
            res = self.con.execute("""
                SELECT COUNT(*) FROM cache
                WHERE ticker = :ticker
                    AND start <= :start
                    AND end >= :end
            """, dict(
                ticker=ticker,
                start = str(start),
                end = str(end)
            ))
            found, = res.fetchone()
            return found != 0
        finally:
            cur.close()

    def get_historical_data(self, ticker, start, end):
        if not self.is_range_in_cache(ticker, start, end):
            return None

        res = self.con.execute("""
            SELECT date, open, high, low, close, adj_close, volume
            FROM eod
            WHERE ticker = :ticker
                AND date >= :start
                AND date <= :end
            ORDER BY date
            """, dict(
                ticker=ticker,
                start=str(start),
                end=str(end)
            ))

        return res.fetchall()

    def store_historical_data(self, ticker, start, end, rows):
        cur = self.con.cursor()
        try:
            with self.con:
                cur.executemany("""
                    INSERT INTO eod(ticker, date, open, high, low, close, adj_close, volume)
                    VALUES (?,?,?,?,?,?,?,?)
                """, rows)
                cur.execute("""
                    INSERT INTO cache(ticker, start, end)
                    VALUES(?,?,?)
                """,(ticker, str(start), str(end)))
        finally:
            cur.close()

    def close(self):
        self.con.close()

def Client(base, *, db_name=CACHE_DEFAULT_DB_NAME):
    # A bit of mro magic to provide the same interface as the base client object
    known_interfaces = { HistoricalData, }
    interfaces = []
    base_mro = base.__class__.mro()
    for c in base_mro:
        if c in known_interfaces:
            interfaces.append(c)

    db = _DB(db_name)

    class _Client(*interfaces):
        def _historical_data(self, ticker, duration, end):
            start = end-duration
            rows = db.get_historical_data(ticker, start, end)
            if rows is None:
                console.info(f"Cache miss for {ticker} ({duration}, {end})")
                t = base._historical_data(ticker, duration, end)
                db.store_historical_data(ticker, start, end, t.select(
                    expr.constant(ticker, name="ticker"),
                    dict(name="date", expr="Date"),
                    dict(name="open", expr="Open"),
                    dict(name="high", expr="High"),
                    dict(name="low", expr="Low"),
                    dict(name="close", expr="Close"),
                    dict(name="adj_close", expr="Adj Close"),
                    dict(name="volume", expr="Volume"),
                    ).row_iterator())
                return t
            else:
                return table.table_from_rows(
                        rows,
                        ("Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"),
                        name=ticker
                        )

        def close(self):
            db.close()

    return _Client()
