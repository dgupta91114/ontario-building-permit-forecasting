# QM640 final report

Upload **[QM640_Capstone_Final_Report_Debodip_Gupta.pdf](QM640_Capstone_Final_Report_Debodip_Gupta.pdf)** after completing the external similarity check described below. The editable source is the matching DOCX. The PDF is exactly **40 pages**, uses **Summer 2026 Term**, and is dated **September 15, 2026**, the assignment due date.

The report follows the supplied final-report section order and retains the prior study title, author, and mentor. It contains a 305-word abstract, 18 labeled tables (including two appendix tables), 6 figures, and 17 cited references. It is self-contained; prior reports and the presentation are not needed to understand it.

## Submission requirements

- Assignment opens September 11, 2026, 8:30 AM; due September 15, 2026, 2:29 PM, as displayed in the assignment.
- PDF only; maximum score 400.
- The user's group-chat clarification requires a 40-page final report. This overrides the supplied template's legacy sentence calling for a 15–20-page "interim report." Forty pages here means the complete PDF, including cover, bibliography, and appendices.
- The user explicitly confirmed Summer 2026 Term.
- The template supplies the report's structure. APA styling supplies 12-point Times New Roman, 24-point double leading, one-inch margins, page numbers beginning on the title page, numbered captions, hanging reference indents, italic publication titles, and linked reference URLs. Tables and figure notes use compact spacing for readability.
- The GitHub link appears immediately after the title page. Template prompts and placeholder instructions have been removed.

## Rubric coverage

| Criterion | Points | Report evidence |
|---|---:|---|
| Abstract and Introduction | 75 | Pages 2–5: problem, data, results, purpose, four RQs, contributions |
| Literature Review | 50 | Pages 6–9: focused review, critical synthesis, 12-source relevance matrix |
| Materials and Methods | 70 | Pages 10–18: filtering, EDA, features, chronology, metrics, inference, uncertainty |
| Research Hypothesis and Sample Size Calculations | 30 | Pages 12–14: H₀/Hₐ, α = .05, explicit calculations, actual evaluation sample and power limitations |
| Model Selection and Architecture Diagram | 75 | Pages 16–21: dated splits, searched/chosen settings, acceptance rule, labeled architecture, tools |
| Results and Implementation | 65 | Pages 22–33: training/CV/test metrics, all RQs, sensitivity, user workflow and historical scorecard |
| Limitations | 10 | Pages 34–35: data vintages, dependence, holdout reuse, interval limits, further improvements |
| Bibliography and overall APA compliance | 25 | Pages 36–38, citations throughout, numbered pages/captions, Appendix A–B on pages 39–40 |

## What was verified

`quality_audit.json` records 40 PDF pages, a 305-word abstract, intact caption locations and links, no blank pages or out-of-margin text, and no missing required headings. `evidence/evidence_audit.json` verifies frozen empirical hashes, recalculates all five holdout metrics from predictions, and confirms that saved estimators reproduce the archived predictions. All 11 existing tests passed on September 13, 2026. The one SciPy precision-loss warning concerns a pre-existing test with nearly identical synthetic errors.

All 40 pages were rendered and visually reviewed. The analysis configuration and original official results were retained. New diagnostics are isolated under `evidence/`: training metrics, verified sample-size calculations, and supplementary comparisons of 12 monthly pooled losses. The full national download and tuning pipeline were not rerun for this report.

The final report corrects material weaknesses in the older draft: it discloses the sample-size shortfalls, distinguishes point and interval fits, qualifies pooled inference, treats release-date availability as unverified, and reports that random forest had stronger earlier CV performance. The 53.8% result remains a historical MAE reduction, not a business-savings estimate.

## External similarity check still required

**No external plagiarism percentage has been obtained. The assignment's 7% requirement remains unverified.** Local checks found no repeated prose sentences of 12 or more words or quotations over 25 words; these checks are not a substitute for a plagiarism database. Three exact-phrase web spot-checks returned unrelated material, not a full-document similarity assessment. A free web checker was inspected, but its interactive full-document scan was not completed from this environment.

Use a freely accessible checker such as [DupliChecker](https://www.duplichecker.com/) and retain its actual result. Follow its current word/file limits and review matching passages and citations; do not infer a whole-document percentage by averaging unrelated batch scores. An institutional checker may use a different corpus and different exclusions.

`report_text.txt` contains the complete extracted PDF text, including tables. `qa/plagiarism_check_batches/` contains prose-only batches of at most 900 words to simplify manual copy/paste if needed; these do not cover table cells, so they cannot by themselves certify the whole PDF. Confirm the final PDF meets the assignment's threshold before uploading it. The assistant has not submitted the assignment.

## Rebuild

From the repository root, using the existing analytical environment:

```powershell
& .venv-final/Scripts/python.exe -X utf8 scripts/14_prepare_final_report_evidence.py
& .venv-final/Scripts/python.exe -X utf8 scripts/15_generate_final_report.py
```

The first command additionally needs the original local estimators under `outputs/models/`. The document generator can reuse the committed diagnostics if those binaries are unavailable. Export the DOCX with Word or LibreOffice, then run:

```powershell
& .venv-final/Scripts/python.exe -X utf8 scripts/16_validate_final_report.py
```

PDF inspection requires PyMuPDF; see `requirements-report.txt`. The validator never claims that a local originality check is an external similarity score. Page count can vary with a different renderer, so verify the actual PDF being uploaded.
