#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# This script is an exmple of using the (optional) ib.opt package
# instead of the regular API.
##

from time import sleep
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from random import randint
import sys
from functools import partial

def my_account_handler(msg):
    print(msg)


def my_tick_handler(msg):
    print(msg)


generic_tick_keys = '100,101,104,106,165,221,225,236'
short_sleep = partial(sleep, 1)

def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
if sys.version_info[0] < 3:
    gen_tick_id = gen_tick_id().next
else:
    gen_tick_id = gen_tick_id().__next__


def make_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_primaryExch = 'SMART'
    contract.m_currency = 'USD'
    contract.m_localSymbol = symbol
    return contract


def test_002(connection):
    ticker_id = gen_tick_id()
    contract = make_contract('NVDA')
    a = connection.reqMktData(ticker_id, contract, generic_tick_keys, False)
    short_sleep()
    b = connection.cancelMktData(ticker_id)
    print (a)
    print (b)

if __name__ == '__main__':
    con = ibConnection(host="127.0.0.1", port=7496, clientId=1)
    con.register(my_account_handler, 'UpdateAccountValue')
    con.register(my_tick_handler, message.tickSize, message.tickPrice)
    connect_result = con.connect()

    test_002(con)

    def inner():

        account = con.reqAccountUpdates(1, '')

        symbol = Contract()
        symbol.m_symbol = 'NVDA'
        symbol.m_secType = 'STK'
        symbol.m_exchange = 'SMART'
        mkt_data = con.reqMktData(1, symbol, '', False)

        print(mkt_data)

    inner()
    sleep(5)
    print('disconnected', con.disconnect())
    sleep(3)
    print('reconnected', con.reconnect())
    inner()
    sleep(3)

    print('again disconnected', con.disconnect())
