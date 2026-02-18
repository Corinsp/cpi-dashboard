import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import base64
import streamlit.components.v1 as components

# הגדרות עמוד
st.set_page_config(
    page_title="מדד המחירים לצרכן - דשבורד",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64_font(font_path):
    try:
        with open(font_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# טעינת הפונט Rubik
font_medium_base64 = get_base64_font("assets/Fonts/Rubik-Medium.ttf")
font_bold_base64 = get_base64_font("assets/Fonts/Rubik-Bold.ttf")

st.markdown(f"""
    <style>
    /* הגדרת הפונט הרגיל/בינוני */
    @font-face {{
        font-family: 'Rubik-Medium';
        src: url(data:font/ttf;base64,{font_medium_base64}) format('truetype');
    }}
    
    /* הגדרת הפונט המודגש */
    @font-face {{
        font-family: 'Rubik-Bold';
        src: url(data:font/ttf;base64,{font_bold_base64}) format('truetype');
    }}
    
    /* הגדרת ברירת המחדל לכל העמוד - Medium */
    * {{
        font-family: 'Rubik-Medium', sans-serif;
    }}

    .trend-tooltip-container {{
        position: relative;
        cursor: help; /* משנה את העכבר לסימן שאלה כדי לרמז שיש פה הסבר */
    }}
    
    .trend-tooltip-container[data-tooltip]::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(10, 38, 71, 0.95);
        color: white;
        padding: 14px 20px;
        border-radius: 8px;
        border: 1px solid #4A90E2;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        font-family: 'Rubik-Medium', sans-serif;
        font-size: 16px;
        line-height: 1.5;
        width: max-content;
        max-width: 340px;
        white-space: pre-line; /* קריטי כדי שירידות השורה יקרו באמת! */
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 100;
        pointer-events: none;
        direction: rtl;
        text-align: right;
        margin-bottom: 5px;
    }}
    
    .trend-tooltip-container[data-tooltip]:hover::after {{
        opacity: 1;
        visibility: visible;
    }}

    .block-container {{
        max-width: 1300px !important;
        padding-left: 50px !important;
        padding-right: 50px !important;
        margin: 0 auto !important;
        overflow-x: hidden !important;
    }}

    /* H1 - כותרת ראשית עליונה (32px) */
    .main-title {{ 
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 72px !important; 
    }}
    
    /* H2 - כותרות ראשיות של סקשנים (25px, Bold) */
    .chart-title, 
    .contributions-title, 
    .time-series-title {{ 
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 45px !important; 
        color: #0A2647 !important;
        margin-bottom: 0.5rem;
    }}
    
    /* H3 - כותרות משנה של סקשנים (20px, Medium) */
    .chart-subtitle, 
    .column-title, 
    .time-series-subtitle {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 35px !important; 
        color: #0A2647 !important;
    }}
    
    .shared-main-title {{
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 45px !important; /* <--- כאן תשני את הגודל של שתי הכותרות הראשיות יחד */
        font-weight: 700 !important;
        color: #0A2647;
        margin-bottom: 0.1rem !important;
        line-height: 1.2;
        text-align: right;
    }}
    
    .shared-subtitle {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 35px !important; /* <--- כאן תשני את הגודל של שתי כותרות המשנה יחד */
        font-weight: 400 !important;
        color: #0A2647;
        margin-top: 0 !important;
        text-align: right;
    }}

    .custom-group-name {{
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 26px !important;
        color: #0A2647 !important;
        margin-bottom: 0.8rem;
        min-height: 3.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .custom-group-percent {{
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 28px !important;
        color: #575756 !important;
    }}
    /* טקסט רגיל ושמות סעיפים (16px, Medium) */
    p, span, td, th, .contributor-name, .legend-text, .price-change-name {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 16px !important; 
    }}
    
    /* הערות וטקסטים קטנים (14px, Medium) */
    .note, .column-subtitle, .chart-note, .metric-subtitle {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 14px !important; 
    }}

    .hero-container {{
        direction: rtl;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    
    .main-title {{
        background-color: #f2f6fc !important;
        width: 100%;
        padding: 2.5rem 0;
        text-align: center !important;
        color: #0A2647 !important;
        border-radius: 0 !important;
        margin: 0 auto;
        display: block;
    }}
    
    .hero-section {{
        background: linear-gradient(135deg, #0A2647 0%, #143560 100%);
        width: 100%;
        padding: 3rem 0 5rem 0;
        border-radius: 0 0 30px 30px;
        position: relative;
        margin: 0 auto;
    }}

    .metrics-row {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 2rem !important;
        width: 100%;
    }}

    .metric-box {{ 
        width: 100% !important; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
    }}
    
    .metric-title {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 35px !important; 
        color: white !important; 
        height: 3rem; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        white-space: nowrap;
        margin-bottom: 1rem; 
    }}

    .circle-container {{ 
        width: 220px !important;
        height: 220px !important;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: help;
    }}
    
    .circle-bg-img {{ 
        position: absolute;
        width: 220px !important;
        height: 220px !important;
        top: 0;
        left: 0;
    }}

    .circle-content {{
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
    }}

    .circle-container[data-tooltip]::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 105%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(10, 38, 71, 0.95);
        color: white;
        padding: 14px 20px;
        border-radius: 8px;
        border: 1px solid #4A90E2;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        font-family: 'Rubik-Medium', sans-serif;
        font-size: 16px; 
        line-height: 1.5;
        width: max-content;
        max-width: 340px;
        white-space: normal;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 100;
        pointer-events: none;
        direction: rtl;
        text-align: right;
    }}

    .circle-container[data-tooltip]:hover::after {{
        opacity: 1;
        visibility: visible;
        bottom: 110%;
    }}

    .arrow-img {{
        width: 50px !important;
        height: auto;
        margin-bottom: 5px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }}

    .percentage-value {{
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 55px !important; 
        color: white !important;
        line-height: 1;
        display: block;
    }}

    .metric-subtitle, .index-level {{ 
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 35px !important; 
        color: white !important;
    }}

    .footer-trigger {{
        position: absolute;
        bottom: -15px; 
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        z-index: 10;
        width: 100%;
    }}

    .table-wrapper {{ 
        width: 100%; 
        display: flex; 
        justify-content: center; 
        margin-top: 20px; 
    }}
    
    .table-container {{
        background: #0A2647;
        padding: 25px;
        border-radius: 30px;
        width: 95%;
        max-width: 1100px;
    }}

    .custom-table {{ 
        width: 100%; 
        border-collapse: separate; 
        border-spacing: 2px; 
        direction: rtl; 
    }}
    
    .custom-table th, .custom-table td {{ 
        padding: 15px; 
        text-align: center !important; 
        background-color: white !important; 
        color: #0A2647 !important; 
    }}

    .minus-fix {{ 
        direction: ltr !important; 
        display: inline-block; 
    }}

    div[data-testid="stButton"] {{
        display: flex;
        justify-content: center;
        margin-top: -85px; /* מושך את הכפתור בדיוק מעל החץ של ה-HTML */
        position: relative;
        z-index: 20;
    }}

    div[data-testid="stButton"] button {{
        width: 120px !important;
        height: 80px !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        cursor: pointer;
    }}

    div[data-testid="stButton"] button:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px;
    }}
    
    div[data-testid="column"] {{
        position: relative;
        z-index: 10;
    }}

    .chart-section {{
        max-width: 760px;
        margin: 3rem auto;
        padding: 0 2rem;
    }}
    
    .chart-title {{
        text-align: center;
    }}
    
    .chart-subtitle {{
        text-align: center;
        margin-bottom: 2rem;
        direction: rtl;
        unicode-bidi: embed;
    }}
    </style>
""", unsafe_allow_html=True)

# פונקציות עזר
@st.cache_data
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return None

def load_table_data():
    files = {
        "מדד המחירים לצרכן": "data/main/cpi_120010_11-2015_11-2025.json",
        "המדד ללא ירקות ופירות": "data/additional/cpi_120020_11-2015_11-2025.json",
        "המדד ללא אנרגיה": "data/additional/cpi_110045_11-2015_11-2025.json",
        "המדד ללא דיור": "data/additional/cpi_110040_11-2015_11-2025.json"
    }
    
    table_rows = []
    for label, path in files.items():
        data = load_json(Path(path))
        if data and data.get('data'):
            latest = data['data'][0]
            table_rows.append({
                "label": label,
                "value": f"{latest['value']:.1f}",
                "monthly": f"{latest['monthly_change']:.1f}%",
                "yearly": f"{latest['yearly_change']:.1f}%"
            })
    return table_rows
    
def load_svg_base64(svg_path):
    try:
        with open(svg_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return ""

def get_circle_svg(value):
    if value > 0:
        return load_svg_base64("assets/SVG/Asset 4.svg")
    elif value < 0:
        return load_svg_base64("assets/SVG/Asset 2.svg")
    else:
        return load_svg_base64("assets/SVG/circle-gray.svg")

def get_arrow_svg(value):
    if value > 0:
        return load_svg_base64("assets/SVG/Asset 3.svg")
    elif value < 0:
        return load_svg_base64("assets/SVG/Asset 1.svg")
    else:
        return load_svg_base64("assets/SVG/neutral gray icn.svg")   
    
@st.cache_data
def load_main_index():
    main_file = Path("data/main/cpi_120010_11-2015_11-2025.json")
    if main_file.exists():
        return load_json(main_file)
    return None

def create_hero_section(latest_data):
    if 'show_table' not in st.session_state:
        st.session_state.show_table = False

    monthly_change = latest_data.get('monthly_change', 0)
    yearly_change = latest_data.get('yearly_change', 0)
    index_val = latest_data.get('index_relative_to_2024_avg', 0)
    
    curr_month = int(latest_data.get('month', 11))
    curr_year = int(latest_data.get('year', 2025))
    
    prev_month = 12 if curr_month == 1 else curr_month - 1
    
    month_names_hebrew = {
        1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
        5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
        9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
    }
    
    curr_month_name = month_names_hebrew.get(curr_month, "")
    prev_month_name = month_names_hebrew.get(prev_month, "")

    m_dir = "ירד" if monthly_change < 0 else "עלה" if monthly_change > 0 else "נותר ללא שינוי"
    y_dir = "ירד" if yearly_change < 0 else "עלה" if yearly_change > 0 else "נותר ללא שינוי"

    if monthly_change == 0:
        m_hover = f"בחודש {curr_month_name} {curr_year} נותר מדד המחירים לצרכן ללא שינוי לעומת {prev_month_name}, והגיע לרמה של {index_val:.1f} נקודות (הבסיס: ממוצע 2024=100.0 נקודות)."
    else:
        m_hover = f"בחודש {curr_month_name} {curr_year} {m_dir} מדד המחירים לצרכן ב-{abs(monthly_change):.1f}% לעומת {prev_month_name}, והגיע לרמה של {index_val:.1f} נקודות (הבסיס: ממוצע 2024=100.0 נקודות)."

    if yearly_change == 0:
        y_hover = f"ב-12 החודשים האחרונים ({curr_month_name} {curr_year} לעומת {curr_month_name} {curr_year-1}) נותר מדד המחירים לצרכן ללא שינוי."
    else:
        y_hover = f"ב-12 החודשים האחרונים ({curr_month_name} {curr_year} לעומת {curr_month_name} {curr_year-1}) {y_dir} מדד המחירים לצרכן ב-{abs(yearly_change):.1f}%."

    current_date = f"{curr_month_name} {curr_year}"
    
    right_trend = 0.9
    left_trend = 1.5

    if st.session_state.show_table:
        asset_action = load_svg_base64("assets/SVG/button up.svg")
        expand_text = "סגור נתונים נוספים"
    else:
        asset_action = load_svg_base64("assets/SVG/button down.svg")
        expand_text = "להרחבה על מדדים נוספים (ללא רכיבים)"

    arrow_m = get_arrow_svg(monthly_change)
    arrow_y = get_arrow_svg(yearly_change)
    circle_m = get_circle_svg(monthly_change)
    circle_y = get_circle_svg(yearly_change)

    def render_arrow(data):
        return f'<img src="data:image/svg+xml;base64,{data}" style="width:50px; margin-bottom:5px;"/>'

    m_title = "ירידה לעומת החודש הקודם" if monthly_change < 0 else "עלייה לעומת החודש הקודם"
    if monthly_change == 0: m_title = "ללא שינוי מהחודש הקודם"

    hero_html = f"""
    <div class="hero-container">
        <div class="main-title">מדד המחירים לצרכן - {current_date}</div>
        <div class="hero-section">
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="metric-title">{m_title}</div>
                    <div class="circle-container" data-tooltip="{m_hover}">
                        <img class="circle-bg-img" src="data:image/svg+xml;base64,{circle_m}" />
                        <div class="circle-content">
                            {render_arrow(arrow_m)}
                            <div class="percentage-value">{abs(monthly_change):.1f}%</div>
                        </div>
                    </div>
                    <div class="bottom-info">
                        <div class="metric-subtitle">רמת המדד</div>
                        <div class="index-level">{index_val:.1f} נק'</div>
                    </div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">שינוי ב-12 חודשים</div>
                    <div class="circle-container" data-tooltip="{y_hover}">
                        <img class="circle-bg-img" src="data:image/svg+xml;base64,{circle_y}" />
                        <div class="circle-content">
                            {render_arrow(arrow_y)}
                            <div class="percentage-value">{abs(yearly_change):.1f}%</div>
                        </div>
                    </div>
                    <div class="bottom-info" style="display: flex; flex-direction: column; align-items: center; width: 100%;">
                        <div class="metric-subtitle">מגמה - מדדי ליבה</div>
                        <div class="trend-tooltip-container" 
                             data-tooltip="קצב שינוי מחושב לפי נתוני אוג&#39;-נוב&#39; 2025,&#10;מנורמל לקצב שנתי.&#10;0.9% - ללא דיור&#10;1.5% - ללא דיור, ירקות ופירות"
                             style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                            <div class="index-level" dir="ltr" style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                                <div>{left_trend:.1f}%</div>
                                <div style="color: rgba(255, 255, 255, 0.5); font-weight: 300;">|</div>
                                <div>{right_trend:.1f}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="footer-trigger">
                <div style="color:white; font-size:1.5rem; margin-bottom:4px;">{expand_text}</div>
                <img src="data:image/svg+xml;base64,{asset_action}" style="width: 55px;" />
            </div>
        </div>
    </div>
    """
    st.markdown("".join(line.strip() for line in hero_html.splitlines()), unsafe_allow_html=True)

    if st.button("TEST_BUTTON", key="btn_toggle_final"):
        st.session_state.show_table = not st.session_state.show_table
        st.rerun()

    if st.session_state.show_table:
        rows = load_table_data()
        table_html = """
        <div class="table-wrapper">
            <div class="table-container">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>מדד</th>
                            <th>רמת המדד</th>
                            <th>שינוי ביחס לחודש קודם</th>
                            <th>שינוי ב-12 חודשים</th>
                        </tr>
                    </thead>
                    <tbody>"""
        for r in rows:
            m_val = f'<span class="minus-fix">{r["monthly"]}</span>' if "-" in r["monthly"] else r["monthly"]
            y_val = f'<span class="minus-fix">{r["yearly"]}</span>' if "-" in r["yearly"] else r["yearly"]
            
            table_html += f"""
                <tr>
                    <td style="background-color:#f8f9fa !important; font-weight:bold; color:#0A2647 !important;">{r['label']}</td>
                    <td>{r['value']}</td>
                    <td>{m_val}</td>
                    <td>{y_val}</td>
                </tr>"""
        table_html += "</tbody></table></div></div>"
        st.markdown(table_html, unsafe_allow_html=True)

def create_monthly_change_chart(data):
    df = pd.DataFrame(data)
    df = df.head(13)
    df = df.iloc[::-1]
    
    month_names = {
        1: "'ינו", 2: "'פבר", 3: 'מרץ', 4: "'אפר",
        5: 'מאי', 6: 'יוני', 7: 'יולי', 8: "'אוג",
        9: "'ספט", 10: "'אוק", 11: "'נוב", 12: "'דצמ"
    }
    
    df['month_name'] = df.apply(
        lambda row: f"{month_names.get(int(row['month']), '')}<br>{int(row['year'])}", 
        axis=1
    )
    
    colors = []
    bar_values = []
    for x in df['monthly_change']:
        if x > 0:
            colors.append('#2E6DB4')
        elif x < 0:
            colors.append('#E05A10')
        else:
            colors.append('#999999')
        bar_values.append(x)
    
    y_min = df['monthly_change'].min()
    y_max = df['monthly_change'].max()
    
    y_range_min = (int(y_min / 0.2) - 1) * 0.2
    y_range_max = (int(y_max / 0.2) + 2) * 0.2
    bottom_line = y_range_min
    
    fig = go.Figure()
    
    general_hover_style = dict(
        bgcolor='rgba(10, 38, 71, 0.95)',
        bordercolor='#4A90E2',
        font=dict(size=20, family='Rubik', color='white'),
        align='right'
    )
    
    value_hover_style = dict(
        bgcolor="#4d4d4d",
        bordercolor="#4d4d4d",
        font=dict(size=20, family="Rubik", color="white")
    )
    
    fig.add_trace(go.Scatter(
        x=df['month_name'],
        y=[y_range_max * 0.8] * len(df),
        mode='markers',
        marker=dict(size=50, color='rgba(0,0,0,0)', symbol='square'),
        hovertemplate='הגרף מציג את אחוז השינוי החודשי<br>במדד המחירים לצרכן בכל אחד מ-13<br>החודשים האחרונים, לעומת החודש שקדם לו.<extra></extra>',
        showlegend=False,
        hoverlabel=general_hover_style,
        hoverinfo='text'
    ))
    
    fig.add_trace(go.Bar(
        x=df['month_name'],
        y=bar_values,
        marker=dict(
            color=colors,
            line_width=0,
            pattern_fillmode="overlay"
    ),
        marker_line_width=0,
        width=0.55, 
        customdata=df['monthly_change'],
        hovertemplate='<b>%{customdata:.1f}</b><extra></extra>',
        showlegend=False,
        hoverlabel=value_hover_style
    ))
    
    fig.add_trace(go.Scatter(
        x=df['month_name'],
        y=[0] * len(df),
        mode='markers',
        marker=dict(size=35, color='rgba(0,0,0,0)'),
        customdata=df['monthly_change'],
        hovertemplate='<b>%{customdata:.1f}</b><extra></extra>',
        showlegend=False,
        hoverlabel=value_hover_style
    ))
    
    fig.add_hline(y=0, line_dash="solid", line_color="#999", line_width=2, opacity=0.7)
    fig.add_hline(y=bottom_line, line_dash="dot", line_color="#d3d3d3", line_width=1, opacity=0.5)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rubik", size=14, color="#999"),
        height=500, 
        margin=dict(l=50, r=50, t=20, b=80),
        xaxis=dict(
            title="",
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(size=16, family="Rubik-Medium", color="#575756")
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            showline=False,
            zeroline=False,
            tickfont=dict(size=16, family="Rubik-Medium", color="#575756"),
            dtick=0.2,
            range=[y_range_min, y_range_max]
        ),
        hovermode='closest'
    )
    
    return fig

# ===================
# לוגיקה חכמה לחישוב התרומות לקבוצות המשנה 
# ===================
@st.cache_data
def get_calculated_contributions():
    classification_file = Path("data/classification/groups_with_parent_level_siblings_depth_has_children.json")
    if not classification_file.exists():
        return []
        
    classification_data = load_json(classification_file)
    if not classification_data or 'data' not in classification_data:
        return []
        
    class_items = classification_data['data']
    
    leaf_codes = [
        item['group_code'] for item in class_items 
        if item.get('has_children') == 0
    ]
    
    special_codes = [120042, 120043] 
    leaf_codes = [c for c in leaf_codes if c not in special_codes]
    
    raw_candidates = []
    
    for code in leaf_codes:
        file_path = Path(f"data/groups/cpi_{code}_11-2015_11-2025.json")
        if file_path.exists():
            data = load_json(file_path)
            if data and data.get('data'):
                latest = data['data'][0]
                contrib = latest.get('contribution', 0)
                if contrib is not None:
                    raw_candidates.append({
                        'code': code,
                        'name': data.get('name', str(code)),
                        'contribution': contrib,
                        'monthly_change': latest.get('monthly_change', 0)
                    })
                    
    unified_contrib = 0
    unified_monthly_changes = []
    unified_valid = False
    
    for code in special_codes:
        file_path = Path(f"data/groups/cpi_{code}_11-2015_11-2025.json")
        if file_path.exists():
            data = load_json(file_path)
            if data and data.get('data'):
                latest = data['data'][0]
                contrib = latest.get('contribution', 0)
                if contrib is not None:
                    unified_contrib += contrib
                    unified_monthly_changes.append(latest.get('monthly_change', 0))
                    unified_valid = True
                    
    if unified_valid:
        avg_monthly = sum(unified_monthly_changes) / len(unified_monthly_changes) if unified_monthly_changes else 0
        raw_candidates.append({
            'code': 'unified_fresh',
            'name': 'ירקות ופירות טריים',
            'contribution': unified_contrib,
            'monthly_change': avg_monthly
        })
        
    raw_candidates.sort(key=lambda x: abs(x['contribution']), reverse=True)
    
    final_items = []
    
    for i, cand in enumerate(raw_candidates):
        if i < 8:
            final_items.append(cand)
        elif i < 10:
            if abs(cand['contribution']) > 0.01:
                final_items.append(cand)
            else:
                break
        else:
            break
            
    return final_items

# ===================
# ממשק המשתמש הראשי
# ===================

main_data = load_main_index()

if not main_data:
    st.error("⚠️ לא ניתן לטעון את נתוני המדד הראשי")
    st.stop()

latest_record = main_data['data'][0]

machine_ready_page = {
    "page_title": "מדד המחירים לצרכן",
    "report_date": f"{latest_record.get('month')}/{latest_record.get('year')}",
    "summary": {
        "monthly_change_percent": latest_record.get('monthly_change'),
        "yearly_change_percent": latest_record.get('yearly_change'),
        "index_level": latest_record.get('index_relative_to_2024_avg'),
        "base": "ממוצע 2024 = 100",
        "core_trend_without_housing_percent": 0.9,
        "core_trend_without_housing_vegetables_fruits_percent": 1.5,
        "core_trend_period": "אוגוסט-נובמבר 2025"
    },
    "monthly_changes_chart": {
        "description": "אחוז שינוי חודשי במדד המחירים לצרכן ב-13 החודשים האחרונים",
        "data": [
            {
                "month": d.get("month"),
                "year": d.get("year"),
                "monthly_change_percent": d.get("monthly_change")
            }
            for d in main_data['data'][:13]
        ]
    },
    "contributions_chart": {
        "description": "תרומת קבוצות מוצרים ושירותים לשינוי החודשי במדד",
        "data": get_calculated_contributions()
    },
    "time_series_chart": {
        "description": "רמת מדד המחירים לצרכן והמדד המנוכה עונתית ב-26 החודשים האחרונים",
        "data": [
            {
                "month": d.get("month"),
                "year": d.get("year"),
                "index_level": d.get("index_relative_to_2024_avg"),
                "seasonally_adjusted": d.get("seasonally_adjusted")
            }
            for d in main_data['data'][:26]
        ]
    }
}

st.markdown(f"""
    <script type="application/ld+json">
    {json.dumps(machine_ready_page, ensure_ascii=False, indent=2)}
    </script>
""", unsafe_allow_html=True)

create_hero_section(latest_record)

st.markdown('<div class="chart-section">', unsafe_allow_html=True)

st.markdown(f"""
    <div class="chart-title">אחוז שינוי בכל חודש לעומת החודש הקודם</div>
    <div class="chart-subtitle">13 החודשים האחרונים</div>
""", unsafe_allow_html=True)

fig_monthly_change = create_monthly_change_chart(main_data['data'])
st.plotly_chart(fig_monthly_change, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===================
# סעיף תרומות קבוצות
# ===================

st.markdown("""
    <style>
    .contributions-title {
        position: relative;
        z-index: 10;
        font-family: 'Rubik-Bold', sans-serif !important;
        font-weight: 700;
        font-size: 45px !important;
        color: #0A2647;
        text-align: center;
        margin-bottom: 3rem;
        margin-top: 2rem;
    }
    
    .contribution-column {
        background: transparent; 
        padding: 0;
        border-radius: 0;
        box-shadow: none;
    }
    
    .column-title {
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 400 !important;
        color: #0A2647 !important;
        text-align: right !important;
        margin-bottom: 0.2rem;
    }
    
    .column-subtitle {
        font-family: 'Rubik';
        font-size: 18px !important;
        color: #0A2647; 
        text-align: right; 
        margin-bottom: 2rem;
    }
    
    .top-contributor-item {
        display: flex;
        align-items: center;
        justify-content: flex-end; 
        gap: 1.5rem;
        padding: 0.5rem;
        margin-bottom: 1.5rem;
        background: transparent; 
        border-radius: 0;
        box-shadow: none; 
        flex-direction: row; 
    }
    
    .contributor-info {
        text-align: right; 
    }
    
    .contributor-name {
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 18px !important; 
        color: #0A2647; 
        margin-bottom: 0.2rem;
    }
    
    /* הגדלת האחוזים השמאליים והפיכתם לאפור כהה אחיד בולט */
    .contributor-change {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.3rem;
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 30px !important; 
        color: #444444 !important;
    }
    
    .contributor-arrow {
        width: 16px; 
        height: 16px;
    }
    </style>
""", unsafe_allow_html=True)

def create_horizontal_contributions_chart():
    contributions_data = get_calculated_contributions()
    if not contributions_data:
        return None
    
    contributions_data.sort(key=lambda x: abs(x['contribution']), reverse=False)
    
    machine_ready_json = json.dumps(contributions_data, ensure_ascii=False)
    st.markdown(f'<div id="machine-ready-contributions" style="display: none;">{machine_ready_json}</div>', unsafe_allow_html=True)
    
    df = pd.DataFrame(contributions_data)
    
    df['hover_text'] = df['contribution'].apply(lambda x: f"{x:.3f} :תרומה")
    
    colors = ['#3A82C4' if x >= 0 else '#E8712A' for x in df['contribution']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['name'],
        x=df['contribution'],
        orientation='h',
        marker=dict(
            color=colors,
            line_width=0,
            opacity=0.85
        ),
        width=0.35, 
        customdata=df['hover_text'],
        hovertemplate='<b>%{y}</b><br>%{customdata}<extra></extra>',
        hoverlabel=dict(
            bgcolor="rgba(10, 38, 71, 0.95)",
            font=dict(size=16, family="Rubik-Medium", color="white"),
            align='right',
            bordercolor='#4A90E2'
        ),
        showlegend=False
    ))
    
    for i, row in df.iterrows():
        fig.add_annotation(
            x=0,
            y=row['name'],
            text=row['display_name'] if 'display_name' in row else row['name'],
            showarrow=False,
            xanchor='right',
            xshift=-10,
            yanchor='bottom',
            yshift=6,
            font=dict(size=16, family="Rubik-Medium", color="#0A2647") 
        )

    fig.add_vline(x=0, line_dash="dash", line_color="#333", line_width=1, opacity=0.8)
    
    max_abs_val = df['contribution'].abs().max()
    if max_abs_val < 0.05:
        dtick_val = 0.01
    elif max_abs_val <= 0.2:
        dtick_val = 0.05
    else:
        dtick_val = 0.1

    x_min = df['contribution'].min()
    x_max = df['contribution'].max()

    import math
    range_min = math.floor(x_min / dtick_val) * dtick_val
    range_max = math.ceil(x_max / dtick_val) * dtick_val

    # וידוא שהrange מכיל לפחות שנתה אחת בכל כיוון
    if range_min == 0:
        range_min = -dtick_val
    if range_max == 0:
        range_max = dtick_val
        
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Rubik-Medium", size=16, color="#0A2647"), 
        height=620,  
        margin=dict(l=10, r=40, t=80, b=20, pad=10), 
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            side='top',
            tickfont=dict(family="Rubik-Medium", size=16, color="#575756"),
            showticklabels=True,
            dtick=dtick_val,
            tick0=0,
            tickformat=".1f",
            showline=False,
            ticks="outside",
            tickcolor='#999',
            tickwidth=1,
            ticklen=5,
            tickangle=0
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            showticklabels=False,
            range=[-1.2, len(df) - 0.3], 
        ),
        hovermode='closest'
    )
    
    fig.add_hline(y=len(df)-0.4, line_dash="dash", line_color="#999", line_width=1, opacity=0.5)

    return fig

