from django.urls import path
from home.views import screening

#all below path with [screening]
urlpatterns = [

    ####### screening.screening_criteria #######
    # Screening Criteria -> Default
    path('screening_criteria/', screening.screening_criteria.default, name='screening_criteria'),
    # Screening Criteria -> Search
    path('stock/search/', screening.screening_criteria.stock_search, name='stock_search'),

    # Menu: Research
    # Screening Criteria -> Screener
    path('stock/screener/', screening.screening_criteria.stock_screener, name='stock_screener'),
    # Screening Criteria -> Stock -> Charts
    path('stock/charts/', screening.screening_criteria.stock_charts, name='stock_charts'),
    # Screening Criteria -> Stock -> Detail
    path('api/stock_data', screening.screening_criteria.get_stock_data, name='get_stock_data'),

    ####### screening.snapshot_research #######
    # Saved Screeners -> Default
    path('snapshot_research/', screening.snapshot_research.default, name='snapshot_research'),

    path('snapshot/fetching/data', screening.snapshot_research.fetching, name='snapshot_fetching'),

    ####### screening.screening_results #######
    # Screening Result -> Default
    path('screening_result/', screening.screening_results.default, name='screening_results'),

    path('rating/output/', screening.screening_results.output, name='screening_output'),


    ####### screening.quote #######
    # Screening Quote -> Default
    path('stock/quote/<str:symbol>', screening.quote.default, name="stock_quote"),


]