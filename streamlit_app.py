import streamlit as st
import streamlit.components.v1 as components
import time
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow

st.set_page_config(page_title="VibeTube Advisor Pro", page_icon="🧠", layout="wide")

# Custom CSS for Main UI
st.markdown("""
<style>
.main { background-color: #f8fafc; }
.log-box {
background-color: #1e293b;
border-left: 4px solid #3b82f6;
padding: 12px;
margin-bottom: 15px;
border-radius: 6px;
color: #f8fafc;
font-size: 14px;
box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.log-title { font-weight: 900; color: #93c5fd; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px; }
.log-section { font-weight: bold; color: #cbd5e1; margin-top: 6px; font-size: 12px; text-transform: uppercase; }
.log-data { background-color: #0f172a; padding: 8px; border-radius: 4px; font-family: 'Consolas', monospace; white-space: pre-wrap; font-size: 13px; color: #10b981; max-height: 150px; overflow-y: auto;}
</style>
""", unsafe_allow_html=True)

# 1. SIDEBAR: AGENT LOGS (TRÁI)
with st.sidebar:
    st.title("⚙️ Agent Logs")
    st.markdown("Giám sát Input/Output thời gian thực.")
    st.divider()
    log_container = st.container()

# 2. MAIN AREA (PHẢI)
st.title("🧠 VibeTube Advisor Pro")
st.markdown("Hệ thống Đa Tác Vụ Phân Tích Cảm Xúc & Đề Xuất Nội Dung")

# HÀM VẼ ĐỒ THỊ MÔ HÌNH MẠNG LƯỚI (HUB & SPOKE)
def render_dynamic_graph(active_node, data_passed):
    nodes = {
        "user": {"icon": "👤", "name": "User", "color": "#64748b", "pos": "top: 15%; left: 50%;"},
        "supervisor": {"icon": "🧠", "name": "Supervisor", "color": "#3b82f6", "pos": "top: 50%; left: 50%;"},
        "analyst": {"icon": "🕵️‍♂️", "name": "Analyst", "color": "#8b5cf6", "pos": "top: 50%; left: 15%;"},
        "researcher": {"icon": "🔍", "name": "Researcher", "color": "#10b981", "pos": "top: 50%; left: 85%;"},
        "writer": {"icon": "✍️", "name": "Writer", "color": "#f59e0b", "pos": "top: 85%; left: 30%;"},
        "finish": {"icon": "🏁", "name": "Finish", "color": "#ef4444", "pos": "top: 85%; left: 70%;"}
    }
    
    html = '<div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 30px; border-top: 6px solid #3b82f6;">\n'
    html += '<h4 style="margin-top:0; text-align: center; color: #475569; font-family: sans-serif; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; margin-bottom: 15px;">Mô Hình Đa Tác Vụ (Hub & Spoke Topology)</h4>\n'
    
    # SVG container for connection lines
    html += '<div style="position: relative; width: 100%; max-width: 550px; height: 350px; margin: 0 auto; background-color: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">\n'
    
    html += '<svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0;">\n'
    # Các đường kẻ từ Supervisor tới các Node khác
    html += '<line x1="50%" y1="15%" x2="50%" y2="50%" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="5,5"/>\n'
    html += '<line x1="15%" y1="50%" x2="50%" y2="50%" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="5,5"/>\n'
    html += '<line x1="85%" y1="50%" x2="50%" y2="50%" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="5,5"/>\n'
    html += '<line x1="30%" y1="85%" x2="50%" y2="50%" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="5,5"/>\n'
    html += '<line x1="70%" y1="85%" x2="50%" y2="50%" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="5,5"/>\n'
    html += '</svg>\n'
    
    # Render các Node
    for n_id, n in nodes.items():
        is_active = (n_id == active_node)
        
        scale = "scale(1.15)" if is_active else "scale(1)"
        opacity = "1" if is_active else "0.5"
        filter_style = "none" if is_active else "grayscale(50%)"
        animation = "pulse 1.5s infinite" if is_active else "none"
        bg_color = "#eff6ff" if is_active else "white"
        border_color = n["color"] if is_active else "#cbd5e1"
        z_index = "10" if is_active else "5"
        
        # Lớp bao bên ngoài để cố định vị trí tuyệt đối
        html += f'<div style="position: absolute; {n["pos"]}; transform: translate(-50%, -50%); z-index: {z_index};">\n'
        
        # Lớp bên trong để định dạng và hiệu ứng (scale/pulse)
        html += f'<div style="transform: {scale}; opacity: {opacity}; filter: {filter_style}; transition: all 0.4s; background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 85px; text-align: center; animation: {animation};">\n'
        
        html += f'<div style="font-size: 30px;">{n["icon"]}</div>\n'
        html += f'<div style="font-weight: 800; color: #1e293b; font-family: sans-serif; font-size: 11px; margin-top: 5px;">{n["name"]}</div>\n'
        if is_active:
            html += f'<div style="font-size: 9px; font-weight: bold; color: white; background: {n["color"]}; padding: 2px 5px; border-radius: 8px; margin-top: 4px; display: inline-block;">ACTIVE</div>\n'
            
        html += '</div>\n' # end inner
        html += '</div>\n' # end outer
        
    # Hộp tin nhắn Data Passed nổi ở dưới cùng trung tâm
    html += '<div style="position: absolute; bottom: -18px; left: 50%; transform: translateX(-50%); z-index: 20;">\n'
    html += f'<div style="background: #1e293b; color: #38bdf8; padding: 8px 25px; border-radius: 20px; font-size: 13px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2); font-family: monospace; border: 1px solid #334155; white-space: nowrap; animation: popIn 0.3s ease-out;">📦 {data_passed}</div>\n'
    html += '</div>\n'
    
    html += '</div>\n' # end relative container
    html += '</div>\n' # end outer white container
    html += '<style>@keyframes pulse { 0% { transform: scale(1.15); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); } 50% { transform: scale(1.25); box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); } 100% { transform: scale(1.15); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } } @keyframes popIn { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }</style>'
    
    return html

