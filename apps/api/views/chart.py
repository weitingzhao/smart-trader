import matplotlib
matplotlib.use('Agg')

import calendar
from django.contrib.staticfiles import finders
from matplotlib.ticker import MaxNLocator, FuncFormatter
from datetime import datetime, timedelta
import mplfinance as mpf
import numpy as np
import pandas as pd
from PIL import Image, ImageFont, ImageDraw
from django.db.models import Count
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from apps.api.serializers.chart import ChartExchangeSerializer, ChartSymbolSerializer
from apps.common.models import MarketSymbol, MarketStockHistoricalBarsByDay

class ChartExchangeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartExchangeSerializer

    def get_queryset(self):
        return MarketSymbol.objects.values('market').annotate(total=Count('symbol'))

class ChartSymbolViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartSymbolSerializer
    lookup_field = 'symbol'

    def get_queryset(self):
        market = self.kwargs.get('market')
        if market:        # Filter MarketSymbol objects by market
            return MarketSymbol.objects.filter(market=market)
        return MarketSymbol.objects.all()


    def No_Symbol_Found(self, symbol, width, height)-> HttpResponse:
        # Create an image with the text "No Data Found"
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        d = ImageDraw.Draw(img)

        # Load a true type font with a larger size
        font_path = finders.find('assets/fonts/dejavu-sans-bold.ttf')  # Use finders to locate the font file
        font_size = 24  # Set the desired font size
        font = ImageFont.truetype(font_path, font_size)

        text = f"symbol [{symbol}] Not Found"
        text_bbox = d.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        d.text((text_x, text_y), text, fill=(0, 0, 0), font=font)

        # Save the image to a BytesIO object
        import io
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        # Return the image as a response
        return HttpResponse(buf, content_type='image/png')

    def fetch_data(self, symbol, interval, elements=None):
        # Base query
        query = MarketStockHistoricalBarsByDay.objects.filter(symbol=symbol)

        # add 200 since results include SMA_200
        elements = elements + 200

        # Filter based on elements
        if elements:
            query = query.order_by('-time')[:elements]
        else:
            # Filter based on interval
            if interval == 'daily':
                cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(days=16 * 30)  # Approx 16 months
            elif interval == 'weekly':
                cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(weeks=7 * 52)  # 7 years
            elif interval == 'monthly':
                cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(weeks=16 * 52)  # 16 years

            cutoff_date = pd.Timestamp(cutoff_date, tz='UTC')  # Ensure cutoff_date is datetime with UTC
            query = query.filter(time__gte=cutoff_date)

        # Convert query to DataFrame
        stock_data = query.values('time', 'open', 'high', 'low', 'close', 'volume')
        df = pd.DataFrame(list(stock_data))

        if len(df) == 0:
            return df

        df['time'] = pd.to_datetime(df['time'], utc=True)  # Ensure 'time' column is datetime with UTC
        # Sort DataFrame by time in ascending order
        df = df.sort_values(by='time', ascending=True)

        # Calculate 50-day and 200-day SMA
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()

        if interval == 'weekly':
            df.set_index('time', inplace=True)
            df = df.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'SMA_50': 'last',
                'SMA_200': 'last'
            }).dropna().reset_index()
        elif interval == 'monthly':
            df.set_index('time', inplace=True)
            df = df.resample('M').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'SMA_50': 'last',
                'SMA_200': 'last'
            }).dropna().reset_index()

        return df


    @action(detail=True, methods=['get'])
    def symbol(self, request, symbol, width, height, timeframe, chart_type, elements):
        # Convert timeframe and chart_type to lowercase
        timeframe = timeframe.lower()
        chart_type = chart_type.lower()

        # Step 1. Fetching Data.
        data = self.fetch_data(symbol, timeframe, elements)
        if len(data) == 0:
            return self.No_Symbol_Found(symbol, width, height)

        # Step 2. Prepare dataframe
        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        df = df.tail(elements)

        # Check if DataFrame is empty after fetching data
        if df.empty:
            return self.No_Symbol_Found(symbol, width, height)

        # Step 3. Map chart types
        chart_type_mapping = {
            'bars': 'ohlc',
            'candles-full': 'candle',
            'candles-hollow': 'hollow_candle',
            'heikin-ashi': 'heikin',
            'line': 'line'
        }
        mpf_chart_type = chart_type_mapping.get(chart_type, 'candle')  # Default to 'candle' if type not found

        # Step 4. Define custom style
        mpf_style = mpf.make_mpf_style(
            base_mpf_style='classic',
            marketcolors=mpf.make_marketcolors(
                up='#00FF00', down='#FF0000',
                edge='inherit',
                wick='inherit',
                volume='inherit'
            ),
            facecolor='#424242',  # Set background color to #424242
            figcolor='#424242',  # Set figure background color to #424242
            edgecolor = '#424242'  # Set edge color to match background color
        )
        width_config = {'candle_linewidth': 0.8, 'candle_width': 0.725, 'volume_width': 0.725}


        # Create additional plots for SMA_50 and SMA_200
        plots = []
        if np.isnan(df['SMA_50']).all() is np.False_:
            plots.append(mpf.make_addplot(df['SMA_50'], color='#0000FF', width=0.5))
        if np.isnan(df['SMA_200']).all() is np.False_:
            plots.append(mpf.make_addplot(df['SMA_200'], color='#FF0000', width=0.5))

        # Step 5. Build Chart
        dpi = 100
        width_in = width / dpi
        height_in = height / dpi

        fig, axes = mpf.plot(
            df,
            type=mpf_chart_type,
            style=mpf_style,
            returnfig=True,
            volume=True,
            volume_panel=1,
            volume_alpha=0.5,
            figsize=(width_in, height_in),
            scale_padding={'left': 0.13, 'top': 2, 'right': 1.3, 'bottom': 0.5},
            panel_ratios=(1, 0.3),
            xrotation=0,
            update_width_config=width_config,
            tight_layout=True,
            addplot=plots
        )

        # Get the last non-NaN values for SMA_50 and SMA_200
        last_sma_50 = df['SMA_50'].dropna().iloc[-1]
        last_sma_200 = df['SMA_200'].dropna().iloc[-1]

        # Retrieve the symbol name
        symbol_name = MarketSymbol.objects.get(symbol=symbol).name

        # Calculate the percentage change
        last_row = df.iloc[-1]
        previous_close = df['close'].iloc[-2]
        percent_change = ((last_row['close'] - previous_close) / previous_close) * 100

        # Determine the color and sign for the percentage change
        if percent_change > 0:
            percent_text = f'+{percent_change:.2f}%'
            percent_color = '#00FF00'  # Green color
        else:
            percent_text = f'{percent_change:.2f}%'
            percent_color = '#FF0000'  # Red color

        # 1st line.
        # Add symbol and timeframe to the top left with larger font
        fig.text(0.01, 0.98, f'{symbol}, {timeframe}', color='#8C8C8C', fontsize=16, ha='left', va='top', weight='bold')
        # Add symbol name to the top middle
        fig.text(0.5, 0.98, f'{symbol_name}', color='#8C8C8C', fontsize=16, ha='center', va='top', weight='bold')
        # Add last closed price to the top right with larger font
        fig.text(0.92, 0.98, f'{last_row["close"]:.2f}', color='#8C8C8C', fontsize=16, ha='right', va='top', weight='bold')
        # Add percentage change to the top right with smaller font
        fig.text(0.97, 0.98, f'{percent_text}', color=percent_color, fontsize=11, ha='right', va='top')
        # Add copyright text to the bottom right
        fig.text(0.075, 0.07, '© SmartTrader', color='#2196f3', fontsize=10, ha='right', va='bottom',weight='bold',
                 bbox=dict(facecolor='#424242', edgecolor='none', boxstyle='round,pad=0.05'))

        # 2nd line.
        # Add last time and OHLCV values to the figure
        fig.text(0.01, 0.93,
                 f'{last_row.name.strftime("%d %b %Y")}   '
                 f'O: {last_row["open"]:.2f},  H: {last_row["high"]:.2f},  '
                 f'L: {last_row["low"]:.2f},  C: {last_row["close"]:.2f},    '
                 f'V: {last_row["volume"]:.0f}',
                 color='#CCCCCC', fontsize=10, ha='left', va='top',
                 bbox=dict(facecolor='#424242', edgecolor='none', boxstyle='round,pad=0.3'))

        # 3rd ~ line.
        # Add SMA labels with last values to the figure
        fig.text(0.01, 0.90, f'- sma (50) {last_sma_50:.2f}', color='#0000FF', fontsize=10, ha='left', va='top',
                 bbox=dict(facecolor='#424242', edgecolor='none', boxstyle='round,pad=0.3'))
        fig.text(0.01, 0.87, f'- sma (200) {last_sma_200:.2f}', color='#FF0000', fontsize=10, ha='left', va='top',
                 bbox=dict(facecolor='#424242', edgecolor='none', boxstyle='round,pad=0.3'))


        # Access the first axis
        ax = axes[0]
        ax.set_ylabel('') # Disable y-axis label
        ax.tick_params(axis='x', colors='#888888')
        ax.tick_params(axis='y', colors='#888888')

        # Set ax_volume
        ax_volume = axes[2] # Access the volume axis (assuming it's the second axis in the list)
        ax_volume.set_ylabel('') # Disable y-axis label for the volume panel
        ax_volume.tick_params(axis='x', colors='#888888')
        ax_volume.tick_params(axis='y', colors='#888888')
        def volume_formatter(x, pos):
            return f'{x / 1000:.0f}k'
        ax_volume.yaxis.set_major_formatter(FuncFormatter(volume_formatter))

        max_ticks = int(elements / 2)  # Adjust factor as needed
        ax.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks))
        ax.xaxis.grid(True, linestyle='-', color='#888888', linewidth=0.5)
        ax_volume.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks))
        ax_volume.xaxis.grid(True, linestyle='-', color='#888888', linewidth=0.5)

        ax.yaxis.set_major_locator(MaxNLocator(nbins=12))  # Adjust nbins to control spacing
        ax.yaxis.grid(True, linestyle='-', color='#888888', linewidth=0.5)
        ax_volume.yaxis.set_major_locator(MaxNLocator(nbins=5))  # Adjust nbins to control spacing
        ax_volume.yaxis.grid(True, linestyle='-', color='#888888', linewidth=0.5)

        def custom_date_formatter(x, pos, date_min):
            # print(f"x={x}, pos={pos}")
            index = int(x)
            if(index < 0 or index >= len(date_min)):
                return ''
            date = date_min[index]
            last_day_of_month = calendar.monthrange(date.year, date.month)[1]
            if date.day == last_day_of_month:
                return date.strftime('%b')
            elif date.day == 1:
                if date.month == 1:
                    return date.strftime('%Y')
                else:
                    return date.strftime('%b')
            else:
                return date.strftime('%d')
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: custom_date_formatter(x,pos, date_min=df.index)))

        # Step 6. Add symbol and symbol name to the figure
        # symbol_name = MarketSymbol.objects.get(symbol=symbol).name
        # fig.text(0.5, 0.5,
        #          f'{symbol}, {timeframe}\n{symbol_name}',
        #          ha='center', va='center', color='#494949',
        #          fontsize=60, fontdict={'weight': 'bold'}, alpha=1
        # )

        # Step 7. Return Img
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

