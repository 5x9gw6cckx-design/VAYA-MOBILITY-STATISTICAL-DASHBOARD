
import streamlit as st
import pandas as pd
import io
import os
from datetime import date
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from fpdf import FPDF
import numpy as np
import hashlib
import statsmodels.api as sm

# ===========================
# GLOBAL FIGURE STYLING
# ===========================
def beautify_fig(fig, title_text=""):

    fig.update_layout(
        template="plotly_white",

        title=dict(
            text=title_text,
            x=0.5,
            font=dict(
                family="Times New Roman",
                size=28,
                color="black"
            )
        ),

        font=dict(
            family="Times New Roman",
            size=20,
            color="black"
        ),

        xaxis=dict(
            title_font=dict(
                family="Times New Roman",
                size=24,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=18,
                color="black"
            ),
            title_standoff=25
        ),

        yaxis=dict(
            title_font=dict(
                family="Times New Roman",
                size=24,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=18,
                color="black"
            )
        ),

        legend=dict(
            font=dict(
                family="Times New Roman",
                size=18,
                color="black"
            )
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",
        height=650
    )

    return fig

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="VAYA Shuttle Hybrid Dashboard",
    layout="wide"
)

# ===========================
# PASSWORD PROTECTION
# ===========================
PASSWORD_HASH = hashlib.sha256(
    "VayaSecure123!".encode()
).hexdigest()

st.sidebar.header("🔒 Login")

password = st.sidebar.text_input(
    "Enter Password",
    type="password"
)

if hashlib.sha256(password.encode()).hexdigest() != PASSWORD_HASH:
    st.warning(
        "Incorrect password. Enter the correct password to access the dashboard."
    )
    st.stop()

# ===========================
# CLEAN STYLING
# ===========================
st.markdown("""
<style>

section[data-testid="stSidebar"] {
    background-color:#0f172a;
}

section[data-testid="stSidebar"] * {
    color:#f8fafc !important;
}

[data-testid="stMetric"] {
    background-color:#f8fafc;
    padding:15px;
    border-radius:10px;
    border:1px solid #d1d5db;
}

</style>
""", unsafe_allow_html=True)

st.title("🚍 VAYA Shuttle Hybrid Executive Dashboard")
st.caption(
    "Advanced Business KPIs + Statistical Analysis + Operational Intelligence"
)

# ===========================
# SESSION STATE
# ===========================
if "manual_data" not in st.session_state:
    st.session_state.manual_data = pd.DataFrame()

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = pd.DataFrame()

vehicle_rates = {
    "4 seater":1.0,
    "7 seater":1.2,
    "15-18 seater":1.57,
    "bus":2.0
}

drivers_list = [
    "Elton",
    "Dave",
    "Vince",
    "P-gun"
]

# ===========================
# PERMANENT STORAGE
# ===========================
DATA_FILE = "shuttle_data.csv"

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except:
        return pd.DataFrame()

# Load saved data
saved_df = load_data()

if not saved_df.empty:
    st.session_state.uploaded_data = saved_df.copy()

# ===========================
# SIDEBAR MENU
# ===========================
st.sidebar.title("📊 Dashboard Menu")

menu = st.sidebar.radio(
    "Select Module",
    [
        "DATA ENTRY & UPLOAD",
        "DATA MANAGEMENT",
        "OVERVIEW & KPIs",
        "DESCRIPTIVE STATISTICS",
        "REGRESSION ANALYSIS",
        "RESIDUAL DIAGNOSTICS",
        "TIME SERIES FORECASTING",
        "ROUTE HOTSPOTS",
        "FLEET USAGE",
        "CORPORATE CLIENT ANALYSIS",
        "REPORTS"
    ]
)

