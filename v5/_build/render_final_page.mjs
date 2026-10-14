import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'outputs/智能体产业研发_V5_04.pptx')));
const b=await p.export({slide:p.slides.items[28],format:'png',scale:1});
await fs.writeFile(path.join(root,'qa/final_backup29.png'),new Uint8Array(await b.arrayBuffer()));
console.log('BACKUP29_RENDERED');
