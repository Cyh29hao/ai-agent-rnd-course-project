import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
process.env.RUNTIME_NODE_MODULES='C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const SKILL='C:/Users/Cyh29hao/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const referencePath=path.join(ROOT,'outputs/智能体产业研发_V5_06.pptx');
const result=await finalizePresentation({
 workspaceDir:ROOT,candidatePath:path.join(ROOT,'_build/b_integration_07/ready.pptx'),
 finalPath:path.join(ROOT,'outputs/智能体产业研发_V5_07.pptx'),explicitTotalSlideCount:34,
 pythonExecutable:'C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry','--require-native-table-slide','20'],
 fontPolicy:{basis:'reference',families:['Microsoft YaHei'],referencePath,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(referencePath)).digest('hex')},
 verifyArtifactToolImport:true,requiredNativeChartOwnerSlides:[13],requiredEmbeddedWorkbookChartOwnerSlides:[13],
 requiredNativeTableOwnerSlides:[20],materializeLiteralChartWorkbooks:false,
 receiptPath:path.join(ROOT,'qa/b_integration_07/validation.json'),
});
console.log(JSON.stringify({path:result.finalPath,sha256:result.finalSha256}));