# ===========================
# DATA ENTRY & UPLOAD
# ===========================
if menu == "DATA ENTRY & UPLOAD":

    uploaded_file = st.file_uploader(
        "Upload Shuttle Excel File",
        type=["xlsx"]
    )

    if uploaded_file:

        df = pd.read_excel(uploaded_file)

        df.columns = df.columns.astype(str).str.strip()

        rename_map = {
            "Date":"date",
            "No. of Buses":"no_of_buses",
            "Trips/bus":"trips_per_bus",
            "Total Trips":"total_trips",
            "Billable Trips":"billable_trips",
            "Number of people":"passengers",
            "Coperate Name":"corporate_name",
            "Vehichle Type":"vehicle_type",
            "Distance":"distance_km",
            "Total fare":"total_fare",
            "ODS Commission":"revenue",
            "Pickup points & Drop Off Locations":"route"
        }

        df = df.rename(columns=rename_map)

        numeric_cols = [
            "no_of_buses",
            "trips_per_bus",
            "total_trips",
            "billable_trips",
            "passengers",
            "distance_km",
            "total_fare",
            "revenue"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        for col in [
            "vehicle_type",
            "route",
            "corporate_name"
        ]:
            if col not in df.columns:
                df[col] = "Unknown"

            df[col] = df[col].fillna("Unknown").astype(str)

        df["revenue_source"] = "ODS Commission"

        df = df.dropna(subset=["date"])

        st.session_state.uploaded_data = df

        save_data(df)

        st.success("✅ Excel uploaded & saved permanently")

        st.dataframe(df, use_container_width=True)

    st.divider()

    # ===========================
    # MANUAL ENTRY
    # ===========================
    with st.form("manual_entry_form"):

        c1,c2,c3 = st.columns(3)

        with c1:
            trip_date = st.date_input(
                "Trip Date",
                date.today()
            )

            vehicle_type = st.selectbox(
                "Vehicle Type",
                list(vehicle_rates.keys())
            )

            driver = st.selectbox(
                "Driver",
                drivers_list
            )

        with c2:
            route = st.text_input("Route")

            corporate = st.text_input(
                "Corporate Name"
            )

            passengers = st.number_input(
                "Passengers",
                min_value=0
            )

        with c3:
            distance = st.number_input(
                "Distance (km)",
                min_value=0.0
            )

        rate = vehicle_rates[vehicle_type]

        total_fare = rate * distance

        revenue = total_fare * 0.17

        submitted = st.form_submit_button(
            "Add Trip"
        )

    if submitted:

        new_row = pd.DataFrame([{
            "date":trip_date,
            "vehicle_type":vehicle_type,
            "route":route if route else "Unknown",
            "driver":driver,
            "passengers":passengers,
            "distance_km":distance,
            "corporate_name":corporate if corporate else "Unknown",
            "rate_per_km":rate,
            "total_fare":total_fare,
            "revenue":revenue,
            "revenue_source":"Manual Calculation"
        }])

        combined = pd.concat(
            [
                st.session_state.uploaded_data,
                new_row
            ],
            ignore_index=True
        )

        st.session_state.uploaded_data = combined

        save_data(combined)

        st.success(
            "✅ Trip added & saved permanently"
        )

# ===========================
# MERGE DATA
# ===========================
def get_combined_data():

    dfs=[]

    if not st.session_state.uploaded_data.empty:
        dfs.append(
            st.session_state.uploaded_data
        )

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(
        dfs,
        ignore_index=True
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    for col in [
        "vehicle_type",
        "route",
        "corporate_name"
    ]:

        if col not in df.columns:
            df[col] = "Unknown"

        df[col] = df[col].fillna(
            "Unknown"
        ).astype(str)

    return df.dropna(subset=["date"])

df_all = get_combined_data()

# ===========================
# DATA MANAGEMENT
# ===========================
if menu == "DATA MANAGEMENT":

    st.subheader("🗂 Manage Shuttle Records")

    df_manage = get_combined_data()

    if df_manage.empty:

        st.warning("No records available.")

    else:

        st.dataframe(
            df_manage,
            use_container_width=True
        )

        st.markdown("### DELETE RECORD")

        delete_index = st.number_input(
            "Enter Row Index To Delete",
            min_value=0,
            max_value=len(df_manage)-1,
            step=1
        )

        if st.button("Delete Selected Record"):

            df_manage = df_manage.drop(
                index=delete_index
            )

            df_manage.reset_index(
                drop=True,
                inplace=True
            )

            save_data(df_manage)

            st.session_state.uploaded_data = (
                df_manage.copy()
            )

            st.success(
                "✅ Record deleted permanently"
            )

            st.rerun()

# ===========================
# FILTERS
# ===========================
filtered_df = df_all.copy()

if not df_all.empty:

    st.sidebar.subheader("📌 Filters")

    min_date = df_all["date"].min()
    max_date = df_all["date"].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date,max_date]
    )

    vehicle_filter = st.sidebar.multiselect(
        "Vehicle Type",
        sorted(df_all["vehicle_type"].unique()),
        default=sorted(df_all["vehicle_type"].unique())
    )

    route_filter = st.sidebar.multiselect(
        "Route",
        sorted(df_all["route"].unique()),
        default=sorted(df_all["route"].unique())
    )

    corporate_filter = st.sidebar.multiselect(
        "Corporate",
        sorted(df_all["corporate_name"].unique()),
        default=sorted(df_all["corporate_name"].unique())
    )

    filtered_df = df_all[
        (df_all["date"] >= pd.to_datetime(date_range[0])) &
        (df_all["date"] <= pd.to_datetime(date_range[1])) &
        (df_all["vehicle_type"].isin(vehicle_filter)) &
        (df_all["route"].isin(route_filter)) &
        (df_all["corporate_name"].isin(corporate_filter))
    ]

