import pandas as pd
import numpy as np
from home.forms.portfolio import *
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import decimal

@csrf_exempt
def fetching(request):

    # Step 0. Check input parameters
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    holdings = Holding.objects.filter(portfolio=portfolio)
    if len(holdings) <= 0:
        return None, None

    page_size = 20

    # Step 1. Prepare summary query script
    showing_repeat_times = {'agg': 'COUNT(ss.*)', 'column': 'showing_repeat_times'}
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
        , count AS (SELECT symbol_id FROM summary GROUP BY symbol_id)
        SELECT COUNT(*) FROM count;
    """
    total_count = pd.read_sql_query(count_query, connection).iloc[0, 0]
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
    )
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
    ORDER BY sd.symbol_id, sd.time
    LIMIT {page_size} OFFSET {offset};
    """
    snapshot_df = pd.read_sql_query(data_query, connection)
    snapshot_df = snapshot_df.replace({np.nan: None})  # Replace NaN with None
    snapshot_df = snapshot_df.applymap(lambda x: str(x) if isinstance(x, (int, decimal.Decimal, float)) else x)
    snapshot_data = snapshot_df.to_dict(orient='records')

    # Prepare the response data
    response_data = {
        'data': snapshot_data,
        'total': paginator.count
    }

    return JsonResponse(response_data)



def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    return render(
        request=request,
        template_name='pages/screening/snapshot_research.html',
        context= {
            'parent': 'screening',
            'segment': 'snapshot_research'
        })