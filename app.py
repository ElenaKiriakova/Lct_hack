import dash
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_auth
import dash_renderer


import pandas as pd
import modin.pandas as mpd
import numpy as np
import dask.dataframe as dd
import datetime as dt
import time

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

import visdcc




import vaex as vx

"""  LOAD DATA  """

dtypes_or_df = dict(ind_name='int8',
                    napr='str',
                    nastranapr='str',
                    tnved='str',
                    edizm='category',
                    # stoim='str',
                    # netto='str',
                    # kol='float16',
                    region='str',
                    region_s='str',
                    region_num='str',
                    region_s_num='str',
                    product_name='str',
                    category_kod='str',
                    okved='str',
                    category_name='str',
                    nastranapr_name='str',
                    # revenue_2021='float32',
                    # profit_2020='float32',
                    # profit_2021='float32',
                    )

# df = dd.read_csv('data_merge.csv',
#                  dtype=dtypes_or_df).compute()

df = pd.read_csv('data_merge.csv',
                 dtype=dtypes_or_df,
                 encoding='utf8',
                 decimal=',',
                 # error_bad_lines=False,
                 # index_col='ind_name',
                 # engine='c',
                 # iterator=True,
                 # chunksize=40000000,
                 )





# df['period'] = pd.to_datetime(df['period'])
df['stoim'] = df['stoim'].astype('float64').round(0)
df['netto'] = df['netto'].astype('float64').round(0)
df['revenue_2020'] = df['revenue_2020'].astype('float64').round(0)
df['revenue_2021'] = df['revenue_2021'].astype('float64').round(0)
df['profit_2020'] = df['profit_2020'].astype('float64').round(0)
df['profit_2021'] = df['profit_2021'].astype('float64').round(0)
df['im_minus_ex'] = df['im_minus_ex'].astype('float32').round(0)


"""  START DASH  """

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP]
                )


'''AUTINTIFICATION'''

auth = dash_auth.BasicAuth(
    app,
    {'aaa': '111',
     'query': '12345'}
)



'''  SLIDERS  '''

# создаем слайдер для выбора категории товара
category_type_selector = dcc.Dropdown(
    id='product-selector',
    options=df['category_name'].unique(),
    value=df['category_name'].unique()[1],
    multi=False,
    optionHeight=40)

# слайдер для выбора региона
region_name_selector = dcc.Dropdown(
    options=df['region_s'].unique(),
    value=df['region_s'].unique()[1],
    id='region-selector',
    multi=False,
    optionHeight=30)

# слайдер для выбора региона
oblast_name_selector = dcc.Dropdown(

    options=df['region_s'].unique(),
    id='oblast-selector',
    multi=True,
    optionHeight=30, )

# слайдер для выбора страны направления
str_napr = dcc.Dropdown(

    options=df['nastranapr_name'].unique(),
    value=df['nastranapr_name'].unique(),
    id='nastranapr-selector',
    multi=True,
    optionHeight=30)

# слайдер для выбора экспорт/импорт

napr_ek_im = dcc.Dropdown(

    options=df['napr'].unique(),
    value=df['napr'].unique(),
    id='ek-im-selector',
    multi=True,
    optionHeight=30)

# слайдер для выбора оквэда

okved_slider = dcc.Dropdown(

    options=sorted(df['okved'].unique()),
    value=df['okved'].unique()[0],
    id='okved-char',
    multi=False,
    optionHeight=30)


# слайдер для выбора тнведа
tnved_slider = dcc.Dropdown(

    options=sorted(df['tnved'].unique()),
    value=df['tnved'].unique()[1],
    id='tnved-char',
    multi=False,
    optionHeight=30)


# слайдер для выбора имени продукта
tnved_product = dcc.Dropdown(

    options=df['product_name'].unique(),
    value=df['product_name'].unique()[1],
    id='product-char',
    multi=False,
    optionHeight=60)


"""  LAYOUT  """