if menu != "DATA ENTRY & UPLOAD" and filtered_df.empty:
    st.warning("⚠ No data available.")
    st.stop()

# ===========================
# OVERVIEW & KPIs
# ===========================
if menu=="OVERVIEW & KPIs":

    df = filtered_df.copy()

    df["day"] = df["date"].dt.date
    df["month"] = df["date"].dt.to_period("M")

    total_revenue = df["revenue"].sum()
    total_trips = len(df)

    avg_trips_day = df.groupby("day").size().mean()

    avg_trips_month = (
        df.groupby("month").size().mean()
    )

    avg_rev_day = (
        df.groupby("day")["revenue"].sum().mean()
    )

    avg_corp_day = (
        df.groupby("day")["corporate_name"]
        .nunique()
        .mean()
    )

    monthly_rev = (
        df.groupby("month")["revenue"].sum()
    )

    growth_rate = (
        monthly_rev.pct_change().mean()*100
    )

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "TOTAL REVENUE",
        f"${total_revenue:,.2f}"
    )

    c2.metric(
        "TOTAL TRIPS",
        total_trips
    )

    c3.metric(
        "MONTHLY GROWTH RATE (%)",
        f"{growth_rate:.2f}%"
    )

    c4.metric(
        "AVG CORPORATE CLIENTS / DAY",
        round(avg_corp_day,2)
    )

    c5,c6,c7 = st.columns(3)

    c5.metric(
        "AVG TRIPS / DAY",
        round(avg_trips_day,2)
    )

    c6.metric(
        "AVG TRIPS / MONTH",
        round(avg_trips_month,2)
    )

    c7.metric(
        "AVG REVENUE / DAY",
        f"${avg_rev_day:,.2f}"
    )

    daily_rev = (
        df.groupby("day")["revenue"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        daily_rev,
        x="day",
        y="revenue",
        markers=True,
        labels={
            "day":"DAY",
            "revenue":"REVENUE"
        }
    )

    fig = beautify_fig(
        fig,
        "DAILY REVENUE TREND"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ===========================
# DESCRIPTIVE STATISTICS
# ===========================
if menu=="DESCRIPTIVE STATISTICS":

    

    df = filtered_df.copy()

    st.write(df["revenue"].describe())

    # ===========================
    # HISTOGRAM
    # ===========================
    fig1 = px.histogram(
        df,
        x="revenue",
        template="plotly_dark",
        title="REVENUE DISTRIBUTION"
    )
    fig1.update_layout(
        font=dict(size=30),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ===========================
    # BOX PLOT
    # ===========================
    fig2 = px.box(
        df,
        y="distance_km",
        template="plotly_dark",
        title="DISTANCE DISTRIBUTION"
    )
    fig2.update_layout(
        font=dict(size=30),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ===========================
    # CORRELATION HEATMAP (FIXED + CLEAN)
    # ===========================

    
    corr = df[["revenue", "distance_km", "passengers"]].corr()

    corr.index = ["Revenue", "Distance Km", "Passengers"]
    corr.columns = ["Revenue", "Distance Km", "Passengers"]

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",



        font=dict(
            family="Times New Roman",
            size=22,
            color="black"
        ),

        xaxis=dict(
            title="",
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            )
        ),

        yaxis=dict(
            title="",
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            )
        ),

        coloraxis_colorbar=dict(
            title=dict(
                text="Correlation",
                font=dict(
                    family="Times New Roman",
                    size=20,
                    color="black"
                )
            ),
            tickfont=dict(
                family="Times New Roman",
                size=18,
                color="black"
            )
        ),

        height=700
    )

    fig.update_traces(
        textfont=dict(
            family="Times New Roman",
            size=22,
            color="black"
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
    

# ===========================
# REGRESSION ANALYSIS
# ===========================
if menu == "REGRESSION ANALYSIS":

    st.subheader("MULTIPLE LINEAR REGRESSION ANALYSIS")

    df = filtered_df.copy()

    df = df[
        [
            "distance_km",
            "passengers",
            "vehicle_type",
            "revenue"
        ]
    ].dropna()

    if len(df) < 5:

        st.warning(
            "Not enough data for regression."
        )

    else:

        df_encoded = pd.get_dummies(
            df,
            columns=["vehicle_type"],
            drop_first=True
        )

        X = df_encoded.drop(
            columns=["revenue"]
        )

        X = X.apply(
            pd.to_numeric,
            errors="coerce"
        )

        X = X.astype(float)

        y = pd.to_numeric(
            df_encoded["revenue"],
            errors="coerce"
        )

        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()

        y_pred = model.predict(X)

        r2 = model.rsquared
        adj_r2 = model.rsquared_adj
        f_stat = model.fvalue
        p_value = model.f_pvalue
        std_error = np.sqrt(model.mse_resid)

        # KPIs
        c1,c2,c3 = st.columns(3)

        c1.metric(
            "R² SCORE",
            round(r2,4)
        )

        c2.metric(
            "ADJUSTED R²",
            round(adj_r2,4)
        )

        c3.metric(
            "F-STATISTIC",
            round(f_stat,4)
        )

        c4,c5 = st.columns(2)

        c4.metric(
            "MODEL P-VALUE",
            round(p_value,6)
        )

        c5.metric(
            "STANDARD ERROR",
            round(std_error,4)
        )

        # Regression Coefficients
        st.subheader("REGRESSION COEFFICIENTS")

        coef_df = pd.DataFrame({
            "VARIABLE": model.params.index,
            "COEFFICIENT": model.params.values,
            "P-VALUE": model.pvalues.values
        })

        st.dataframe(
            coef_df,
            use_container_width=True
        )

# ===========================
# RESIDUAL DIAGNOSTICS
# ===========================
if menu == "RESIDUAL DIAGNOSTICS":

    st.subheader("MODEL RESIDUAL DIAGNOSTICS")

    df = filtered_df.copy()

    df = df[
        [
            "distance_km",
            "passengers",
            "vehicle_type",
            "revenue"
        ]
    ].dropna()

    if len(df) < 5:

        st.warning("Not enough data.")

    else:

        df_encoded = pd.get_dummies(
            df,
            columns=["vehicle_type"],
            drop_first=True
        )

        X = df_encoded.drop(
            columns=["revenue"]
        )

        X = X.apply(
            pd.to_numeric,
            errors="coerce"
        )

        X = X.astype(float)

        y = pd.to_numeric(
            df_encoded["revenue"],
            errors="coerce"
        )

        X = sm.add_constant(X)

        model = sm.OLS(y, X).fit()

        fitted = model.predict(X)

        residuals = y - fitted

        # Residual Histogram
        fig1 = px.histogram(
            residuals,
            nbins=20,
            template="plotly_white"
        )

        fig1.update_yaxes(
            title="COUNT"
        )

        fig1 = beautify_fig(
            fig1,
            "RESIDUAL DISTRIBUTION"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # Residual Scatter
        fig2 = px.scatter(
            x=fitted,
            y=residuals,
            labels={
                "x":"FITTED VALUES",
                "y":"RESIDUALS"
            },
            template="plotly_white"
        )

        fig2 = beautify_fig(
            fig2,
            "RESIDUALS VS FITTED VALUES"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ===========================
# TIME SERIES FORECASTING
# ===========================
if menu == "TIME SERIES FORECASTING":

    st.subheader("TIME SERIES FORECASTING")

    df = filtered_df.copy()

    daily = (
        df.groupby(df["date"].dt.date)
        ["revenue"]
        .sum()
        .reset_index()
    )

    daily.columns = [
        "date",
        "revenue"
    ]

    if len(daily) < 5:

        st.warning(
            "Not enough time data."
        )

    else:

        daily["t"] = range(len(daily))

        model = LinearRegression()

        model.fit(
            daily[["t"]],
            daily["revenue"]
        )

        daily["forecast"] = model.predict(
            daily[["t"]]
        )

        fig = px.line(
            daily,
            x="date",
            y=["revenue","forecast"],
            template="plotly_white",
            labels={
                "date":"DATE",
                "value":"REVENUE"
            }
        )

        fig = beautify_fig(
            fig,
            "REVENUE FORECASTING"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



# ===========================
# ROUTE HOTSPOTS
# ===========================
if menu == "ROUTE HOTSPOTS":

    df = df_all.copy()

    hotspots = df.groupby("route", dropna=False).agg(
        TRIPS=("route", "count"),
        REVENUE=("revenue", "sum")
    ).reset_index()

    hotspots["REVENUE_SHARE_%"] = (
        hotspots["REVENUE"] / hotspots["REVENUE"].sum()
    ) * 100

    hotspots = hotspots.sort_values(
        "TRIPS",
        ascending=False
    ).head(10)

    hotspots["CATEGORY"] = "NORMAL"
    hotspots.loc[
        hotspots.head(3).index,
        "CATEGORY"
    ] = "TOP 3 ROUTES"

    # ===========================
    # CHART 1: TRIPS
    # ===========================
    fig1 = px.bar(
        hotspots,
        x="TRIPS",
        y="route",
        orientation="h",
        color="CATEGORY",
        text="TRIPS",
        title="ROUTE HOTSPOTS (TOP 10)",
        color_discrete_map={
            "TOP 3 ROUTES": "#D62828",
            "NORMAL": "#1D4ED8"
        }
    )

    fig1.update_traces(
        textfont_size=24,
        textfont_family="Times New Roman",
        marker_line_color="black",
        marker_line_width=1.5
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Times New Roman",
            size=24,
            color="black"
        ),

        title=dict(
            font=dict(
                family="Times New Roman",
                size=32,
                color="black"
            ),
            x=0.5
        ),

        xaxis=dict(
            title="TRIPS",
            title_font=dict(
                family="Times New Roman",
                size=28,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            ),
            showgrid=True,
            gridcolor="#D9D9D9"
        ),

        yaxis=dict(
            title="ROUTE",
            title_font=dict(
                family="Times New Roman",
                size=28,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            ),
            automargin=True
        ),

        legend=dict(
            font=dict(
                family="Times New Roman",
                size=20,
                color="black"
            )
        ),

        margin=dict(
            l=320,
            r=60,
            t=100,
            b=70
        ),

        height=850
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ===========================
    # CHART 2: REVENUE
    # ===========================
    fig2 = px.bar(
        hotspots.sort_values("REVENUE", ascending=True),
        x="REVENUE",
        y="route",
        orientation="h",
        color="REVENUE",
        title="ROUTE REVENUE CONTRIBUTION",
        color_continuous_scale="Turbo"
    )

    fig2.update_traces(
        marker_line_color="black",
        marker_line_width=1.5
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Times New Roman",
            size=24,
            color="black"
        ),

        title=dict(
            font=dict(
                family="Times New Roman",
                size=32,
                color="black"
            ),
            x=0.5
        ),

        xaxis=dict(
            title="REVENUE",
            title_font=dict(
                family="Times New Roman",
                size=28,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            ),
            showgrid=True,
            gridcolor="#D9D9D9"
        ),

        yaxis=dict(
            title="ROUTE",
            title_font=dict(
                family="Times New Roman",
                size=28,
                color="black"
            ),
            tickfont=dict(
                family="Times New Roman",
                size=22,
                color="black"
            ),
            automargin=True
        ),

        coloraxis_colorbar=dict(
            title=dict(
                text="REVENUE",
                font=dict(
                    family="Times New Roman",
                    size=22,
                    color="black"
                )
            ),
            tickfont=dict(
                family="Times New Roman",
                size=18,
                color="black"
            )
        ),

        margin=dict(
            l=320,
            r=80,
            t=100,
            b=70
        ),

        height=850
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ===========================
    # TABLE
    # ===========================
    st.subheader("ROUTE PERFORMANCE SUMMARY")

    st.dataframe(
        hotspots,
        use_container_width=True
    )
# ===========================
# FLEET USAGE
# ===========================
if menu == "FLEET USAGE":

    st.subheader("FLEET USAGE ANALYSIS")

    df = filtered_df.copy()

    fleet = (
        df.groupby("vehicle_type")
        .agg(
            trips=("vehicle_type","count"),
            revenue=("revenue","sum")
        )
        .reset_index()
    )

    fig = px.pie(
        fleet,
        values="trips",
        names="vehicle_type",
        template="plotly_white"
    )

    fig = beautify_fig(
        fig,
        "FLEET USAGE DISTRIBUTION"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        fleet,
        use_container_width=True
    )

# ===========================
# CORPORATE CLIENT ANALYSIS
# ===========================
if menu == "CORPORATE CLIENT ANALYSIS":

    st.subheader(
        "CORPORATE CLIENT ANALYSIS"
    )

    df = filtered_df.copy()

    corp = (
        df.groupby("corporate_name")
        .agg(
            trips=("corporate_name","count"),
            revenue=("revenue","sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    fig = px.bar(
        corp,
        x="corporate_name",
        y="revenue",
        template="plotly_white",
        labels={
            "corporate_name":"CORPORATE CLIENT",
            "revenue":"REVENUE"
        }
    )

    fig = beautify_fig(
        fig,
        "CORPORATE REVENUE ANALYSIS"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        corp,
        use_container_width=True
    )

# ===========================
# REPORTS
# ===========================
if menu == "REPORTS":

    st.subheader("DOWNLOAD REPORTS")

    df = filtered_df.copy()

    st.dataframe(
        df,
        use_container_width=True
    )

    # Excel Export
    excel_buffer = io.BytesIO()

    df.to_excel(
        excel_buffer,
        index=False
    )

    excel_buffer.seek(0)

    st.download_button(
        "Download Excel Report",
        excel_buffer,
        "shuttle_report.xlsx"
    )

    # PDF Export
    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        0,
        10,
        "VAYA Shuttle Executive Report",
        ln=True
    )

    pdf.ln(10)

    pdf.set_font(
        "Arial",
        "",
        12
    )

    pdf.cell(
        0,
        8,
        f"Total Trips: {len(df)}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Total Revenue: ${df['revenue'].sum():,.2f}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Average Revenue: ${df['revenue'].mean():,.2f}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Total Passengers: {df['passengers'].sum()}",
        ln=True
    )

    pdf_bytes = pdf.output(
        dest="S"
    ).encode("latin1")

    st.download_button(
        "Download PDF Report",
        pdf_bytes,
        "shuttle_report.pdf"
    )
