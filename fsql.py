import os

pragmas = """
PRAGMA synchronous = OFF;
PRAGMA journal_mode = TRUNCATE;
PRAGMA foreign_constraints = ON;"""

schema = """
CREATE TABLE IF NOT EXISTS Devices (
   did INT NOT NULL UNIQUE,
   uuid TEXT PRIMARY KEY,
   node TEXT,
   volumename TEXT);

CREATE TABLE IF NOT EXISTS Groups (
   gid INT NOT NULL UNIQUE,
   uuid TEXT PRIMARY KEY,
   name TEXT,
   realname TEXT);

CREATE TABLE IF NOT EXISTS Users (
   uid INT NOT NULL UNIQUE,
   uuid TEXT PRIMARY KEY,
   name TEXT,
   realname TEXT);

CREATE TABLE IF NOT EXISTS Inodes (
   dev INT NOT NULL REFERENCES Devices(did) ON UPDATE CASCADE ON DELETE CASCADE,
   inode INT NOT NULL,
   mode INT NOT NULL,
   uid INT NOT NULL REFERENCES Users(uid) ON UPDATE CASCADE ON DELETE CASCADE,
   gid INT NOT NULL REFERENCES Groups(gid) ON UPDATE CASCADE ON DELETE CASCADE,
   mtime DATETIME NOT NULL,
   size INT NOT NULL,
   hash TEXT,
   PRIMARY KEY (dev, inode));

CREATE TABLE IF NOT EXISTS Paths (
   path TEXT NOT NULL, dev TEXT NOT NULL, inode INT NOT NULL,
   PRIMARY KEY (path), FOREIGN KEY (dev, inode) REFERENCES Inodes (dev, inode));

CREATE INDEX IF NOT EXISTS inode_Paths ON Paths (dev, inode);

CREATE VIEW IF NOT EXISTS PathNodes AS
   SELECT path, p.dev AS dev, p.inode AS inode,
          mode, uid, gid, mtime, size, hash
   FROM Paths p JOIN Inodes i USING (dev, inode);

CREATE TRIGGER IF NOT EXISTS PathNodes_del INSTEAD OF
    DELETE ON PathNodes FOR EACH ROW BEGIN
        DELETE FROM Inodes WHERE dev = old.dev AND inode = old.inode;
        DELETE FROM Paths WHERE dev = old.dev AND inode = old.inode;
    END;

CREATE TRIGGER IF NOT EXISTS PathNodes_ins INSTEAD OF
    INSERT ON PathNodes FOR EACH ROW BEGIN
        INSERT OR REPLACE INTO Inodes (dev, inode, mode, uid, gid,
            mtime, size, hash) VALUES (new.dev, new.inode, new.mode,
            new.uid, new.gid, new.mtime, new.size, new.hash);
        INSERT OR REPLACE INTO Paths (path, dev, inode)
            VALUES (new.path, new.dev, new.inode);
    END;

CREATE TRIGGER IF NOT EXISTS PathNodes_upd INSTEAD OF
    UPDATE ON PathNodes FOR EACH ROW BEGIN
        UPDATE OR REPLACE Inodes SET dev=new.dev, inode=new.inode,
            mode=new.mode, uid=new.uid, gid=new.gid, mtime=new.mtime,
            size=new.size, hash=new.hash
            WHERE dev=old.dev AND inode=old.inode;
        UPDATE OR REPLACE Paths SET dev=new.dev, inode=new.inode,
            path=new.path
            WHERE dev=old.dev AND inode=old.inode;
    END;
""" % {'mtimetype': 'REAL' if os.stat_float_times() else 'INT'}