app.layout = html.Div([

    # header
    dbc.Row([], className='header'),
    dbc.Row([

        # barside LEFT
        # dbc.Col([], className='barside', width={'size': 1}),

        # main_side
        dbc.Col([
            dbc.Row([

                dbc.Col([
                ], id='head-TAG', width={'size': 12}),

            ]),

            # ЗАГОЛОВОК СТАТИСТИКА
            dbc.Row(['СТАТИСТИКА ПО СУБЪЕКТАМ'], className='title-stat', justify='center'),

            dbc.Row(['В данном разделе находится статистика: какие категории продукта являются наиболее востребованными по субъектам.'], className='text'),
            dbc.Row(['Для просмотра выберите параметры:'], className='text'),
            dbc.Row(["- Федеральный округ;"], className='text'),
            dbc.Row(["- Субъект;"], className='text'),
            dbc.Row(["- Импорт\Экспорт;"], className='text'),
            dbc.Row(["- Страна направления (из какой страны /в какую страну осуществляется импорт/экспорт); "], className='text'),

            # графики
            dbc.Row([
                # RIGHT main col sect 2
                dbc.Col([
                    dbc.Row([
                        html.Div(id='graph-container', children=[], className='figs')
                    ])

                ], width={'size': 6}),

                #  LEFT main col sect 2

                dbc.Col([
                    dbc.Row([
                        html.Div(id='graph-container-all', children=[], className='figs')
                    ]),

                    dbc.Row([

                    ])

                ], width={'size': 6}),

            ]),
            dbc.Row(['СТАТИСТИКА ПО ПРОДУКТАМ'], className='title-stat', justify='center'),
            dbc.Row(['В данном разделе находится статистика: в каких субъектах наиболее востребована выбранная категория продукта.'], className='text'),
            dbc.Row(['Для просмотра выберите параметры:'], className='text'),
            dbc.Row(["- Федеральный округ;"], className='text'),
            dbc.Row(["- Выбор продукта"], className='text'),
            dbc.Row(["- Импорт\Экспорт;"], className='text'),
            dbc.Row(["- Страна направления (из какой страны /в какую страну осуществляется импорт/экспорт); "], className='text'),

            dbc.Row([

                #  LEFT main col sect 3
                dbc.Col([
                    dbc.Row([
                        html.Div(id='graph-container-pie', children=[])
                    ], className='figs')

                ], width={'size': 6}),

                #  RIGHT main col sect 3
                dbc.Col([
                    dbc.Row([
                        html.Div(id='graph-container-prod-graf', children=[])
                    ], className='figs')
                ], width={'size': 6}),
            ]),

            dbc.Row(['ТАБЛИЦА ДАННЫХ'], className='title-stat', justify='center'),
            dbc.Row(['В таблице представлены данные статистики по продуктам.'], className='text'),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        dash_table.DataTable(
                            id='datatable-interactivity',
                            # editable=True,
                            # filter_action="custom",
                            # filter_query='',
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            row_selectable="multi",
                            # row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            # page_current=0,
                            fill_width=True,
                            page_size=10,
                            style_cell={
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'maxWidth': '700px',

                                        },

                        ),
                    ]),
                ], className='tables', width={'size': 10}),
            ]),

            dbc.Row(['ПЕРСПЕКТИВНЫЕ НАПРАВЛЕНИЯ ДЛЯ ИМПОРТЗАМЕЩЕНИЯ'], className='title-stat', justify='center'),

            dbc.Row(['В данном разделе находится статистика: сводная информация по самым перспективным направлениям для импортзамещения'],
                    className='text'),
            dbc.Row(['Для просмотра выберите параметры:'], className='text'),
            dbc.Row(["- Федеральный округ;"], className='text'),
            dbc.Row(["- Субъект;"], className='text'),
            dbc.Row(["- Выбор продукта;"], className='text'),
            dbc.Row(["- Страна направления (из какой страны /в какую страну осуществляется импорт/экспорт); "],
                    className='text'),
            dbc.Row(["- ОКВЭД; "],
                    className='text'),



            dbc.Row(['Выберите ОКВЭД:'], className='text text-select'),
            dbc.Row([
                dbc.Col([
                    html.Div(okved_slider),
                ], width={'size': 6})
            ], className='select-main-side'),
            dbc.Row(['Таблица с наиболее перспективными категориями продукции для импортзамещения в выбранном субъекте:'], className='text'),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dash_table.DataTable(
                            id='datatable-okved',
                            # editable=True,
                            # filter_action="custom",
                            # filter_query='',
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            row_selectable="multi",
                            # row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            # page_current=0,
                            page_size=10,
                            fill_width=True,
                            style_cell={
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'maxWidth': '400px',

                                    },
                        ),
                    ]),
                ], className='tables', width={'size': 10}),

            ]),

            dbc.Row([
                dbc.Col([
                    html.Div(id='graph-container-okved-rev', children=[]),
                ], width={'size': 8}),
            ]),
            dbc.Row(['СТАТИСТИКА ПО ТНВЭД'], className='title-stat', justify='center'),

            dbc.Row(['В данном разделе находится статистика: по ТНВЭД продукции.'],
                    className='text'),
            dbc.Row(['Для просмотра выберите параметры:'], className='text'),
            dbc.Row(["- Федеральный округ;"], className='text'),
            dbc.Row(["- Субъект;"], className='text'),
            dbc.Row(["- ТНВЭД;"], className='text'),
            dbc.Row(["- Страна направления (из какой страны /в какую страну осуществляется импорт/экспорт); "],
                    className='text'),


            dbc.Row(['Выберите ТНВЭД продукта:'], className='text text-select'),
            dbc.Row([
                dbc.Col([tnved_slider
                ], width={'size': 4}),
            ], className='select-main-side'),
            dbc.Row(['Название продукта:'], className='text'),
            dbc.Row([
                dbc.Col([
                    html.Div(id='tnvd-name'),

                     ], width={'size': 6}),
                ], className='text-as-site'),

            dbc.Row(['Таблица данных распределения количества продукта в зависимости от выбранного ТНВЭД и субъекта:'],
                    className='text text-margin'),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        dash_table.DataTable(
                            id='datatable-tnved',
                            # editable=True,
                            # filter_action="custom",
                            # filter_query='',
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            row_selectable="multi",
                            # row_deletable=False,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            # page_current=0,
                            page_size=10,
                            fill_width=True,
                            style_cell={
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': '400px',

                            },
                        ),
                    ]),
                ], className='tables table-bottom', width={'size': 10}),

            ]),


            dbc.Row([
                dbc.Col([
                    html.Div(id='tnvd-graphpie', children=[], className='figs'),
                    ], width={'size': 6}),

                dbc.Col([
                    html.Div(id='tnvd-graph', children=[], className='figs'),
                    ], width={'size': 6}),

                ]),





        ], className='wrapper'),

        # barside RIGHT
        dbc.Col([
            dbc.Row(['ВЫБОР ПАРАМЕТРОВ'], justify='center'),
            dbc.Row([
                html.Div(['ФЕДЕРАЛЬНЫЙ ОКРУГ'], className='selector-title'),
                # категория продукции
                html.Div(region_name_selector, className='selector-box')
            ]),
            dbc.Row([
                html.Div(['СУБЪЕКТ'], className='selector-title'),
                # категория продукции
                html.Div(oblast_name_selector, className='selector-box')
            ]),
            dbc.Row([
                html.Div(['ВЫБОР ПРОДУКТА'], className='selector-title'),
                html.Div(category_type_selector, className='selector-box')
            ]),
            dbc.Row([
                html.Div(['ИМПОРТ\ЭКСПОРТ'], className='selector-title'),
                html.Div(napr_ek_im, className='selector-box')
            ]),
            dbc.Row([
                html.Div(['СТРАНА НАПРАВЛЕНИЯ'], className='selector-title'),
                dbc.Col(str_napr, className='selector-box'),
            ]),

            dbc.Row([dbc.Col([html.Button(["ВЫБРАТЬ ВСЕ СТРАНЫ"], id="select-all", n_clicks=0)], width={'size': 10}),
            ]),

            dbc.Row(['СПРАВОЧНИК ПО ТНВЭД'], justify='center'),
            dbc.Row([
                dbc.Col(tnved_product, className='selector-box'),
                html.Div(['ТНВЭД:'], className='selector-title-text'),
                html.Div(id='prod-name', className='text-as-site-bar'),
                html.Div(['Категория продукта:'], className='selector-title-text'),
                html.Div(id='cat-name', className='text-as-site-bar'),
            ]),

            dbc.Row([
                html.Div([
                    html.Button('ПЕЧАТЬ ОТЧЕТА', id='click1'),
                    visdcc.Run_js(id='javascript')
                ]),
            ]),

            dbc.Row([]),
            dbc.Row([]),
            dbc.Row([]),
        ], className='barside', width={'size': 3})
    ]),
    dbc.Row([], className='header'),

], className='main-wrapper')

