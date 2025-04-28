#     This code is a part of program Advisor
#     Copyright (C) 2022 contributors Advisor
#     The full list is available at the link
#     https://github.com/tagezi/advisor/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" The module provides an API for working with the database. It creates a
multi-level API that can be used in other modules to create requests using
a minimum of transmitted data.

Function:
    get_columns(sColumns, sConj='AND')

Class:
    SQL

Using:
    Foo = SQL(_DataBaseFile_)
"""

import logging
import sqlite3
from sqlite3 import DatabaseError

from advisor.lib.log import start_logging
from advisor.lib.str import str_get_file_patch


def check_connect_db(oConnector, sBasePath, sDBDir, sDBFile):
    """ Checks for the existence of a database and if it does not find it, then
        creates it with default values.

    :param oConnector: Instance attribute of SQL.
    :type oConnector: SQL
    :param sBasePath: A path of the executed script.
    :type sBasePath: str
    :param sDBDir: A dir when database is by default.
    :type sDBDir: str
    :param sDBFile:
    :type sDBFile: str
    :return: None
    """
    # The list of tables in DB
    lTables = ['Engines', 'UpdateData']

    for sTable in lTables:
        bExist = oConnector.select('sqlite_master', '*', 'name, type',
                                   (sTable, 'table',)).fetchone()
        if not bExist:
            sDBPath = str_get_file_patch(sBasePath, sDBDir)
            sFile = str_get_file_patch(sDBPath, sDBFile)
            with open(sFile) as sql_file:
                sql_script = sql_file.read()
                oConnector.execute_script(sql_script)
                break


def get_columns(sColumns, sConj='AND'):
    """ The function of parsing a string, accepts a list of table columns
    separated by commas and returns this list with '=? AND' or '=? OR'
    as separator.

    :param sColumns: A string with a list of table columns separated by commas.
    :type sColumns: str
    :param sConj: The one from 'AND' or 'OR' operator condition.
        By default, is used 'AND'.
    :type sConj: str or None
    :return: The string with a list of table columns separated
        by '=? AND' or '=? OR'.
    :rtype: str
    """
    return sColumns.replace(', ', '=? ' + sConj + ' ') + "=?"


def get_increase_value(sColumns, tValues):
    """ Checks counting elements of values, and if them fewer,
     then makes them equal.

     Note:
        In the rison that tuple can't be multiplied on flot, the process
        of increasing the tuple becomes somewhat resource-intensive. So,
        tValues should be consisting of one element.

    :param sColumns: Colum(s) in query.
    :type sColumns: str
    :param tValues: Values should be specified in the request.
    :type tValues: tuple or list
    :return: A tuple with values, which equal to sColumns.
    :rtype: list
    """
    if len(sColumns.split(',')) > len(tValues) == 1:
        return tValues * len(sColumns.split(', '))

    logging.error('The tuple must be filled or consist of one element.'
                  f'The columns: {sColumns} \n The tuple: {tValues}')
    return


class SQL:
    """
    Provides interface for working with database from others scripts.

    *Methods*
      # Standard methods.
        * __init__ -- Method initializes a cursor of sqlite database.
        * __del__ -- Method closes the cursor of sqlite database.
      # Low level methods.
        * export_db -- Method exports from db to sql script.
        * execute_script -- Method imports from slq script to db.
        * execute_query -- Method execute sql_search query.
        * insert_row -- Method inserts a record in the database table.
        * delete_row -- Method deletes a row from the table.
        * update -- Method updates value(s) in record of the database table.
        * select -- Method does selection from the table.
      # Average level API.
        * sql_get_id: Finds id of the row by value(s) of table column(s).
        * sql_get_all: Method gets all records in database table.
        * sql_count: Method counts number of records in database table.
        * sql_table_clean: Method cleans up the table.
    """

    # Standard methods
    def __init__(self, sFileDB):
        """ Initializes connect with database.

        :param sFileDB: Path to database as string.
        :type sFileDB: str
        """
        self.logging = start_logging()
        try:
            self.oConnector = sqlite3.connect(sFileDB)
        except DatabaseError as e:
            print(f"An error has occurred: {e}.\n"
                  f"String of query: {sFileDB}\n")
            self.logging.exception(f"An error has occurred: {e}.\n"
                                   f"String of query: {sFileDB}\n")

    def __del__(self):
        """ Closes connection with the database. """
        self.oConnector.close()

    # Low methods level
    def export_db(self):
        """ Method exports from db to sql script. """
        return self.oConnector.iterdump()

    def execute_script(self, sSQL):
        """ Method executes sql script.

        The main difference from the method is the ability to execute
        several commands at the same time. For example, using this method,
        you can restore the database from sql dump.

        :param sSQL: SQL Script as string.
        :type sSQL: str
        :return: True if script execution is successful, otherwise False.
        :rtype: bool
        """
        oCursor = self.oConnector.cursor()
        try:
            oCursor.executescript(sSQL)
        except DatabaseError as e:
            logging.exception(f'An error has occurred: {e}.\n'
                              f'String of query: {sSQL}\n')
            return False

        return True

    def execute_query(self, sSQL, tValues=None):
        """ Method executes sql script.

        :param sSQL: SQL query.
        :type sSQL: str
        :param tValues: value(s) that need to safe inserting into query
            (by default, None).
        :type tValues: tuple or list or None
        :return: Cursor or bool -- True if script execution is successful,
            otherwise False.
        """
        oCursor = self.oConnector.cursor()
        try:
            if tValues is None:
                oCursor.execute(sSQL)
            else:
                oCursor.execute(sSQL, tValues)
        except DatabaseError as e:
            logging.exception(f'An error has occurred: {e}.\n'
                              f'String of query: {sSQL}\n'
                              f'Parameters: {tValues}')
            return False

        return oCursor

    def insert_row(self, sTable, sColumns, tValues):
        """ Inserts a record in the database table.

        :param sTable: Table name as string.
        :type sTable: str
        :param sColumns: Columns names of the table by where needs inserting.
        :type sColumns: str
        :param tValues: Value(s) as tuple for inserting.
        :type tValues: tuple or list
        :return: ID of an inserted row  if the insert was successful.
            Otherwise, False.
        :rtype: str or bool
        """
        sSQL = ("?, " * len(sColumns.split(", ")))[:-2]
        sqlString = f'INSERT INTO {sTable} ({sColumns}) VALUES ({sSQL})'
        oCursor = self.execute_query(sqlString, tValues)
        if oCursor:
            self.oConnector.commit()
            return oCursor.lastrowid

        return False

    def delete_row(self, sTable, sColumns=None, tValues=None):
        """ Deletes row in the database table by value(s).

        :param sTable: A table as string in where need to delete row.
        :type sTable: str or None
        :param sColumns: Column(s) where the value(s) will be found.
            (by default, None).
        :type sColumns: str or None
        :param tValues: value(s) as tuple for search of rows.
            (by default, None).
        :type tValues: tuple or list
        :return: True if the deletion is successful, otherwise False.
        :rtype: bool
        """
        if sColumns is not None:
            sSQL = f'DELETE FROM {sTable} WHERE {get_columns(sColumns)}'
            oCursor = self.execute_query(sSQL, tValues)
        else:
            sSQL = f'DELETE FROM {sTable}'
            oCursor = self.execute_query(sSQL)

        if oCursor:
            self.oConnector.commit()
            return True

        return False

    def update(self, sTable, sSetUpdate, sWhereUpdate, tValues):
        """ Updates value(s) in the record of the database table.

        :param sTable: A Table as string where update is need to do.
        :type sTable: str
        :param sSetUpdate: Column(s) where the value are writen.
        :type sSetUpdate: str
        :param sWhereUpdate: A column where values correspond to the required.
        :type sWhereUpdate: str
        :param tValues: value(s) as tuple for search corresponding rows.
        :type tValues: tuple or list
        :return: True if the insert was successful, otherwise False.
        :rtype: bool
        """
        sSetUpdate = get_columns(sSetUpdate, ', ')
        sWhereUpdate = get_columns(sWhereUpdate)
        sSQL = f'UPDATE {sTable} SET {sSetUpdate} WHERE {sWhereUpdate}'
        oCursor = self.execute_query(sSQL, tValues)
        if oCursor:
            self.oConnector.commit()
            return True

        return False

    def select(self, sTable, sGet, sWhere='', tValues='', sConj='', sFunc=''):
        """ Looks for row by value(s) in table column(s).

        :param sTable: Table name as string.
        :type sTable: str
        :param sGet: Name of the column of the table, which will be returned.
        :type sGet: str
        :param sWhere: Names of columns of the table, by which to search
            (by default, empty).
        :type sWhere: str or None
        :param sConj: The one from 'AND' or 'OR' operator condition.
            By default, is used 'AND'.
        :type sConj: str or None
        :param tValues: Value(s) as tuple for search
            (by default, empty).
        :type tValues: tuple or list or None
        :param sFunc: Function name of sqlite, which need to apply
            (by default, empty). Note: Now, you can use only two sqlite
            functions: Count and DISTINCT.
        :type sFunc: str or None
        :return: Cursor or bool -- Cursor object within rows that was found,
            or False, if the row not found.
        """
        if sFunc == 'Count':
            sGet = f'Count({sGet})'
        elif sFunc == 'DISTINCT':
            sGet = f'{sFunc} {sGet}'

        if sWhere:
            if sConj:
                sCol = get_columns(sWhere, sConj)
            else:
                sCol = get_columns(sWhere)

            sSQL = f'SELECT {sGet} FROM {sTable} WHERE {sCol}'
            oCursor = self.execute_query(sSQL, tValues)
        else:
            oCursor = self.execute_query(f'SELECT {sGet} FROM {sTable}')

        if oCursor:
            return oCursor

        return False

    # Average API level
    def sql_get_values(self, sTable, sColumns, sWhere, tValues, sConj=''):
        """ Looks for ID of the row by value(s) of table column(s).

        :param sTable: Table name as string.
        :type sTable: str
        :param sColumns: Name of the column of the table by which to search.
        :type sColumns: str
        :param sWhere: Names of columns of the table by which to search.
        :type sWhere: str
        :param tValues: Value(s) as tuple for search.
        :type tValues: tuple or list
        :param sConj: The one from 'AND' or 'OR' operator condition.
            By default, is used 'AND'.
        :type sConj: str or None
        :return: ID as Number in the row cell, or 0, if the row not found.
        :rtype: list or bool
        """
        if sWhere:
            if sConj:
                tValues = get_increase_value(sWhere, tValues)
                sWhere = get_columns(sWhere, sConj)
            else:
                sWhere = get_columns(sWhere)
        sSQL = f'SELECT {sColumns} FROM {sTable} WHERE {sWhere}'
        oCursor = self.execute_query(sSQL, tValues)
        if oCursor:
            lRows = oCursor.fetchall()
            if lRows:
                return lRows

        return False

    def sql_get_id(self, sTable, sID, sWhere, tValues, sConj=''):
        lRows = self.sql_get_values(sTable, sID, sWhere, tValues, sConj)
        if lRows:
            return lRows[0][0]

        return False

    def sql_get_all(self, sTable, sColumns=''):
        """ Gets all records in database table.

        :param sColumns:
        :param sTable: Table name as string where records should be received.
        :type sTable: str
        :return: Tuple of all rows of table.
        :rtype: tuple or bool
        """
        sQuery = f'SELECT * FROM {sTable}'
        if sColumns:
            sQuery = f'SELECT {sColumns} FROM {sTable}'
        oCursor = self.execute_query(sQuery)
        if oCursor:
            return oCursor.fetchall()

        return False

    def sql_count(self, sTable):
        """ Counts number of records in database table.

        :param sTable: Table name as string where records should be count.
        :type sTable: str
        :return: Number of found records.
        :rtype: int or bool
        """
        # sTable, sGet, sWhere, tValues, sFunc=None
        oCursor = self.select(sTable, sGet='*', sFunc='Count')
        if oCursor:
            row = oCursor.fetchall()
            return row[0][0]

        return False

    def sql_table_clean(self, lTable):
        """ Cleans up the table.

        :param lTable: Table names as list or tuple of string, or table name
            as string where cleaning is need to do.
        :type lTable: tuple or list or str
        :return: True, if execution is successful. Otherwise, False.
            Note: False is returned even if cleaning the last table in
            the tuple was not successful.
        :rtype: bool
        """
        if type(lTable) == str:
            lTable = [lTable]

        for sTable in lTable:
            bDel = self.delete_row(str(sTable))
            if not bDel:
                return False

        return True

    def check_value(self, sTable, sGet, sWhere, aValue):
        """

        :param sTable:
        :type sTable: str
        :param sGet:
        :type sGet: str
        :param sWhere:
        :type sWhere: str
        :param aValue:
        :return:
        """
        oCursor = self.select(sTable, sGet, sWhere, (aValue,))
        if oCursor:
            queryISIN = oCursor.fetchone()
            if queryISIN:
                return True

        return False

    def check_update(self, sTable, sColumns, sWhere, lValues):
        """

        :param sTable:
        :param sColumns:
        :param sWhere:
        :param lValues:
        :return:
        """
        tQuery = self.sql_get_values(sTable, sColumns, sWhere, (lValues[0],))
        lQuery = list(tQuery)
        if lQuery == lValues:
            return True

        return False

    def portfolio(self, pd):
        """

        :return:
        """
        dfb = pd.read_sql_query(
            "SELECT PortfolioTool.type_tool, "
            "Portfolio.tool_code, "
            "BordSecurities.SHORTNAME, "
            "Portfolio.price, "
            "Portfolio.count "
            "FROM Portfolio "
            "JOIN PortfolioTool "
            "ON PortfolioTool.id_tool=Portfolio.id_tool "
            "JOIN BordSecurities "
            "ON BordSecurities.SECID=Portfolio.tool_code;",
            self.oConnector)

        dfs = pd.read_sql_query(
            "SELECT PortfolioTool.type_tool, Portfolio.tool_code, "
            "SharesCollections.SHORTNAME, "
            "Portfolio.price, "
            "Portfolio.count "
            "FROM Portfolio "
            "JOIN PortfolioTool "
            "ON PortfolioTool.id_tool=Portfolio.id_tool "
            "JOIN SharesCollections "
            "ON SharesCollections.SECID=Portfolio.tool_code; ",
            self.oConnector)

        return pd.concat([dfb, dfs], axis=0, join='outer', ignore_index=True)

    def get_bonds_by_value(self,
                           pd,
                           iInitialFaceValue=1000,
                           sFaceUnit='SUR',
                           fMinYield=10,
                           fMaxYield=30,
                           bOFZ=False,
                           bIN=False,
                           iMinPeriod=30,
                           iMaxPeriod=182,
                           fMinCouponValue=16.00
                           ):
        sQuery = (
            "SELECT BordSecurities.SECID, BordSecurities.ISIN, "
            "BordSecurities.SHORTNAME, BordSecurities.MATDATE, "
            "BordSecurities.PREVPRICE, BordSecurities.YIELDATPREVWAPRICE, "
            "BordSecurities.COUPONPERCENT, BordSecurities.COUPONVALUE, "
            "BordSecurities.ACCRUEDINT, BordSecurities.NEXTCOUPON, "
            "BordSecurities.COUPONPERIOD, BondDescription.INITIALFACEVALUE, "
            "BondDescription.FACEVALUE, BondDescription.FACEUNIT, "
            "BordSecurities.LISTLEVEL, BondDescription.EMITTER "
            "FROM BordSecurities "
            "JOIN BondDescription "
            "ON BondDescription.SECID=BordSecurities.SECID "
            f"WHERE BondDescription.INITIALFACEVALUE <= {iInitialFaceValue} "
            f"AND BondDescription.FACEUNIT = \"{sFaceUnit}\" "
            "AND BondDescription.ISQUALIFIEDINVESTORS=0 "
            "AND BordSecurities.PREVPRICE is not NULL "
            "AND BordSecurities.OFFERDATE is NULL "
            "AND BordSecurities.COUPONPERCENT>1 "
            "AND BordSecurities.MATDATE>\"2025-09-01\" "
            "AND BondDescription.INITIALFACEVALUE=BondDescription.FACEVALUE "
            f"AND BordSecurities.COUPONPERIOD>={int(iMinPeriod)} "
            f"AND BordSecurities.COUPONPERIOD<={int(iMaxPeriod)} "
            )

        if bOFZ:
            sQuery = f" {sQuery} AND BordSecurities.SECNAME like \"%ОФЗ%\" "
        else:
            sQuery = (
                f" {sQuery} AND BordSecurities.YIELDATPREVWAPRICE>{fMinYield} "
                f"AND BordSecurities.YIELDATPREVWAPRICE<{fMaxYield} "
                f"AND BordSecurities.SECNAME not like \"%ОФЗ%\" "
                "AND BondDescription.EMITTER not like \"%икрофинансовая%\" "
                "AND BondDescription.EMITTER not like \"%коллектор%\" "
            )

        sQuery = (f"{sQuery} AND BordSecurities.SECNAME not like \"%ОФЗ-АД%\" "
                  "AND BordSecurities.SECNAME not like \"%ОФЗ-ПК%\" ")

        if bIN:
            sQuery = f" {sQuery} AND BordSecurities.SECNAME like \"%ОФЗ-ИН%\" "
        else:
            sQuery = (f" {sQuery} AND BordSecurities.SECNAME not like "
                      f"\"%ОФЗ-ИН%\" ")

        sQuery = f" {sQuery} GROUP BY BordSecurities.MATDATE;"

        return pd.read_sql_query(sQuery, self.oConnector)

    def get_period_list(self,
                        iInitialFaceValue=1000,
                        sFaceUnit='SUR',
                        sMatDateStart='2025-09-01',
                        iMaxPeriod=182
                        ):
        lAnswer = self.execute_query(
            "select distinct BordSecurities.COUPONPERIOD "
            "FROM BordSecurities "
            "JOIN BondDescription "
            "ON BondDescription.SECID=BordSecurities.SECID "
            "WHERE BondDescription.ISQUALIFIEDINVESTORS=0 "
            f"AND BondDescription.INITIALFACEVALUE <= {iInitialFaceValue} "
            f"AND BondDescription.FACEUNIT = \"{sFaceUnit}\" "
            "AND BordSecurities.PREVPRICE is not NULL "
            "AND BordSecurities.OFFERDATE is NULL "
            "AND BordSecurities.COUPONPERCENT > 1 "
            f"AND BordSecurities.MATDATE > \"{sMatDateStart}\" "
            f"AND BordSecurities.COUPONPERIOD<={int(iMaxPeriod)} "
            "AND BondDescription.INITIALFACEVALUE=BondDescription.FACEVALUE "
            "AND BondDescription.EMITTER not like \"%икрофинансовая%\" "
            "AND BondDescription.EMITTER not like \"%коллектор%\" "
            "order by COUPONPERIOD;")

        return lAnswer


if __name__ == '__main__':
    pass
