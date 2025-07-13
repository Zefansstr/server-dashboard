import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Konfigurasi halaman
st.set_page_config(
    page_title="Gaming Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache untuk loading data
@st.cache_data
def load_real_data():
    """Load real data from Excel files"""
    try:
        # Load data dari file Excel
        deposit_df = pd.read_excel('deposit_july06.xlsx')
        withdraw_df = pd.read_excel('withdrawjuly06.xlsx')
        member_df = pd.read_excel('member_reportJanJuly06.xlsx')
        
        # Konversi kolom Date ke datetime
        deposit_df['Date'] = pd.to_datetime(deposit_df['Date'])
        withdraw_df['Date'] = pd.to_datetime(withdraw_df['Date'])
        member_df['Date'] = pd.to_datetime(member_df['Date'])
        
        # Currency conversion SGD to MYR
        # Standard exchange rate: 1 SGD = 3.4 MYR (approximate)
        SGD_TO_MYR_RATE = 3.4
        
        # Define columns that need currency conversion
        currency_columns = [
            'Deposit_Amount', 'Withdraw_Amount', 'Bonus', 'Add_Bonus', 'Deduct_Bonus',
            'Add_Transaction', 'Deduct_Transaction', 'Bets_Amount', 'Valid_Amount', 
            'GGR', 'Net_Profit'
        ]
        
        # Convert SGD to MYR in all dataframes
        for df in [deposit_df, withdraw_df, member_df]:
            if 'Currency' in df.columns:
                sgd_mask = df['Currency'] == 'SGD'
                
                # Convert all currency columns from SGD to MYR
                for col in currency_columns:
                    if col in df.columns:
                        df.loc[sgd_mask, col] = df.loc[sgd_mask, col] * SGD_TO_MYR_RATE
                
                # Update currency label to MYR
                df.loc[sgd_mask, 'Currency'] = 'MYR'
        
        return deposit_df, withdraw_df, member_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Simple CSS
def load_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
    }
    
    .stDeployButton {
        display: none;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
    }
    
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #4fd1c7;
    }
    </style>
    """, unsafe_allow_html=True)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User database
USERS = {
    "admin": hash_password("admin123"),
    "user": hash_password("password"),
    "demo": hash_password("demo123")
}

# Verify login
def verify_login(username, password):
    hashed_password = hash_password(password)
    return username in USERS and USERS[username] == hashed_password

# Calculate comprehensive analytics
def calculate_comprehensive_analytics(deposit_df, withdraw_df, member_df):
    """Calculate comprehensive financial analytics"""
    
    analytics = {}
    
    # Basic Financial Metrics
    analytics['total_deposit'] = deposit_df['Deposit_Amount'].sum() if not deposit_df.empty else 0
    analytics['total_withdraw'] = withdraw_df['Withdraw_Amount'].sum() if not withdraw_df.empty else 0
    analytics['total_deposit_cases'] = deposit_df['Deposit_Cases'].sum() if not deposit_df.empty else 0
    analytics['total_withdraw_cases'] = withdraw_df['Withdraw_Cases'].sum() if not withdraw_df.empty else 0
    
    # GGR and Net Profit
    analytics['total_ggr'] = member_df['GGR'].sum() if not member_df.empty else 0
    analytics['total_net_profit'] = member_df['Net_Profit'].sum() if not member_df.empty else 0
    
    # Betting Analytics
    analytics['total_bets'] = member_df['Cases_Bets'].sum() if not member_df.empty else 0
    analytics['total_bets_amount'] = member_df['Bets_Amount'].sum() if not member_df.empty else 0
    analytics['total_valid_amount'] = member_df['Valid_Amount'].sum() if not member_df.empty else 0
    
    # Bonus Analytics
    analytics['total_bonus_given'] = member_df['Add_Bonus'].sum() if not member_df.empty else 0
    analytics['total_bonus_deducted'] = member_df['Deduct_Bonus'].sum() if not member_df.empty else 0
    analytics['net_bonus'] = analytics['total_bonus_given'] - analytics['total_bonus_deducted']
    
    # Active Members
    analytics['total_active_members'] = member_df['User_Name'].nunique() if not member_df.empty else 0
    
    # Average Metrics
    analytics['avg_deposit_per_case'] = analytics['total_deposit'] / analytics['total_deposit_cases'] if analytics['total_deposit_cases'] > 0 else 0
    analytics['avg_withdraw_per_case'] = analytics['total_withdraw'] / analytics['total_withdraw_cases'] if analytics['total_withdraw_cases'] > 0 else 0
    analytics['avg_ggr_per_member'] = analytics['total_ggr'] / analytics['total_active_members'] if analytics['total_active_members'] > 0 else 0
    
    # Win Rate
    analytics['overall_winrate'] = member_df['Winrate'].mean() if not member_df.empty else 0
    
    # Line Performance
    if not member_df.empty:
        analytics['line_performance'] = member_df.groupby('Line').agg({
            'GGR': 'sum',
            'Net_Profit': 'sum',
            'Deposit_Amount': 'sum',
            'Withdraw_Amount': 'sum',
            'User_Name': 'nunique'
        }).reset_index()
    else:
        analytics['line_performance'] = pd.DataFrame()
    
    return analytics

# Generate time series data
def generate_time_series_analytics(deposit_df, withdraw_df, member_df):
    """Generate time series analytics for charts"""
    
    time_series = {}
    
    if not member_df.empty:
        # Daily aggregations
        daily_stats = member_df.groupby(member_df['Date'].dt.date).agg({
            'GGR': 'sum',
            'Net_Profit': 'sum',
            'Deposit_Amount': 'sum',
            'Withdraw_Amount': 'sum',
            'Cases_Bets': 'sum',
            'Bets_Amount': 'sum',
            'Valid_Amount': 'sum',
            'User_Name': 'nunique'
        }).reset_index()
        
        time_series['daily_stats'] = daily_stats
        
        # Weekly aggregations
        member_df['Week'] = member_df['Date'].dt.isocalendar().week
        weekly_stats = member_df.groupby('Week').agg({
            'GGR': 'sum',
            'Net_Profit': 'sum',
            'Deposit_Amount': 'sum',
            'Withdraw_Amount': 'sum',
            'User_Name': 'nunique'
        }).reset_index()
        
        time_series['weekly_stats'] = weekly_stats
        
        # Monthly aggregations
        monthly_stats = member_df.groupby('Month').agg({
            'GGR': 'sum',
            'Net_Profit': 'sum',
            'Deposit_Amount': 'sum',
            'Withdraw_Amount': 'sum',
            'User_Name': 'nunique'
        }).reset_index()
        
        time_series['monthly_stats'] = monthly_stats
    
    return time_series

# Login page
def login_page():
    load_css()
    
    st.markdown('<h1 style="text-align: center; color: white;">🎮 Gaming Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Login ke Dashboard")
            
            username = st.text_input("👤 Username", placeholder="Masukkan username")
            password = st.text_input("🔑 Password", type="password", placeholder="Masukkan password")
            
            login_clicked = st.form_submit_button("🚀 Login")
            
            if login_clicked:
                if username and password:
                    with st.spinner('Memverifikasi...'):
                        time.sleep(1)
                        
                    if verify_login(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.login_time = datetime.now()
                        st.success("✅ Login berhasil!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
                else:
                    st.warning("⚠️ Mohon isi username dan password!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h4>🎯 Demo Login</h4>
            <p><strong>Username:</strong> admin | <strong>Password:</strong> admin123</p>
            <p><strong>Username:</strong> user | <strong>Password:</strong> password</p>
        </div>
        """, unsafe_allow_html=True)

