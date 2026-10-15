"""Fill the CSE 491 Supervisor Meeting Form for the meeting of 16 October 2026.

Usage: uv run --no-project --python 3.12 --with python-docx python fill_form.py
Writes build/supervisor-meeting-form.docx. Decisions, duration, attendees and the next date are
left for the meeting itself; the action items are proposals to confirm there.
"""

from pathlib import Path

import docx

HERE = Path(__file__).resolve().parent
TEMPLATE = Path("/Users/efe/cse/CSE-491-Senior-Design-Project-I/resources/2026-2027-fall/CSE491_Supervisor_Meeting_Form.docx")

FIELDS = {
    "Project title": "A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and Schema Drift in LLMs: An Application on Hadith Isnad Chains",
    "Group members (name, no.)": "Yahya Efe Kuruçay - 20220808005\nDeniz Büyükşahin - 20240808701\nAlperen Ulukaya - 20220808006",
    "Project supervisor": "Res. Asst. Dr. Taha Yiğit Alkan",
    "Date / duration": "16.10.2026 /",
    "Work completed since the last meeting": (
        "Reviewed similar work on the hadith side and the 27 papers of the team's reading list on knowledge graph "
        "construction, validation and review, plus two systems one survey pointed to. Narrowed the project's "
        "difference to what we did not find there: a check that the extracted value occurs in the model's own "
        "quotation, the contribution of each deterministic check measured against an outside reference, and a "
        "comparison of that check with the model's confidence at the same review share. Finished the project "
        "proposal text, drafts of the thesis and of a paper, and a draft of the TÜBİTAK 2209-A form. Prepared the "
        "labelling guideline and handouts for the domain expert. Code, data and documents are in one private "
        "repository; references are in a shared Zotero group library."
    ),
    "Issues, risks and blockers discussed": (
        "No human labels and no human reviewer yet: all figures so far are measured against labels of an existing "
        "hadith platform, with one model. The domain expert has not reviewed the guideline yet. The licences of the "
        "Ifta and AR-Sanad labels are not confirmed in writing; they are used for measurement only and not "
        "redistributed. Narrator identity decisions exist only as a simulation, not in the engine."
    ),
    "Decisions and action items (with owner and due date)": (
        "Proposed, to be confirmed in the meeting:\n"
        "- Submit the project proposal on Teams (Yahya Efe Kuruçay, 18.10.2026).\n"
        "- Meet the domain expert and finish guideline v1 (all members, week 6).\n"
        "- Label 50 hadiths independently (Deniz Büyükşahin, Alperen Ulukaya, week 7).\n"
        "- Ablation table of the checks on the existing runs and the rule \"the Prophet is not a narrator\" "
        "(Yahya Efe Kuruçay, week 6).\n"
        "- Add the supervisor and the course assistant to the repository (Yahya Efe Kuruçay, before week 10)."
    ),
    "Plan until the next meeting": (
        "Architecture, data model and sketches of the three main screens (week 6). Guideline reviewed with the "
        "domain expert and labelling started. Ablation table on the existing runs. Next meeting in week 6 or 7."
    ),
}


def main():
    document = docx.Document(str(TEMPLATE))
    table = document.tables[0]
    for row in table.rows:
        label = row.cells[0].text.strip()
        if label in FIELDS:
            target = row.cells[1]
            target.text = FIELDS[label]
            for paragraph in target.paragraphs:
                for run in paragraph.runs:
                    run.font.size = docx.shared.Pt(9.5)
    out = HERE / "build" / "supervisor-meeting-form.docx"
    document.save(str(out))
    print(out)


if __name__ == "__main__":
    main()
