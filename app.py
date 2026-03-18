import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import json
import os

st.set_page_config(layout="wide", page_title="Ellie's Brain", page_icon="🧠")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #f2ede8;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: #1c1c1c !important;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] * { color: #ddd6cc !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #272727 !important;
    border: 1px solid #383838 !important;
    border-radius: 8px !important;
    color: #ddd6cc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #272727 !important;
    border: 1px solid #383838 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] label {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #666 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stExpander {
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    background: #222 !important;
    margin-bottom: 8px;
}
[data-testid="stSidebar"] details summary p {
    font-size: 13px !important;
    font-weight: 500 !important;
}

.stButton > button {
    border-radius: 8px !important;
    background: #e8e0d5 !important;
    color: #1c1c1c !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 9px 14px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #d4c9b8 !important;
    transform: translateY(-1px) !important;
}

.sidebar-title {
    font-family: 'Instrument Serif', serif;
    font-size: 20px;
    color: #ddd6cc;
    margin-bottom: 18px;
    letter-spacing: -0.3px;
}

.page-title {
    font-family: 'Instrument Serif', serif;
    font-size: 30px;
    color: #1c1c1c;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.page-sub {
    font-size: 12px;
    color: #999;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-top: 2px;
    margin-bottom: 14px;
}

.toolbar-row {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
}