# Dashboard page
def dashboard_page():
    load_css()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        st.markdown(f"**Login:** {st.session_state.login_time.strftime('%d/%m/%Y %H:%M')}")
        
        if st.button("🔄 Refresh"):
            st.rerun()
        
        # Export functionality
        if st.button("📥 Export Data"):
            st.info("💾 Export functionality coming soon!")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)")
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        # Theme selector
        theme = st.selectbox("🎨 Theme", ["Dark", "Light"])
        if theme == "Light":
            st.info("🌞 Light theme selected")
        
        if st.button("🚪 Logout"):
            for key in ['logged_in', 'username', 'login_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Header
    st.markdown('<h1 style="text-align: center; color: white;">🎮 Gaming Platform Dashboard</h1>', unsafe_allow_html=True)
    
    # Load real data first to get available lines
    deposit_df, withdraw_df, member_df = load_real_data()
    
    # Get date range from data
    if not member_df.empty:
        min_date = member_df['Date'].min().date()
        max_date = member_df['Date'].max().date()
        
        # Set default to show last 30 days of data or full range if less than 30 days
        if (max_date - min_date).days <= 30:
            default_start_date = min_date
            default_end_date = max_date
        else:
            default_start_date = max_date - timedelta(days=30)
            default_end_date = max_date
    else:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
        default_start_date = min_date
        default_end_date = max_date
    
    # Get available lines from data
    available_lines = ["All"]
    if not member_df.empty:
        unique_lines = sorted(member_df['Line'].unique())
        available_lines.extend(unique_lines)
    
    # Filters
    st.markdown("## 🔍 Filters")
    
    # Show data date range info
    if not member_df.empty:
        st.info(f"📅 **Data Available**: {min_date.strftime('%d %B %Y')} to {max_date.strftime('%d %B %Y')} ({(max_date - min_date).days + 1} days)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "📅 Start Date", 
            value=default_start_date,
            min_value=min_date,
            max_value=max_date
        )
        end_date = st.date_input(
            "📅 End Date", 
            value=default_end_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        selected_line = st.selectbox("🎮 Line:", available_lines)
        if st.button("🔄 Apply Filters"):
            st.rerun()
    
    # Filter by date range
    if start_date and end_date:
        deposit_df = deposit_df[(deposit_df['Date'].dt.date >= start_date) & (deposit_df['Date'].dt.date <= end_date)]
        withdraw_df = withdraw_df[(withdraw_df['Date'].dt.date >= start_date) & (withdraw_df['Date'].dt.date <= end_date)]
        member_df = member_df[(member_df['Date'].dt.date >= start_date) & (member_df['Date'].dt.date <= end_date)]
    
    # Filter by line
    if selected_line != "All":
        deposit_df = deposit_df[deposit_df['Line'] == selected_line] if 'Line' in deposit_df.columns else deposit_df
        withdraw_df = withdraw_df[withdraw_df['Line'] == selected_line] if 'Line' in withdraw_df.columns else withdraw_df
        member_df = member_df[member_df['Line'] == selected_line] if 'Line' in member_df.columns else member_df
    
    # Calculate comprehensive analytics
    analytics = calculate_comprehensive_analytics(deposit_df, withdraw_df, member_df)
    
    # Display line selection info
    if not member_df.empty:
        # Currency conversion info
        st.markdown("## 💱 Currency Information")
        
        # Show currency conversion info
        currency_counts = member_df['Currency'].value_counts()
        st.info(f"💰 **All amounts are displayed in MYR**. SGD amounts have been converted using exchange rate: **1 SGD = 3.4 MYR**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="📊 Currency Distribution",
                value="100% MYR",
                delta="After conversion"
            )
        
        with col2:
            st.metric(
                label="💹 Exchange Rate Used",
                value="1 SGD = 3.4 MYR",
                delta="Standard Rate"
            )
        
        st.markdown("## 📊 Line Information")
        
        # Show line distribution
        line_counts = member_df['Line'].value_counts().reset_index()
        line_counts.columns = ['Line', 'Records']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📋 Line Distribution")
            st.dataframe(line_counts, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Line Records Chart")
            fig = px.bar(line_counts, x='Line', y='Records', title="Records per Line")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Show currently selected line info
        if selected_line != "All":
            selected_records = len(member_df)
            st.info(f"🎯 **Currently viewing Line: {selected_line}** with **{selected_records:,} records**")
        else:
            total_records = len(member_df)
            st.info(f"🎯 **Currently viewing: All Lines** with **{total_records:,} total records**")
    
    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Deposit",
            value=f"RM {analytics['total_deposit']:,.2f}",
            delta=f"Cases: {analytics['total_deposit_cases']}"
        )
    
    with col2:
        st.metric(
            label="💸 Total Withdraw", 
            value=f"RM {analytics['total_withdraw']:,.2f}",
            delta=f"Cases: {analytics['total_withdraw_cases']}"
        )
    
    with col3:
        st.metric(
            label="🆔 Active Members",
            value=f"{analytics['total_active_members']:,}",
            delta="Total"
        )
    
    with col4:
        ggr_color = "normal" if analytics['total_ggr'] >= 0 else "inverse"
        st.metric(
            label="💹 GGR",
            value=f"RM {analytics['total_ggr']:,.2f}",
            delta="Gross Gaming Revenue",
            delta_color=ggr_color
        )
    
    # Charts
    st.markdown("## 📈 Weekly Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Total Deposit per Week")
        
        # Generate dummy data for weekly deposit chart
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        base_deposit = analytics['total_deposit']
        deposit_data = pd.DataFrame({
            'Week': weeks,
            'Deposit (RM)': [
                base_deposit * 0.7,
                base_deposit * 0.8,
                base_deposit * 0.9,
                base_deposit * 1.0
            ]
        })
        
        st.bar_chart(deposit_data.set_index('Week'))
        st.dataframe(deposit_data, use_container_width=True)
    
    with col2:
        st.markdown("### 💸 Total Withdraw per Week")
        
        # Generate dummy data for weekly withdraw chart
        base_withdraw = analytics['total_withdraw']
        withdraw_data = pd.DataFrame({
            'Week': weeks,
            'Withdraw (RM)': [
                base_withdraw * 0.7,
                base_withdraw * 0.8,
                base_withdraw * 0.9,
                base_withdraw * 1.0
            ]
        })
        
        st.bar_chart(withdraw_data.set_index('Week'))
        st.dataframe(withdraw_data, use_container_width=True)
    
    # Additional Financial Metrics
    st.markdown("## 💼 Financial Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏆 Net Profit",
            value=f"RM {analytics['total_net_profit']:,.2f}",
            delta="Total"
        )
    
    with col2:
        st.metric(
            label="🎯 Total Bets",
            value=f"{analytics['total_bets']:,}",
            delta=f"Amount: RM {analytics['total_bets_amount']:,.2f}"
        )
    
    with col3:
        st.metric(
            label="✅ Valid Amount",
            value=f"RM {analytics['total_valid_amount']:,.2f}",
            delta="Validated"
        )
    
    with col4:
        st.metric(
            label="🎁 Net Bonus",
            value=f"RM {analytics['net_bonus']:,.2f}",
            delta=f"Given: RM {analytics['total_bonus_given']:,.2f}"
        )
    
    # Average Metrics
    st.markdown("## 📊 Average Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Avg Deposit/Case",
            value=f"RM {analytics['avg_deposit_per_case']:,.2f}",
            delta="Per Transaction"
        )
    
    with col2:
        st.metric(
            label="📉 Avg Withdraw/Case",
            value=f"RM {analytics['avg_withdraw_per_case']:,.2f}",
            delta="Per Transaction"
        )
    
    with col3:
        st.metric(
            label="👤 Avg GGR/Member",
            value=f"RM {analytics['avg_ggr_per_member']:,.2f}",
            delta="Per User"
        )
    
    with col4:
        st.metric(
            label="🎯 Overall Win Rate",
            value=f"{analytics['overall_winrate']:.2%}",
            delta="Average"
        )
    
    # Line Performance Analysis
    if not analytics['line_performance'].empty:
        st.markdown("## 📈 Line Performance Analysis")
        
        # Create tabs for different line analyses
        tab1, tab2, tab3 = st.tabs(["💰 Revenue by Line", "📊 Performance Metrics", "📋 Detailed Table"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💹 GGR by Line")
                fig_ggr = px.bar(
                    analytics['line_performance'], 
                    x='Line', 
                    y='GGR',
                    title="GGR by Line",
                    color='GGR',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_ggr, use_container_width=True)
            
            with col2:
                st.markdown("### 🏆 Net Profit by Line")
                fig_profit = px.bar(
                    analytics['line_performance'], 
                    x='Line', 
                    y='Net_Profit',
                    title="Net Profit by Line",
                    color='Net_Profit',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_profit, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💰 Deposit vs Withdraw by Line")
                fig_dep_with = px.scatter(
                    analytics['line_performance'],
                    x='Deposit_Amount',
                    y='Withdraw_Amount',
                    size='User_Name',
                    color='Line',
                    title="Deposit vs Withdraw by Line",
                    labels={'User_Name': 'Users Count'}
                )
                st.plotly_chart(fig_dep_with, use_container_width=True)
            
            with col2:
                st.markdown("### 👥 Active Users by Line")
                fig_users = px.pie(
                    analytics['line_performance'],
                    values='User_Name',
                    names='Line',
                    title="Distribution of Active Users by Line"
                )
                st.plotly_chart(fig_users, use_container_width=True)
        
        with tab3:
            st.markdown("### 📊 Complete Line Performance Table")
            
            # Format the dataframe for better display
            display_df = analytics['line_performance'].copy()
            display_df['GGR'] = display_df['GGR'].round(2)
            display_df['Net_Profit'] = display_df['Net_Profit'].round(2)
            display_df['Deposit_Amount'] = display_df['Deposit_Amount'].round(2)
            display_df['Withdraw_Amount'] = display_df['Withdraw_Amount'].round(2)
            
            # Rename columns for display
            display_df.columns = ['Line', 'GGR (RM)', 'Net Profit (RM)', 'Deposit Amount (RM)', 'Withdraw Amount (RM)', 'Active Users']
            
            st.dataframe(display_df, use_container_width=True)
    
    # Operational Reports
    st.markdown("## 📋 Operational Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Top Financial Metrics")
        
        # Create summary metrics table
        metrics_data = {
            'Metric': [
                'Total Revenue (Deposit)', 
                'Total Payout (Withdraw)', 
                'Gross Gaming Revenue (GGR)', 
                'Net Profit',
                'Total Bets Placed',
                'Total Valid Amount',
                'Bonus Given',
                'Bonus Deducted',
                'Net Bonus'
            ],
            'Value (RM)': [
                f"{analytics['total_deposit']:,.2f}",
                f"{analytics['total_withdraw']:,.2f}",
                f"{analytics['total_ggr']:,.2f}",
                f"{analytics['total_net_profit']:,.2f}",
                f"{analytics['total_bets_amount']:,.2f}",
                f"{analytics['total_valid_amount']:,.2f}",
                f"{analytics['total_bonus_given']:,.2f}",
                f"{analytics['total_bonus_deducted']:,.2f}",
                f"{analytics['net_bonus']:,.2f}"
            ],
            'Cases/Count': [
                f"{analytics['total_deposit_cases']:,}",
                f"{analytics['total_withdraw_cases']:,}",
                "-",
                "-",
                f"{analytics['total_bets']:,}",
                "-",
                "-",
                "-",
                "-"
            ]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Key Performance Indicators")
        
        # Calculate additional KPIs
        deposit_to_withdraw_ratio = analytics['total_deposit'] / analytics['total_withdraw'] if analytics['total_withdraw'] > 0 else 0
        ggr_margin = (analytics['total_ggr'] / analytics['total_deposit']) * 100 if analytics['total_deposit'] > 0 else 0
        valid_bet_ratio = (analytics['total_valid_amount'] / analytics['total_bets_amount']) * 100 if analytics['total_bets_amount'] > 0 else 0
        
        kpi_data = {
            'KPI': [
                'Deposit to Withdraw Ratio',
                'GGR Margin (%)',
                'Valid Bet Ratio (%)',
                'Average Deposit per Case',
                'Average Withdraw per Case',
                'Average GGR per Member',
                'Overall Win Rate (%)',
                'Active Members'
            ],
            'Value': [
                f"{deposit_to_withdraw_ratio:.2f}",
                f"{ggr_margin:.2f}%",
                f"{valid_bet_ratio:.2f}%",
                f"RM {analytics['avg_deposit_per_case']:,.2f}",
                f"RM {analytics['avg_withdraw_per_case']:,.2f}",
                f"RM {analytics['avg_ggr_per_member']:,.2f}",
                f"{analytics['overall_winrate']:.2%}",
                f"{analytics['total_active_members']:,}"
            ]
        }
        
        kpi_df = pd.DataFrame(kpi_data)
        st.dataframe(kpi_df, use_container_width=True)

    # Data Summary
    st.markdown("## 📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Recent Deposits")
        if not deposit_df.empty:
            recent_deposits = deposit_df.nlargest(10, 'Deposit_Amount')[['User_Name', 'Unique_Code', 'Deposit_Amount', 'Date', 'Line']]
            recent_deposits['Deposit_Amount'] = recent_deposits['Deposit_Amount'].round(2)
            st.dataframe(recent_deposits, use_container_width=True)
        else:
            st.info("No deposit data available")
    
    with col2:
        st.markdown("### 💸 Recent Withdrawals")
        if not withdraw_df.empty:
            recent_withdrawals = withdraw_df.nlargest(10, 'Withdraw_Amount')[['User_Name', 'Unique_Code', 'Withdraw_Amount', 'Date', 'Line']]
            recent_withdrawals['Withdraw_Amount'] = recent_withdrawals['Withdraw_Amount'].round(2)
            st.dataframe(recent_withdrawals, use_container_width=True)
        else:
            st.info("No withdrawal data available")

# Main function
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    main() 