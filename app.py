from flask import Flask, render_template
import requests
import datetime
import json
from collections import Counter
import plotly
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)

API_KEY = '778d66dc3744f41da20fa88d135afa7c9dc2ddfa9ba7c96e49783a5e809ed33f'

def get_air_data():
    """API에서 미세먼지 데이터 조회"""
    try:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().strftime('%m')
        url = f'http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getUlfptcaAlarmInfo?serviceKey={API_KEY}&returnType=json&numOfRows=100&pageNo=1&year={year}&month={month}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get('response', {}).get('body', {}).get('items', [])
        return items, None
    except Exception as e:
        return [], f"API 호출 오류: {str(e)}"

def normalize_level(level_name):
    """경보 수준을 정규화된 클래스 이름으로 변환"""
    level_map = {
        '주의': 'warning',
        '경보': 'alert',
        '심각': 'critical'
    }
    return level_map.get(level_name, 'default')

def create_charts(items):
    """Plotly 차트 생성"""
    charts = {}
    
    if not items:
        return {}
    
    # issueGbn 필드 추가 (정규화된 클래스명)
    for item in items:
        item['issueGbn_class'] = normalize_level(item.get('issueGbn', ''))
    
    df = pd.DataFrame(items)
    
    # 1. 지역별 경보 현황 (막대 그래프)
    if 'districtName' in df.columns and len(df['districtName'].dropna()) > 0:
        district_counts = df['districtName'].value_counts().head(10)
        fig1 = go.Figure(data=[
            go.Bar(x=district_counts.index, y=district_counts.values, 
                   marker=dict(color=district_counts.values,
                              colorscale='Reds',
                              showscale=False),
                   text=district_counts.values,
                   textposition='outside',
                   textfont=dict(size=14, color='#333'))
        ])
        fig1.update_layout(title='📊 지역별 경보 발령 현황 TOP 10',
                           title_font_size=20,
                           xaxis_title='지역 (Region)',
                           yaxis_title='발령 횟수 (Alerts)',
                           xaxis=dict(tickfont=dict(size=12), tickangle=-45),
                           yaxis=dict(tickfont=dict(size=12)),
                           hovermode='x unified',
                           showlegend=False,
                           plot_bgcolor='rgba(240,240,240,0.3)',
                           paper_bgcolor='white',
                           margin=dict(l=60, r=60, t=80, b=100),
                           height=500)
        charts['chart1'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 2. 경보 레벨별 분포 (원형 그래프)
    if 'issueGbn' in df.columns and len(df['issueGbn'].dropna()) > 0:
        issue_counts = df['issueGbn'].value_counts()
        colors = {'주의': '#FFA500', '경보': '#FF6347', '심각': '#8B0000'}
        fig2 = go.Figure(data=[
            go.Pie(labels=issue_counts.index, values=issue_counts.values,
                   marker_colors=[colors.get(x, '#gray') for x in issue_counts.index],
                   textinfo='label+percent',
                   textfont=dict(size=12),
                   hole=0.2,
                   domain=dict(x=[0, 0.55], y=[0, 1]))
        ])
        fig2.update_layout(title='⚠️ 경보 단계별 분포',
                           title_font_size=18,
                           hovermode='closest',
                           height=500,
                           margin=dict(l=20, r=20, t=80, b=20),
                           legend=dict(x=0.58, y=0.5, orientation='v'))
        charts['chart2'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 3. 권역별 경보 (수평 막대 그래프)
    if 'moveName' in df.columns and len(df['moveName'].dropna()) > 0:
        move_counts = df['moveName'].value_counts()
        fig3 = go.Figure(data=[
            go.Bar(y=move_counts.index, x=move_counts.values,
                   orientation='h', marker_color='steelblue',
                   text=move_counts.values, textposition='outside',
                   textfont=dict(size=12, color='#333'))
        ])
        fig3.update_layout(title='🗺️ 권역별 경보 발령 현황',
                           title_font_size=18,
                           xaxis_title='발령 횟수 (Alerts)',
                           yaxis_title='권역 (Region)',
                           xaxis=dict(tickfont=dict(size=11)),
                           yaxis=dict(tickfont=dict(size=11)),
                           hovermode='y unified', showlegend=False,
                           plot_bgcolor='rgba(240,240,240,0.3)',
                           paper_bgcolor='white',
                           margin=dict(l=150, r=60, t=60, b=60),
                           height=500)
        charts['chart3'] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    return charts

def get_statistics(items):
    """통계 정보 계산"""
    if not items:
        return {
            'total_alerts': 0,
            'unique_districts': 0,
            'unique_regions': 0,
            'most_common_level': 'N/A'
        }
    
    stats = {
        'total_alerts': len(items),
        'unique_districts': len(set([item.get('districtName', 'N/A') for item in items if item.get('districtName')])),
        'unique_regions': len(set([item.get('moveName', 'N/A') for item in items if item.get('moveName')]))
    }
    
    issue_types = [item.get('issueGbn', 'N/A') for item in items if item.get('issueGbn')]
    if issue_types:
        stats['most_common_level'] = Counter(issue_types).most_common(1)[0][0]
    else:
        stats['most_common_level'] = 'N/A'
    
    return stats

@app.route('/')
def index():
    items, error = get_air_data()
    charts = create_charts(items)
    statistics = get_statistics(items)
    
    return render_template('index.html', 
                          items=items, 
                          error=error,
                          charts=charts,
                          statistics=statistics)

if __name__ == '__main__':
    app.run(debug=True)
