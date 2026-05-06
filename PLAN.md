# Kế hoạch triển khai Dự án Multi-Agent: VibeTube Advisor

## Chủ đề dự án
**VibeTube Advisor**: Hệ thống Multi-Agent tiếp nhận cảm xúc/tâm trạng của người dùng, đưa ra những lời khuyên đồng cảm và tìm kiếm, đề xuất các video YouTube (âm nhạc, video thư giãn, vlog tư vấn...) phù hợp nhất để giúp người dùng xoa dịu hoặc nâng cao tâm trạng.

## Tiến độ bám sát README.md (Trạng thái: ⏳ TODO, 🔄 IN PROGRESS, ✅ DONE)

### Milestone 1: Setup, chạy baseline skeleton (0-15')
- [x] ✅ Khảo sát dự án base và chốt chủ đề.
- [ ] ⏳ Setup môi trường, config API keys trong file `.env`.
- [x] ✅ TODO 1: Implement `llm_client.py` (trong `src/multi_agent_research_lab/services/`): Khởi tạo Client cho LLM (Sử dụng OpenAI gpt-4o-mini).
- [ ] ⏳ Chạy thử lệnh baseline: `python -m multi_agent_research_lab.cli baseline --query "..."` để đảm bảo code skeleton hoạt động.

### Milestone 2: Cài đặt Tool Tìm kiếm
- [x] ✅ TODO 2: Implement web/search client. Xây dựng tool tìm kiếm (Sử dụng YouTube Data API v3) trả về Tiêu đề, Link, và URL Thumbnail của video.

### Milestone 3: Build Supervisor / Router (15-45')
- [x] ✅ TODO 3: Implement routing decision trong `agents/supervisor.py`. Cấu hình LLM để nó làm nhiệm vụ điều phối luồng (Quyết định xem gọi Analyst, Researcher hay Writer tiếp theo dựa trên state).

### Milestone 4: Thêm Researcher, Analyst, Writer (45-75')
- [x] ✅ Cập nhật `core/state.py` để định nghĩa cấu trúc dữ liệu truyền giữa các agent (gồm `user_prompt`, `emotion_analysis`, `search_queries`, `video_results`, `final_answer`).
- [x] ✅ TODO 4.1: Implement `Analyst Agent` (Phân tích cảm xúc, xuất search queries).
- [x] ✅ TODO 4.2: Implement `Researcher Agent` (Dùng search client tìm video).
- [x] ✅ TODO 4.3: Implement `Writer Agent` (Tổng hợp thành bài viết và định dạng UI).

### Milestone 5: Build Workflow LangGraph
- [x] ✅ TODO 5: Build LangGraph workflow trong `graph/workflow.py`. Nối các node (Supervisor, Analyst, Researcher, Writer) lại với nhau thành 1 graph hoàn chỉnh.

### Milestone 6: Trace + Benchmark Single vs Multi (75-95')
- [x] ✅ TODO 6: Thêm tracing provider thật (LangSmith hoặc Langfuse) vào `observability/tracing.py`.
- [x] ✅ TODO 7: Chạy và lưu benchmark report (`reports/benchmark_report.md`), đánh giá sự khác biệt giữa Baseline và Multi-Agent.

- [x] ✅ Milestone 7: Tích hợp Giao diện người dùng UI (Bổ sung cho chủ đề)
- [x] ✅ Xây dựng Streamlit UI nhận query và hiển thị lời khuyên kèm các thẻ video YouTube + hiển thị chi phí (cost).

### Milestone 8: Peer review & Exit ticket (95-120')
- [x] ✅ Peer review theo rubric `docs/peer_review_rubric.md`.
- [x] ✅ Hoàn thành Exit ticket trong `docs/lab_guide.md`.
