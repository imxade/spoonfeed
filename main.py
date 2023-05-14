import json, requests, re
import streamlit as st
from pyvis.network import Network
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

def dec():
  global data, class_name, url, qrl, headers, gpath, bpath
  
  # Comment the declaration below store database instead of overwriting
  data = upld('> Have Database ?')
  if not data:
    data = {
        "category": {
        }
    }
      
  # Get the class name
  class_name = list(data.keys())[0]
  
  # Analyze sentiment
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
  url = 'https://old.reddit.com/'
  qrl = '{}search.json?q={}&limit={}'
  gpath = "graph.html"
  bpath = "base.json"
 
def extract(url):
    with requests.Session() as session:
        response = session.get(url, headers=headers, allow_redirects=True)
        return response.text

def match(para, regex):
  para = re.sub(r'&\S+?;', '', para)
  matches = re.findall(regex, para)
  return matches
 
def ijson(json_data, category, value):
  if category in json_data:
      values = set(json_data[category])
      values.add(value)
      json_data[category] = list(values)
  else:
      json_data[category] = [value]

def catg(txt):
  analyzer = SentimentIntensityAnalyzer()
  score = analyzer.polarity_scores(txt)
  if score['compound'] < 0.3:
    catg = 'negative'
  elif score['compound'] > 0.4:
    catg = 'positive'
  else:
    catg = 'neutral'
  return catg

def has(string, term):
  return any(word in string for word in term.split())

def cdata(url, term):

  urls = match(extract(url), r'https://old\.reddit\.com/r[^"]+')
  for i in urls:
    paras = match(extract(i), r'<p>(.*?)</p>')
    for j in paras:
      if has(j, term):
        ijson(data[class_name], catg(j) , j)

  # Save the updated JSON back to the file
  with open(bpath, "w") as f:
      json.dump(data, f)
  mek_graf()

def mek_graf():
  # Create an instance of the Network class
  g = Network(directed=True)

  # Add the class node to the graph
  g.add_node(class_name, size=50, color="pink")

  # Iterate through the labels and add nodes and edges
  labels = data[class_name]
  for label, values in labels.items():
      # Add the label as a node
      g.add_node(label, size=30, color="violet")
      # Add an edge from the class node to the label node
      g.add_edge(class_name, label)
      for value in values:
          # Add the value as a node
          g.add_node(value, shape="box")
          # Add an edge from the label node to the value node
          g.add_edge(label, value)
  # Set the physics layout of the graph
  g.barnes_hut()
  g.show_buttons(filter_=["physics"])

  # Save the graph as HTML
  g.write_html(gpath)
  
def sho_graf():
  # Read the HTML
  with open(gpath, 'r') as f:
    html_page = f.read()
  
  # Render HTML

  st.components.v1.html(html_page, width=700, height=1200, scrolling=False)

def upld(desc):
  # Upload File 
  f = st.file_uploader(desc)
  if f is not None:
    data = f.read()
    st.write('File uploaded successfully!')
    return data

def dnld(desc, fpath):
  with open(fpath, 'r') as f:
    st.download_button(f'Download {desc}', f.read(), file_name=fpath)

def hide_brand():
  # Hide Streamlit Branding
  footer = """
              <style>
              footer {visibility: hidden;}
              </style>
              """
  st.markdown(footer, unsafe_allow_html=True) 
  
def main():
  # Title 
  st.title(':orange[Have Some Feedback]')

  
  # Input Form
  with st.form("input_form"):
    term = st.text_input('', label_visibility='collapsed', placeholder="Search")
    thrs = st.text_input('', label_visibility='collapsed', placeholder="Analysis Threshold")
    
    # Declare Global Var
    dec()

    # Submit
    st.form_submit_button("Submit")
    
  # No Input: Do nothing
  if term:
    link = qrl.format(url, term, thrs)
    cdata(link, term)
    sho_graf()
    dnld('Graph', gpath)
    dnld('Database', bpath)

# Run the app
if __name__ == "__main__":
  main()