def get_top_contributors():
    contributions_data = get_calculated_contributions()
    if not contributions_data:
        return []
    contributions_data.sort(key=lambda x: abs(x['contribution']), reverse=True)
    return contributions_data[:5]

st.markdown("""
    <div style="position: absolute; width: 100%; height: 950px; right: 0; background-color: #f2f6fc; z-index: 0; pointer-events: none; margin-top: -20px;"></div>
    <div class="contributions-title">תרומת קבוצות מוצרים ושירותים לשינוי החודשי במדד</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# עמודה שמאלית - 5 התורמים העיקריים
with col1:
    st.markdown("""
        <div class="contribution-column">
            <div class="column-title">התורמים העיקריים לשינוי החודשי</div>
            <div class="column-subtitle">(אחוז השינוי של הסעיף)</div>
        </div>
    """, unsafe_allow_html=True)
    
    top_contributors = get_top_contributors()
    
    icon_mapping = {
        121390: "assets/SVG/Asset 13.svg",
        121190: "assets/SVG/Asset 15.svg",
        121360: "assets/SVG/icon-car.svg", 
        121410: "assets/SVG/Asset 18.svg",
        'unified_fresh': "assets/SVG/Asset 17.svg" 
    }
    
    for contributor in top_contributors:
        change = contributor['monthly_change']
        item_code = contributor.get('code')
        
        icon_path = icon_mapping.get(item_code, "assets/SVG/Asset 15.svg")
        center_icon_svg = load_svg_base64(icon_path)
        
        if change > 0:
            circle_svg = load_svg_base64("assets/SVG/Asset 4.svg")
            arrow_svg = load_svg_base64("assets/SVG/Asset 3.svg")
            change_class = "positive"
        elif change < 0:
            circle_svg = load_svg_base64("assets/SVG/Asset 2.svg")
            arrow_svg = load_svg_base64("assets/SVG/Asset 1.svg")
            change_class = "negative"
        else:
            circle_svg = load_svg_base64("assets/SVG/circle-gray.svg")
            arrow_svg = load_svg_base64("assets/SVG/icon_neutral.svg")
            change_class = ""
        
        st.markdown(f"""
            <div class="top-contributor-item">
                <div class="contributor-info">
                    <div class="contributor-name">{contributor['display_name'] if 'display_name' in contributor else contributor['name']}</div>
                    <div class="contributor-change {change_class}">
                        <img class="contributor-arrow" src="data:image/svg+xml;base64,{arrow_svg}" alt="arrow" />
                        <span dir="ltr">{abs(change):.1f}%</span>
                    </div>
                </div>
                <div class="contributor-circle" style="position: relative; width: 96px; height: 96px;">
                    <img src="data:image/svg+xml;base64,{circle_svg}" alt="circle" style="width: 100%; height: 100%; display: block;" />
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                                width: 52px; height: 52px; overflow: hidden;">
                        <img src="data:image/svg+xml;base64,{center_icon_svg}" alt="icon" 
                             style="width: 100%; height: 100%; display: block; object-fit: contain;" />
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="contribution-column" style="padding-right: 40px;">
            <div class="column-title">תרומה לשינוי החודשי</div>
            <div class="column-subtitle">(נקודות מדד)</div>
        </div>
    """, unsafe_allow_html=True)
    
    fig_contributions = create_horizontal_contributions_chart()
    if fig_contributions:
        st.plotly_chart(fig_contributions, use_container_width=True)

# רווח כדי להפריד היטב לפני הסקשן הבא
st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)


# ===================
# סעיף שינויים בסעיפי צריכה נבחרים (חוזר לרקע לבן)
# ===================

st.markdown("""
    <style>
    .selected-changes-section {
        background: white;
        padding: 3rem 0;
        margin: 0 auto;
        max-width: 950px;
    }
    
    .selected-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        direction: rtl;
    }
    
    .selected-titles {
        text-align: right;
        flex: 1;
    }
    
    /* תאום זהה לחלוטין לכותרת הראשית למטה */
    .selected-main-title {
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #0A2647;
        margin-bottom: 0.5rem !important;
        line-height: 1.2;
    }
    
    /* תאום זהה לחלוטין לתת כותרת למטה */
    .selected-subtitle {
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #0A2647;
        margin-top: 0 !important;
    }
    
    .selected-image {
        width: 220px !important;
        height: auto;
        margin-left: 1rem !important;
    }
    
    .price-changes-title {
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 35px !important;
        color: #575756 !important;
        text-align: right;
        margin: 0 0 1rem 0;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="selected-changes-section" style="margin-top: -3.5em;">', unsafe_allow_html=True)

cart_image = load_svg_base64("assets/SVG/Asset 8.svg")

st.markdown(f"""
    <div class="selected-header">
        <div class="selected-titles">
            <div class="shared-main-title">שינויים בסעיפי צריכה נבחרים</div>
            <div class="shared-subtitle">שיעור השינוי במחירים לעומת החודש הקודם</div>
        </div>
        <img src="data:image/svg+xml;base64,{cart_image}" class="selected-image" alt="cart" />
    </div>
    <div class="price-changes-title">עליות וירידות מחירים בולטות</div>
""", unsafe_allow_html=True)

def get_top_selected_consumption_items():
    classification_file = Path("data/classification/groups_with_parent_level_siblings_depth.json")
    if not classification_file.exists():
        return []
    
    classification_data = load_json(classification_file)
    if not classification_data or 'data' not in classification_data:
        return []
    
    class_items = classification_data['data']
    
    level_1_groups = [
        item for item in class_items 
        if item.get('level') == 1 or item.get('parent_code') is None
    ]
    
    level_1_stats = []
    
    for group in level_1_groups:
        code = group['group_code']
        file_path = Path(f"data/groups/cpi_{code}_11-2015_11-2025.json")
        if file_path.exists():
            data = load_json(file_path)
            if data and data.get('data'):
                latest = data['data'][0]
                change = latest.get('monthly_change', 0)
                if change is not None:
                    level_1_stats.append({
                        'code': code,
                        'name': data.get('name', group.get('group_name', str(code))),
                        'change': change,
                        'score': abs(change)
                    })
                    
    level_1_stats.sort(key=lambda x: x['score'], reverse=True)
    top_5_level_1 = level_1_stats[:5]
    
    final_results = []
    
    for parent in top_5_level_1:
        parent_code = parent['code']
        parent_score = parent['score']
        
        children = [item for item in class_items if item.get('parent_code') == parent_code]
        children_to_evaluate = []
        
        if parent_code == 120040:
            special_codes = [120042, 120043]
            special_changes = []
            
            children = [c for c in children if c['group_code'] not in special_codes]
            
            for code in special_codes:
                c_file = Path(f"data/groups/cpi_{code}_11-2015_11-2025.json")
                if c_file.exists():
                    c_data = load_json(c_file)
                    if c_data and c_data.get('data'):
                        c_change = c_data['data'][0].get('monthly_change', 0)
                        special_changes.append(c_change)
            
            if special_changes:
                avg_change = sum(special_changes) / len(special_changes)
                children_to_evaluate.append({
                    'name': 'פירות וירקות טריים',
                    'change': avg_change,
                    'score': abs(avg_change)
                })
        
        for child in children:
            c_code = child['group_code']
            c_file = Path(f"data/groups/cpi_{c_code}_11-2015_11-2025.json")
            if c_file.exists():
                c_data = load_json(c_file)
                if c_data and c_data.get('data'):
                    c_latest = c_data['data'][0]
                    c_change = c_latest.get('monthly_change', 0)
                    if c_change is not None:
                        children_to_evaluate.append({
                            'name': c_data.get('name', child.get('group_name', str(c_code))),
                            'change': c_change,
                            'score': abs(c_change)
                        })
        
        best_child_score = -1
        best_child_change = 0
        best_child_name = ""
        
        for child_eval in children_to_evaluate:
            if child_eval['score'] > best_child_score:
                best_child_score = child_eval['score']
                best_child_change = child_eval['change']
                best_child_name = child_eval['name']
        
        if best_child_score > parent_score:
            final_results.append({
                'name': best_child_name,
                'change': best_child_change
            })
        else:
            final_results.append({
                'name': parent['name'],
                'change': parent['change']
            })

    final_results.sort(key=lambda x: abs(x['change']), reverse=True)       
    return final_results

top_changes = get_top_selected_consumption_items()

# בניית העמודות באמצעות HTML גמיש
grid_html = '<div style="display: flex; justify-content: space-between; direction: rtl; width: 100%;">\n'

for i, item in enumerate(top_changes):
    change = item['change']
    
    if change > 0:
        arrow_svg = load_svg_base64("assets/SVG/Asset 3.svg")
    elif change < 0:
        arrow_svg = load_svg_base64("assets/SVG/Asset 1.svg")
    else:
        arrow_svg = load_svg_base64("assets/SVG/neutral gray icn.svg")
    
    # הוספת קו הפרדה עבה ואפור.
    border_style = 'border-left: 8px solid #cccccc;' if i < len(top_changes) - 1 else ''
    
    # בניית הקובייה עם המחלקות החדשות שעוקפות את החסימה
    grid_html += f'<div style="flex: 1; text-align: center; padding: 0.5rem; display: flex; flex-direction: column; justify-content: space-between; {border_style}">\n'


    
    # שם הקבוצה מקבל את העיצוב המוגדל
    grid_html += f'<div class="custom-group-name">\n'
    grid_html += f'{item["name"]}\n'
    grid_html += f'</div>\n'
    
    grid_html += f'<div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-top: 0.5rem;">\n'
    grid_html += f'<div dir="ltr" class="custom-group-percent">\n'
    grid_html += f'{change:.1f}%\n'
    grid_html += f'</div>\n'
    grid_html += f'<img src="data:image/svg+xml;base64,{arrow_svg}" style="width: 24px; height: 24px;" alt="arrow" />\n'
    grid_html += f'</div>\n'
    grid_html += f'</div>\n'

grid_html += '</div>'
st.markdown(grid_html, unsafe_allow_html=True)


# ===================
# גרף מדד לאורך זמן
# ===================

st.markdown("""
    <style>
    .time-series-section {
        background: #f2f6fc !important;
        padding: 0;
        margin: 0;
    }
    
    .time-series-container {
        max-width: 760px;
        margin: 0 auto;
        background: #f2f6fc !important;
    }
    
    /* תאום זהה לחלוטין לכותרת הראשית למעלה */
    .time-series-title {
        font-family: 'Rubik-Bold', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #0A2647;
        text-align: right;
        margin-bottom: 0.5rem !important;
        line-height: 1.2;
    }
    
    /* תאום זהה לחלוטין לתת כותרת למעלה */
    .time-series-subtitle {
        font-family: 'Rubik-Medium', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #0A2647;
        text-align: right;
        margin-bottom: 2rem !important;
    }
    
    .custom-legend {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        margin-bottom: 1.5rem;
        direction: rtl;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .legend-icon {
        width: 24px;
        height: 24px;
        flex-shrink: 0;
    }
    
    .legend-text {
        font-family: Rubik;
        font-size: 0.95rem;
        color: #666;
        line-height: 1.3;
    }
    
    .chart-note {
        font-family: Rubik;
        font-size: 1rem;
        color: #666;
        text-align: right;
        margin-top: 1rem;
        padding-bottom: 1rem;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="time-series-section">', unsafe_allow_html=True)

st.markdown("""
    <div style="background: #f2f6fc; padding: 1.5rem 2rem 1rem 2rem; margin: 0; text-align: right;">
        <div class="shared-main-title">
            מדד המחירים לצרכן לאורך זמן
        </div>
        <div class="shared-subtitle" style="margin-bottom: 2rem !important;">
            רמת המדד והרכיב העונתי
        </div>
    </div>
""", unsafe_allow_html=True)

icon_11 = load_svg_base64("assets/SVG/Asset 11.svg")
icon_12 = load_svg_base64("assets/SVG/Asset 12.svg")

st.markdown(f"""
    <div style="background: #f2f6fc; padding: 0 2rem 1rem 2rem; margin: 0;">
        <div class="custom-legend" style="margin: 0;">
            <div class="legend-item">
                <img class="legend-icon" src="data:image/svg+xml;base64,{icon_11}" alt="icon" />
                <span class="legend-text">מדד המחירים לצרכן</span>
            </div>
            <div class="legend-item">
                <img class="legend-icon" src="data:image/svg+xml;base64,{icon_12}" alt="icon" />
                <span class="legend-text">מדד המחירים לצרכן<br>מנוכה עונתית</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

def create_time_series_chart():
    df = pd.DataFrame(main_data['data'])
    df = df.head(26).iloc[::-1]
    df['date_str'] = df.apply(lambda row: f"{int(row['month']):02d}/{int(row['year'])}", axis=1)
    
    month_names_short = {
        1: "'ינו", 2: "'פבר", 3: 'מרץ', 4: "'אפר",
        5: 'מאי', 6: 'יוני', 7: 'יולי', 8: "'אוג",
        9: "'ספט", 10: "'אוק", 11: "'נוב", 12: "'דצמ"
    }
    
    df['x_label'] = df.apply(lambda row: f"{month_names_short.get(int(row['month']), '')}<br>{int(row['year'])}", axis=1)
    
    x_values = []
    x_labels = []
    for i in range(len(df)-1, -1, -2):
        x_values.insert(0, i)  
        x_labels.insert(0, df.iloc[i]['x_label'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df['index_relative_to_2024_avg'],
        mode='lines+markers',
        name='מדד המחירים לצרכן',
        line=dict(color='#0a1e44', width=3),
        marker=dict(size=6, color='#0a1e44'),
        customdata=df['date_str'],
        hovertemplate='<b>מדד</b><br><b style="font-size:18px;">%{y:.1f}</b><extra></extra>',
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#4d4d4d",
            bordercolor="#4d4d4d",
            font=dict(size=14, family="Rubik", color="white")
        )
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df['seasonally_adjusted'],
        mode='lines+markers',
        name='מדד מנוכה עונתית',
        line=dict(color='#6fe1d9', width=3),
        marker=dict(size=6, color='#6fe1d9'),
        customdata=df['date_str'],
        hovertemplate='<b>מנוכה עונתית</b><br><b style="font-size:18px;">%{y:.1f}</b><extra></extra>',
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#4d4d4d",
            bordercolor="#4d4d4d",
            font=dict(size=14, family="Rubik", color="white")
        )
    ))
    
    fig.update_layout(
        plot_bgcolor='#f2f6fc',
        paper_bgcolor='#f2f6fc',
        font=dict(family="Rubik", size=13, color="#666"),
        height=450,
        margin=dict(l=50, r=20, t=20, b=80),
        xaxis=dict(
            title="",
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='#ccc',
            tickmode='array',
            tickvals=x_values,
            ticktext=x_labels,
            tickfont=dict(size=14, family="Rubik-Medium", color="#666"),
            ticks="outside",
            ticklen=8,
            tickwidth=2,
            tickcolor='#ccc',
            range=[-0.5, len(df)-0.5]
        ),
        yaxis=dict(
            title=dict(
                text="מדד",
                font=dict(size=14, family="Rubik-Medium", color="#666")
            ),
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='#ccc',
            range=[97, 105],
            dtick=1,
            tickfont=dict(size=14, family="Rubik-Medium", color="#666")
        ),
        hovermode='closest'
    )
    
    return fig

fig_time_series = create_time_series_chart()
st.plotly_chart(fig_time_series, use_container_width=True)

collapse_icon = load_svg_base64("assets/SVG/buttton colaps light.svg")
expand_icon = load_svg_base64("assets/SVG/button expand light.svg")

st.markdown(f"""
    <div style="background: #f2f6fc; padding: 1rem 2rem; margin: -2rem 0 0 0;">
        <div style="font-family: 'Rubik-Medium', sans-serif; font-size: 1.1rem; color: #575756; text-align: right; margin-bottom: 2rem; direction: rtl;">
            *המדד המנוכה עונתיות מוצג לצורך המחשה; ייתכנו עדכונים רטרואקטיביים.
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)