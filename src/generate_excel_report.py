"""
Superstore Excel Report Generator — Senior Analyst Edition
Run from project root: python3 src/generate_excel_report.py
"""

import pandas as pd
import xlsxwriter
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_PATH   = "data/processed/superstore_cleaned.csv"
RFM_PATH    = "data/processed/rfm_segments.csv"
OUTPUT_PATH = "outputs/reports/Superstore_Executive_Report.xlsx"

C_DARK      = "#1F3864"
C_MID       = "#2E75B6"
C_LIGHT     = "#D6E4F0"
C_ACCENT    = "#E8A838"
C_GREEN     = "#1B5E20"
C_GREEN_BG  = "#E8F5E9"
C_RED       = "#B71C1C"
C_RED_BG    = "#FFEBEE"
C_AMBER     = "#F57F17"
C_AMBER_BG  = "#FFF8E1"
C_WHITE     = "#FFFFFF"
C_GREY_BG   = "#F5F7FA"
C_BORDER    = "#CFD8DC"
C_TEXT      = "#212121"
C_SUBTEXT   = "#546E7A"


# ── Data ───────────────────────────────────────────────────────────────────────
def load_data():
    df  = pd.read_csv(DATA_PATH, parse_dates=["Order Date", "Ship Date"])
    rfm = pd.read_csv(RFM_PATH)
    return df, rfm


def build_summaries(df, rfm):
    kpis = [
        ("Total Sales",       f"${df['Sales'].sum():,.0f}"),
        ("Total Profit",      f"${df['Profit'].sum():,.0f}"),
        ("Profit Margin",     f"{df['Profit'].sum()/df['Sales'].sum()*100:.2f}%"),
        ("Transactions",      f"{len(df):,}"),
        ("Unique Customers",  f"{df['Customer ID'].nunique():,}"),
        ("Period",            "2014 – 2017"),
    ]

    cat = (df.groupby("Category")
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                  Transactions=("Order ID","count"),
                  Avg_Discount=("Discount","mean"))
             .reset_index())
    cat["Margin %"]       = (cat["Profit"]/cat["Sales"]*100).round(2)
    cat["Avg Discount %"] = (cat["Avg_Discount"]*100).round(2)
    cat = cat.drop("Avg_Discount",axis=1).sort_values("Sales",ascending=False)

    reg = (df.groupby("Region")
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                  Transactions=("Order ID","count"),
                  Avg_Discount=("Discount","mean"))
             .reset_index())
    reg["Margin %"]       = (reg["Profit"]/reg["Sales"]*100).round(2)
    reg["Avg Discount %"] = (reg["Avg_Discount"]*100).round(2)
    reg = reg.drop("Avg_Discount",axis=1).sort_values("Profit",ascending=False)

    seg = (df.groupby("Segment")
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                  Transactions=("Order ID","count"))
             .reset_index())
    seg["Margin %"] = (seg["Profit"]/seg["Sales"]*100).round(2)
    seg = seg.sort_values("Sales",ascending=False)

    sub = (df.groupby("Sub-Category")
             .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
             .reset_index())
    sub["Margin %"] = (sub["Profit"]/sub["Sales"]*100).round(2)
    sub = sub.sort_values("Profit",ascending=False)

    disc = df.groupby("Discount")["Profit"].mean().reset_index()
    disc.columns = ["Discount Rate", "Avg Profit"]
    disc["Discount Rate"] = (disc["Discount Rate"]*100).round(0).astype(int)
    disc["Avg Profit"]    = disc["Avg Profit"].round(2)

    yoy = (df.groupby("Order Year")
             .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"))
             .reset_index())
    yoy["Margin %"] = (yoy["Profit"]/yoy["Revenue"]*100).round(2)

    rfm_sum = (rfm.groupby("Segment")
                  .agg(Customers=("Customer ID","count"),
                       Total_Revenue=("Monetary","sum"),
                       Avg_Spend=("Monetary","mean"),
                       Avg_Recency=("Recency","mean"),
                       Avg_Frequency=("Frequency","mean"))
                  .reset_index().round(2))
    rfm_sum = rfm_sum.sort_values("Total_Revenue",ascending=False)
    rfm_sum.columns = ["Segment","Customers","Total Revenue",
                       "Avg Spend","Avg Recency (days)","Avg Frequency"]

    return kpis, cat, reg, seg, sub, disc, yoy, rfm_sum


