import json
import requests
import re
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streamlit_agraph import agraph, Node, Edge, Config


def initialize_data():
    return (
        {"category": {}}
        if not upload_database("> Have Database ?")
        else {"category": {}}
    )


def fetch_html_content(url, headers):
    with requests.Session() as session:
        response = session.get(url, headers=headers, allow_redirects=True)
        return response.text


def find_matches_in_paragraph(para, regex):
    para = re.sub(r"&\S+?;", "", para)
    return re.findall(regex, para)


def update_json_data(json_data, category, value):
    category_values = set(json_data[category]) if category in json_data else set()
    category_values.add(value)
    json_data[category] = list(category_values)


def categorize_text_sentiment(txt):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(txt)
    return (
        "negative"
        if score["compound"] < 0.3
        else "positive" if score["compound"] > 0.4 else "neutral"
    )


def contains_term(string, term):
    return any(word in string for word in term.split())


def extract_and_update_data(data, class_name, url, term, headers):
    bpath = "base.json"
    urls = find_matches_in_paragraph(
        fetch_html_content(url, headers), r'https://old\.reddit\.com/r[^"]+'
    )

    for i in urls:
        paras = find_matches_in_paragraph(
            fetch_html_content(i, headers), r"<p>(.*?)</p>"
        )
        for j in paras:
            if contains_term(j, term):
                update_json_data(data[class_name], categorize_text_sentiment(j), j)

    with open(bpath, "w") as f:
        json.dump(data, f)


def create_graph(data, class_name):
    nodes = [Node(id=class_name, label=class_name, size=50, color="pink")]
    edges = []

    labels = data[class_name]
    for label, values in labels.items():
        nodes.append(Node(id=label, label=label, size=30, color="violet"))
        edges.append(Edge(source=class_name, target=label))

        for value in values:
            nodes.append(Node(id=value, label=value, shape="box"))
            edges.append(Edge(source=label, target=value))

    config = Config(
        width="", height=600, directed=True, physics=True, hierarchical=False
    )
    agraph_widget_key = "agraph_" + class_name
    st.write(agraph(nodes=nodes, edges=edges, config=config), key=agraph_widget_key)


def upload_database(description):
    f = st.file_uploader(description)
    if f is not None:
        st.write("File uploaded successfully!")
        return f.read()
    return None


def download_file(description, file_path, content):
    with open(file_path, "w") as f:
        f.write(content)
    st.download_button(f"Download {description}", content, file_name=file_path)


def hide_streamlit_branding():
    footer = """<style> footer {visibility: hidden;} </style>"""
    st.markdown(footer, unsafe_allow_html=True)


def get_search_link(url, term, threshold):
    return "{}search.json?q={}&limit={}".format(url, term, threshold)


def main():
    st.set_page_config(layout="wide")
    st.title(":orange[Have Some Feedback]")

    with st.form("input_form"):
        term = st.text_input("", label_visibility="collapsed", placeholder="Search")
        threshold = st.text_input(
            "", label_visibility="collapsed", placeholder="Analysis Threshold"
        )
        data = initialize_data()
        st.form_submit_button("Submit")

    if term:
        url = "https://old.reddit.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        search_link = get_search_link(url, term, threshold)
        extract_and_update_data(data, list(data.keys())[0], search_link, term, headers)
        create_graph(data, list(data.keys())[0])
        download_file("Database", "base.json", json.dumps(data))

    st.write("> [Source Code](https://codeberg.org/zz/SpoonFeed)")


if __name__ == "__main__":
    main()
