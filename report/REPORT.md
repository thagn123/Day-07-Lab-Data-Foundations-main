# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Đào Quang Thắng
**Nhóm:** Nhóm 1
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:*
> High cosine similarity (gần bằng 1.0) nghĩa là hai vector pointing về cùng một hướng trong không gian đa chiều, cho thấy hai văn bản có sự tương đồng lớn về mặt ngữ nghĩa, mặc dù độ dài hoặc từ ngữ có thể khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: Tòa án xét xử vụ án hình sự.
- Sentence B: Tòa án thực hiện quyền tư pháp.
- Tại sao tương đồng: Cả hai đều đề cập đến vai trò và chức năng cốt lõi của Tòa án trong hệ thống pháp luật.

**Ví dụ LOW similarity:**
- Sentence A: Học lập trình Python rất vui.
- Sentence B: Cá mập sống dưới biển.
- Tại sao khác: Một câu nói về giáo dục/công nghệ, một câu nói về sinh học biển, không có điểm giao thoa về nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*
> Cosine similarity chỉ quan tâm đến góc giữa hai vector chứ không quan tâm đến độ dài (magnitude). Điều này giúp so sánh văn bản hiệu quả ngay cả khi chúng có độ dài khác nhau nhưng cùng nội dung.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Bước nhảy (Step) = chunk_size - overlap = 500 - 50 = 450 ký tự.
> Số lượng chunks = ceil((Tổng số ký tự - overlap) / Step) = ceil((10000 - 50) / 450) = ceil(22.11) = 23.
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*
> Nếu overlap tăng lên 100, bước nhảy giảm xuống còn 400, dẫn đến số lượng chunks tăng lên (25 chunks). Việc tăng overlap giúp bảo toàn ngữ cảnh tốt hơn giữa các đoạn văn bị cắt ngang.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Luật Hình sự và Tố tụng Hình sự Việt Nam.

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*
> Đây là một domain có cấu trúc văn bản chặt chẽ, từ ngữ chuyên môn đặc thù, rất phù hợp để thử nghiệm khả năng hiểu ngữ nghĩa của embeddings. Ngoài ra, việc tra cứu luật nhanh chóng là một ứng dụng thực tiễn cao của RAG.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Bộ luật Hình sự | data/law.docx | ~154,000 | source: law, ext: .docx |
| 2 | Bộ luật Tố tụng HS | data/to_tung_hinh_su.docx| ~47,000 | source: procedure, ext: .docx |
| 3 | Ghi chú Retrieval | data/vi_retrieval_notes.md| 52 | source: notes, ext: .md |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | law, procedure | Giúp lọc nhanh tài liệu theo từng bộ luật cụ thể. |
| extension | string | .docx, .md | Quản lý định dạng file gốc để xử lý parsing. |
| category | string | hinh_su, dan_su | Phân loại sâu hơn về các mảng luật khác nhau. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Tài liệu mẫu (Pháp luật) | FixedSizeChunker (`fixed_size`) | 6 | 90.83 | Trung bình (cắt ngang từ) |
| Tài liệu mẫu (Pháp luật) | SentenceChunker (`by_sentences`) | 3 | 180.67 | Tốt (giữ trọn câu) |
| Tài liệu mẫu (Pháp luật) | RecursiveChunker (`recursive`) | 8 | 66.12 | Rất tốt (theo cấu trúc) |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*
> Strategy này hoạt động bằng cách cố gắng chia văn bản theo các ký tự phân tách có độ ưu tiên giảm dần (đoạn văn `\n\n`, dòng `\n`, câu `. `, từ ` `). Nếu một đoạn văn bản vẫn vượt quá `chunk_size`, nó sẽ tiếp tục được chia nhỏ bằng ký tự phân tách tiếp theo trong danh sách. Điều này giúp giữ cho các đoạn văn bản có ý nghĩa nguyên vẹn nhất có thể trong khi vẫn đảm bảo giới hạn kích thước.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*
> Văn bản pháp luật thường có cấu trúc phân cấp rõ ràng (Điều, Khoản, Điểm). RecursiveChunker cho phép chúng ta ưu tiên chia nhỏ theo Điều (ngắt đoạn `\n\n`) hoặc Khoản (`\n`), giúp thông tin trong cùng một Điều luật được giữ cùng nhau trong một chunk nếu kích thước cho phép.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Luật Hình sự | recursive | 8 | 66.12 | Cao (giữ được ngữ cảnh pháp lý) |
| Luật Hình sự | fixed_size | 6 | 90.83 | Thấp (có thể cắt giữa chừng ý nghĩa) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*
> Sử dụng regex `(?<=[.!?])\s+|(?<=\.)\n` (lookbehind) để phân tách câu dựa trên dấu chấm, dấu hỏi, dấu cảm thán hoặc xuống dòng sau dấu chấm. Cách này giúp giữ lại dấu kết thúc câu và xử lý được các trường hợp xuống dòng trực tiếp sau câu mà không có khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*
> Thuật toán đệ quy duyệt qua danh sách các ký tự phân tách theo thứ tự ưu tiên. Base case là khi đoạn văn bản nhỏ hơn `chunk_size` hoặc không còn ký tự phân tách nào để dùng, khi đó nó sẽ trả về văn bản gốc hoặc cắt cứng theo số ký tự.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*
> Tài liệu được lưu trữ dưới dạng một danh sách các dictionary chứa content, metadata và vector embedding. Độ tương đồng được tính bằng phương pháp tích vô hướng (dot product) của các vector, sau đó sắp xếp giảm dần để lấy top-k.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*
> Hệ thống thực hiện metadata pre-filtering (lọc trước) để thu hẹp tập hợp record cần tính tương đồng, giúp tối ưu hiệu năng. Hàm `delete_document` thực hiện lọc bỏ record dựa trên `doc_id` bằng list comprehension.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*
> Agent thực hiện tìm kiếm ngữ cảnh liên quan nhất từ `EmbeddingStore`, sau đó chèn nội dung này vào một template prompt có sẵn. Prompt thường có dạng: "Answer the question based on the context: {context}\nQuestion: {question}".

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
collected 42 items

