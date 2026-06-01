import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            if not jobs:
                st.warning("No jobs were extracted from the URL.")
                return

            # Create a dropdown for selecting a job
            job_titles = [job.get("title", f"Job {i+1}") for i, job in enumerate(jobs)]
            selected_index = st.selectbox("Select a job to generate email for:", range(len(job_titles)), format_func=lambda i: job_titles[i])

            selected_job = jobs[selected_index]
            skills = selected_job.get('skills', [])
            links = portfolio.query_links(skills)
            email = llm.write_mail(selected_job, links)
            st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
