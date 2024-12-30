import pandas as pd
import numpy as np
from home.forms.portfolio import *
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import decimal
from sqlalchemy import create_engine
from django.conf import settings
from dotenv import load_dotenv
import os

from urllib.parse import quote 

from django.db.utils import (
    DEFAULT_DB_ALIAS
)

load_dotenv()

@csrf_exempt
def fetching(request):
    engine = create_engine(conStr_sqlalchemy())
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(
        user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    holdings = Holding.objects.filter(portfolio=portfolio)
    if len(holdings) <= 0:
        return None, None

    page_size = int(request.GET.get('pageSize'))

    sortColumn = request.GET.get('sortColumn')
    sortDirection = request.GET.get('sortDirection')

    keyWords = request.GET.get('keywords')
    whereStr = " where 1=1 "
    params = ()
    if len(keyWords) > 0:
        params = (f'%{keyWords}%',)
        whereStr += " and ( sd.symbol_id) ILIKE %s"

    sort_criteria = " sd.symbol_id, sd.time"
    if sortColumn and sortDirection:
        # 将它们连接起来，通常可以用逗号或其他分隔符
        sort_criteria = f" {sortColumn} {sortDirection}"

    # Step 1. Prepare summary query script
    showing_repeat_times = {
        'agg': 'COUNT(ss.*)', 'column': 'showing_repeat_times'}
    last_showing = {'agg': 'MAX(ss.time)', 'column': 'last_showing'}

    def summary_query(field) -> str:
        return f"""
        SELECT
             ss.symbol_id
             , ss.screening_id
             , {field['agg']} AS {field['column']} 
         FROM
             snapshot_screening ss
             LEFT JOIN screening s ON ss.screening_id = s.screening_id
         WHERE
             s.status = '1'
             AND (s.ref_screening_id is not null or s.description = 'ROOT')
         GROUP BY
             ss.symbol_id, ss.screening_id
        """

    # Step 2. Paginate the DataFrame
    # Step 2.a. Get Page Number & calculate the offset
    page_number = int(request.GET.get('page', 1))
    offset = (page_number - 1) * page_size
    # Step 2.b. Get the total count
    count_query = f"""
        WITH summary AS ( {summary_query(showing_repeat_times)})
        , count AS (SELECT symbol_id FROM summary  GROUP BY symbol_id)
        SELECT COUNT(*) FROM count sd {whereStr};
    """
    total_count = 0
    try:
        total_count = pd.read_sql_query(
            count_query, engine, params=params).iloc[0, 0]
    except Exception as e:
        print(e.args)

    paginator = Paginator(range(total_count), page_size)

    # Step 3. Sorting parameters
    sort_column = request.GET.get('sortColumn', 'default_column')
    sort_direction = request.GET.get('sortDirection', 'asc')

    # Query to fetch the specific page data
    data_query = f"""
    WITH pivot_screening AS (
        SELECT *
        FROM crosstab(
            $$
            {summary_query(showing_repeat_times)}
            ORDER BY symbol_id, screening_id
            $$,
            $$ VALUES ('1'), ('6'),('7'),('8'),('9'),('10'),('11') $$
        ) AS pivot_table (
            symbol_id TEXT,
            /* 1*/BASE INT,
            /* 6*/REV_Q INT,
            /* 7*/REV_Y INT,
            /* 8*/ALL_Y INT,
            /* 9*/ALL_Q INT,
            /*10*/EPS_Y INT,
            /*11*/EPS_Q INT
        )
    ),pivot_last_showing AS (
        SELECT *
        FROM crosstab(
            $$
            {summary_query(last_showing)}
            ORDER BY symbol_id, screening_id
            $$,
            $$ VALUES ('1'), ('6'),('7'),('8'),('9'),('10'),('11') $$
        ) AS pivot_table (
            symbol_id TEXT,
            /* 1*/BASE_T DATE,
            /* 6*/REV_Q_T DATE,
            /* 7*/REV_Y_T DATE,
            /* 8*/ALL_Y_T DATE,
            /* 9*/ALL_Q_T DATE,
            /*10*/EPS_Y_T DATE,
            /*11*/EPS_Q_T DATE
        )
    ), summary AS (
        SELECT
            ps.symbol_id
            /*date column*/
            ,GREATEST(pls.base_t, pls.rev_q_t, pls.rev_y_t, pls.all_y_t, pls.all_q_t, pls.eps_y_t, pls.eps_q_t) AS time
            /*screening*/
           ,ps.base, ps.rev_q, ps.rev_y, ps.all_y, ps.all_q, ps.eps_y, ps.eps_q
           /*screening time*/
           ,pls.base_t, pls.rev_q_t, pls.rev_y_t, pls.all_y_t, pls.all_q_t, pls.eps_y_t, pls.eps_q_t
        FROM
            pivot_screening ps
            LEFT JOIN pivot_last_showing pls on ps.symbol_id = pls.symbol_id
    ),result_table as (
    SELECT
           ROW_NUMBER() OVER (ORDER BY sd.symbol_id, sd.time) AS row_num,
           /*Summary*/
           /*screening*/
            sd.symbol_id, sd.base, sd.rev_q, sd.rev_y, sd.all_y, sd.all_q, sd.eps_y, sd.eps_q
           /*screening time*/
           ,pls.base_t, pls.rev_q_t, pls.rev_y_t, pls.all_y_t, pls.all_q_t, pls.eps_y_t, pls.eps_q_t
           /*overview*/
           ,so.name, so.setup_rating, so.technical_rating,so.fundamental_rating
           ,so.relative_strength,so.percent_change
           ,so.one_month_performance,so.three_month_performance,so.six_month_performance
           ,so.price_earnings,so.market_cap,so.avg_volume_50
           /*technical*/
           ,st.lower_bollinger_band, st.upper_bollinger_band
           ,st."RSI_14",	st."MACD_12_26_9"
           ,st."ADX_14", st.asset_turnover ,st.daily_effective_ratio
           /*setup*/
           ,ss.market_cap, ss.high_52_week ,ss.weekly_support ,ss."GICS_sector"
           /*fundamental*/
           ,sf.valuation_rating ,sf."price_FCF" ,sf."PEG_next_year"
           ,sf.growth_rating ,sf."EPS_growth_Q2Q"
           ,sf.profitability_rating ,sf.high_growth_momentum_rating ,sf."avg_ROIC_5y" ,sf."FCF_margin"
           ,sf.health_rating, sf.interest_coverage
           ,sf.shares_outstanding_5y_change
           /*bull_flag*/
           ,sbf.bull_indicator, sbf.bull_flag , sbf.weekly_bull_flag
           ,sbf.bullish_engulfing_daily, sbf.bullish_hammer_daily, sbf.bullish_harami_daily
           ,sbf.bullish_engulfing_weekly, sbf.bullish_hammer_weekly, sbf.bullish_harami_weekly
           ,sbf.flag_type, sbf.flag_pole, sbf.flag_length, sbf.flag_width, sbf.weekly_flag_type

    FROM 
        summary sd
        LEFT JOIN pivot_last_showing pls ON sd.symbol_id = pls.symbol_id
        LEFT JOIN snapshot_overview so ON sd.symbol_id = so.symbol_id AND sd.time = so.time
        LEFT JOIN snapshot_technical st ON sd.symbol_id = st.symbol_id AND sd.time = st.time
        LEFT JOIN snapshot_setup ss ON sd.symbol_id = ss.symbol_id AND sd.time = ss.time
        LEFT JOIN snapshot_fundamental sf ON sd.symbol_id = sf.symbol_id AND sd.time = sf.time
        LEFT JOIN snapshot_bull_flag sbf ON sd.symbol_id = sbf.symbol_id AND sd.time = sbf.time
    )
    select * from result_table sd
    {whereStr}
    ORDER BY {sort_criteria}
    LIMIT {page_size} OFFSET {offset};
    """
    # print(data_query)
    try:
        snapshot_df = pd.read_sql_query(data_query, engine, params=params)
        snapshot_df = snapshot_df.replace({np.nan: None})  # Replace NaN with None
        snapshot_df = snapshot_df.applymap(lambda x: str(
            x) if isinstance(x, (int, decimal.Decimal, float)) else x)
        snapshot_data = snapshot_df.to_dict(orient='records')

        # Prepare the response data
        response_data = {
            'data': snapshot_data,
            'total': paginator.count
        }

        return JsonResponse(response_data)
    except Exception as e:
        print(e.args)
        return JsonResponse([])


def conStr_sqlalchemy():
    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    DB_NAME     = os.getenv('DB_NAME'     , None)
    DB_USERNAME = os.getenv('DB_USERNAME' , None)
    DB_PASS     = os.getenv('DB_PASS'     , None)
    DB_HOST     = os.getenv('DB_HOST'     , None)
    DB_PORT     = os.getenv('DB_PORT'     , None)
    # db_config = settings.DATABASES[DEFAULT_DB_ALIAS]
    db_name = DB_NAME
    db_user = DB_USERNAME
    db_password = quote(DB_PASS)
    db_host = DB_HOST
    db_port = DB_PORT
    conStr = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    return conStr


def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    try:
        portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

        if not portfolio:
            return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

        return render(
            request=request,
            template_name='pages/screening/snapshot_research.html',
            context= {
                'parent': 'screening',
                'segment': 'snapshot_research'})
    except Exception as e:
        print(e.args)
