import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='C:/Users/Cyh29hao/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const v=process.env.DECK_REVISION||'01';
const candidate=process.env.DECK_CANDIDATE||'deck_normalized.pptx';
const r=await finalizePresentation({workspaceDir:ROOT,candidatePath:path.join(ROOT,'_build',candidate),finalPath:path.join(ROOT,'outputs',`智能体产业研发_V5_${v}.pptx`),explicitTotalSlideCount:34,pythonExecutable:'C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Microsoft YaHei']},verifyArtifactToolImport:true,requiredNativeChartOwnerSlides:[13],materializeLiteralChartWorkbooks:true,receiptPath:path.join(ROOT,'qa',`validation_${v}.json`)});
console.log(JSON.stringify({file:r.finalPath,sha256:r.finalSha256}));
