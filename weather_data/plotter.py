from datetime import datetime
from dateutil import tz
from typing import Union, Iterable, List

import calendar
import click
import pandas
import plotly.graph_objects as go
import plotly.express as px

METRIC_COLORS = px.colors.cyclical.mrybm * 2
# METRIC_COLORS = px.colors.sequential.Electric * 2


# Based on https://plotly.com/python/range-slider/.
def create_plot(df: pandas.DataFrame, html_name: str):
  # Create figure
  fig = go.Figure()

  axis_domain_size = 1.0 / 12
  y_axes = {}
  for i in range(12):
    monthly_df = df[df['datetime'].dt.month == i + 1]
    print(monthly_df)
    y_data = []
    y_str = '' if i == 0 else str(i + 1)
    fig.add_trace(
        go.Scatter(
            x=[dt.time() for dt in monthly_df['datetime']],
            y=monthly_df['QPCP'],
            name=calendar.month_name[i + 1],
            # text=[p.description for p in pts],
            yaxis=f'y{y_str}',
            marker=dict(color=METRIC_COLORS[i]),
        ))
    y_axes[f'yaxis{y_str}'] = dict(
        anchor='x',
        autorange=True,
        domain=[axis_domain_size * i, axis_domain_size * (i + 1)],
        linecolor=METRIC_COLORS[i],
        mirror=True,
        range=[min(y_data), max(y_data)],
        showline=True,
        side='right',
        tickfont={'color': METRIC_COLORS[i]},
        tickmode='auto',
        ticks='',
        title=calendar.month_name[i + 1],
        titlefont={'color': METRIC_COLORS[i]},
        type='linear',
        zeroline=False)

  # style all the traces
  fig.update_traces(
      hoverinfo='name+x+text',
      # https://plotly.com/python/line-charts/
      line=dict(width=1.5, shape='hv'),
      marker={'size': 8},
      mode='lines+markers',
      showlegend=False)

  # Update axes
  fig.update_layout(xaxis=dict(
      autorange=True,
      range=[parse_datetime('00:00'), parse_datetime('24:00')],
      rangeslider=dict(
          autorange=True,
          range=[parse_datetime('00:00'), parse_datetime('24:00')],
      ),
      type='date'),
      **y_axes)

  # Update layout
  fig.update_layout(
      title='Glucose monitoring data',
      legend_title='Legend',
      dragmode='zoom',
      hovermode='closest',
      legend=dict(traceorder='reversed'),
      height=2000,
      template='plotly_white',
      margin=dict(t=50, b=50),
  )

  fig.write_html(html_name)


def parse_datetime(s: Union[str, datetime]) -> datetime:
  if isinstance(s, datetime):
    return s
  for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y%m%d %H:%M', '%H:%M'):
    try:
      return datetime.strptime(s, fmt).replace(tzinfo=DEFAULT_TIMEZONE)
    except ValueError:
      pass
  raise ValueError('no valid date format found')


DEFAULT_TIMEZONE = tz.gettz('PST')


@click.command()
@click.option('--datafile')
@click.option('--station',
              default='SEATTLE SAND POINT WEATHER FORECAST OFFICE WA US')
@click.option('--start_date', default='2000-01-01')
@click.option('--end_date',
              default=datetime.now().replace(tzinfo=DEFAULT_TIMEZONE))
def main(datafile: str, station: str, start_date: str, end_date: str):
  # start_date, end_date = parse_datetime(start_date), parse_datetime(end_date)

  df = pandas.read_csv(datafile)
  # df = df[df['STATION_NAME'] == station]
  df = df[-df['QPCP'].isin({999.99, -9999.99, -9999.00})]
  df['datetime'] = df['DATE'].map(parse_datetime)
  print(df)
  print(set(df['QPCP']))

  create_plot(df, 'out.html')


if __name__ == '__main__':
  main()