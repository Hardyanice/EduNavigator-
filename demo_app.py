import requests
import pandas as pd
import streamlit as st
import time

# ----------------------------------------
# SCRAPER FUNCTIONS
# ----------------------------------------

def scrape_coursera(query):
    url = f"https://api.coursera.org/api/courses.v1?q=search&query={query}"
    resp = requests.get(url)
    data = resp.json()
    courses = []
    for c in data.get('elements', []):
        courses.append({
            'Platform': 'Coursera',
            'Title': c.get('name', 'N/A'),
            'URL': f"https://www.coursera.org/learn/{c.get('slug', '')}",
            'Price': "Free to audit / Paid for certificate"
        })
    return courses

def get_universities_by_country(country):
    url = f"http://universities.hipolabs.com/search?country={country}"
    resp = requests.get(url)
    data = resp.json()
    universities = []
    for uni in data:
        universities.append({
            "Name": uni.get("name"),
            "Country": uni.get("country"),
            "State/Province": uni.get("state-province"),
            "Website": ", ".join(uni.get("web_pages", []))
        })
    return universities

# ----------------------------------------
# STREAMLIT APP
# ----------------------------------------

st.set_page_config(page_title="Student Guidance App", layout="wide")
st.title("🎓 Student Guidance App")

tab1, tab2 = st.tabs(["🔍 Find Online Courses", "🏫 Find Universities by Country"])

with tab1:
    st.subheader("Find Online Courses")
    query = st.text_input("What do you want to learn?", placeholder="e.g. Data Science, Web Development", key="course_query")
    if st.button("Search Courses"):
        if not query.strip():
            st.error("Please enter a valid query.")
        else:
            all_courses = []
            with st.spinner("Scraping courses, please wait..."):
                try:
                    st.info("Scraping Coursera...")
                    all_courses.extend(scrape_coursera(query))
                    time.sleep(1)
                except Exception as e:
                    st.error(f"Error during scraping: {e}")

            if all_courses:
                df = pd.DataFrame(all_courses)
                st.success(f"Found {len(df)} courses!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Results as CSV", csv, "courses.csv", "text/csv")
            else:
                st.warning("No courses found. Try a different query.")

with tab2:
    st.subheader("Find Universities by Country")
    country = st.text_input("Enter the country name (e.g., India, United States, Canada):", key="country_query")
    if st.button("Search Universities"):
        if not country.strip():
            st.warning("Please enter a country name.")
        else:
            with st.spinner("Fetching universities..."):
                unis = get_universities_by_country(country)
                if unis:
                    df = pd.DataFrame(unis)
                    st.write(f"Found {len(df)} universities in {country}:")
                    st.dataframe(df)
                else:
                    st.info("No universities found for this country.")

st.markdown("---")
st.caption("Built for educational use. Respect robots.txt of each site.")
