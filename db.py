import os
import sqlite3 as lite
import sys


class database:
    name_db = 'test.db'

    def __init__(self):
        exists = os.path.exists(f'./{database.name_db}')

        self.con = lite.connect(database.name_db)
        self.region_id = 0
        self.settlementType_id = 0
        self.settlement_id = 0
        self.street_id = 0

        self.cur = self.con.cursor()

        if exists:
            self.region_id = self.get_last_region_id()
            self.settlementType_id = self.get_last_id('SettlementType')
            self.settlement_id = self.get_last_id('Settlement')
            self.street_id = self.get_last_id('Street')
            return

        self.cur.execute("CREATE TABLE Region ("
                         "   Id INT PRIMARY KEY, "
                         "   Name TEXT, "
                         "   Reg INT, "
                         "   URL TEXT"
                         ");")

        self.cur.execute("CREATE TABLE SettlementType ("
                         "   Id INT PRIMARY KEY, "
                         "   Name TEXT, "
                         "   'Order' INT"
                         ");")

        self.cur.execute("CREATE TABLE Settlement ("
                         "   Id INT PRIMARY KEY, "
                         "   Name TEXT, "
                         "   ParentId INT NULL, "
                         "   RegionId INT NULL, "
                         "   SettlementTypeId INT, "
                         "   Tier INT, "
                         "   URL TEXT, "
                         "   FOREIGN KEY (ParentId) REFERENCES Settlement(Id), "
                         "   FOREIGN KEY (RegionId) REFERENCES Region(Id), "
                         "   FOREIGN KEY (SettlementTypeId) REFERENCES SettlementType(Id)"
                         ");")

        self.cur.execute("CREATE TABLE Street ("
                         "   Id INTEGER PRIMARY KEY, "
                         "   Name TEXT, "
                         "   RegionId INT NULL, "
                         "   SettlementId INT, "
                         "   URL TEXT, "
                         "   FOREIGN KEY (RegionId) REFERENCES Region(Id), "
                         "   FOREIGN KEY (SettlementId) REFERENCES Settlement(Id)"
                         ");")

        self.con.commit()

    def add_region(self, name, reg, url):
        self.region_id += 1
        self.cur.execute(f"INSERT INTO Region VALUES ({self.region_id}, '{name}', {reg}, '{url}')")
        return self.region_id

    def add_settlementType(self, name):
        self.settlementType_id += 1
        self.cur.execute(f"INSERT INTO SettlementType VALUES ({self.settlementType_id}, '{name}', 1)")
        return self.settlementType_id

    def add_settlement(self, name, parent_id, region_id, settlementType_id, tier, url):
        self.settlement_id += 1
        self.cur.execute(f"INSERT INTO Settlement VALUES ({self.settlement_id}, '{name}', {parent_id}, {region_id}, {settlementType_id}, {tier}, '{url}')")
        return self.settlement_id

    def add_street(self, name, region_id, settlement_id, url):
        self.street_id += 1
        self.cur.execute(f"INSERT INTO Street VALUES ({self.street_id}, '{name}', {region_id}, {settlement_id}, '{url}')")
        return self.street_id

    def save_changes(self):
        self.con.commit()

    def get_last_region_id(self):
        return self.get_last_id('Region')

    def get_last_id(self, table):
        self.cur.execute(f"SELECT * FROM {table}")
        rows = self.cur.fetchall()
        last_id = rows[-1][0]
        return last_id
