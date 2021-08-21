from datetime import datetime
from dateutil import tz
from typing import Union, Iterable, List

import calendar
import click
import pandas
import plotly.graph_objects as go
import plotly.express as px
from tqdm import tqdm


# Amount of rain required for the code to consider it to be raining.
IT_RAINED_CUTOFF = 0.3

METRIC_COLORS = px.colors.cyclical.mrybm * 2
# METRIC_COLORS = px.colors.sequential.Electric * 2


# Based on https://plotly.com/python/range-slider/.
def create_plot(df: pandas.DataFrame, datafile: str):
  fig = go.Figure()
  axis_domain_size = 1.0 / 12
  y_axes = {}
  for i in range(12):
    monthly_df = df[df['datetime'].dt.month == i + 1].sort_values('time')
    agg_df = monthly_df.groupby('time', as_index=False).agg(
        {'itrained': ['mean', 'std']})
    print(agg_df)

    # Setup Y-Axis
    y_str = '' if i == 0 else str(i + 1)
    y_axes[f'yaxis{y_str}'] = dict(
        anchor='x',
        domain=[axis_domain_size * i, axis_domain_size * (i + 1)],
        linecolor=METRIC_COLORS[i],
        mirror=True,
        range=[0.0, 0.5],
        showline=True,
        side='right',
        tickfont={'color': METRIC_COLORS[i]},
        tickmode='auto',
        ticks='',
        title=calendar.month_name[i + 1],
        titlefont={'color': METRIC_COLORS[i]},
        type='linear',
        zeroline=False)

    # Data
    fig.add_trace(go.Scatter(
        name=calendar.month_name[i + 1],
        x=agg_df['time'],
        y=agg_df['itrained', 'mean'],
        mode='lines',
        yaxis=f'y{y_str}',
        line=dict(color=METRIC_COLORS[i]),
    ))

    # Average Line with label
    overall_mean = agg_df['itrained', 'mean'].mean()
    fig.add_trace(go.Scatter(
        x=[list(agg_df['time'])[-int(0.06 * len(agg_df['time']))]],
        y=[overall_mean + 0.05],
        text=[f'<b>{100 * overall_mean:.1f}% chance</b>'],
        mode="text",
        yaxis=f'y{y_str}',
        marker=dict(color='black'),
    ))
    fig.add_trace(go.Scatter(
        x=agg_df['time'],
        y=[overall_mean for _ in agg_df['time']],
        yaxis=f'y{y_str}',
        marker=dict(size=0, color='rgba(0, 0, 0, 0.3)'),
        line_dash='dash'))

    # Error bars.
    error_bar_color = 'rgba(68, 68, 68, 0.2)'
    error_bar_options = dict(
        marker=dict(size=0, color=error_bar_color),
        line=dict(width=0),
        yaxis=f'y{y_str}',
        mode='lines')
    fig.add_trace(go.Scatter(
        name='Lower Bound',
        x=agg_df['time'],
        y=(agg_df['itrained', 'mean'] - agg_df['itrained', 'std']).clip(0),
        **error_bar_options
    ))
    fig.add_trace(go.Scatter(
        name='Upper Bound',
        x=agg_df['time'],
        y=agg_df['itrained', 'mean'] + agg_df['itrained', 'std'],
        fillcolor=error_bar_color,
        fill='tonexty',
        **error_bar_options
    ))

  # style all the traces
  fig.update_traces(
      hoverinfo='name+x+text',
      showlegend=False)

  # Update axes
  fig.update_layout(**y_axes)

  fig.update_layout(
      title=(
          f'24 Hour Precipitation ({datafile}) <br>'
          '<sup>Units: 1/100 of an inch (15min windows)</sup>'),
      dragmode='zoom',
      hovermode='closest',
      height=2000,
      template='plotly_white',
      margin=dict(t=50, b=50),
  )

  fig.write_html(f'{datafile}.html')
  fig.write_json(f'{datafile}.json')


def parse_datetime(s: Union[str, datetime]) -> datetime:
  if isinstance(s, datetime):
    return s
  for fmt in (
      '%Y-%m-%d %H%M', '%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y%m%d %H:%M',
      '%H:%M'):
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

  if True:
    # NEW CSV FILE
    raw_df = pandas.read_csv(datafile)
    time_columns = [c for c in raw_df.columns if 'Val' in c]
    dicts = []
    for idx, row in tqdm(raw_df.iterrows()):
      for tc in time_columns:
        dicts.append(
            dict(QGAG=float(row[tc]),
                 datetime=parse_datetime(f'{row["DATE"]} {tc[:4]}')))
    df = pandas.DataFrame(dicts)
  else:
    # OLD CSV FILE
    df = pandas.read_csv(datafile)
    # df = df[df['STATION_NAME'] == station]
    df['datetime'] = df['DATE'].map(parse_datetime)
  df = df[-df['QGAG'].isin({999.99, -9999.99, -9999.00})]
  df['itrained'] = df['QGAG'].map(
      lambda qgag: 1.0 if qgag >= IT_RAINED_CUTOFF else 0.0)
  df['time'] = df['datetime'].map(lambda dt: dt.time())
  print(df)
  print(set(df['QGAG']))

  create_plot(df, datafile)


if __name__ == '__main__':
  main()
