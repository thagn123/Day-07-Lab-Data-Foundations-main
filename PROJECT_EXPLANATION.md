# 📘 Tài liệu Giải thích Kỹ thuật Hệ thống RAG (Law Chatbot)

Tài liệu này cung cấp cái nhìn chi tiết về cấu trúc, luồng xử lý dữ liệu và logic nghiệp vụ của dự án **Day 07 Lab: Data Foundations**.

---

## 1. Kiến thức nền tảng: RAG là gì?

**RAG (Retrieval-Augmented Generation)** là quy trình tối ưu hóa đầu ra của một mô hình ngôn ngữ lớn (LLM), bằng cách tham chiếu đến một kho kiến thức tin cậy nằm ngoài dữ liệu đào tạo của nó trước khi tạo ra câu trả lời.

Hệ thống của chúng ta hoạt động theo 3 giai đoạn chính:
1.  **Ingestion:** Nạp và xử lý dữ liệu thô.
2.  **Retrieval:** Tìm kiếm thông tin liên quan từ câu hỏi.
3.  **Generation:** Kết hợp thông tin tìm được và gửi cho AI để trả lời.

---

## 2. Phân tích chi tiết các thành phần (Source Code)

### 📂 `src/chunking.py` - Quản lý chia nhỏ văn bản
Văn bản luật thường rất dài. Để AI không bị "quá tải" và giúp việc tìm kiếm chính xác hơn, chúng ta cần chia nhỏ chúng.
*   **`FixedSizeChunker`**: Chia theo số ký tự. Ưu điểm là nhanh, nhưng nhược điểm là có thể cắt ngang một từ hoặc một câu, làm mất nghĩa.
*   **`SentenceChunker`**: Sử dụng Regular Expression (`(?<=[.!?])\s+`) để nhận diện kết thúc của một câu. Nó gom các câu lại thành một nhóm cho đến khi đủ số lượng yêu cầu.
*   **`RecursiveChunker`**: Đây là phương pháp chuyên nghiệp nhất. Nó cố gắng cắt theo các dấu hiệu cấu trúc (đoạn văn `\n\n` -> dòng `\n` -> câu `. ` -> từ ` `). Nếu đoạn văn bản vẫn quá lớn, nó sẽ đệ quy xuống cấp độ nhỏ hơn để chia.

### 📂 `src/embeddings.py` - Chuyển đổi ngôn ngữ thành Vector
*   **Vector là gì?** Là một danh sách các số thực (ví dụ: `[0.1, -0.5, 0.8, ...]`).
*   **Embedding**: Một mô hình toán học biến một đoạn văn bản thành một Vector sao cho: **Các đoạn văn có nghĩa giống nhau sẽ có các Vector nằm gần nhau trong không gian**.
*   **MockEmbedder**: Trong bài lab này, chúng ta dùng bản giả lập. Nó tạo ra các vector dựa trên mã băm (hash) của văn bản để mô phỏng quy trình mà không cần tốn tiền gọi API OpenAI.

### 📂 `src/store.py` - Cơ sở dữ liệu Vector (Vector Database)
Đây là nơi lưu trữ "trí nhớ" của hệ thống.
*   **Lưu trữ**: Nó lưu một danh sách các Dictionary, mỗi bản ghi gồm: `{content, embedding, metadata}`.
*   **Tìm kiếm (Similarity Search)**: Sử dụng hàm **Cosine Similarity**. Nó tính góc giữa vector câu hỏi và hiệu suất của tất cả các vector trong kho. 
    *   Góc nhỏ (điểm cao) = Nội dung tương đồng.
*   **Pre-filtering**: Một tính năng nâng cao giúp lọc dữ liệu theo metadata (ví dụ: chỉ tìm trong "Luật Hình sự") trước khi tính toán tương đồng, giúp hệ thống chạy nhanh hơn.

### 📂 `src/agent.py` - Logic RAG Agent
Đây là "người điều phối" (Orchestrator).
*   **Hàm `answer()`**:
    1.  Nhận câu hỏi từ người dùng.
    2.  Gọi `store.search()` để lấy ra `top_k` đoạn văn bản liên quan nhất.
    3.  Tạo ra một **Context block** (khối ngữ cảnh).
    4.  Xây dựng **System Prompt**: *"Bạn là trợ lý pháp luật. Hãy dùng Context dưới đây để trả lời câu hỏi"*.
    5.  Gửi tất cả sang LLM (OpenAI) để nhận câu trả lời cuối cùng.

---

## 3. Luồng dữ liệu khi chạy `main.py`

Hãy theo dõi điều gì xảy ra khi bạn gõ một câu hỏi:

1.  **Khởi tạo**: `main.py` load các file từ thư mục `data/`.
2.  **Mã hóa**: Từng file được chia nhỏ (chunking) và đẩy vào `EmbeddingStore`. Tại đây, mỗi đoạn được gắn một "tọa độ" (embedding vector).
3.  **Hỏi**: Bạn nhập: *"Người bị buộc tội có quyền gì?"*
4.  **Truy xuất**: 
    *   Hệ thống biến câu hỏi của bạn thành vector `V_query`.
    *   Nó so sánh `V_query` với hàng trăm vector trong kho.
    *   Nó thấy các vector của Điều 16, Điều 17 (Bộ luật Tố tụng HS) có điểm cao nhất.
5.  **Tổng hợp**: Nó bốc nội dung Điều 16, 17 và dán vào câu lệnh.
6.  **Kết quả**: AI đọc Điều 16, 17 và trả lời: *"Dựa trên Bộ luật tố tụng, người bị buộc tội có quyền bào chữa, quyền im lặng..."*

---

## 4. Các điểm cần lưu ý để mở rộng

*   **API Keys**: Trong thực tế, bạn sẽ thay `mock` bằng `OpenAI` trong file `.env` để có độ chính xác cao nhất.
*   **Chất lượng dữ liệu**: "Rác vào thì rác ra" (Garbage in, Garbage out). Nếu file PDF/Word của bạn bị lỗi font hoặc thiếu trang, RAG sẽ trả lời sai.
*   **Kích thước Chunk**: 
    *   Quá nhỏ: Thiếu ngữ cảnh xung quanh.
    *   Quá lớn: AI bị nhiễu thông tin không liên quan.

---
*Tài liệu này được biên soạn bởi Antigravity AI Assistant.*