'''  CALLBACKS  '''
'''  FILTER DATASETS'''

'''FILTER REGION'''


@app.callback(
    Output('oblast-selector', 'options'),
    Output('oblast-selector', 'value'),
    Input('region-selector', 'value'),
)
def set_cities_options(chosen_state):
    dff = df[df.region_s == chosen_state]
    counties_of_states = [{'label': c, 'value': c} for c in sorted(dff.region.unique())]
    values_selected = [x['value'] for x in counties_of_states]
    return counties_of_states, values_selected


'''FIGURS'''


@app.callback(
    Output('graph-container-all', 'children'),
    Output('graph-container', 'children'),
    Output('graph-container-pie', 'children'),
    Output('graph-container-prod-graf', 'children'),
    Output('datatable-interactivity', "data"),
    Output('datatable-interactivity', 'columns'),
    Output('datatable-okved', "data"),
    Output('datatable-okved', 'columns'),
    Output('graph-container-okved-rev', 'children'),
    Output('tnvd-name', 'children'),
    Output('tnvd-graphpie', 'children'),
    Output('tnvd-graph', 'children'),
    Output('datatable-tnved', "data"),
    Output('datatable-tnved', 'columns'),
    Output('prod-name', 'children'),
    Output('cat-name', 'children'),
    Input('oblast-selector', 'value'),
    Input('region-selector', 'value'),
    Input('ek-im-selector', 'value'),
    Input('product-selector', 'value'),
    Input('nastranapr-selector', 'value'),
    Input('okved-char', 'value'),
    Input('tnved-char', 'value'),
    Input('product-char', 'value'),
    prevent_initial_call=True
)
def update_grpah(selected_counties, selected_state, ekim_selector, category_type_selector, str_napr, okved_char, tnved_char, prod_char):
    if len(selected_counties) == 0 or ekim_selector == None or category_type_selector == None or str_napr == None:
        return dash.no_update

    else:

        dff = df[
            (df.region_s == selected_state) &
            (df.region.isin(selected_counties)) &
            (df.napr.isin(ekim_selector)) &
            (df.nastranapr_name.isin(str_napr))
            ]

        df_top_10_group = dff.groupby(['category_kod', 'category_name'])['netto', 'stoim'].sum().sort_values(by='netto',
                                                                                                             ascending=False).reset_index()

        fig1 = px.bar(df_top_10_group.head(20),
                      x='category_kod',
                      y='netto',
                      color='stoim',
                      height=400,
                      hover_data=['category_name'],
                      title='Количество(нетто) экспорта/импорта продукции по выбранным субъектам(Топ 10)')

        # Фильтрация датафрема по всей РФ
        dff_all = df[(df.napr.isin(ekim_selector))]

        df_all_top_10_group = dff_all.groupby(['category_kod', 'category_name'])['netto', 'stoim'].sum().sort_values(
            by='netto',
            ascending=False).reset_index()
        fig2 = px.bar(df_all_top_10_group.head(10),
                      x='category_kod',
                      y='netto',
                      color='stoim',
                      height=400,
                      hover_data=['category_name'],
                      title='Количество(нетто) экспорта/импорта продукции\nпо всей территории РФ (Топ 10)')

        dff_product_pie = df[df.region_s == selected_state]
        dff_product_pie = dff_product_pie[dff_product_pie.region.isin(selected_counties)]
        dff_product_pie = dff_product_pie[dff_product_pie.category_name.isin([category_type_selector])]
        dff_product_pie = dff_product_pie[dff_product_pie.nastranapr_name.isin(str_napr)]

        df_top_10_pie = dff_product_pie.groupby(['napr', 'category_name'])['netto'].sum().reset_index()


        fig3 = go.Figure(data=[go.Pie(labels=df_top_10_pie.napr,
                                      values=df_top_10_pie.netto,
                                      pull=[0, 0.2])],

                         )
        # fig3 = px.pie(df_top_10_pie,
        #               values='netto',
        #               names='napr',
        #               height=400,
        #               title='Импорт/Экспорт выбранной категории товаров')

        dff_product_graf = df[df.region_s == selected_state]
        dff_product_graf = dff_product_graf[dff_product_graf.region.isin(selected_counties)]
        dff_product_graf = dff_product_graf[dff_product_graf.napr.isin(ekim_selector)]
        dff_product_graf = dff_product_graf[dff_product_graf.category_name.isin([category_type_selector])]
        dff_product_graf = dff_product_graf[dff_product_graf.nastranapr_name.isin(str_napr)]

        df_top_10_prod = dff_product_graf.groupby(['region_num', 'region', 'category_name'])[
            'netto'].sum().reset_index().sort_values(by='netto',
                                                     ascending=False)
        fig4 = px.bar(df_top_10_prod.head(10),
                      x='region',
                      y='netto',
                      height=400,
                      hover_data=['category_name', 'region'],
                      title='Количество(нетто) ЭК\ИМ выбранной\nкатегории продуктов по субъектам(ТОП 10)'
                      )


        dff_product_table = dff_product_graf[dff_product_graf.region.isin(selected_counties)]

        dff_product_table = dff_product_table.groupby(['category_name', 'region', 'napr', 'nastranapr_name', 'okved'])[
            'netto', 'stoim'].sum().sort_values(by='netto',
                                                ascending=False).reset_index()



        columns = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in dff_product_table.columns]


        df_okved_filter = df[df.region_s == selected_state]
        df_okved_filter = df_okved_filter[df_okved_filter.napr == 'ИМ']
        df_okved_filter = df_okved_filter[df_okved_filter.okved.isin([okved_char])]

        df_okved_table = df_okved_filter.groupby(['okved', 'tnved', 'product_name', 'category_name']).agg({'revenue_2021': 'mean',
                                                                                                           'netto': 'sum',
                                                                                                           'im_minus_ex': 'mean'}).sort_values(
            by=['im_minus_ex',
                'netto',
                'revenue_2021'],
            ascending=[False, False, False]).reset_index()

        columns_okved = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in df_okved_table.columns]


        fig5 = px.bar(df_okved_table.sort_values(
            by=['im_minus_ex', 'netto'],
            ascending=[False, False]).head(10),
                      x="tnved",
                      y="im_minus_ex",
                      color='netto',
                      barmode='group',
                      height=400,
                      title="Категории товаров по ТНВЭД (ТОП 10 по импортзамещению)",
                      hover_data=['product_name'])







        tnvd_name = df.product_name[df.tnved == tnved_char].reset_index()
        tnvd_name = tnvd_name.loc[0, 'product_name']
        html1 = [html.Div([f'{tnvd_name}'])]

        dff_product_pie_tnvd = df[(df.region_s == selected_state) &
                             (df.region.isin(selected_counties)) &
                             (df.tnved == tnved_char) &
                             (df.nastranapr_name.isin(str_napr))]



        df_top_10_pie_tnvd = dff_product_pie_tnvd.groupby(['tnved',
                                                           'region',
                                                           'product_name',
                                                           'napr',
                                                           'nastranapr_name'])['netto',
                                                                            'stoim'].sum().reset_index().sort_values(by='netto', ascending=False)


        fig6 = go.Figure(data=[go.Pie(labels=df_top_10_pie_tnvd.napr,
                                      values=df_top_10_pie_tnvd.netto,
                                      pull=[0, 0.2])],

                         )


        df_tnvd_table =  df_top_10_pie_tnvd[df_top_10_pie_tnvd.napr.isin(ekim_selector)]

        # df_tnvd_table = dff_product_tnvd_table.groupby(['tnved',
        #                                                    'region',
        #                                                    'product_name',
        #                                                    'napr',
        #                                                    'nastranapr_name'])['netto',
        #                                                                        'stoim'].sum().reset_index().sort_values(
        #     by='netto', ascending=False)



        fig7 = px.bar(df_tnvd_table.head(20),
                      x='region',
                      y='netto',
                      color='stoim',
                      height=400,
                      hover_data=['product_name', 'tnved'],
                      title='Количество(нетто) ЭК/ИМ по выбранному субъекту')

        columns_tnved = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in df_tnvd_table.columns]


        #Справочник
        prod_name = df.tnved[df.product_name == prod_char].reset_index()
        prod_name = prod_name.loc[0, 'tnved']
        html2 = [html.Div([f'{prod_name}'])]
        cat_name = df.category_name[df.product_name == prod_char].reset_index()
        cat_name = cat_name.loc[0, 'category_name']
        html3 = [html.Div([f'{cat_name}'])]

        # Стиль для графиков
        size_fig = 10
        # family_fig = 'Courier New, monospace'
        family_fig = 'Oswald'
        color_fig = "#2a2b2b"

        fig1.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig,
            ),
            title_x=0.5,
            xaxis_title="Код Категории Продукции",
            yaxis_title="Количество(нетто) ЭК/ИМ продукции"
        )
        fig2.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title_x=0.5,
            xaxis_title="Код Категории Продукции",
            yaxis_title="Количество(нетто) ЭК/ИМ продукции"
        )

        fig3.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title_x=0.5,
            title='Импорт/Экспорт выбранной категории товаров по субъектам',
            height=400,

        )

        fig4.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title_x=0.5,
            xaxis_title="Субъект",
            yaxis_title="Количество(нетто) ЭК/ИМ продукции"
        )

        fig5.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title_x=0.5,
            xaxis_title="ТНВЭД продукции",
            yaxis_title="Количество(нетто) импорта продукции"
        )

        fig6.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title='Импорт/Экспорт выбранной категории товаров по субъектам',
            height=400,
            title_x=0.5,
        )

        fig7.update_layout(
            font=dict(
                family=family_fig,
                size=size_fig,  # Set the font size here
                color=color_fig
            ),
            title_x=0.5,
            xaxis_title="Субъект",
            yaxis_title="Количество(нетто) ИМ/ЭК продукции"
        )



        return dcc.Graph(id='display-map', figure=fig1), \
               dcc.Graph(id='display-map-all', figure=fig2), \
               dcc.Graph(id='display-pie-imek', figure=fig3), \
               dcc.Graph(id='display-graf-prod', figure=fig4), \
               dff_product_table.to_dict('records'), \
               columns, \
               df_okved_table.to_dict('records'), \
               columns_okved, \
               dcc.Graph(id='display-graf-okved', figure=fig5), \
               html1, \
               dcc.Graph(id='display-grafpie-tnved', figure=fig6), \
               dcc.Graph(id='display-graf-tnved', figure=fig7), \
               df_tnvd_table.to_dict('records'), \
               columns_tnved, \
               html2, \
               html3


'''DOWNLOAD BUTTON'''


@app.callback(
    Output('javascript', 'run'),
    [Input('click1', 'n_clicks')])
def myfun(x):
    if x:
        return 'window.print()'
    else:
        return ''


'''DATA TABLE'''

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns'),

)

def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# Колбэк для кнопки ВЫБРАТЬ ВСЕ
@app.callback(Output("nastranapr-selector", "value"),
              Input("select-all", "n_clicks"))

def select_all(n_clicks):
    return df['nastranapr_name'].unique()


if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