# ── Formats ────────────────────────────────────────────────────────────────────
def make_formats(wb):
    def f(**kw):
        base = {"font_name":"Calibri","font_size":10,
                "font_color":C_TEXT,"border":0,"valign":"vcenter"}
        base.update(kw)
        return wb.add_format(base)

    fmt = {}
    fmt["title"]        = f(bold=True,font_size=20,font_color=C_WHITE,
                            bg_color=C_DARK,align="center")
    fmt["subtitle"]     = f(font_size=10,font_color=C_WHITE,
                            bg_color=C_DARK,align="center",italic=True)
    fmt["date_stamp"]   = f(font_size=9,font_color=C_SUBTEXT,
                            align="right",italic=True)
    fmt["section"]      = f(bold=True,font_size=10,font_color=C_WHITE,
                            bg_color=C_MID,align="left",indent=1)
    fmt["col_hdr"]      = f(bold=True,font_size=10,font_color=C_WHITE,
                            bg_color=C_MID,align="center",
                            top=1,bottom=1,left=1,right=1,
                            border_color=C_WHITE)
    # KPI
    fmt["kpi_lbl"]      = f(bold=True,font_size=9,font_color=C_SUBTEXT,
                            bg_color=C_GREY_BG,align="center",
                            top=1,left=1,right=1,
                            top_color=C_BORDER,left_color=C_BORDER,
                            right_color=C_BORDER)
    fmt["kpi_val"]      = f(bold=True,font_size=15,font_color=C_DARK,
                            bg_color=C_WHITE,align="center",
                            bottom=1,left=1,right=1,
                            bottom_color=C_BORDER,left_color=C_BORDER,
                            right_color=C_BORDER)
    # Callout boxes
    fmt["insight_hdr"]  = f(bold=True,font_size=10,font_color=C_WHITE,
                            bg_color=C_DARK,align="left",indent=1,
                            top=1,bottom=1,left=1,right=1,
                            border_color=C_DARK)
    fmt["insight_item"] = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_LIGHT,align="left",indent=2,
                            top=0,bottom=0,left=1,right=1,
                            left_color=C_BORDER,right_color=C_BORDER)
    fmt["insight_last"] = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_LIGHT,align="left",indent=2,
                            bottom=1,left=1,right=1,
                            bottom_color=C_BORDER,left_color=C_BORDER,
                            right_color=C_BORDER)
    fmt["action_hdr"]   = f(bold=True,font_size=10,font_color=C_WHITE,
                            bg_color=C_AMBER,align="left",indent=1,
                            top=1,bottom=1,left=1,right=1,
                            border_color=C_AMBER)
    fmt["action_item"]  = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_AMBER_BG,align="left",indent=2,
                            top=0,bottom=0,left=1,right=1,
                            left_color=C_BORDER,right_color=C_BORDER)
    fmt["action_last"]  = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_AMBER_BG,align="left",indent=2,
                            bottom=1,left=1,right=1,
                            bottom_color=C_BORDER,left_color=C_BORDER,
                            right_color=C_BORDER)
    fmt["warn_hdr"]     = f(bold=True,font_size=10,font_color=C_WHITE,
                            bg_color=C_RED,align="left",indent=1,
                            top=1,bottom=1,left=1,right=1,
                            border_color=C_RED)
    fmt["warn_item"]    = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_RED_BG,align="left",indent=2,
                            top=0,bottom=0,left=1,right=1,
                            left_color=C_BORDER,right_color=C_BORDER)
    fmt["warn_last"]    = f(font_size=10,font_color=C_TEXT,
                            bg_color=C_RED_BG,align="left",indent=2,
                            bottom=1,left=1,right=1,
                            bottom_color=C_BORDER,left_color=C_BORDER,
                            right_color=C_BORDER)
    # Table cells
    fmt["cell"]         = f(align="center",bg_color=C_WHITE,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["cell_L"]       = f(align="left",bg_color=C_WHITE,indent=1,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["cell_alt"]     = f(align="center",bg_color=C_GREY_BG,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["cell_altL"]    = f(align="left",bg_color=C_GREY_BG,indent=1,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["money"]        = f(num_format="$#,##0",align="center",
                            bg_color=C_WHITE,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["money_alt"]    = f(num_format="$#,##0",align="center",
                            bg_color=C_GREY_BG,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["pct"]          = f(num_format='0.00"%"',align="center",
                            bg_color=C_WHITE,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["pct_alt"]      = f(num_format='0.00"%"',align="center",
                            bg_color=C_GREY_BG,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["neg"]          = f(bold=True,num_format="$#,##0",
                            font_color=C_RED,bg_color=C_RED_BG,
                            align="center",
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["pos_green"]    = f(bold=True,num_format="$#,##0",
                            font_color=C_GREEN,bg_color=C_GREEN_BG,
                            align="center",
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["date_cell"]    = f(num_format="yyyy-mm-dd",align="center",
                            bg_color=C_WHITE,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    fmt["date_alt"]     = f(num_format="yyyy-mm-dd",align="center",
                            bg_color=C_GREY_BG,
                            left=1,right=1,top=1,bottom=1,
                            border_color=C_BORDER)
    return fmt


# ── Helpers ────────────────────────────────────────────────────────────────────
MONEY_KEYS = {"sales","profit","revenue","spend","monetary",
              "total revenue","avg spend","avg profit","total profit"}
PCT_KEYS   = {"margin %","margin","discount %","avg discount %",
              "avg discount","% of total"}

def write_callout(ws, r, c1, c2, title, bullets, fmt,
                  hdr_key="insight_hdr",
                  item_key="insight_item",
                  last_key="insight_last"):
    ws.merge_range(r, c1, r, c2, f"  {title}", fmt[hdr_key])
    ws.set_row(r, 18)
    r += 1
    for i, bullet in enumerate(bullets):
        is_last = (i == len(bullets)-1)
        fk = last_key if is_last else item_key
        ws.merge_range(r, c1, r, c2, bullet, fmt[fk])
        ws.set_row(r, 16)
        r += 1
    return r


def section_hdr(ws, r, c1, c2, label, fmt):
    ws.merge_range(r, c1, r, c2, f"  {label}", fmt["section"])
    ws.set_row(r, 18)
    return r+1


def write_table(ws, r0, c0, df, fmt):
    for ci, col in enumerate(df.columns):
        ws.write(r0, c0+ci, col, fmt["col_hdr"])
    for ri, (_, row) in enumerate(df.iterrows()):
        rr  = r0+1+ri
        alt = (ri % 2 == 1)
        for ci, (col, val) in enumerate(zip(df.columns, row)):
            ck = col.lower()
            is_money = any(m in ck for m in MONEY_KEYS)
            is_pct   = any(p in ck for p in PCT_KEYS)
            if is_money and isinstance(val,(int,float)):
                if val < 0:
                    ws.write(rr, c0+ci, val, fmt["neg"])
                else:
                    ws.write(rr, c0+ci, val,
                             fmt["pos_green"] if "profit" in ck
                             else fmt["money_alt" if alt else "money"])
            elif is_pct and isinstance(val,(int,float)):
                ws.write(rr, c0+ci, val,
                         fmt["pct_alt" if alt else "pct"])
            elif isinstance(val,(int,float)):
                ws.write(rr, c0+ci, val,
                         fmt["cell_alt" if alt else "cell"])
            else:
                ws.write(rr, c0+ci, str(val),
                         fmt["cell_altL" if alt else "cell_L"])
    return r0+1+len(df)


def spacer(ws, r, h=8):
    ws.set_row(r, h)
    return r+1


def chart_defaults(c):
    c.set_title({"none":True})
    c.set_chartarea({"border":{"none":True},"fill":{"color":C_WHITE}})
    c.set_plotarea({"border":{"color":C_BORDER}})
    c.set_legend({"position":"bottom","font":{"size":9}})


# ── Sheet 1: Dashboard ─────────────────────────────────────────────────────────
def build_dashboard(wb, fmt, kpis, cat, reg, seg, yoy):
    ws = wb.add_worksheet("Dashboard")
    ws.hide_gridlines(2)
    ws.set_zoom(85)
    ws.set_tab_color(C_DARK)

    ws.set_column("A:A", 1.5)
    ws.set_column("B:C", 18)
    ws.set_column("D:D", 16)
    ws.set_column("E:E", 16)
    ws.set_column("F:F", 16)
    ws.set_column("G:G", 16)
    ws.set_column("H:H", 1.5)

    # Title
    ws.set_row(0, 4)
    ws.merge_range("B2:G2","SUPERSTORE BUSINESS PERFORMANCE ANALYSIS",fmt["title"])
    ws.set_row(1, 38)
    ws.merge_range("B3:G3",
        "Executive Dashboard  ·  Four-Year Analysis  ·  2014 – 2017",
        fmt["subtitle"])
    ws.set_row(2, 22)
    ws.write("G4", f"Generated: {datetime.today().strftime('%B %d, %Y')}",
             fmt["date_stamp"])
    ws.set_row(3, 14)

    # KPIs
    section_hdr(ws, 4, 1, 6, "KEY PERFORMANCE INDICATORS", fmt)
    ws.set_row(5, 16)
    ws.set_row(6, 36)
    for i,(lbl,val) in enumerate(kpis):
        ws.write(5, 1+i, lbl, fmt["kpi_lbl"])
        ws.write(6, 1+i, val, fmt["kpi_val"])
    r = spacer(ws, 7, 12)

    # Key Insights callout
    r = write_callout(ws, r, 1, 3,
        "KEY INSIGHTS", [
            "▸  Revenue grew from $484K (2014) to $733K (2017) — strong top-line growth",
            "▸  Furniture margins collapsed to 2.49% driven by Tables (-$17,725 total loss)",
            "▸  Transactions with 30%+ discounts generated -$135,364 in net losses",
        ], fmt,
        hdr_key="insight_hdr",
        item_key="insight_item",
        last_key="insight_last")

    # Recommended Actions callout (same row range, columns 4-6)
    ra_r = r - 4  # align with insights start
    ws.merge_range(ra_r, 4, ra_r, 6,
                   "  RECOMMENDED ACTIONS", fmt["action_hdr"])
    ws.set_row(ra_r, 18)
    actions = [
        "▸  Cap all discounts at 20% — pilot in Central region first",
        "▸  Conduct pricing review on Tables and Bookcases immediately",
        "▸  Launch retention campaign for At Risk + Cannot Lose customers",
    ]
    for i, act in enumerate(actions):
        is_last = (i == len(actions)-1)
        fk = "action_last" if is_last else "action_item"
        ws.merge_range(ra_r+1+i, 4, ra_r+1+i, 6, act, fmt[fk])
        ws.set_row(ra_r+1+i, 16)

    r = spacer(ws, r, 12)

    # Category table
    r = section_hdr(ws, r, 1, 6, "PERFORMANCE BY CATEGORY", fmt)
    r = write_table(ws, r, 1,
        cat[["Category","Sales","Profit","Margin %",
             "Avg Discount %","Transactions"]], fmt)
    r = spacer(ws, r, 12)

    # Region table
    r = section_hdr(ws, r, 1, 6, "PERFORMANCE BY REGION", fmt)
    r = write_table(ws, r, 1,
        reg[["Region","Sales","Profit","Margin %",
             "Avg Discount %","Transactions"]], fmt)
    r = spacer(ws, r, 12)

    # Segment table
    r = section_hdr(ws, r, 1, 6, "PERFORMANCE BY CUSTOMER SEGMENT", fmt)
    r = write_table(ws, r, 1,
        seg[["Segment","Sales","Profit","Margin %","Transactions"]], fmt)
    r = spacer(ws, r, 12)

    # YoY data (used by chart)
    r = section_hdr(ws, r, 1, 6,
                    "REVENUE & PROFIT MARGIN TREND (2014–2017)", fmt)
    data_r = r
    ws.write(data_r, 1, "Year",     fmt["col_hdr"])
    ws.write(data_r, 2, "Revenue",  fmt["col_hdr"])
    ws.write(data_r, 3, "Margin %", fmt["col_hdr"])
    for i, row in yoy.iterrows():
        rr = data_r+1+i
        ws.write(rr, 1, int(row["Order Year"]), fmt["cell"])
        ws.write(rr, 2, round(row["Revenue"],0), fmt["money"])
        ws.write(rr, 3, row["Margin %"],        fmt["pct"])

    # Dual axis: Revenue bars + Margin % line
    bar = wb.add_chart({"type":"column"})
    bar.add_series({
        "name":       "Revenue ($)",
        "categories": ["Dashboard", data_r+1, 1, data_r+4, 1],
        "values":     ["Dashboard", data_r+1, 2, data_r+4, 2],
        "fill":       {"color": C_MID},
        "gap":        50,
    })
    bar.set_y_axis({
        "name":           "Revenue ($)",
        "num_format":     "$#,##0",
        "major_gridlines":{"visible":True,"line":{"color":C_BORDER}},
    })
    bar.set_x_axis({"name":"Year","major_gridlines":{"visible":False}})
    chart_defaults(bar)

    line = wb.add_chart({"type":"line"})
    line.add_series({
        "name":       "Profit Margin %",
        "categories": ["Dashboard", data_r+1, 1, data_r+4, 1],
        "values":     ["Dashboard", data_r+1, 3, data_r+4, 3],
        "line":       {"color":C_ACCENT,"width":2.5},
        "marker":     {"type":"circle","size":7,
                       "fill":{"color":C_ACCENT},
                       "border":{"color":C_WHITE,"width":1.5}},
        "y2_axis":    True,
    })
    line.set_y2_axis({
        "name":       "Profit Margin (%)",
        "num_format": '0.0"%"',
        "min":        0,
        "max":        20,
    })
    bar.combine(line)
    bar.set_size({"width":520,"height":270})
    ws.insert_chart(data_r, 3, bar, {"x_offset":8,"y_offset":4})


# ── Sheet 2: Sales Summary ──────────────────────────────────────────────────────
def build_sales_summary(wb, fmt, cat, reg, seg, sub):
    ws = wb.add_worksheet("Sales Summary")
    ws.hide_gridlines(2)
    ws.set_tab_color(C_MID)
    ws.set_column("A:A", 1.5)
    ws.set_column("B:B", 22)
    ws.set_column("C:H", 15)

    ws.merge_range("B2:H2","SALES & PROFIT SUMMARY",fmt["title"])
    ws.set_row(1, 38)
    ws.set_row(2, 8)

    r = 3
    r = section_hdr(ws, r, 1, 7, "BY CATEGORY", fmt)
    r = write_table(ws, r, 1,
        cat[["Category","Sales","Profit","Margin %",
             "Avg Discount %","Transactions"]], fmt)
    r = spacer(ws, r)

    r = section_hdr(ws, r, 1, 7, "BY REGION", fmt)
    r = write_table(ws, r, 1,
        reg[["Region","Sales","Profit","Margin %",
             "Avg Discount %","Transactions"]], fmt)
    r = spacer(ws, r)

    r = section_hdr(ws, r, 1, 7, "BY CUSTOMER SEGMENT", fmt)
    r = write_table(ws, r, 1,
        seg[["Segment","Sales","Profit","Margin %","Transactions"]], fmt)
    r = spacer(ws, r)

    r = section_hdr(ws, r, 1, 7,
                    "BY SUB-CATEGORY  (high profit → low profit)", fmt)
    sub_r = r
    r = write_table(ws, r, 1,
        sub[["Sub-Category","Sales","Profit","Margin %"]], fmt)

    # Horizontal bar chart
    chart = wb.add_chart({"type":"bar"})
    chart.add_series({
        "name":       "Total Profit",
        "categories": ["Sales Summary", sub_r+1, 1, sub_r+len(sub), 1],
        "values":     ["Sales Summary", sub_r+1, 2, sub_r+len(sub), 2],
        "fill":       {"color": C_MID},
        "gap":        35,
    })
    chart.set_x_axis({"name":"Total Profit ($)","num_format":"$#,##0",
                      "major_gridlines":{"visible":True,
                                         "line":{"color":C_BORDER}}})
    chart.set_y_axis({"name":"Sub-Category",
                      "major_gridlines":{"visible":False}})
    chart_defaults(chart)
    chart.set_legend({"none":True})
    chart.set_size({"width":440,"height":400})
    ws.insert_chart(sub_r, 4, chart, {"x_offset":10,"y_offset":4})


# ── Sheet 3: Discount Analysis ──────────────────────────────────────────────────
def build_discount_sheet(wb, fmt, df, disc):
    ws = wb.add_worksheet("Discount Analysis")
    ws.hide_gridlines(2)
    ws.set_tab_color(C_RED)
    ws.set_column("A:A", 1.5)
    ws.set_column("B:B", 26)
    ws.set_column("C:G", 18)

    ws.merge_range("B2:G2","DISCOUNT IMPACT ANALYSIS",fmt["title"])
    ws.set_row(1, 38)
    ws.set_row(2, 8)

    r = 3
    # Key finding callout
    r = write_callout(ws, r, 1, 6,
        "KEY FINDING", [
            "▸  14% of transactions (1,392 orders) carried discounts of 30% or more",
            "▸  These transactions generated a TOTAL NET LOSS of -$135,364",
            "▸  Break-even threshold is between 20–30% discount",
            "▸  Recommendation: Cap discounts at 20% and pilot in Central region first",
        ], fmt,
        hdr_key="warn_hdr",
        item_key="warn_item",
        last_key="warn_last")
    r = spacer(ws, r)

    over  = df[df["Discount"] >= 0.3]
    under = df[df["Discount"] <  0.3]
    split = pd.DataFrame({
        "Group":          ["Under 30% Discount","30%+ Discount"],
        "Transactions":   [len(under), len(over)],
        "% of Total":     [round(len(under)/len(df)*100,1),
                           round(len(over)/len(df)*100,1)],
        "Avg Profit":     [round(under["Profit"].mean(),2),
                           round(over["Profit"].mean(),2)],
        "Total Profit":   [round(under["Profit"].sum(),2),
                           round(over["Profit"].sum(),2)],
    })

    r = section_hdr(ws, r, 1, 6,
                    "HIGH VS LOW DISCOUNT — PROFIT COMPARISON", fmt)
    r = write_table(ws, r, 1, split, fmt)
    r = spacer(ws, r)

    r = section_hdr(ws, r, 1, 6,
                    "AVERAGE PROFIT BY DISCOUNT RATE", fmt)
    disc_r = r
    r = write_table(ws, r, 1, disc, fmt)

    # Write positive / negative series for two-color chart
    for i, row in disc.iterrows():
        rr  = disc_r+1+i
        val = row["Avg Profit"]
        ws.write(rr, 5, val if val >= 0 else None, fmt["cell"])
        ws.write(rr, 6, val if val < 0  else None, fmt["cell"])

    chart = wb.add_chart({"type":"column"})
    chart.add_series({
        "name":       "Profitable",
        "categories": ["Discount Analysis", disc_r+1, 1,
                       disc_r+len(disc), 1],
        "values":     ["Discount Analysis", disc_r+1, 5,
                       disc_r+len(disc), 5],
        "fill":       {"color": C_MID},
        "gap":        45,
    })
    chart.add_series({
        "name":       "Loss-Making",
        "categories": ["Discount Analysis", disc_r+1, 1,
                       disc_r+len(disc), 1],
        "values":     ["Discount Analysis", disc_r+1, 6,
                       disc_r+len(disc), 6],
        "fill":       {"color": C_RED},
        "gap":        45,
    })
    chart.set_x_axis({"name":"Discount Rate (%)",
                      "major_gridlines":{"visible":False}})
    chart.set_y_axis({"name":"Average Profit ($)","num_format":"$#,##0",
                      "major_gridlines":{"visible":True,
                                         "line":{"color":C_BORDER}}})
    chart_defaults(chart)
    chart.set_size({"width":500,"height":290})
    ws.insert_chart(disc_r, 3, chart, {"x_offset":10,"y_offset":4})


# ── Sheet 4: Customer Segments ──────────────────────────────────────────────────
def build_rfm_sheet(wb, fmt, rfm_sum):
    ws = wb.add_worksheet("Customer Segments")
    ws.hide_gridlines(2)
    ws.set_tab_color(C_ACCENT)
    ws.set_column("A:A", 1.5)
    ws.set_column("B:B", 22)
    ws.set_column("C:H", 16)

    ws.merge_range("B2:H2","RFM CUSTOMER SEGMENTATION",fmt["title"])
    ws.set_row(1, 38)
    ws.set_row(2, 8)

    r = 3
    # Interpretation callout
    r = write_callout(ws, r, 1, 7,
        "WHAT THIS MEANS", [
            "▸  44% of customers are Inactive / Low Value — the business has a serious retention problem",
            "▸  At Risk + Cannot Lose (107 customers) represent $530K in revenue showing signs of disengagement",
            "▸  Champions (34 customers) average $5,863 spend — protect these customers with a VIP program",
            "▸  Loyal customers (142) average $4,251 spend and bought within the last 37 days on average",
        ], fmt)
    r = spacer(ws, r)

    r = section_hdr(ws, r, 1, 7, "SEGMENT SUMMARY", fmt)
    r = write_table(ws, r, 1, rfm_sum, fmt)
    r = spacer(ws, r)

    # Pie chart data
    pie_r = r
    r = section_hdr(ws, r, 1, 7,
                    "CUSTOMER DISTRIBUTION BY SEGMENT", fmt)
    ws.write(r, 1, "Segment",    fmt["col_hdr"])
    ws.write(r, 2, "Customers",  fmt["col_hdr"])
    n = len(rfm_sum)
    for i, row in rfm_sum.iterrows():
        rr = r+1+list(rfm_sum.index).index(i)
        ws.write(rr, 1, row["Segment"],       fmt["cell_L"])
        ws.write(rr, 2, int(row["Customers"]),fmt["cell"])

    pie = wb.add_chart({"type":"pie"})
    pie.add_series({
        "name":        "Customers",
        "categories":  ["Customer Segments", r+1, 1, r+n, 1],
        "values":      ["Customer Segments", r+1, 2, r+n, 2],
        "data_labels": {"percentage":True,"category":True,
                        "separator":"\n",
                        "font":{"size":9,"color":C_TEXT}},
        "points": [
            {"fill":{"color":"#607D8B"}},
            {"fill":{"color":C_MID}},
            {"fill":{"color":"#26A69A"}},
            {"fill":{"color":C_RED}},
            {"fill":{"color":C_GREEN}},
            {"fill":{"color":C_ACCENT}},
        ],
    })
    pie.set_title({"none":True})
    pie.set_legend({"position":"right","font":{"size":9}})
    pie.set_chartarea({"border":{"none":True},"fill":{"color":C_WHITE}})
    pie.set_size({"width":440,"height":290})
    ws.insert_chart(r, 3, pie, {"x_offset":10,"y_offset":4})


# ── Sheet 5: Cleaned Data Export ───────────────────────────────────────────────
def build_raw_sheet(wb, fmt, df):
    ws = wb.add_worksheet("Cleaned Data Export")
    ws.set_tab_color(C_BORDER)
    ws.freeze_panes(1, 0)

    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    for ci, col in enumerate(df.columns):
        ws.write(0, ci, col, fmt["col_hdr"])

    for ri, (_, row) in enumerate(df.iterrows()):
        alt = (ri % 2 == 1)
        for ci, (col, val) in enumerate(zip(df.columns, row)):
            if pd.isna(val):
                ws.write(ri+1, ci, "",
                         fmt["cell_altL" if alt else "cell_L"])
            elif col in date_cols:
                # Write clean date string — no timestamp
                ws.write(ri+1, ci,
                         str(val)[:10],
                         fmt["cell_alt" if alt else "cell"])
            elif isinstance(val, float):
                ws.write(ri+1, ci, val,
                         fmt["cell_alt" if alt else "cell"])
            elif isinstance(val, int):
                ws.write(ri+1, ci, val,
                         fmt["cell_alt" if alt else "cell"])
            else:
                ws.write(ri+1, ci, str(val),
                         fmt["cell_altL" if alt else "cell_L"])

    ws.autofilter(0, 0, len(df), len(df.columns)-1)

    # Auto-fit column widths
    for ci, col in enumerate(df.columns):
        max_w = max(len(str(col)),
                    df.iloc[:,ci].astype(str).str.len().max())
        ws.set_column(ci, ci, min(max_w+2, 28))


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    df, rfm = load_data()

    print("Building summaries...")
    kpis, cat, reg, seg, sub, disc, yoy, rfm_sum = build_summaries(df, rfm)

    print("Creating workbook...")
    wb  = xlsxwriter.Workbook(OUTPUT_PATH)
    fmt = make_formats(wb)

    print("  → Dashboard")
    build_dashboard(wb, fmt, kpis, cat, reg, seg, yoy)
    print("  → Sales Summary")
    build_sales_summary(wb, fmt, cat, reg, seg, sub)
    print("  → Discount Analysis")
    build_discount_sheet(wb, fmt, df, disc)
    print("  → Customer Segments")
    build_rfm_sheet(wb, fmt, rfm_sum)
    print("  → Cleaned Data Export")
    build_raw_sheet(wb, fmt, df)

    wb.close()
    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
