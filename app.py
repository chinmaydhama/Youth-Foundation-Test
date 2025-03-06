############################################################
#                   STREAMLIT DASHBOARD
#         Youth Impact Tutoring Program - Mega UI
#    An example with ~500 lines, advanced UX & analytics
############################################################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

# -----------------------------------------------------------
# 1. SET PAGE CONFIG & CUSTOM PAGE STYLING
# -----------------------------------------------------------
# Sets the layout to wide screen and a custom page title/icon
st.set_page_config(
    page_title="Youth Impact Tutoring Dashboard",
    page_icon="📊",
    layout="wide",
)

# CUSTOM STYLING (CSS) FOR IMPROVED UI
# Example: Slightly bigger font, custom colors, etc.
custom_css = """
<style>
/* Center the main title */
h1 {
    text-align: center !important;
}

/* Make subheaders more visible */
h2, h3 {
    margin-top: 1rem;
    font-weight: 600;
}

/* Style the sidebar */
[data-testid="stSidebar"] {
    background-color: #FAFAFA;
    border-right: 1px solid #DDD;
}

/* Customize metric boxes */
.element-container .stMetric {
    background-color: #F2F2F2;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 8px;
}

/* Table styling */
.dataframe table {
    border-collapse: collapse;
    width: 100%;
}
.dataframe th, .dataframe td {
    border: 1px solid #CCC;
    padding: 6px;
}

/* Add some spacing between sections */
.block-container {
    padding-top: 1rem;
}

/* Subtle text color for instructions */
.instruction-text {
    color: #555;
    font-size: 14px;
    margin-bottom: 10px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# -----------------------------------------------------------
# 2. LOAD DATA
# -----------------------------------------------------------
@st.cache_data
def load_data():
    """
    Load and cache the final_output.csv to optimize performance.
    In this example, we assume 'final_output.csv' has columns:
      - 'week'
      - 'district', 'block', 'school'
      - 'teachers_registered'
      - 'baseline_assessments'
      - 'endline_assessments'
      - 'baseline_average_level'
      - 'endline_average_level'
      - 'tutoring_calls'
    Additionally, we convert 'week' to a datetime (week_start).
    """
    df = pd.read_csv("final_output.csv")
    # Convert 'week' column to a datetime representing the start of the week
    df['week_start'] = pd.to_datetime(df['week'].str.split('/').str[0])
    return df


try:
    df_analysis = load_data()
except FileNotFoundError:
    st.error("File 'final_output.csv' not found. Please make sure the file is in the correct path.")
    st.stop()

# -----------------------------------------------------------
# 3. SIDEBAR & FILTERS
# -----------------------------------------------------------
st.sidebar.title("Filter & Options")

# Multiselect filters
districts = st.sidebar.multiselect(
    "Select District(s)",
    options=sorted(df_analysis['district'].unique()),
    default=None
)

blocks = st.sidebar.multiselect(
    "Select Block(s)",
    options=sorted(df_analysis['block'].unique()),
    default=None
)

schools = st.sidebar.multiselect(
    "Select School(s)",
    options=sorted(df_analysis['school'].unique()),
    default=None
)

# Date range filter (if you want to limit the weeks)
min_date = df_analysis['week_start'].min()
max_date = df_analysis['week_start'].max()
date_range = st.sidebar.date_input(
    label="Select Date Range (Week Start)",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters to data
filtered_df = df_analysis.copy()

# Filter by date range
start_date, end_date = date_range
if start_date > end_date:
    st.sidebar.error("Start date cannot be after end date.")
else:
    filtered_df = filtered_df[
        (filtered_df['week_start'] >= pd.to_datetime(start_date)) &
        (filtered_df['week_start'] <= pd.to_datetime(end_date))
        ]

# Filter by district
if districts:
    filtered_df = filtered_df[filtered_df['district'].isin(districts)]

# Filter by block
if blocks:
    filtered_df = filtered_df[filtered_df['block'].isin(blocks)]

# Filter by school
if schools:
    filtered_df = filtered_df[filtered_df['school'].isin(schools)]

# Display total rows after filtering
st.sidebar.write(f"Filtered Rows: {len(filtered_df)}")

# -----------------------------------------------------------
# 4. MAIN TITLE & INSTRUCTIONS
# -----------------------------------------------------------
st.title("Youth Impact Tutoring Program - Advanced Dashboard")

st.markdown(
    """
    Welcome to the **enhanced** Youth Impact Tutoring Program Dashboard! 
    Use the filters on the **left sidebar** to refine the view. Explore the 
    tabs below for in-depth analyses, visualizations, and insights.
    """,
    help="Use the sidebar to filter data by District, Block, School, and Date Range."
)

# -----------------------------------------------------------
# 5. TOP METRICS / KPIs
# -----------------------------------------------------------
st.markdown("## Overall Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_teachers = int(filtered_df['teachers_registered'].sum())
    st.metric("Total Teachers Registered", f"{total_teachers:,}")

with col2:
    total_baseline = int(filtered_df['baseline_assessments'].sum())
    st.metric("Total Baseline Assessments", f"{total_baseline:,}")

with col3:
    total_endline = int(filtered_df['endline_assessments'].sum())
    st.metric("Total Endline Assessments", f"{total_endline:,}")

with col4:
    total_tutoring = int(filtered_df['tutoring_calls'].sum())
    st.metric("Total Tutoring Calls", f"{total_tutoring:,}")

st.markdown("---")

# -----------------------------------------------------------
# 6. CREATE TABS FOR DIFFERENT INSIGHTS
# -----------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1) Teacher Registrations",
    "2) Assessments Conducted",
    "3) Learning Level Trends",
    "4) Tutoring Calls & Top Schools",
    "5) Deep Dives & Distribution",
    "6) Additional Analytics"
])

############################################################
# TAB 1: TEACHER REGISTRATIONS
############################################################
with tab1:
    st.header("Week over Week: Teachers Registered")
    st.write(
        "This section shows how many teachers have registered on the platform over time."
    )

    # Group data by week
    weekly_teachers = (
        filtered_df
        .groupby('week_start')['teachers_registered']
        .sum()
        .reset_index()
        .sort_values('week_start')
    )

    # Plot line chart
    fig_teachers = px.line(
        weekly_teachers,
        x='week_start',
        y='teachers_registered',
        title="Teachers Registered Over Time",
        markers=True
    )
    fig_teachers.update_layout(
        xaxis_title="Week",
        yaxis_title="Number of Teachers",
        hovermode="x unified"
    )
    st.plotly_chart(fig_teachers, use_container_width=True)

    # Show a data table with the raw numbers
    with st.expander("Show/Hide Raw Weekly Teachers Data"):
        st.dataframe(weekly_teachers.style.format({"teachers_registered": "{:,.0f}"}))

    st.markdown("---")

    # Group Teacher Registrations By: District, Block, or School
    st.subheader("Breakdown of Teacher Registrations")
    st.write(
        "Select a grouping from the dropdown below to view teacher registrations by District, Block, or School."
    )
    group_option = st.selectbox(
        "Group Teacher Registrations By:",
        ["District", "Block", "School"]
    )

    if group_option == "District":
        group_data = (
            filtered_df
            .groupby(['week_start', 'district'])['teachers_registered']
            .sum()
            .reset_index()
            .sort_values(['week_start', 'district'])
        )
        pivot_df = group_data.pivot(
            index='week_start',
            columns='district',
            values='teachers_registered'
        ).fillna(0)
        fig_group = px.line(
            group_data,
            x='week_start',
            y='teachers_registered',
            color='district',
            title="Teachers Registered by District Over Time",
            markers=True
        )
    elif group_option == "Block":
        group_data = (
            filtered_df
            .groupby(['week_start', 'block'])['teachers_registered']
            .sum()
            .reset_index()
            .sort_values(['week_start', 'block'])
        )
        pivot_df = group_data.pivot(
            index='week_start',
            columns='block',
            values='teachers_registered'
        ).fillna(0)
        fig_group = px.line(
            group_data,
            x='week_start',
            y='teachers_registered',
            color='block',
            title="Teachers Registered by Block Over Time",
            markers=True
        )
    else:  # School
        group_data = (
            filtered_df
            .groupby(['week_start', 'school'])['teachers_registered']
            .sum()
            .reset_index()
            .sort_values(['week_start', 'school'])
        )
        pivot_df = group_data.pivot(
            index='week_start',
            columns='school',
            values='teachers_registered'
        ).fillna(0)
        fig_group = px.line(
            group_data,
            x='week_start',
            y='teachers_registered',
            color='school',
            title="Teachers Registered by School Over Time",
            markers=True
        )

    fig_group.update_layout(xaxis_title="Week", yaxis_title="Teachers Registered")
    st.plotly_chart(fig_group, use_container_width=True)

    with st.expander("Show/Hide Pivot Table"):
        st.dataframe(pivot_df.style.format("{:,.0f}"))

############################################################
# TAB 2: ASSESSMENTS CONDUCTED
############################################################
with tab2:
    st.header("Baseline vs. Endline Assessments")
    st.write(
        "Here, you can observe how many Baseline and Endline assessments have been conducted each week."
    )

    # Weekly sums
    weekly_assessments = (
        filtered_df
        .groupby('week_start')[['baseline_assessments', 'endline_assessments']]
        .sum()
        .reset_index()
        .sort_values('week_start')
    )

    fig_assessments = px.line(
        weekly_assessments,
        x='week_start',
        y=['baseline_assessments', 'endline_assessments'],
        markers=True,
        title="Assessments Conducted Over Time (Baseline vs. Endline)"
    )
    fig_assessments.update_layout(
        xaxis_title="Week",
        yaxis_title="Number of Assessments",
        legend_title="Assessment Type"
    )
    st.plotly_chart(fig_assessments, use_container_width=True)

    with st.expander("Show/Hide Weekly Assessments Data"):
        st.dataframe(weekly_assessments.style.format("{:,.0f}"))

    st.markdown("---")

    st.subheader("Proportion of Baseline vs. Endline Assessments (Overall)")
    total_baseline = filtered_df['baseline_assessments'].sum()
    total_endline = filtered_df['endline_assessments'].sum()
    fig_pie = px.pie(
        names=['Baseline Assessments', 'Endline Assessments'],
        values=[total_baseline, total_endline],
        title="Overall Proportion of Baseline vs. Endline Assessments",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Extra: Show a bar chart by district or block
    st.markdown("---")
    st.subheader("Assessments by District or Block")
    assess_option = st.radio(
        "Choose grouping:",
        ("By District", "By Block")
    )

    if assess_option == "By District":
        group_assess = (
            filtered_df
            .groupby("district")[["baseline_assessments", "endline_assessments"]]
            .sum()
            .reset_index()
        )
        fig_bar_assess = px.bar(
            group_assess,
            x="district",
            y=["baseline_assessments", "endline_assessments"],
            title="Assessments by District",
            barmode="group"
        )
        fig_bar_assess.update_layout(xaxis_title="District", yaxis_title="Assessments")
        st.plotly_chart(fig_bar_assess, use_container_width=True)
        with st.expander("Show/Hide District Assessment Data"):
            st.dataframe(group_assess.style.format("{:,.0f}"))
    else:
        group_assess = (
            filtered_df
            .groupby("block")[["baseline_assessments", "endline_assessments"]]
            .sum()
            .reset_index()
        )
        fig_bar_assess = px.bar(
            group_assess,
            x="block",
            y=["baseline_assessments", "endline_assessments"],
            title="Assessments by Block",
            barmode="group"
        )
        fig_bar_assess.update_layout(xaxis_title="Block", yaxis_title="Assessments")
        st.plotly_chart(fig_bar_assess, use_container_width=True)
        with st.expander("Show/Hide Block Assessment Data"):
            st.dataframe(group_assess.style.format("{:,.0f}"))

############################################################
# TAB 3: LEARNING LEVEL TRENDS
############################################################
with tab3:
    st.header("Baseline vs. Endline Student Learning Level Trends")
    st.write(
        "Monitor the change in average student learning levels from baseline to endline over the weeks."
    )

    weekly_levels = (
        filtered_df
        .groupby('week_start')[['baseline_average_level', 'endline_average_level']]
        .mean()
        .reset_index()
        .sort_values('week_start')
    )
    fig_levels = px.line(
        weekly_levels,
        x='week_start',
        y=['baseline_average_level', 'endline_average_level'],
        markers=True,
        title="Student Learning Level Trends Over Time"
    )
    fig_levels.update_layout(
        xaxis_title="Week",
        yaxis_title="Average Level",
        legend_title="Assessment Type"
    )
    st.plotly_chart(fig_levels, use_container_width=True)

    with st.expander("Show/Hide Weekly Learning Level Data"):
        st.dataframe(weekly_levels.style.format("{:.2f}"))

    st.markdown("---")

    st.subheader("Comparison: Baseline vs. Endline by District/Block")
    compare_option = st.selectbox(
        "Compare Baseline vs. Endline By:",
        ["District", "Block", "School"]
    )

    if compare_option == "District":
        level_df = (
            filtered_df
            .groupby("district")[["baseline_average_level", "endline_average_level"]]
            .mean()
            .reset_index()
        )
        fig_compare = px.bar(
            level_df,
            x="district",
            y=["baseline_average_level", "endline_average_level"],
            barmode="group",
            title="Baseline vs. Endline Average Levels by District"
        )
        fig_compare.update_layout(xaxis_title="District", yaxis_title="Average Level")
        st.plotly_chart(fig_compare, use_container_width=True)
        with st.expander("Show/Hide District-Level Comparison Data"):
            st.dataframe(level_df.style.format("{:.2f}"))

    elif compare_option == "Block":
        level_df = (
            filtered_df
            .groupby("block")[["baseline_average_level", "endline_average_level"]]
            .mean()
            .reset_index()
        )
        fig_compare = px.bar(
            level_df,
            x="block",
            y=["baseline_average_level", "endline_average_level"],
            barmode="group",
            title="Baseline vs. Endline Average Levels by Block"
        )
        fig_compare.update_layout(xaxis_title="Block", yaxis_title="Average Level")
        st.plotly_chart(fig_compare, use_container_width=True)
        with st.expander("Show/Hide Block-Level Comparison Data"):
            st.dataframe(level_df.style.format("{:.2f}"))

    else:  # School
        level_df = (
            filtered_df
            .groupby("school")[["baseline_average_level", "endline_average_level"]]
            .mean()
            .reset_index()
        )
        # Maybe only plot top 20 schools by baseline
        level_df = level_df.nlargest(20, 'baseline_average_level').copy()
        fig_compare = px.bar(
            level_df,
            x="school",
            y=["baseline_average_level", "endline_average_level"],
            barmode="group",
            title="Baseline vs. Endline Average Levels (Top 20 Schools by Baseline)"
        )
        fig_compare.update_layout(xaxis_title="School", yaxis_title="Average Level")
        st.plotly_chart(fig_compare, use_container_width=True)
        with st.expander("Show/Hide School-Level Comparison Data"):
            st.dataframe(level_df.style.format("{:.2f}"))

############################################################
# TAB 4: TUTORING CALLS & TOP SCHOOLS
############################################################
with tab4:
    st.header("Tutoring Calls Trends & Top Schools")
    st.write(
        "Examine the number of tutoring calls over time and identify schools with the highest calls."
    )

    # Weekly Tutoring Calls
    weekly_tutoring_calls = (
        filtered_df
        .groupby('week_start')['tutoring_calls']
        .sum()
        .reset_index()
        .sort_values('week_start')
    )
    fig_tutoring = px.line(
        weekly_tutoring_calls,
        x='week_start',
        y='tutoring_calls',
        markers=True,
        title="Tutoring Calls Over Time"
    )
    fig_tutoring.update_layout(
        xaxis_title="Week",
        yaxis_title="Number of Tutoring Calls",
        hovermode="x unified"
    )
    st.plotly_chart(fig_tutoring, use_container_width=True)

    with st.expander("Show/Hide Weekly Tutoring Calls Data"):
        st.dataframe(weekly_tutoring_calls.style.format("{:,.0f}"))

    st.markdown("---")

    st.subheader("Top 10 Schools with Highest Tutoring Calls")
    top_schools_tutoring = (
        filtered_df
        .groupby('school')['tutoring_calls']
        .sum()
        .reset_index()
        .nlargest(10, 'tutoring_calls')
        .sort_values('tutoring_calls', ascending=True)
    )
    fig_top_schools = px.bar(
        top_schools_tutoring,
        x='tutoring_calls',
        y='school',
        orientation='h',
        title="Top 10 Schools with Highest Tutoring Calls"
    )
    fig_top_schools.update_layout(
        xaxis_title="Number of Tutoring Calls",
        yaxis_title="School",
        hovermode="y"
    )
    st.plotly_chart(fig_top_schools, use_container_width=True)

    with st.expander("Show/Hide Top 10 Schools Data"):
        st.dataframe(top_schools_tutoring.style.format("{:,.0f}"))

############################################################
# TAB 5: DEEP DIVES & DISTRIBUTION
############################################################
with tab5:
    st.header("Deep-Dive Visuals & Distributions")
    st.write(
        "Explore heatmaps, box plots, and distribution plots for a deeper understanding of student performance."
    )

    st.subheader("Heatmap: Baseline vs. Endline Levels Across Districts")
    district_levels = (
        filtered_df
        .groupby('district')[['baseline_average_level', 'endline_average_level']]
        .mean()
        .reset_index()
        .sort_values('district')
    )
    # Construct 2D data for the heatmap
    heatmap_z = [
        district_levels['baseline_average_level'].values,
        district_levels['endline_average_level'].values
    ]
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_z,
        x=district_levels['district'].values,
        y=['Baseline Level', 'Endline Level'],
        colorscale='Viridis'
    ))
    fig_heatmap.update_layout(
        title="Baseline vs. Endline Levels Across Districts",
        xaxis_title="Districts",
        yaxis_title="Assessment Type",
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    with st.expander("Show District-Level Averages Table"):
        st.dataframe(district_levels.style.format("{:.2f}"))

    st.markdown("---")

    st.subheader("Distribution of Student Levels Across Blocks (Box Plot)")
    fig_box = px.box(
        filtered_df,
        x='block',
        y='baseline_average_level',
        title="Distribution of Baseline Levels Across Blocks",
        labels={'baseline_average_level': 'Baseline Level', 'block': 'Block'},
        color='block'
    )
    fig_box.update_layout(
        xaxis_title="Block",
        yaxis_title="Baseline Level",
        showlegend=False
    )
    st.plotly_chart(fig_box, use_container_width=True)

    with st.expander("Customize the Box Plot"):
        # Let users choose which column to plot
        numeric_cols = [col for col in filtered_df.columns if filtered_df[col].dtype in [np.number]]
        selected_y = st.selectbox("Select numeric column for the Y-axis:", numeric_cols, index=0)
        fig_box_custom = px.box(
            filtered_df,
            x="block",
            y=selected_y,
            color="block",
            title=f"Distribution of {selected_y} Across Blocks"
        )
        st.plotly_chart(fig_box_custom, use_container_width=True)

############################################################
# TAB 6: ADDITIONAL ANALYTICS
############################################################
with tab6:
    st.header("Additional Analytics & Tools")
    st.write(
        "In this section, we dive into correlations, pivot tables, and user-driven analysis. "
        "You can also download filtered data for further offline analysis."
    )

    # -------------------------------------------------------
    # 6.1 CORRELATION MATRIX
    # -------------------------------------------------------
    st.subheader("Correlation Matrix")
    st.write("Evaluate correlations between numeric columns in the filtered dataset.")

    # Select numeric columns
    numeric_df = filtered_df.select_dtypes(include=[np.number]).copy()
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix",
            color_continuous_scale="RdBu_r",
            range_color=[-1, 1]
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        with st.expander("Show/Hide Correlation DataFrame"):
            st.dataframe(corr_matrix)
    else:
        st.warning("No numeric columns available for correlation in the filtered dataset.")

    st.markdown("---")

    # -------------------------------------------------------
    # 6.2 PIVOT TABLE EXPLORER
    # -------------------------------------------------------
    st.subheader("Pivot Table Explorer")
    st.write("Create a custom pivot table for deeper insight. Choose rows, columns, and a numeric metric.")

    # Let the user pick pivot table parameters
    columns_list = list(filtered_df.columns)
    pivot_index = st.selectbox("Select Row Field:", options=columns_list, index=0)
    pivot_columns = st.selectbox("Select Column Field:", options=columns_list, index=1)
    pivot_values = st.selectbox("Select Values Field:", options=columns_list, index=2)

    # Check if pivot_values is numeric
    if not np.issubdtype(filtered_df[pivot_values].dtype, np.number):
        st.warning("Please select a numeric field for 'Values Field'.")
    else:
        pivot_data = pd.pivot_table(
            filtered_df,
            index=pivot_index,
            columns=pivot_columns,
            values=pivot_values,
            aggfunc=np.sum
        )
        with st.expander("Show/Hide Pivot Table"):
            st.dataframe(pivot_data.style.format("{:,.2f}"))

    st.markdown("---")

    # -------------------------------------------------------
    # 6.3 DOWNLOAD FILTERED DATA
    # -------------------------------------------------------
    st.subheader("Download Filtered Data")
    st.write("Use the button below to download the currently filtered dataset as a CSV.")

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    # -------------------------------------------------------
    # 6.4 USER FEEDBACK SECTION
    # -------------------------------------------------------
    st.markdown("---")
    st.subheader("Feedback & Suggestions")
    st.write("Please share your feedback to help us improve this dashboard.")

    user_feedback = st.radio(
        "How would you rate this dashboard?",
        ("Excellent", "Good", "Fair", "Needs Improvement")
    )

    additional_comments = st.text_area("Additional Comments or Suggestions:", value="", max_chars=300)

    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
        # Here you could write the feedback to a database or a file if desired

############################################################
# 7. INSIGHTS & RECOMMENDATIONS
############################################################
st.markdown("---")
st.markdown("## Insights & Recommendations")
st.write(
    """
    - **Increase teacher engagement** in underperforming districts: Provide additional training, 
      support, or incentives to boost registrations.
    - **Monitor tutoring call effectiveness**: Correlate call frequency with student performance 
      improvements to identify best practices.
    - **Identify low-performing schools**: Focus resources where baseline levels are low and 
      endline improvements are minimal.
    - **Encourage frequent assessments**: Encourage teachers and administrators to conduct 
      regular baseline/endline assessments to track student progress.
    """
)

st.markdown(
    """
    **Thank you for using the Advanced Youth Impact Tutoring Dashboard!**  
    *Use the filters on the left to dive deeper into specific districts, blocks, or schools.*
    """,
    help="Click the tabs above to navigate different metrics."
)

# END OF CODE
