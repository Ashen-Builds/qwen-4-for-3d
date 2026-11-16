import fs from 'node:fs';
import validator from 'gltf-validator';

const file=process.argv[2];
if(!file)throw new Error('Usage: node scripts/validate_glb.js FILE');
const bytes=fs.readFileSync(file);
const report=await validator.validateBytes(new Uint8Array(bytes),{uri:file.split('/').pop(),maxIssues:2000});
const jsonLength=bytes.readUInt32LE(12);
const doc=JSON.parse(bytes.subarray(20,20+jsonLength).toString('utf8'));
const summary={bytes:bytes.length,errors:report.issues.numErrors,warnings:report.issues.numWarnings,
  meshes:doc.meshes?.length||0,nodes:doc.nodes?.length||0,materials:doc.materials?.length||0,
  animations:doc.animations?.map(a=>({name:a.name||'',channels:a.channels?.length||0}))||[],
  extensionsUsed:doc.extensionsUsed||[]};
fs.writeFileSync(file+'.validation.json',JSON.stringify({summary,report},null,2)+'\n');
console.log(JSON.stringify(summary));
if(report.issues.numErrors)process.exitCode=1;
