import fs from 'node:fs';
import path from 'node:path';
import validator from 'gltf-validator';
const root=process.argv[2];if(!root)throw new Error('Usage: node scripts/validate_replay_glbs.js DATA_DIRECTORY');
const source=JSON.parse(fs.readFileSync(path.join(root,'PROVENANCE.json'),'utf8'));
const rows=[];
for(const item of source.selected){
 const file=path.join(root,'provided-glbs',item.id+'.glb');
 const bytes=fs.readFileSync(file);
 const result=await validator.validateBytes(new Uint8Array(bytes),{uri:item.id+'.glb',maxIssues:200});
 rows.push({id:item.id,split:item.split,errors:result.issues.numErrors,warnings:result.issues.numWarnings,bytes:bytes.length,animations:item.provided_glb_animations});
}
const result={scope:'Independent Khronos validation of supplied publisher exports; not source re-execution or visual/motion-quality certification',examples:rows.length,error_examples:rows.filter(x=>x.errors>0).length,total_errors:rows.reduce((a,x)=>a+x.errors,0),warning_examples:rows.filter(x=>x.warnings>0).length,rows};
fs.writeFileSync(path.join(root,'GLB_VALIDATION.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,rows:undefined}));
if(result.total_errors)process.exitCode=1;
