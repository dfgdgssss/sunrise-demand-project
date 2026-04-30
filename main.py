import pandas as pd
import numpy as np
import os

class SunriseDemandSystem:

    def __init__(self):

        self.sales = pd.read_csv(
            "data/sales_history.csv"
        )

        self.sales['week_start_date'] = pd.to_datetime(
            self.sales['week_start_date']
        )

        self.inventory = pd.read_csv(
            "data/inventory_snapshot.csv"
        )

        self.sku = pd.read_csv(
            "data/sku_master.csv"
        )

        self.outlet = pd.read_csv(
            "data/outlet_master.csv"
        )


    def process_data(self):

        self.sales = self.sales.merge(
            self.outlet,
            on="outlet_id",
            how="left"
        )

        self.sales['units_sold'] = self.sales[
            'units_sold'
        ].fillna(0)

        self.sales['promotional_flag'] = self.sales[
            'promotional_flag'
        ].fillna(0)


    def generate_forecast(self):

        self.sales['adjusted_sales'] = np.where(
            self.sales['promotional_flag'] == 1,
            self.sales['units_sold'] * 0.60,
            self.sales['units_sold']
        )

        weekly = self.sales.groupby(
            ['sku_id','week_start_date']
        )['adjusted_sales'].sum().reset_index()

        weekly['weekly_demand_forecast'] = weekly.groupby(
            'sku_id'
        )['adjusted_sales'].transform(
            lambda x: x.rolling(6,min_periods=1).mean()
        )

        forecast = weekly.groupby(
            'sku_id'
        )['weekly_demand_forecast'].last().reset_index()

        forecast.to_csv(
            "reports/D1_6_Week_Forecast.csv",
            index=False
        )

        self.forecast = forecast


    def reorder_report(self):

        df = self.forecast.merge(
            self.inventory,
            on="sku_id"
        ).merge(
            self.sku,
            on="sku_id"
        )

        df['net_stock'] = \
        df['warehouse_stock'] + \
        df['in_transit_qty'] - \
        df['committed_qty']

        df['recommended_order_qty'] = np.where(
            df['weekly_demand_forecast']*6 > df['net_stock'],
            df['moq_from_supplier'],
            0
        )

        report = df[
            df['recommended_order_qty'] > 0
        ][[
            'sku_id',
            'product_name',
            'recommended_order_qty'
        ]]

        report.to_csv(
            "reports/D4_Monday_Morning_Report.csv",
            index=False
        )


    def run_pipeline(self):

        self.process_data()
        self.generate_forecast()
        self.reorder_report()


if __name__ == "__main__":
    SunriseDemandSystem().run_pipeline()