# Design Template

## Problem

Xây dựng hệ thống "VibeTube Advisor" - một chuyên gia AI phân tích cảm xúc người dùng từ các đoạn văn bản (text), thấu hiểu tâm lý và sau đó tìm kiếm, gợi ý các video YouTube phù hợp để giúp người dùng thư giãn, giải trí hoặc học tập, nhằm giải quyết các vấn đề tâm lý hiện tại của họ.

## Why multi-agent?

Single-agent không đủ vì:
1. **Quá tải Context**: Một Agent duy nhất vừa phải làm bác sĩ tâm lý (phân tích cảm xúc), vừa phải làm Data Engineer (tạo query, gọi YouTube API), vừa làm Content Writer (định dạng Markdown). Điều này dễ dẫn đến việc LLM bị "ảo giác" (hallucination) hoặc quên mất mục tiêu chính.
2. **Khó sử dụng Tools**: Kết hợp công cụ tìm kiếm YouTube (SearchClient) vào chung một Agent chung chung khiến Agent dễ bị rối khi quyết định lúc nào nên gọi API, lúc nào nên suy luận.
3. **Phân chia trách nhiệm**: Chia Multi-Agent giúp mỗi Agent có System Prompt chuyên biệt, dễ test, dễ debug và dễ dàng đánh giá (benchmark) từng phần.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Quản lý luồng, quyết định Agent nào chạy tiếp theo | `ResearchState` | Quyết định routing (next node) | Lặp vô hạn (infinite loop) nếu không biết khi nào kết thúc. |
| Analyst | Phân tích tâm lý, cảm xúc người dùng. Tạo danh sách từ khóa tìm kiếm (Search queries). | `user_query` | `emotion_analysis`, `search_queries` | Phân tích sai cảm xúc hoặc trả về query quá chung chung. |
| Researcher | Nhận queries, gọi YouTube Data API để thu thập danh sách video. | `search_queries` | `sources` (Danh sách Video metadata) | API hết quota, lỗi mạng, hoặc không tìm thấy video nào. |
| Writer | Tổng hợp lời khuyên từ Analyst và Video từ Researcher để viết thư phản hồi. | `emotion_analysis`, `sources` | `final_answer` (Markdown) | Trả về nội dung khô khan, thiếu đồng cảm hoặc quên chèn link video. |

## Shared state

- `request.query`: Lưu câu hỏi ban đầu của người dùng (cần để Analyst phân tích).
- `emotion_analysis`: Lời khuyên và phân tích tâm lý (Cần cho Writer).
- `search_queries`: Danh sách từ khóa (Cần cho Researcher tìm kiếm).
- `sources`: Danh sách Video YouTube thu thập được (Cần cho Writer chèn vào bài).
- `final_answer`: Phản hồi cuối cùng (Trả về cho User).
- `total_cost`: Tổng chi phí USD (Để đo lường hiệu quả).
- `route_history`: Lịch sử các bước di chuyển (Để debug và tránh loop).

## Routing policy

Luồng hoạt động (Workflow Graph):
1. **START** ➡️ `Supervisor`
2. `Supervisor` kiểm tra state:
   - Chưa có phân tích? ➡️ Gọi `Analyst`.
   - Đã có từ khóa nhưng chưa có video? ➡️ Gọi `Researcher`.
   - Đã có video nhưng chưa có bài viết? ➡️ Gọi `Writer`.
   - Đã có bài viết? ➡️ `FINISH`.

## Guardrails

- Max iterations: Cần giới hạn vòng lặp trong LangGraph (ví dụ max_steps=10) để tránh Supervisor bị kẹt.
- Timeout: Thêm timeout cho YouTube API call.
- Retry: Nếu Analyst trả về lỗi định dạng JSON, retry LLM call 1-2 lần.
- Fallback: Nếu Researcher không tìm thấy video qua API, sử dụng list video tĩnh dự phòng (fallback videos).
- Validation: Đảm bảo Writer luôn trả về Markdown hợp lệ.

## Benchmark plan

| Query | Metric | Expected Outcome |
|---|---|---|
| "Tôi thấy mệt mỏi" | Latency | Multi-agent < 30s |
| "Tôi thất tình" | Quality Score | Điểm độ đồng cảm > 8/10 |
| "Tôi mất ngủ" | Cost | < $0.01 / request |