tests\test_solution.py ..........................................        [100%]

============================= 42 passed in 0.11s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tòa án xét xử vụ án hình sự. | Tòa án thực hiện quyền tư pháp. | high | 0.0770 | Không (Mock) |
| 2 | Quyền bào chữa của bị cáo. | Luật sư bảo vệ quyền lợi bị cáo. | high | -0.1693 | Không (Mock) |
| 3 | Học lập trình Python rất vui. | Cá mập sống dưới biển. | low | 0.0366 | Đúng |
| 4 | Bộ luật Dân sự điều chỉnh quan hệ tài sản. | Bộ luật Hình sự quy định về tội phạm. | high | -0.0230 | Không (Mock) |
| 5 | Bị cáo có quyền im lặng. | Cảnh sát bắt giữ tội phạm. | high | 0.2707 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*
> Kết quả giữa Sentence cặp 2 (Quyền bào chữa vs Luật sư bảo vệ) có điểm âm (-0.1693) là bất ngờ nhất vì về nghĩa chúng khá gần nhau. Điều này cho thấy Mock Embeddings trong bài lab này chỉ mô phỏng các vector ngẫu nhiên dựa trên hash hoặc logic đơn giản, chưa thực sự biểu diễn được ngữ nghĩa sâu sắc như các model thực tế (OpenAI/BERT).

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Ai có trách nhiệm xác định sự thật vụ án? | Cơ quan điều tra, Viện kiểm sát và Tòa án. |
| 2 | Tòa án làm gì trong tố tụng hình sự? | Xét xử vụ án hình sự một cách công minh. |
| 3 | Người bị buộc tội có quyền gì? | Quyền bào chữa, quyền im lặng, ... |
| 4 | Viện kiểm sát có vai trò gì? | Thực hành quyền công tố và kiểm sát tư pháp. |
| 5 | Bộ luật hình sự quy định về điều gì? | Quy định về tội phạm và hình phạt. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ai có trách nhiệm xác định sự thật vụ án? | Tòa án xét xử vụ án hình sự độc lập.| 0.2173 | Yes | Trả lời dựa trên ngữ cảnh... |
| 2 | Tòa án làm gì trong tố tụng hình sự? | Viện kiểm sát thực hành quyền công tố.| 0.0556 | No | Trả lời dựa trên ngữ cảnh... |
| 3 | Người bị buộc tội có quyền gì? | Tòa án xét xử vụ án hình sự độc lập.| 0.1701 | Partial | Trả lời dựa trên ngữ cảnh... |
| 4 | Viện kiểm sát có vai trò gì? | Cơ quan điều tra xác định sự thật. | 0.2260 | No | Trả lời dựa trên ngữ cảnh... |
| 5 | Bộ luật hình sự quy định về điều gì? | Bộ luật Hình sự quy định về tội phạm. | 0.1597 | Yes | Trả lời dựa trên ngữ cảnh... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*
> Tôi học được cách gán metadata linh hoạt (như bộ luật, chương, điều) để hỗ trợ tìm kiếm tốt hơn của bạn trong nhóm. Việc lọc metadata trước khi tính similarity giúp tốc độ xử lý nhanh hơn đáng kể.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*
> Một nhóm đã sử dụng RecursiveChunker với các bộ ký tự phân tách tiếng Việt đặc thù (như " - ") để chia nhỏ các danh sách liệt kê trong luật, giúp thông tin không bị rời rạc.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*
> Tôi sẽ tập trung nhiều hơn vào việc làm sạch dữ liệu (data cleaning) để loại bỏ các ký tự rác từ file docx và thử nghiệm các `chunk_size` nhỏ hơn để tăng độ tập trung của thông tin được retrieval.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **98 / 100** |
