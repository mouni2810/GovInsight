# GovInsight - Guardrails, Limitations & Future Enhancements

## Table of Contents
- [Guardrails](#guardrails)
- [Current Limitations](#current-limitations)
- [Future Enhancements](#future-enhancements)

---

## Guardrails

### Data Integrity Guardrails

| Guardrail | Description |
|-----------|-------------|
| **Source-Only Responses** | The system ONLY uses data from indexed PDF documents. No external knowledge or web searches. |
| **Mandatory Citations** | Every numerical figure in responses must include a citation with document name and page number. |
| **No Fabrication Policy** | If data is not found in context, the system explicitly states "Data not found in provided documents." |
| **Manual Metadata Only** | All document metadata is manually configured in `metadata_config.py` - no automatic extraction that could introduce errors. |

### Query Processing Guardrails

| Guardrail | Description |
|-----------|-------------|
| **Input Validation** | Queries are validated for minimum length and sanitized before processing. |
| **Token Limits** | Chunk sizes are controlled (300 tokens) to ensure context fits within LLM limits. |
| **Retrieval Limits** | Maximum of 25 chunks retrieved, reranked to top 7 to prevent context overflow. |
| **Rate Limiting Ready** | API structure supports rate limiting implementation for production deployment. |

### Response Quality Guardrails

| Guardrail | Description |
|-----------|-------------|
| **Structured Output** | System prompt enforces table format for numerical data. |
| **Confidence Signals** | Reranking scores help prioritize high-quality, data-dense chunks. |
| **Traceability** | Every response includes source documents, page numbers, and metadata. |
| **No Policy Recommendations** | System provides data only - does not make autonomous policy suggestions. |

---

## Current Limitations

### Data Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **Static Dataset** | No real-time budget updates | Manual re-indexing required for new documents |
| **Federal Focus Only** | State budgets not included | Architecture supports extension to state data |
| **Limited Document Types** | Primarily Demands for Grants, Expenditure Budgets | Can add more document types to `metadata_config.py` |
| **English Only** | Hindi/regional language PDFs not supported | Would require multilingual embedding models |

### Technical Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **No Chart/Graph Extraction** | Visual data in PDFs not captured | Manual data entry or OCR pipeline needed |
| **Table Parsing Imperfect** | Complex PDF tables may lose structure | Pre-processing or manual verification |
| **Single LLM Dependency** | Relies on Gemini 2.5 Flash availability | Can swap to other LLMs (OpenAI, Claude) |
| **No Streaming Responses** | Full response generated before display | Streaming can be implemented in FastAPI |

### Retrieval Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **Semantic Search Only** | Exact keyword matches may be missed | Query preprocessing expands abbreviations |
| **No Cross-Document Reasoning** | Cannot synthesize across 10+ documents at once | Increase top_k for broader context |
| **Chunk Boundary Issues** | Information may be split across chunks | 75-token overlap mitigates this |
| **No Query History** | Each query is independent | Session management can be added |

### Accuracy Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **OCR Errors in Source PDFs** | Original PDF quality affects extraction | Use high-quality official PDFs |
| **Metadata Dependency** | Wrong metadata leads to incorrect citations | Validate `metadata_config.py` carefully |
| **No Fact Verification** | System trusts extracted text | Manual verification for critical data |

---

## Future Enhancements

### Short-Term (1-3 Months)

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **OCR-Based Chart Extraction** | High | Extract numerical data from bar charts, pie charts, and graphs using EasyOCR/Tesseract |
| **Streaming Responses** | High | Implement SSE (Server-Sent Events) for real-time answer streaming |
| **Query History & Sessions** | Medium | Store user queries and enable follow-up questions |
| **Advanced Filters UI** | Medium | Add year, ministry, and scheme filters in the frontend |
| **Batch Query API** | Medium | Allow multiple queries in a single API call |

### Medium-Term (3-6 Months)

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **State Budget Support** | High | Extend system to include state-level budget documents |
| **Multi-Year Trend Analysis** | High | Automatic year-over-year comparison for schemes |
| **Hindi/Regional Language Support** | Medium | Multilingual embeddings for non-English PDFs |
| **Export to Excel/PDF** | Medium | Download query results in structured formats |
| **User Authentication** | Medium | Login system with query history and preferences |

### Long-Term (6-12 Months)

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **Real-Time Data Ingestion** | High | Automatic indexing when new budget PDFs are released |
| **Comparative Dashboard** | High | Visual dashboard comparing schemes, ministries, and years |
| **API Rate Limiting & Quotas** | Medium | Production-ready API with usage tracking |
| **Fine-Tuned Budget LLM** | Medium | Train a specialized model for Indian budget terminology |
| **Mobile Application** | Low | Native mobile app for on-the-go budget queries |

### Research & Experimental

| Enhancement | Description |
|-------------|-------------|
| **Knowledge Graph Integration** | Build a graph of ministries → schemes → allocations for better reasoning |
| **Anomaly Detection** | Flag unusual budget changes or discrepancies |
| **Predictive Analytics** | Forecast future allocations based on historical trends |
| **Voice Query Interface** | Speech-to-text for verbal budget queries |
| **Multi-Modal RAG** | Combine text, tables, and chart images in retrieval |

---

## Contributing

When extending the system, please:

1. **Document new PDFs** in `metadata_config.py` with complete metadata
2. **Test retrieval quality** after adding new documents
3. **Update this file** with any new limitations or enhancements
4. **Follow the existing code patterns** for consistency

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2025 | Initial release with core RAG pipeline |