.hint-text {
    font-size: 11px;
    color: #aaa;
    letter-spacing: 0.3px;
    margin-top: 6px;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    width: auto !important;
    padding: 8px 18px !important;
}
</style>
""", unsafe_allow_html=True)

SAVE_FILE = "ellie_brain_final.json"

TAGS = ["core", "idea", "task", "reference", "question", "memory"]
TAG_COLORS = {
    "core":      "#c4af92",
    "idea":      "#96c9a8",
    "task":      "#e8a0a0",
    "reference": "#96aee8",
    "question":  "#e8d496",
    "memory":    "#c096e8",
}
# Sticky note background tints per tag
STICKY_BG = {
    "core":      "#fefce8",
    "idea":      "#f0fdf4",
    "task":      "#fff5f5",
    "reference": "#eff6ff",
    "question":  "#fffbeb",
    "memory":    "#faf5ff",
}

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {
        "nodes": {
            "Ellie": {"note": "This is your central mind map.\nClick any node to open a sticky note.", "color": "#c4af92", "url": "", "size": 42, "tag": "core"}
        },
        "edges": []
    }

def save_this_data():
    with open(SAVE_FILE, "w") as f:
        json.dump({"nodes": st.session_state.nodes, "edges": st.session_state.edges}, f)

if "nodes" not in st.session_state:
    data = load_data()
    st.session_state.nodes = data["nodes"]
    st.session_state.edges = data["edges"]

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🧠 Ellie\'s Brain</div>', unsafe_allow_html=True)

    with st.expander("＋  New Node", expanded=False):
        new_topic = st.text_input("Name", key="nn_name")
        new_note  = st.text_area("Note", key="nn_note", height=80)
        new_url   = st.text_input("Link", key="nn_url", placeholder="https://...")
        new_tag   = st.selectbox("Category", TAGS, key="nn_tag")
        parent    = st.selectbox("Connect to", list(st.session_state.nodes.keys()), key="nn_parent")
        if st.button("Deploy Node", key="deploy_btn"):
            if new_topic and new_topic not in st.session_state.nodes:
                st.session_state.nodes[new_topic] = {
                    "note":  new_note,
                    "color": TAG_COLORS.get(new_tag, "#c4af92"),
                    "url":   new_url,
                    "size":  26,
                    "tag":   new_tag,
                }
                st.session_state.edges.append([parent, new_topic])
                save_this_data()
                st.rerun()
            elif new_topic in st.session_state.nodes:
                st.warning("Name already exists.")

    with st.expander("✏️  Edit Node", expanded=False):
        edit_target = st.selectbox("Select node", list(st.session_state.nodes.keys()), key="edit_sel")
        if edit_target:
            ei = st.session_state.nodes[edit_target]
            edit_note = st.text_area("Note",  value=ei.get("note", ""),  key="edit_note",  height=80)
            edit_url  = st.text_input("Link", value=ei.get("url",  ""),  key="edit_url")
            edit_tag  = st.selectbox(
                "Category", TAGS,
                index=TAGS.index(ei.get("tag","core")) if ei.get("tag","core") in TAGS else 0,
                key="edit_tag"
            )
            if st.button("Save Changes", key="save_edit"):
                st.session_state.nodes[edit_target]["note"]  = edit_note
                st.session_state.nodes[edit_target]["url"]   = edit_url
                st.session_state.nodes[edit_target]["tag"]   = edit_tag
                st.session_state.nodes[edit_target]["color"] = TAG_COLORS.get(edit_tag, "#c4af92")
                save_this_data()
                st.rerun()

    with st.expander("🗑  Delete Node", expanded=False):
        deletable = [n for n in st.session_state.nodes if n != "Ellie"]
        if deletable:
            del_target = st.selectbox("Select node", deletable, key="del_sel")
            if st.button(f"Delete  {del_target}", key="del_btn"):
                del st.session_state.nodes[del_target]
                st.session_state.edges = [e for e in st.session_state.edges if del_target not in e]
                save_this_data()
                st.rerun()
        else:
            st.caption("No deletable nodes.")

    st.markdown("---")

    export_data = json.dumps({"nodes": st.session_state.nodes, "edges": st.session_state.edges}, indent=2)
    st.download_button("⬇  Export JSON", data=export_data, file_name="ellie_brain.json", mime="application/json", key="export_btn")

    st.markdown("---")
    if st.button("↺  Reset Brain", key="reset_btn"):
        st.session_state.nodes = {"Ellie": {"note": "Central Mind", "color": "#c4af92", "url": "", "size": 42, "tag": "core"}}
        st.session_state.edges = []
        save_this_data()
        st.rerun()

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Mind Map</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-sub">{len(st.session_state.nodes)} nodes · {len(st.session_state.edges)} connections</div>', unsafe_allow_html=True)

# Toolbar: Centre Map button + legend
tcol1, tcol2 = st.columns([1, 6])
with tcol1:
    centre_clicked = st.button("⊕  Centre Map", key="centre_btn")
with tcol2:
    legend_bits = " &nbsp; ".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:#555;font-family:DM Sans,sans-serif;">'
        f'<span style="width:9px;height:9px;border-radius:50%;background:{TAG_COLORS[t]};display:inline-block;"></span>{t}</span>'
        for t in TAGS
    )
    st.markdown(legend_bits, unsafe_allow_html=True)

st.markdown('<div class="hint-text">Click a node to open its sticky note &nbsp;·&nbsp; Double-click to follow its link</div>', unsafe_allow_html=True)

# ── Build pyvis ───────────────────────────────────────────────────────────────
net = Network(height="700px", width="100%", bgcolor="#f2ede8", font_color="#1c1c1c")
net.force_atlas_2based(gravity=-55, central_gravity=0.02, spring_length=130, spring_strength=0.08, damping=0.4)
net.set_options(json.dumps({
    "nodes": {
        "borderWidth": 1,
        "borderWidthSelected": 2.5,
        "font": {"size": 13, "face": "DM Sans"},
        "chosen": True
    },
    "edges": {
        "smooth": {"type": "curvedCW", "roundness": 0.08},
        "color": {"inherit": False},
        "selectionWidth": 2
    },
    "interaction": {
        "hover": True,
        "tooltipDelay": 100,
        "hideEdgesOnDrag": False,
        "zoomView": True,
        "zoomSpeed": 1
    },
    "manipulation": {
        "enabled": False
    },
    "layout": {
        "improvedLayout": True
    },
    "physics": {
        "enabled": True
    }
}))

nodes_json  = json.dumps(st.session_state.nodes)
sticky_bg_json = json.dumps(STICKY_BG)
tag_colors_json = json.dumps(TAG_COLORS)

for name, info in st.session_state.nodes.items():
    net.add_node(
        name,
        label=name,
        title="",   # we handle interaction ourselves
        color={
            "background": info["color"],
            "border":     info["color"],
            "highlight":  {"background": info["color"], "border": "#1c1c1c"},
            "hover":      {"background": info["color"], "border": "#555"}
        },
        size=info.get("size", 26),
        shape="dot",
        shadow={"enabled": True, "color": "rgba(0,0,0,0.12)", "size": 8, "x": 2, "y": 3},
        font={"size": 13, "face": "DM Sans", "color": "#1c1c1c"},
    )

for edge in st.session_state.edges:
    net.add_edge(edge[0], edge[1], color={"color": "#c4af92", "opacity": 0.7}, width=1.5)

graph_path = "ellie_brain_map.html"
net.save_graph(graph_path)

with open(graph_path, "r", encoding="utf-8") as f:
    html_content = f.read()

centre_js = ""
if centre_clicked:
    centre_js = """
    if (typeof network !== 'undefined') {
        network.fit({ animation: { duration: 700, easingFunction: 'easeInOutQuad' } });
    }
    """

injection = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Instrument+Serif&display=swap');
body {{ background: transparent !important; overflow: hidden; margin:0; }}
#mynetwork {{ border: none !important; background: transparent !important; }}

/* ── Sticky note base ── */
.ellie-sticky {{
    position: fixed;
    width: 240px;
    min-height: 150px;
    min-width: 180px;
    border-radius: 5px 5px 4px 4px;
    box-shadow: 3px 5px 22px rgba(0,0,0,0.14), 0 1px 4px rgba(0,0,0,0.08);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    resize: both;
    font-family: 'DM Sans', sans-serif;
    animation: stickyPop 0.18s cubic-bezier(0.34,1.56,0.64,1);
    transform-origin: top left;
}}
@keyframes stickyPop {{
    from {{ transform: scale(0.85); opacity: 0; }}
    to   {{ transform: scale(1);    opacity: 1; }}
}}

.ellie-sticky-header {{
    padding: 7px 8px 7px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: move;
    user-select: none;
    flex-shrink: 0;
    gap: 6px;
}}

.ellie-sticky-title {{
    font-size: 12px;
    font-weight: 500;
    color: #1c1c1c;
    letter-spacing: 0.2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}}

.ellie-sticky-actions {{
    display: flex;
    gap: 3px;
    align-items: center;
    flex-shrink: 0;
}}

.ellie-sticky-btn {{
    background: rgba(0,0,0,0.1);
    border: none;
    border-radius: 3px;
    width: 19px; height: 19px;
    cursor: pointer;
    font-size: 12px;
    line-height: 1;
    color: #1c1c1c;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    transition: background 0.12s ease;
    font-family: monospace;
}}
.ellie-sticky-btn:hover {{ background: rgba(0,0,0,0.2); }}
.ellie-sticky-btn.danger:hover {{ background: rgba(180,40,40,0.25); color: #c03030; }}

.ellie-sticky-body {{
    display: flex;
    flex-direction: column;
    padding: 10px 12px 10px 12px;
    gap: 6px;
    flex: 1;
    overflow: hidden;
}}

.ellie-sticky-textarea {{
    border: none;
    outline: none;
    background: transparent;
    resize: none;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: #2c2c2c;
    line-height: 1.65;
    flex: 1;
    min-height: 70px;
    width: 100%;
}}
.ellie-sticky-textarea::placeholder {{ color: #bbb; }}

.ellie-sticky-link {{
    font-size: 11px;
    color: #888;
    text-decoration: none;
    letter-spacing: 0.3px;
    border-top: 1px solid rgba(0,0,0,0.07);
    padding-top: 7px;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.ellie-sticky-link:hover {{ color: #444; }}

.ellie-sticky-tag {{
    font-size: 10px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: rgba(0,0,0,0.35);
    margin-top: auto;
    padding-top: 4px;
}}
</style>

<script>
const NODES_DATA    = {nodes_json};
const STICKY_BG     = {sticky_bg_json};
const TAG_COLORS    = {tag_colors_json};

let stickyMap = {{}};
let zTop = 1000;

function makeSticky(nodeId, x, y) {{
    // If already open, just bring to front
    if (stickyMap[nodeId]) {{
        const el = stickyMap[nodeId];
        el.style.display = 'flex';
        el.style.zIndex  = ++zTop;
        return;
    }}

    const info = NODES_DATA[nodeId];
    if (!info) return;

    const tag   = info.tag   || 'core';
    const bg    = STICKY_BG[tag]   || '#fefce8';
    const hdr   = TAG_COLORS[tag]  || '#c4af92';
    const note  = info.note  || '';
    const url   = info.url   || '';

    // Clamp position to viewport
    const vw = window.innerWidth, vh = window.innerHeight;
    const sx = Math.min(Math.max(x + 20, 10), vw - 260);
    const sy = Math.min(Math.max(y - 10, 10), vh - 200);

    const sticky = document.createElement('div');
    sticky.className = 'ellie-sticky';
    sticky.style.cssText = `left:${{sx}}px;top:${{sy}}px;background:${{bg}};border:1px solid ${{hdr}};z-index:${{++zTop}};`;

    // ── Header ──────────────────────────────────────────────
    const header = document.createElement('div');
    header.className = 'ellie-sticky-header';
    header.style.background = hdr;

    const title = document.createElement('div');
    title.className = 'ellie-sticky-title';
    title.textContent = nodeId;

    const acts = document.createElement('div');
    acts.className = 'ellie-sticky-actions';

    // Minimise
    const minBtn = document.createElement('button');
    minBtn.className = 'ellie-sticky-btn';
    minBtn.textContent = '−';
    minBtn.title = 'Minimise';
    let minimised = false;
    minBtn.addEventListener('click', (e) => {{
        e.stopPropagation();
        minimised = !minimised;
        body.style.display = minimised ? 'none' : 'flex';
        sticky.style.resize = minimised ? 'none' : 'both';
        minBtn.textContent = minimised ? '□' : '−';
    }});

    // Close (hide, keep in memory)
    const closeBtn = document.createElement('button');
    closeBtn.className = 'ellie-sticky-btn';
    closeBtn.textContent = '✕';
    closeBtn.title = 'Close';
    closeBtn.addEventListener('click', (e) => {{
        e.stopPropagation();
        sticky.style.display = 'none';
    }});

    // Delete (remove entirely)
    const delBtn = document.createElement('button');
    delBtn.className = 'ellie-sticky-btn danger';
    delBtn.textContent = '🗑';
    delBtn.title = 'Remove sticky';
    delBtn.addEventListener('click', (e) => {{
        e.stopPropagation();
        sticky.remove();
        delete stickyMap[nodeId];
    }});

    [minBtn, closeBtn, delBtn].forEach(b => acts.appendChild(b));
    header.appendChild(title);
    header.appendChild(acts);

    // ── Body ────────────────────────────────────────────────
    const body = document.createElement('div');
    body.className = 'ellie-sticky-body';

    const ta = document.createElement('textarea');
    ta.className = 'ellie-sticky-textarea';
    ta.value = note;
    ta.placeholder = 'No note yet...';
    body.appendChild(ta);

    if (url) {{
        const a = document.createElement('a');
        a.className = 'ellie-sticky-link';
        a.href = url;
        a.target = '_blank';
        a.textContent = '↗  ' + url.replace(/^https?:\\/\\//, '').split('/')[0];
        body.appendChild(a);
    }}

    const tagLabel = document.createElement('div');
    tagLabel.className = 'ellie-sticky-tag';
    tagLabel.textContent = tag;
    body.appendChild(tagLabel);

    sticky.appendChild(header);
    sticky.appendChild(body);
    document.body.appendChild(sticky);
    stickyMap[nodeId] = sticky;

    // ── Drag ────────────────────────────────────────────────
    let ox = 0, oy = 0;
    header.addEventListener('mousedown', (e) => {{
        if (e.target.tagName === 'BUTTON') return;
        e.preventDefault();
        sticky.style.zIndex = ++zTop;
        const r = sticky.getBoundingClientRect();
        ox = e.clientX - r.left;
        oy = e.clientY - r.top;
        const mv = (ev) => {{
            sticky.style.left = (ev.clientX - ox) + 'px';
            sticky.style.top  = (ev.clientY - oy) + 'px';
        }};
        const up = () => {{
            document.removeEventListener('mousemove', mv);
            document.removeEventListener('mouseup', up);
        }};
        document.addEventListener('mousemove', mv);
        document.addEventListener('mouseup', up);
    }});

    sticky.addEventListener('mousedown', () => {{ sticky.style.zIndex = ++zTop; }});
}}

// ── Wait for vis network ─────────────────────────────────────────────────
function waitForNetwork(cb) {{
    if (typeof network !== 'undefined' && network) cb();
    else setTimeout(() => waitForNetwork(cb), 200);
}}

waitForNetwork(() => {{
    // ── Clamp minimum zoom so the map never vanishes ──────────────────────
    const MIN_SCALE = 0.25;   // won't zoom out past 25 % of original size
    network.on('zoom', (params) => {{
        if (params.scale < MIN_SCALE) {{
            network.moveTo({{ scale: MIN_SCALE }});
        }}
    }});

    network.on('click', (params) => {{
        if (params.nodes.length > 0) {{
            const nodeId = params.nodes[0];
            const c = params.event.center;
            makeSticky(nodeId, c ? c.x : 400, c ? c.y : 300);
        }}
    }});

    network.on('doubleClick', (params) => {{
        if (params.nodes.length > 0) {{
            const info = NODES_DATA[params.nodes[0]];
            if (info && info.url) window.open(info.url, '_blank');
        }}
    }});

    {centre_js}
}});
</script>
"""

html_content = html_content.replace("</body>", injection + "\n</body>")
components.html(html_content, height=750, scrolling=False)
