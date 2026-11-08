"""Editable prospective meeting drafts requested by the project owner.

These files are prepared for the user's review and editing; they do not update
the canonical meeting history or publish completed-meeting records.
"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import hashlib
import json
from lxml import etree as E

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / '2026-10-16/supervisor-meeting-2-original.docx'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'

FORMS = {
    4: {
        'date': '13.11.2026 / 15 minutes',
        'completed': (
            'We reviewed the midterm report and project proposal, including the functional and '
            'non-functional requirements, system architecture, data model and selected technologies. '
            'The group repository was made public and the report archive was organized. The current '
            'prototype supports text ingestion, isnad segmentation, extraction, validation, human '
            'review and chain exploration. We reviewed the remaining implementation and evaluation '
            'tasks against the semester plan.'
        ),
        'issues': (
            'Independent annotation and expert assessment had not started. Expert availability, '
            'annotation guidelines and adjudication procedures required coordination. We also '
            'identified the need to verify review-duration capture, provenance enforcement, decision '
            'persistence and consistency between PostgreSQL and Neo4j.'
        ),
        'decisions': (
            'We agreed to prioritize expert coordination and annotation preparation. Yahya Efe '
            'Kurucay will review validation and decision records; Deniz Buyuksahin will refine the '
            'review interface and annotation guideline; Alperen Ulukaya will test segmentation and '
            'chain exploration. All members will review integration issues and document evidence '
            'for the remaining acceptance criteria.\n\n'
            'Owner: All group members. Due: Before Meeting 5 (27.11.2026).'
        ),
        'plan': (
            'Confirm the expert review process, conduct an annotation calibration round and begin '
            'independent labelling toward the 50-hadith reference set. Review the existing engine '
            'as a group and record defects. Prepare the review protocol and a reproducible input '
            'batch for the 100-hadith end-to-end acceptance run.'
        ),
        'next': '27.11.2026',
    },
    5: {
        'date': '27.11.2026 / 15 minutes',
        'completed': (
            "We reviewed the prototype's ingestion-to-graph workflow and the status of the component "
            'review, annotation preparation and integration tasks assigned in the previous meeting. '
            'The discussion covered candidate validation, the review queue, decision records, graph '
            'commit and chain exploration. We compared the current implementation with the S1-S5 '
            'acceptance criteria and identified the evidence still needed for the final '
            'demonstration and report.'
        ),
        'issues': (
            'The final evaluation depends on independently labelled hadiths and expert adjudication. '
            'Real-database integration, duplicate-free commits, evidence traceability and clean-machine '
            'setup still required explicit acceptance checks. Human-review outcomes and expert '
            'agreement must be reported after the corresponding data have been collected.'
        ),
        'decisions': (
            'We agreed to prioritize the reproducible end-to-end scenario and resolve blocking '
            'defects before the final demonstration. Yahya Efe Kurucay will prepare the scoring and '
            'provenance audit; Deniz Buyuksahin will organize review records and finish interface '
            'corrections; Alperen Ulukaya will verify persistent integration and chain evidence. All '
            'members will contribute to the README, final report and demo.\n\n'
            'Owner: All group members. Target: 04.12.2026.'
        ),
        'plan': (
            'Complete the remaining acceptance checks, run the planned 100-hadith scenario and '
            'evaluate against the independently labelled reference when available. Report unresolved '
            'and contested items explicitly. Reproduce the measured results, verify setup from a '
            'clean environment and prepare the final presentation, report and demonstration '
            'for Weeks 14-15.'
        ),
        'next': 'To be confirmed during final preparation in Weeks 14-15.',
    },
}


def fill_cell(tc, text):
    old = tc.find('w:p', NS)
    p = deepcopy(old)
    first = old.find('w:r', NS)
    rpr = deepcopy(first.find('w:rPr', NS)) if first is not None and first.find('w:rPr', NS) is not None else None
    for child in list(p):
        if child.tag != W + 'pPr':
            p.remove(child)
    run = E.SubElement(p, W + 'r')
    if rpr is not None:
        run.append(rpr)
    for i, line in enumerate(text.split('\n')):
        if i:
            E.SubElement(run, W + 'br')
        node = E.SubElement(run, W + 't')
        node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        node.text = line
    for child in list(tc):
        if child.tag != W + 'tcPr':
            tc.remove(child)
    tc.append(p)


def build():
    original_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert original_hash == '0319fbb3a349765b8f0f325c0b95188aa2c18b40e0fcd7553e23f32e4a5664f6'
    audit = []
    for number, data in FORMS.items():
        with ZipFile(SOURCE) as z:
            root = E.fromstring(z.read('word/document.xml'))
            original_geometry = E.tostring(root.find('.//w:sectPr', NS))
            rows = root.findall('.//w:tbl/w:tr', NS)
            cells = lambda i: rows[i].findall('w:tc', NS)
            fill_cell(cells(2)[3], str(number))
            fill_cell(cells(3)[1], data['date'])
            fill_cell(cells(3)[3], 'All group members and the project supervisor')
            for row, key in [(4, 'completed'), (5, 'issues'), (6, 'decisions'), (7, 'plan'), (8, 'next')]:
                text = data[key].replace('Kurucay', 'Kuruçay').replace('Buyuksahin', 'Büyükşahin')
                fill_cell(cells(row)[1], text)
            # Preserve the unmarked assessment and empty signature from the source.
            assert not ''.join(cells(10)[1].itertext()).strip()
            assert E.tostring(root.find('.//w:sectPr', NS)) == original_geometry
            path = HERE / f'10_CSE491_Meeting{number}.docx'
            with ZipFile(path, 'w') as out:
                for info in z.infolist():
                    content = E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True) if info.filename == 'word/document.xml' else z.read(info.filename)
                    out.writestr(deepcopy(info), content)
            with ZipFile(path) as out:
                preserved = [name for name in z.namelist() if name != 'word/document.xml']
                assert all(z.read(name) == out.read(name) for name in preserved)
            audit.append({'meeting': number, 'path': str(path), 'date': data['date'], 'preserved_parts': len(preserved), 'source_sha256': original_hash})
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == original_hash
    Path('/tmp/giraffe-meeting-simulations/fidelity-audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    build()
