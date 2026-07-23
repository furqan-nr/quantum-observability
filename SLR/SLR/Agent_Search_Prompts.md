# Agent Search Prompts — one database per run

**How to use.** Run ONE prompt per agent session (they are self-contained). When the agent replies, paste its two tables back to me and I will ingest them into the review workbook, de-duplicate, run the second-reviewer screening, and build the PRISMA funnel.

**Priority if agent tries are scarce:** the five that failed before — ACM Digital Library, ScienceDirect, Scopus, Web of Science, Google Scholar — then optionally re-run IEEE Xplore, arXiv, and SpringerLink to get auditable candidate lists.

---
## 1. IEEE Xplore

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — IEEE Xplore — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH IEEE Xplore. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
("quantum" AND ("transpiler" OR "quantum compiler" OR "compilation" OR "pass manager" OR "qubit mapping")) AND ("testing" OR "test" OR "bug" OR "fault" OR "miscompilation" OR "oracle" OR "equivalence checking" OR "regression testing" OR "test selection" OR "test prioritisation")
Search fields: Document title, Abstract, and Index terms
Access note: Subscription database; export is usually available.
If IEEE Xplore is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 2. ACM Digital Library

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — ACM Digital Library — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH ACM Digital Library. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
("quantum" AND ("transpiler" OR "quantum compiler" OR "compilation" OR "pass manager" OR "qubit mapping")) AND ("testing" OR "test" OR "bug" OR "fault" OR "miscompilation" OR "oracle" OR "equivalence checking" OR "regression testing" OR "test selection" OR "test prioritisation")
Search fields: Title and Abstract (Advanced Search)
Access note: May be behind Cloudflare bot-protection; if you cannot reach it, report that and stop.
If ACM Digital Library is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 3. ScienceDirect (Elsevier)

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — ScienceDirect (Elsevier) — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH ScienceDirect (Elsevier). Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
quantum AND (transpiler OR "quantum compiler" OR compilation) AND (testing OR bug OR oracle OR "regression testing")
Search fields: Title, abstract, keywords (note: ScienceDirect allows at most 8 Boolean connectors, so this is a simplified string)
Access note: May require subscription; if blocked, report that and stop.
If ScienceDirect (Elsevier) is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 4. SpringerLink

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — SpringerLink — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH SpringerLink. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
("quantum" AND ("transpiler" OR "quantum compiler" OR "compilation" OR "pass manager" OR "qubit mapping")) AND ("testing" OR "test" OR "bug" OR "fault" OR "miscompilation" OR "oracle" OR "equivalence checking" OR "regression testing" OR "test selection" OR "test prioritisation")
Search fields: Full text
Access note: Full-text search returns many low-precision hits; screen strictly by title/abstract and return only the records that pass.
If SpringerLink is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 5. Scopus

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — Scopus — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH Scopus. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
TITLE-ABS-KEY(("quantum" AND ("transpiler" OR "quantum compiler" OR "compilation" OR "pass manager" OR "qubit mapping")) AND ("testing" OR "test" OR "bug" OR "fault" OR "miscompilation" OR "oracle" OR "equivalence checking" OR "regression testing" OR "test selection" OR "test prioritisation")) AND PUBYEAR > 2014
Search fields: TITLE-ABS-KEY
Access note: Subscription database; if you cannot reach it, report that and stop.
If Scopus is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 6. Web of Science

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — Web of Science — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH Web of Science. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
TS=(("quantum" AND ("transpiler" OR "quantum compiler" OR "compilation" OR "pass manager" OR "qubit mapping")) AND ("testing" OR "test" OR "bug" OR "fault" OR "miscompilation" OR "oracle" OR "equivalence checking" OR "regression testing" OR "test selection" OR "test prioritisation"))
Search fields: Topic (TS = title, abstract, keywords)
Access note: Subscription (Core Collection); if you cannot reach it, report that and stop.
If Web of Science is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 7. arXiv

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — arXiv — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH arXiv. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
quantum AND (transpiler OR "quantum compiler") AND (testing OR bug OR oracle)
Search fields: All fields (categories cs.SE and quant-ph)
Access note: Open access; use the arXiv API/listing. Preprints are eligible as citable preprints.
If arXiv is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
## 8. Google Scholar

```
You are helping me conduct a Systematic Literature Review (SLR) in software engineering. The review's topic is the testing and regression testing of quantum software compilers (transpilers), such as the Qiskit transpiler. In THIS session, search ONE database only — Google Scholar — and complete the entire task in this single reply. Do not stop early and do not omit any qualifying record.

The review must answer five research questions:
RQ1: What testing techniques have been proposed for quantum software compilers (transpilers)?
RQ2: What correctness oracles are used for compiled quantum circuits, and what are their limitations?
RQ3: How is regression testing, including test selection and prioritisation, addressed for quantum compilers?
RQ4: What benchmarks, datasets, and tools support the evaluation of quantum-compiler testing?
RQ5: What are the open challenges and research gaps in testing quantum compilers?

STEP 1 — SEARCH Google Scholar. Use this query, adapting ONLY to this database's required syntax while keeping the meaning, and restrict results to the years 2015–2026:
quantum compiler OR transpiler testing OR "regression testing" quantum
Search fields: All fields
Access note: Results are capped (~1000) and noisy; may be bot-protected. If blocked, report that and stop.
If Google Scholar is not accessible to you, say so explicitly, explain why, and stop (do not substitute another source).

STEP 2 — REPORT THE SEARCH. State: (a) the exact final query string you used; (b) the date and time of the search in the Asia/Karachi timezone; and (c) the TOTAL number of records the database returned.

STEP 3 — SCREEN BY TITLE AND ABSTRACT. Apply these criteria to every record:
INCLUDE a record if it is a peer-reviewed paper or a citable preprint published 2015–2026 that proposes or evaluates a testing technique, a correctness oracle, or a regression-testing / test-selection / prioritisation method for a quantum compiler or transpiler, and it describes an approach and some evaluation.
EXCLUDE a record if it is not in English; if it is not about quantum compiler/transpiler testing (for example, it is about quantum algorithms, quantum hardware or physics, or general quantum software with no compiler-testing angle); or if it is a short abstract, poster, or editorial with no described method.

STEP 4 — RETURN TWO TABLES, as plain markdown I can copy.
TABLE A — every record that PASSES title/abstract screening (do not truncate; if none pass, say "none"). Columns:
No | Title | Authors | Year | Venue | DOI or URL | Abstract summary (2–3 sentences) | Decision (Include or Maybe) | Reason
TABLE B — counts. Give: total records returned; number excluded at title/abstract; number passing to full-text (= number of rows in Table A); and the 3–5 most common exclusion reasons.

Do not summarise away any candidate; every record that passes screening must appear as its own row in Table A.
```

---
