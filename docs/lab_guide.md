# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. Case nào nên dùng multi-agent? Vì sao?
- **Trả lời:** Nên dùng Multi-Agent cho các bài toán phức tạp, đòi hỏi nhiều kỹ năng chuyên biệt (như phân tích cảm xúc, tìm kiếm dữ liệu thực tế, tổng hợp nội dung). Việc chia nhỏ giúp mỗi Agent tập trung làm tốt một việc với công cụ (tools) và prompt riêng biệt, tăng chất lượng đầu ra và dễ dàng bảo trì, bắt lỗi (debug).

2. Case nào không nên dùng multi-agent? Vì sao?
- **Trả lời:** Không nên dùng Multi-Agent cho các tác vụ đơn giản, có câu trả lời trực tiếp (ví dụ: dịch thuật, tóm tắt văn bản ngắn, tính toán cơ bản). Việc áp dụng Multi-Agent vào đây sẽ làm tăng độ trễ (latency), tốn kém chi phí (token cost) và làm phức tạp hóa hệ thống không cần thiết.
