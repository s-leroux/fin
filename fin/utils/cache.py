import pickle
import sqlite3
from time import time

from functools import wraps

CACHE_DEFAULT_TTL = 3600

class Cache:
    pass

class SqliteCacheProvider(Cache):
    def __init__(self, db_name, *, ttl=CACHE_DEFAULT_TTL):
        if not ttl > 0:
            raise ValueError(f"The time-to-live must be > 0 (here {ttl})")

        self._default_ttl = ttl
        self.miss = self.hit = 0
        self.con = con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)

        con.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key BLOB NOT NULL,
                eol INTEGER NOT NULL,
                content BLOB NOT NULL,
                PRIMARY KEY(key)
            )
        """)

        con.execute("""
            CREATE INDEX IF NOT EXISTS cache_idx ON cache ( eol )
        """)

    def close(self):
        self.con.close()

    def kill_obsolete(self):
        self.con.execute(
            "DELETE FROM cache WHERE eol <= :limit",
            dict(limit=int(time()))
        )
        self.con.commit()

    def store(self, key, content, ttl):
        self.con.execute(
                "INSERT INTO cache ( key, content, eol ) VALUES ( :key, :content, :eol )",
            dict(key=key, content=content, eol=int(time()+ttl+1))
        )
        self.con.commit()

    def find(self, key):
        cur = self.con.cursor()
        try:
            res = cur.execute(
                    "SELECT content FROM cache WHERE key = :key AND eol > :now",
                    dict(key=key, now=int(time()))
            )
            rows = res.fetchall()
        finally:
            cur.close()

        if len(rows) > 1:
            raise ValueError(f"Number of rows {len(rows)} > 1")
        if len(rows) == 1:
            return rows[0][0]
        else:
            return None

    def __call__(self, fct, *, ttl=None):
        if ttl is None:
            ttl = self._default_ttl
        elif not ttl > 0:
            raise ValueError(f"The time-to-live must be > 0 (here {ttl})")

        @wraps(fct)
        def cached(*args, **kwargs):
            self.kill_obsolete()

            key = pickle.dumps((args, kwargs))
            content = self.find(key)
            
            if content is not None:
                # found
                self.hit += 1
                return pickle.loads(content)
            else:
                # not found
                self.miss += 1
                result = fct(*args, **kwargs)
                self.store(key, pickle.dumps(result), ttl)

                return result
        
        return cached
