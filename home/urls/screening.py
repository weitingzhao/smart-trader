from django.urls import path
from home.views import screening

#all below path with [screening]
urlpatterns = [

    ####### screening.screening_criteria #######
    # Screening Criteria -> Default
    path(
        'screening_criteria/',
        screening.screening_criteria.default,
        name='screening_criteria'),

    # Screening Criteria -> Search
    path(
        'stock/search/',
        screening.screening_criteria.stock_search,
        name='stock_search'),

    # Menu: Research
    # Screening Criteria -> Screener
    path(
        'stock/screener/',
        screening.screening_criteria.stock_screener,
        name='stock_screener'),
    # Screening Criteria -> Stock -> Charts
    path(
        'stock/charts/',
        screening.screening_criteria.stock_charts,
        name='stock_charts'),
    # Screening Criteria -> Stock  -> Quote
    path(
        'stock/quote/<str:symbol>',
        screening.screening_criteria.stock_quote,
        name="stock_quote"),

    # Screening Criteria -> Stock -> Detail
    path(
        'api/stock_data',
        screening.screening_criteria.get_stock_data,
        name='get_stock_data'),

    ####### screening.saved_screeners #######
    # Saved Screeners -> Default
    path(
        'saved_screeners/',
        screening.saved_screeners.default,
        name='saved_screeners'),

    ####### screening.screening_results #######
    # Screening Result -> Default
    path(
        'screening_result/',
        screening.screening_results.default,
        name='screening_results'),

]