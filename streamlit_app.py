import pandas as pd
import streamlit as st

# Page Config
st.set_page_config(page_title="QuickDataScan", layout="wide")

# Title
st.markdown("""
    <h1 style='color: #4CAF50;'>📊 QuickDataScan</h1>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("""
    <h2 style='color: #1976D2;'>Navigation</h2>
""", unsafe_allow_html=True)

section = st.sidebar.radio("Go to:", ["Data Preview", "Missing Values", "Duplicates", "Column Stats", "Download Report"])

# File Upload
uploaded_file = st.file_uploader("Upload CSV, Excel, or JSON file", type=['csv', 'xlsx', 'json'])

max_size_mb = 200  # File size limit

if uploaded_file:
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        st.error(f"🛑 File too large! Please upload files smaller than {max_size_mb} MB.")
        st.stop()

    # Load the uploaded file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        df = pd.read_json(uploaded_file)
    else:
        st.error("Unsupported file format.")
        st.stop()

    st.success(f"✅ Loaded `{uploaded_file.name}` with {df.shape[0]} rows and {df.shape[1]} columns.")

    # Section 1: Data Preview
    if section == "Data Preview":
        st.subheader("🔍 Data Preview")

        # Display number of rows and columns
        st.write(f"**Dataset Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
        st.write(f"**Total Columns:** {df.shape[1]}")

        num_rows = st.slider("Number of rows to display", min_value=5, max_value=100, value=10)

        styled_df = df.head(num_rows).style.applymap(
            lambda val: 'background-color: #ffcdd2; color: black' if pd.isnull(val) else 'background-color: #e8f5e9; color: black'
        )

        st.dataframe(styled_df)

    # Section 2: Missing Values
    elif section == "Missing Values":
        st.subheader("🧐 Missing Value Summary")

        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing Values': df.isnull().sum(),
            'Missing %': (df.isnull().sum() / len(df)) * 100
        }).sort_values(by='Missing %', ascending=False)

        try:
            st.dataframe(missing_df.style.background_gradient(cmap='OrRd'))
        except ImportError:
            st.dataframe(missing_df)

        high_missing_cols = missing_df[missing_df['Missing %'] > 50]['Column'].tolist()
        if high_missing_cols:
            st.warning(f"⚠️ Columns with >50% missing: {', '.join(high_missing_cols)}")

    # Section 3: Duplicates
    elif section == "Duplicates":
        st.subheader("🔁 Duplicate Rows")
        duplicates_count = df.duplicated().sum()
        st.info(f"Total duplicate rows: {duplicates_count}")

        if duplicates_count > 0:
            st.write("Showing duplicate rows:")
            st.dataframe(df[df.duplicated()])

    # Section 4: Column Stats
    elif section == "Column Stats":
        st.subheader("📈 Column Statistics")

        dtype_df = pd.DataFrame(df.dtypes, columns=['Data Type']).reset_index().rename(columns={'index': 'Column'})
        st.dataframe(dtype_df)

        selected_col = st.selectbox("Select a column to visualize", options=df.columns)

        st.write("**Unique Values:**", df[selected_col].nunique())

        if not df[selected_col].mode().empty:
            st.write("**Most Frequent:**", df[selected_col].mode()[0])

        if pd.api.types.is_numeric_dtype(df[selected_col]):
            st.write("**Mean:**", round(df[selected_col].mean(), 2))
            st.write("**Min:**", df[selected_col].min())
            st.write("**Max:**", df[selected_col].max())
            st.line_chart(df[selected_col])

        else:
            if df[selected_col].nunique() < 20:
                st.bar_chart(df[selected_col].value_counts())
            else:
                st.write("Too many categories to visualize clearly.")

    # Section 5: Download Report
    elif section == "Download Report":
        st.subheader("📂 Download Data & Summary")

        csv_data = df.to_csv(index=False).encode('utf-8')
        json_data = df.to_json(orient='records')

        st.download_button("📅 Download CSV", csv_data, "cleaned_data.csv", "text/csv")
        st.download_button("📅 Download JSON", json_data, "cleaned_data.json", "application/json")

        summary_csv = df.describe().to_csv().encode('utf-8')
        st.download_button("📅 Download Quick Summary", summary_csv, "summary.csv", "text/csv")



