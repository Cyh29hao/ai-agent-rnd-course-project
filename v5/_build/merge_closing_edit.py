"""Retain the original deck/media and replace only authored closing edits."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'outputs/智能体产业研发_V5_04.pptx'
draft=ROOT/'_build/deck_draft.pptx';dst=ROOT/'_build/deck_closing_edit.pptx'
slides=[3,5,6,20,21,22,23]
parts={f'ppt/slides/slide{n}.xml' for n in slides}
parts.update(f'ppt/notesSlides/notesSlide{n}.xml' for n in range(1,25))
with ZipFile(src) as original,ZipFile(draft) as authored,ZipFile(dst,'w',ZIP_DEFLATED) as merged:
    for item in original.infolist():
        body=authored.read(item.filename) if item.filename in parts else original.read(item.filename)
        merged.writestr(copy.copy(item),body)
    # Edited slides contain text, diagrams and one native table, no new links.
    for n in slides:
        xml=authored.read(f'ppt/slides/slide{n}.xml')
        assert b'r:embed=' not in xml and b'r:link=' not in xml,n
with ZipFile(src) as original,ZipFile(dst) as merged:
    assert original.read('ppt/slides/slide11.xml')==merged.read('ppt/slides/slide11.xml')
(ROOT/'qa/closing_merge.json').write_text(json.dumps({'editedSlideNumbers':slides,'notesUpdated':24,'embeddedMediaAndOtherPartsPreserved':True,'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
print('CLOSING_EDITS_MERGED',slides)
