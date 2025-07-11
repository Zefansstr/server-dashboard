import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Gaming Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Generate dummy data
def generate_dummy_data():
    """Generate realistic dummy data for gaming platform"""
    
    # Create date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Gaming products
    products = ['Pussy888', 'Mega888', '918kiss', 'Joker123', 'XE88']
    
    # Generate usernames
    usernames = [f"user_{i:03d}" for i in range(1, 201)]
    
    # Generate deposit data
    deposit_data = []
    for _ in range(500):  # 500 deposit transactions
        deposit_data.append({
            'Unique Code': f"USR{np.random.randint(100000, 999999)}",
            'Username': np.random.choice(usernames),
            'Product': np.random.choice(products),
            'Amount': np.random.uniform(20, 1000),
            'Date': np.random.choice(date_range),
            'Type': 'Deposit'
        })
    
    # Generate withdraw data  
    withdraw_data = []
    for _ in range(300):  # 300 withdraw transactions
        withdraw_data.append({
            'Unique Code': f"USR{np.random.randint(100000, 999999)}",
            'Username': np.random.choice(usernames),
            'Product': np.random.choice(products),
            'Amount': np.random.uniform(10, 800),
            'Date': np.random.choice(date_range),
            'Type': 'Withdraw'
        })
    
    deposit_df = pd.DataFrame(deposit_data)
    withdraw_df = pd.DataFrame(withdraw_data)
    
    return deposit_df, withdraw_df

# Calculate analytics
def calculate_analytics(deposit_df, withdraw_df):
    """Calculate key metrics"""
    
    analytics = {}
    
    # Basic metrics
    analytics['total_deposit'] = deposit_df['Amount'].sum() if not deposit_df.empty else 0
    analytics['total_withdraw'] = withdraw_df['Amount'].sum() if not withdraw_df.empty else 0
    analytics['total_case_deposit'] = len(deposit_df)
    analytics['total_case_withdraw'] = len(withdraw_df)
    
    # GGR
    analytics['ggr'] = analytics['total_deposit'] - analytics['total_withdraw']
    
    # Active members by unique code
    unique_codes = set()
    if not deposit_df.empty:
        unique_codes.update(deposit_df['Unique Code'].unique())
    if not withdraw_df.empty:
        unique_codes.update(withdraw_df['Unique Code'].unique())
    analytics['active_members_by_code'] = len(unique_codes)
    
    return analytics

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
        
        if st.button("🚪 Logout"):
            for key in ['logged_in', 'username', 'login_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Header
    st.markdown('<h1 style="text-align: center; color: white;">🎮 Gaming Platform Dashboard</h1>', unsafe_allow_html=True)
    
    # Filters
    st.markdown("## 🔍 Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("📅 Start Date", value=datetime.now().date() - timedelta(days=7))
        end_date = st.date_input("📅 End Date", value=datetime.now().date())
    
    with col2:
        selected_line = st.selectbox("🎮 Line:", ["All", "STMY", "JMMY"])
        if st.button("🔄 Apply Filters"):
            st.rerun()
    
    # Generate dummy data
    deposit_df, withdraw_df = generate_dummy_data()
    
    # Filter by date range
    if start_date and end_date:
        deposit_df = deposit_df[(deposit_df['Date'].dt.date >= start_date) & (deposit_df['Date'].dt.date <= end_date)]
        withdraw_df = withdraw_df[(withdraw_df['Date'].dt.date >= start_date) & (withdraw_df['Date'].dt.date <= end_date)]
    
    # Calculate analytics
    analytics = calculate_analytics(deposit_df, withdraw_df)
    
    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Deposit Amount",
            value=f"RM {analytics['total_deposit']:,.2f}",
            delta=f"Cases: {analytics['total_case_deposit']}"
        )
    
    with col2:
        st.metric(
            label="💸 Withdraw Amount", 
            value=f"RM {analytics['total_withdraw']:,.2f}",
            delta=f"Cases: {analytics['total_case_withdraw']}"
        )
    
    with col3:
        st.metric(
            label="🆔 Active Members",
            value=f"{analytics['active_members_by_code']:,}",
            delta="By Unique Code"
        )
    
    with col4:
        ggr_color = "normal" if analytics['ggr'] >= 0 else "inverse"
        st.metric(
            label="💹 GGR",
            value=f"RM {analytics['ggr']:,.2f}",
            delta="Gross Gaming Revenue",
            delta_color=ggr_color
        )
    
    # Charts
    st.markdown("## 📈 Weekly Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Active Members per Week")
        
        # Sample weekly data
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        base_members = analytics['active_members_by_code']
        member_data = pd.DataFrame({
            'Week': weeks,
            'Active Members': [
                int(base_members * 0.8),
                int(base_members * 0.9),
                int(base_members * 1.0),
                int(base_members * 1.1)
            ]
        })
        
        st.line_chart(member_data.set_index('Week'))
        st.dataframe(member_data, use_container_width=True)
    
    with col2:
        st.markdown("### 💹 GGR per Week")
        
        # Sample GGR data
        base_ggr = analytics['ggr']
        ggr_data = pd.DataFrame({
            'Week': weeks,
            'GGR (RM)': [
                base_ggr * 0.7,
                base_ggr * 0.85,
                base_ggr * 1.0,
                base_ggr * 1.2
            ]
        })
        
        st.bar_chart(ggr_data.set_index('Week'))
        st.dataframe(ggr_data, use_container_width=True)
    
    # Data Summary
    st.markdown("## 📋 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Recent Deposits")
        if not deposit_df.empty:
            recent_deposits = deposit_df.head(10)[['Username', 'Product', 'Amount', 'Date']]
            recent_deposits['Amount'] = recent_deposits['Amount'].round(2)
            st.dataframe(recent_deposits, use_container_width=True)
        else:
            st.info("No deposit data available")
    
    with col2:
        st.markdown("### 💸 Recent Withdrawals")
        if not withdraw_df.empty:
            recent_withdrawals = withdraw_df.head(10)[['Username', 'Product', 'Amount', 'Date']]
            recent_withdrawals['Amount'] = recent_withdrawals['Amount'].round(2)
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