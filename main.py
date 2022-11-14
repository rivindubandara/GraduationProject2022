# -------------------
# IMPORTING LIBRARIES
# import streamlit
from requests import head
import streamlit as st

# import specklepy
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

# import pandas
import pandas as pd

# import plotly express
import plotly_express as px

# -------------------

# -------------------
# PAGE CONFIG
st.set_page_config(page_title="Embodied Carbon Dashboard", page_icon="🧮")
# -------------------

# -------------------
# CONTAINERS
header = st.container()
input = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()
# -------------------

# -------------------
# HEADER
# Page Header
with header:
    st.title("Embodied Carbon Dashboard")
# About App
with header.expander("25 King Street, Brisbane🔽", expanded=True):
    st.markdown(
        """25 King is currently the tallest and largest engineered-timber office building in Australia. A co-creation between Lendlease and Aurecon, together with Bates Smart.

            Height : 46.8 meters

    Building Floor Area : 16,445m2 

    Construction Complete : 2018

  """
    )
# -------------------

# -------------------
# INPUTS
with input:
    st.subheader("Inputs")

    # ------
    # Columns for inputs
    serverCol, tokenCol = st.columns([1, 2])
    # User input boxes
    speckleServer = serverCol.text_input("Server URL", "speckle.xyz")
    speckleToken = tokenCol.text_input(
        "Speckle Token", "2195712381dff635fa55a923930d7ea63d4797d871"
    )
    # ------

    # ------
    # CLIENT
    client = SpeckleClient(host=speckleServer)
    # Get account from token
    account = get_account_from_token(speckleToken, speckleServer)
    # Authenticate
    client.authenticate_with_account(account)
    # ------

    # ------
    # Streams list
    streams = client.stream.list()
    # Get Stream names
    streamNames = [s.name for s in streams]
    # Dropdown for stream selection
    sName = st.selectbox(label="Select your stream", options=streamNames)
    # Selected Stream
    stream = client.stream.search(sName)[0]
    # Selected Branches
    branches = client.branch.list(stream.id)
    # Stream Commits
    commits = client.commit.list(stream.id, limit=100)
    commitMessage = [d.message for d in commits]
    commitNum = [c.id for c in commits]
    commitDict = dict(zip(commitMessage, commitNum))
    cName = st.selectbox(label="Select your category", options=commitDict)
    iD = commitDict[cName]
    # ------
# -------------------

# -------------------
# DEFINITIONS
# Python list to markdown list
def listToMarkdown(list, column):
    list = ["- " + i + "\n" for i in list]
    list = "".join(list)
    return column.markdown(list)


# creates an iframe from commit
def commit2viewer(stream, commit):
    embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + iD
    return st.components.v1.iframe(src=embed_src, width=700, height=1000)


# VIEWER
with viewer:
    st.subheader("Viewer")
    commit2viewer(stream, cName)
# -------------------
# STATS
with report:
    st.subheader("Speckle Statistics")
    # ------
    # Columns for cards
    branchCol, commitCol, connectorCol, contributorCol = st.columns(4)
    # ------

    # ------
    # Branch Card
    branchCol.metric(label="Number of branches", value=stream.branches.totalCount)
    # List of branches
    listToMarkdown([b.name for b in branches], branchCol)
    # ------

    # ------
    # Commit Card
    commitCol.metric(label="Number of commits", value=len(commits))

    # ------

    # ------
    # Connector Card
    # Connector List
    connectorList = [c.sourceApplication for c in commits]
    # connector names
    connectorNames = list(dict.fromkeys(connectorList))
    # number of connectors
    connectorCol.metric(
        label="Number of connectors", value=len(dict.fromkeys(connectorList))
    )
    # connectors list
    listToMarkdown(connectorNames, connectorCol)
    # ------

    # ------
    # Contributor Card
    contributorCol.metric(
        label="Number of contributors", value=len(stream.collaborators)
    )
    # contributor names
    contributorNames = list(dict.fromkeys([col.name for col in stream.collaborators]))
    # contributor list
    listToMarkdown(contributorNames, contributorCol)
    # ------
# ----------------------------

with graphs:
    st.subheader("Graphs")

# ------------
# LCA Stages Chart
# ------------
data = pd.read_csv("25KingTally_LCS_CSV.csv")
df = pd.DataFrame(
    data, columns=["Row Labels", "Sum of Global Warming Potential Total (kgCO2eq)"]
)
df.columns = ["lca_stage", "kgCO2eq"]

lcs_graph = px.bar(df, x=df.lca_stage, y=df.kgCO2eq, color=df.kgCO2eq)
lcs_graph.update_layout(
    autotypenumbers="convert types",
    showlegend=False,
    height=500,
    margin=dict(l=1, r=1, t=1, b=1),
)
st.subheader("kgCO2eq by LCA Stage")
st.write(lcs_graph)

# ------------
# Material Divison Chart
# ------------
data1 = pd.read_csv("25KingTally_div.csv")
df2 = pd.DataFrame(data1, columns=["Row Labels", "GWP"])
df2.columns = ["material", "kgCO2eq"]
div_chart = px.pie(df2, names=df2["material"], values=df2["kgCO2eq"], hole=0.5)
st.subheader("kgCO2eq by Material")
st.write(div_chart)

# ------------
# Renewable Energy by category Chart
# ------------

data2 = pd.read_csv("25KingTally_category.csv")
df3 = pd.DataFrame(
    data2, columns=["Row Labels", "Sum of Renewable Energy Demand Total (MJ)"]
)

df4 = pd.DataFrame(
    data2, columns=["Row Labels", "Sum of Global Warming Potential Total (kgCO2eq)"]
)

st.subheader("Sum of GWP per Revit Category")
st.write(df4)

df3.columns = ["revit_category", "renewable_energy_demand(mj)"]
cat_graph = px.bar(
    df3,
    x=df3.revit_category,
    y="renewable_energy_demand(mj)",
    color="renewable_energy_demand(mj)",
    log_y=True,
)

cat_graph.update_layout(
    autotypenumbers="convert types",
    showlegend=False,
    height=500,
    margin=dict(l=1, r=1, t=1, b=1),
)
st.subheader("Sum of Renewable Energy Demand by Category")
st.write(cat_graph)