# Khu vực hiển thị đồ thị động
graph_placeholder = st.empty()
graph_placeholder.markdown(render_dynamic_graph("user", "Chờ phản hồi..."), unsafe_allow_html=True)

# Input Box
user_query = st.text_area("Hôm nay bạn thấy thế nào?", placeholder="Nhập cảm xúc hoặc câu chuyện của bạn vào đây...", height=100)

if st.button("🚀 Bắt đầu Phân Tích & Tư Vấn", use_container_width=True, type="primary"):
    if len(user_query) < 5:
        st.warning("Vui lòng chia sẻ thêm (ít nhất 5 ký tự).")
    else:
        state = ResearchState(request=ResearchQuery(query=user_query))
        workflow = MultiAgentWorkflow()
        final_state = state
        data_passed = "Phân tích User Query"
        
        with st.spinner("Hệ thống đang xử lý..."):
            for event in workflow.stream(state):
                for node_name, node_state_dict in event.items():
                    final_state = ResearchState(**node_state_dict)
                    
                    log_input = f"State({data_passed})"
                    log_output = ""
                    
                    if node_name == "analyst":
                        log_output = f"Analysis: {final_state.emotion_analysis[:80]}...\nQueries: {final_state.search_queries}"
                        next_data_passed = "Gửi Cảm Xúc & Từ Khóa cho Supervisor"
                    elif node_name == "researcher":
                        log_output = f"YouTube API Response: Found {len(final_state.sources)} videos."
                        next_data_passed = "Gửi Danh Sách Video cho Supervisor"
                    elif node_name == "writer":
                        log_output = "Final Markdown Response generated based on videos and analysis."
                        next_data_passed = "Gửi Kết Quả Cuối Cùng"
                    elif node_name == "supervisor":
                        route = final_state.route_history[-1] if final_state.route_history else "FINISH"
                        log_output = f"LLM Routing Decision -> Handoff to {route.upper()}"
                        next_data_passed = f"Kích hoạt Agent {route.upper()}"
                    
                    # Cập nhật đồ thị (Hiện toàn bộ Agent, highlight node hiện tại)
                    graph_placeholder.markdown(render_dynamic_graph(node_name, data_passed), unsafe_allow_html=True)
                    
                    # Cập nhật Log bên Sidebar Trái
                    log_html = '<div class="log-box">\n'
                    log_html += f'<div class="log-title">[{time.strftime("%H:%M:%S")}] 🤖 {node_name.upper()}</div>\n'
                    log_html += '<div class="log-section">📥 INPUT</div>\n'
                    log_html += f'<div class="log-data">{log_input}</div>\n'
                    log_html += '<div class="log-section">📤 OUTPUT</div>\n'
                    log_html += f'<div class="log-data">{log_output}</div>\n'
                    log_html += '</div>\n'
                    
                    with log_container:
                        st.markdown(log_html, unsafe_allow_html=True)
                    
                    data_passed = next_data_passed
                    time.sleep(1)
            
            # Kết thúc luồng
            graph_placeholder.markdown(render_dynamic_graph("finish", "Hoàn thành quy trình tư vấn!"), unsafe_allow_html=True)

        # 3. KẾT QUẢ TRẢ VỀ
        st.markdown("---")
        st.markdown("### 💌 Phản hồi từ VibeTube Advisor")
        st.info(final_state.emotion_analysis)
        st.markdown(final_state.final_answer)
        
        # HIỂN THỊ CHI PHÍ (COST)
        st.success(f"💳 **Tổng chi phí Agent:** ${final_state.total_cost:.5f} | **Số bước đồ thị:** {len(final_state.route_history)}")
        
        # HIỂN THỊ VIDEO CUỘN NGANG AN TOÀN
        if final_state.sources:
            st.markdown("### 🎥 Video Đề Xuất (Cuộn ngang)")
            
            video_cards_html = ""
            for doc in final_state.sources:
                thumb = doc.metadata.get("thumbnail", "https://via.placeholder.com/300x160")
                title = doc.title
                channel = doc.metadata.get("channel_title", "YouTube")
                url = doc.url
                
                video_cards_html += f"""
                <a href="{url}" target="_blank" style="text-decoration: none;">
                    <div style="flex: 0 0 280px; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; border: 1px solid #e2e8f0; transition: transform 0.2s; height: 100%;">
                        <img src="{thumb}" style="width: 100%; height: 150px; object-fit: cover; border-bottom: 1px solid #e2e8f0;">
                        <div style="padding: 15px; display: flex; flex-direction: column; flex-grow: 1;">
                            <div style="font-family: sans-serif; font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{title}</div>
                            <div style="font-family: sans-serif; font-size: 12px; color: #64748b; margin-top: auto;">📺 {channel}</div>
                        </div>
                    </div>
                </a>
                """
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ margin: 0; padding: 0; background-color: transparent; font-family: sans-serif; }}
                .scroll-container {{
                    display: flex;
                    overflow-x: auto;
                    gap: 20px;
                    padding: 15px 10px 25px 10px;
                    scrollbar-width: thin;
                    scrollbar-color: #3b82f6 #f1f5f9;
                }}
                .scroll-container::-webkit-scrollbar {{ height: 8px; }}
                .scroll-container::-webkit-scrollbar-track {{ background: #f1f5f9; border-radius: 4px; }}
                .scroll-container::-webkit-scrollbar-thumb {{ background-color: #3b82f6; border-radius: 4px; }}
                a:hover div {{ transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
            </style>
            </head>
            <body>
                <div class="scroll-container">
                    {video_cards_html}
                </div>
            </body>
            </html>
            """
            
            components.html(full_html, height=290, scrolling=False)
