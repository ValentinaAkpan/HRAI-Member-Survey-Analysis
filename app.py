import pandas as pd
import streamlit as st
import plotly.express as px

# Streamlit app title
st.title("HRAI Member Survey Analysis")

# Define the path to the CSV file
file_path = "HRAI Member Survey on Potential US Tariffs.csv"

try:
    # Load the dataset
    df = pd.read_csv(file_path)

    # Simplify sales columns
    if 'Global sales ($), including sales in Canada: (Select one)' in df.columns:
        df['Global Sales Grouped'] = df['Global sales ($), including sales in Canada: (Select one)'].apply(
            lambda x: 'Over $100M' if '100,000,000' in str(x) else 'Under $100M'
        )
    if 'Sales ($) in Canada: (Select one)' in df.columns:
        df['Canadian Sales Grouped'] = df['Sales ($) in Canada: (Select one)'].apply(
            lambda x: 'Over $10M' if '10,000,000' in str(x) else 'Under $10M'
        )

    # Define questions and breakdown columns
    questions = [
        'What would the likely impact be on your company’s business if a 25% tariff imposed by the US Government on products imported into the United States?',
        'What would the likely impact be on your company’s business of a retaliatory 25% tariff imposed by the Government of Canada on products imported from the United States into Canada?',
        'How concerned are you about the likelihood of a potential 25% tariff on products imported into the United States?',
        'How concerned are you about the likelihood of a potential retaliatory 25% tariff on products imported into Canada?',
        'How likely are the following potential impacts of tariffs on your business globally?',
        'How likely are any of the following potential impacts of tariffs on your business in Canada?',
        'How strongly do you support the following potential policies/actions that might be taken by the Government of Canada?',
        'Does your company manufacture products in Canada?',
        'Please estimate what share of the products you sell in Canada are imported into Canada from the United States?',
        'Please estimate what share of the products you sell in Canada are imported into Canada from countries other than the US?'
    ]

    breakdowns = [
        'Type of Company: (Select one)',
        'Location of Headquarters: (Select one)',
        'Location of Production Facilities: (Select all that apply)',
        'Global Sales Grouped',
        'Canadian Sales Grouped'
    ]

    # Sidebar selection
    st.sidebar.header("Filter Options")
    selected_question = st.sidebar.selectbox("Select a question", options=questions)
    breakdown_column = st.sidebar.selectbox("Select a category for breakdown", options=breakdowns)

    # Validate selected columns
    if selected_question in df.columns and breakdown_column in df.columns:
        # Filter dataset to remove irrelevant entries
        filtered_df = df[df[selected_question].notnull() & (df[selected_question] != 'Response')]

        # Group by breakdown and question to count responses
        grouped_data = filtered_df.groupby([breakdown_column, selected_question]).size().reset_index(name='Count')

        # Add a filter for specific categories
        categories = grouped_data[breakdown_column].unique()
        valid_categories = [cat for cat in categories if cat != "Response"]
        selected_category = st.sidebar.selectbox("Filter by specific category", options=["All"] + valid_categories)

        # Apply category filter if a specific category is selected
        if selected_category != "All":
            grouped_data = grouped_data[grouped_data[breakdown_column] == selected_category]

        # Display question title
        if selected_category != "All":
            st.subheader(f"'{selected_question}' filtered by '{selected_category}'")
        else:
            st.subheader(f"'{selected_question}' by '{breakdown_column}'")

        # Create a pie chart for visualization
        fig = px.pie(
            grouped_data,
            values='Count',
            names=selected_question,
            title=f"Proportional Responses for '{selected_question}' by {breakdown_column}",
            hole=0.4
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(title_x=0.5)

        st.plotly_chart(fig)

        # Display the grouped data
        st.subheader("Data Table")
        st.dataframe(grouped_data)

        # Download option for grouped data
        st.download_button(
            label="Download Grouped Data as CSV",
            data=grouped_data.to_csv(index=False).encode('utf-8'),
            file_name="grouped_survey_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("Selected question or breakdown column is not available in the dataset.")
except FileNotFoundError:
    st.error(f"The file '{file_path}' could not be found. Ensure it is in the same directory as this script.")
