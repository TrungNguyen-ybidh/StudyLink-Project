
import streamlit as st
from streamlit import session_state as ss
from modules.nav import SideBarLinks

# Page config
st.set_page_config(
    page_title="StudyLink | Smart Study Planning",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* ============================================= */
    /* GLOBAL BACKGROUND GRADIENT                   */
    /* ============================================= */
    
    /* Main app background - Circular radial gradient (blue & white) */
    .stApp {
        background: radial-gradient(circle at 50% 50%, 
            #ffffff 0%,
            #E3F2FD 25%,
            #90CAF9 50%,
            #42A5F5 75%,
            #1E88E5 100%
        );
        background-attachment: fixed;
        min-height: 100vh;
        overflow: hidden;
    }
    
    /* Sidebar background - semi-transparent white */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
    }
    
    /* ============================================= */
    /* TRANSPARENT WHITE CONTAINERS                 */
    /* ============================================= */
    
    /* Main content container - semi-transparent white */
    .main .block-container {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem !important;
        margin: 1rem;
    }
    
    /* All container boxes with borders - semi-transparent white */
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlockBorderWrapper"]) > [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Streamlit containers with border=True */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Info, success, warning boxes - semi-transparent */
    .stAlert {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(8px);
        border-radius: 10px;
    }
    
    /* Selectbox and input fields */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(5px);
    }
    
    /* Buttons - semi-transparent with hover effect */
    .stButton > button {
        background: rgba(30, 136, 229, 0.85) !important;
        backdrop-filter: blur(5px);
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(30, 136, 229, 1) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.4);
    }
    
    /* Divider lines */
    hr {
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Header transparency */
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* ============================================= */
    /* ANIMATED PARTICLES                           */
    /* ============================================= */
    
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 0;
    }
    
    .particle {
        position: absolute;
        width: 10px;
        height: 10px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        animation: float 15s infinite ease-in-out;
    }
    
    .particle.small {
        width: 6px;
        height: 6px;
        background: rgba(255, 255, 255, 0.4);
    }
    
    .particle.medium {
        width: 12px;
        height: 12px;
        background: rgba(255, 255, 255, 0.5);
    }
    
    .particle.large {
        width: 18px;
        height: 18px;
        background: rgba(255, 255, 255, 0.3);
    }
    
    .particle.blue {
        background: rgba(30, 136, 229, 0.3);
    }
    
    .particle.light-blue {
        background: rgba(144, 202, 249, 0.4);
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    .particle:nth-child(1) { left: 5%; animation-duration: 20s; animation-delay: 0s; }
    .particle:nth-child(2) { left: 10%; animation-duration: 25s; animation-delay: 2s; }
    .particle:nth-child(3) { left: 15%; animation-duration: 18s; animation-delay: 4s; }
    .particle:nth-child(4) { left: 20%; animation-duration: 22s; animation-delay: 1s; }
    .particle:nth-child(5) { left: 25%; animation-duration: 28s; animation-delay: 3s; }
    .particle:nth-child(6) { left: 30%; animation-duration: 15s; animation-delay: 5s; }
    .particle:nth-child(7) { left: 35%; animation-duration: 20s; animation-delay: 0s; }
    .particle:nth-child(8) { left: 40%; animation-duration: 24s; animation-delay: 2s; }
    .particle:nth-child(9) { left: 45%; animation-duration: 19s; animation-delay: 4s; }
    .particle:nth-child(10) { left: 50%; animation-duration: 26s; animation-delay: 1s; }
    .particle:nth-child(11) { left: 55%; animation-duration: 21s; animation-delay: 3s; }
    .particle:nth-child(12) { left: 60%; animation-duration: 17s; animation-delay: 5s; }
    .particle:nth-child(13) { left: 65%; animation-duration: 23s; animation-delay: 0s; }
    .particle:nth-child(14) { left: 70%; animation-duration: 27s; animation-delay: 2s; }
    .particle:nth-child(15) { left: 75%; animation-duration: 16s; animation-delay: 4s; }
    .particle:nth-child(16) { left: 80%; animation-duration: 22s; animation-delay: 1s; }
    .particle:nth-child(17) { left: 85%; animation-duration: 25s; animation-delay: 3s; }
    .particle:nth-child(18) { left: 90%; animation-duration: 19s; animation-delay: 5s; }
    .particle:nth-child(19) { left: 95%; animation-duration: 24s; animation-delay: 0s; }
    .particle:nth-child(20) { left: 8%; animation-duration: 21s; animation-delay: 2s; }
    .particle:nth-child(21) { left: 22%; animation-duration: 18s; animation-delay: 4s; }
    .particle:nth-child(22) { left: 38%; animation-duration: 26s; animation-delay: 1s; }
    .particle:nth-child(23) { left: 52%; animation-duration: 20s; animation-delay: 3s; }
    .particle:nth-child(24) { left: 68%; animation-duration: 23s; animation-delay: 5s; }
    .particle:nth-child(25) { left: 82%; animation-duration: 17s; animation-delay: 0s; }
    
    /* ============================================= */
    /* TEXT AND HEADER STYLING                      */
    /* ============================================= */
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E88E5 0%, #7C4DFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        padding-top: 1rem;
    }
    
    .tagline {
        font-size: 1.4rem;
        color: #444;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #222;
        text-align: center;
        margin: 2rem 0 1rem 0;
    }
    
    .section-subheader {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Data source badges - semi-transparent */
    .data-badge {
        display: inline-block;
        background: rgba(227, 242, 253, 0.8);
        color: #1565C0;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        padding: 2rem 0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in ss:
    ss.authenticated = False
if 'role' not in ss:
    ss.role = None
if 'user_name' not in ss:
    ss.user_name = None

# Sidebar
SideBarLinks(show_home=True)

# =============================================================================
# ANIMATED PARTICLES BACKGROUND
# =============================================================================
st.markdown("""
<div class="particles">
    <div class="particle small"></div>
    <div class="particle medium blue"></div>
    <div class="particle large"></div>
    <div class="particle small light-blue"></div>
    <div class="particle medium"></div>
    <div class="particle small blue"></div>
    <div class="particle large light-blue"></div>
    <div class="particle medium"></div>
    <div class="particle small"></div>
    <div class="particle large blue"></div>
    <div class="particle small"></div>
    <div class="particle medium light-blue"></div>
    <div class="particle large"></div>
    <div class="particle small blue"></div>
    <div class="particle medium"></div>
    <div class="particle small light-blue"></div>
    <div class="particle large"></div>
    <div class="particle medium blue"></div>
    <div class="particle small"></div>
    <div class="particle large light-blue"></div>
    <div class="particle medium"></div>
    <div class="particle small blue"></div>
    <div class="particle large"></div>
    <div class="particle medium light-blue"></div>
    <div class="particle small"></div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# HERO SECTION
# =============================================================================
st.markdown('<h1 class="main-title">📚 StudyLink</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Smart Study Planning, Powered by Your Data</p>', unsafe_allow_html=True)

# Show different content based on authentication status
if ss.authenticated:
    # LOGGED IN VIEW
    st.success(f"Welcome back, **{ss.user_name}**!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"🎯 You're logged in as **{ss.role}**. Use the sidebar to navigate to your dashboard.")
        
        if st.button("🚪 Logout", use_container_width=True):
            ss.authenticated = False
            ss.role = None
            ss.user_name = None
            st.rerun()

else:
    # NOT LOGGED IN VIEW - Full landing page
    
    # Centered description
    col_left, col_center, col_right = st.columns([1, 3, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; padding: 0 1rem;">
            <p style="font-size: 1.15rem; color: #333; line-height: 1.8; margin-bottom: 1.5rem;">
                StudyLink is a smart, data-driven planner designed to optimize your daily study schedule 
                by integrating data from your <strong>calendar</strong>, <strong>sleep patterns</strong>, 
                and <strong>class workload</strong>. Say goodbye to inefficient time management and 
                stress from juggling multiple deadlines.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="data-badge">📅 Calendar Integration</span>
            <span class="data-badge">😴 Sleep Tracking</span>
            <span class="data-badge">📊 Grade Analytics</span>
            <span class="data-badge">⏱️ Time Tracking</span>
            <span class="data-badge">📈 User Behavior</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # =========================================================================
    # KEY FEATURES SECTION
    # =========================================================================
    st.markdown('<h2 class="section-header">✨ Key Features</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subheader">Everything you need to study smarter, not harder</p>', unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
    
    with feat_col1:
        with st.container(border=True):
            st.markdown("### 📅")
            st.markdown("**Centralized Calendar**")
            st.caption("All your assignments, exams, club meetings, and work shifts in one place")
    
    with feat_col2:
        with st.container(border=True):
            st.markdown("### 🧠")
            st.markdown("**Smart Optimization**")
            st.caption("AI-powered study plans that adapt to your schedule and energy levels")
    
    with feat_col3:
        with st.container(border=True):
            st.markdown("### 🔔")
            st.markdown("**Smart Reminders**")
            st.caption("Never miss a deadline with intelligent notifications and alerts")
    
    with feat_col4:
        with st.container(border=True):
            st.markdown("### 📊")
            st.markdown("**Progress Analytics**")
            st.caption("Track your study habits, sleep, and grades with visual insights")
    
    feat_col5, feat_col6, feat_col7, feat_col8 = st.columns(4)
    
    with feat_col5:
        with st.container(border=True):
            st.markdown("### 😴")
            st.markdown("**Sleep Integration**")
            st.caption("Balance rest and productivity based on your sleep patterns")
    
    with feat_col6:
        with st.container(border=True):
            st.markdown("### 🎯")
            st.markdown("**Grade Calculator**")
            st.caption("Know exactly what you need to achieve your target GPA")
    
    with feat_col7:
        with st.container(border=True):
            st.markdown("### 👥")
            st.markdown("**Advisor Connect**")
            st.caption("Stay connected with your academic advisor for support")
    
    with feat_col8:
        with st.container(border=True):
            st.markdown("### 🛡️")
            st.markdown("**Risk Alerts**")
            st.caption("Early warning system to catch academic issues before they grow")
    
    st.divider()
    
    # =========================================================================
    # HOW IT WORKS SECTION
    # =========================================================================
    st.markdown('<h2 class="section-header">🔄 How It Works</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subheader">Three simple steps to transform your study habits</p>', unsafe_allow_html=True)
    
    step_col1, step_col2, step_col3 = st.columns(3)
    
    with step_col1:
        with st.container(border=True):
            st.markdown("### Step 1️⃣")
            st.markdown("**Connect Your Data**")
            st.write("Link your calendar, import your class schedule, and set up sleep tracking.")
    
    with step_col2:
        with st.container(border=True):
            st.markdown("### Step 2️⃣")
            st.markdown("**Get Your Plan**")
            st.write("Our algorithm creates an optimized study schedule tailored just for you.")
    
    with step_col3:
        with st.container(border=True):
            st.markdown("### Step 3️⃣")
            st.markdown("**Track & Improve**")
            st.write("Monitor progress and watch your grades improve as StudyLink adapts.")
    
    st.divider()
    
    # =========================================================================
    # LOGIN SECTION
    # =========================================================================
    st.markdown('<h2 class="section-header">🚀 Get Started</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subheader">Select your role and choose a user to continue</p>', unsafe_allow_html=True)
    
    role_col1, role_col2 = st.columns(2)
    
    with role_col1:
        with st.container(border=True):
            st.markdown("### 🎓 Student")
            st.markdown("*For students seeking to improve study habits*")
            st.markdown("""
            - 📅 View centralized calendar with all deadlines
            - 📊 Track grades and calculate outcomes
            - 😴 Get workload analysis with rest suggestions
            """)        
            student_users = {
                "Maya Johnson": {
                    "email": "maya.j@northeastern.edu",
                    "studentID": 1
                }
            }

            selected_student = st.selectbox("Select Student:", student_users.keys())

            
            if st.button("Login as Student", type="primary", key="student_btn", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.role = "Student"
                st.session_state.user_name = selected_student
                st.session_state.user_email = student_users[selected_student]["email"]
                st.session_state.studentID = student_users[selected_student]["studentID"]  
                st.switch_page("pages/19_Student_homepage.py")

    
    with role_col2:
        with st.container(border=True):
            st.markdown("### 👨‍🏫 Academic Advisor")
            st.markdown("*For advisors supporting student success*")
            st.markdown("""
            - 👥 Monitor all advisee study activity
            - 🚨 Identify at-risk students early
            - 📝 Maintain meeting notes and follow-ups
            """)
            
            advisor_users = {
                "Dr. Jack Crash": "jack.crash@northeastern.edu",
            }
            
            selected_advisor = st.selectbox("Select Advisor:", list(advisor_users.keys()), key="advisor_select")
            
            if st.button("Login as Advisor", type="primary", key="advisor_btn", use_container_width=True):
                ss.authenticated = True
                ss.role = "Advisor"
                ss.user_name = selected_advisor
                ss.user_email = advisor_users[selected_advisor]
                st.switch_page('pages/04_Advisor_Dashboard.py')
    
    role_col3, role_col4 = st.columns(2)
    
    with role_col3:
        with st.container(border=True):
            st.markdown("### 📊 Data Analyst")
            st.markdown("*For analysts monitoring platform effectiveness*")
            st.markdown("""
            - 📈 View dashboards with study/sleep/GPA trends
            - 📁 Manage and archive datasets
            - 🔧 Fix data quality issues
            """)
            
            analyst_users = {
                "Jordan Lee": "jordan.lee@northeastern.edu",
            }
            
            selected_analyst = st.selectbox("Select Analyst:", list(analyst_users.keys()), key="analyst_select")
            
            if st.button("Login as Data Analyst", type="primary", key="analyst_btn", use_container_width=True):
                ss.authenticated = True
                ss.role = "Data Analyst"
                ss.user_name = selected_analyst
                ss.user_email = analyst_users[selected_analyst]
                st.switch_page('pages/01_Data_Analyst_homepage.py')
    
    with role_col4:
        with st.container(border=True):
            st.markdown("### ⚙️ System Administrator")
            st.markdown("*For admins managing the platform*")
            st.markdown("""
            - 🔗 Manage calendar connections and syncs
            - 📥 Import sleep and grade data files
            - 🩺 Run system health checks
            """)
            
            admin_users = {
                "John Smith": "john.smith@northeastern.edu",
            }
            
            selected_admin = st.selectbox("Select Admin:", list(admin_users.keys()), key="admin_select")
            
            if st.button("Login as System Admin", type="primary", key="admin_btn", use_container_width=True):
                ss.authenticated = True
                ss.role = "System Admin"
                ss.user_name = selected_admin
                ss.user_email = admin_users[selected_admin]
                st.switch_page('pages/40_Admin_Home.py')

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")

foot_col1, foot_col2, foot_col3 = st.columns(3)

with foot_col1:
    st.markdown("**📚 StudyLink**")
    st.caption("Smart Study Planning")

with foot_col2:
    st.markdown("**👥 Team OurSQL**")
    st.caption("Bennett, Alex, Alastaire, Tam, Trung")

with foot_col3:
    st.markdown("**🏫 Northeastern University**")
    st.caption("CS 3200 - Fall 2025")

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 1rem;">
    © 2025 StudyLink | Built with ❤️ using Streamlit, Flask, and MySQL
</div>
""", unsafe_allow_html=True)