/* Run in Codex functions.exec, not Node or a browser. Set load('driveArchiveConfig')
   to {cwd: CHAT_WORKSPACE, execute: false|true, concurrency: 4}. Never run over
   another active transfer: inspect the task handoff/receipt first. Credentials
   remain in the connector. Destination IDs are read only from private receipts. */
const cfg=load('driveArchiveConfig');
if(!cfg?.cwd)throw new Error('Set driveArchiveConfig.cwd to the task workspace');
const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
const raw=await tools.exec_command({cmd:"python3 -c 'import json,pathlib;p=pathlib.Path(\"work/sprint-prep\");print(json.dumps({\"packages\":json.loads((p/\"packages/PACKAGE_MANIFEST.json\").read_text()),\"receipt\":json.loads((p/\"drive-transfer-receipt.json\").read_text())}))'",workdir:cfg.cwd,max_output_tokens:24000});
const data=JSON.parse(raw.output),{folders,modelFolders}=data.receipt;
const remote={};
for(const id of [...Object.values(folders),...modelFolders]){
 const r=await tools.mcp__codex_apps__google_drive_list_folder({url:'https://drive.google.com/drive/folders/'+id,top_k:100});
 if(r.isError||!Array.isArray(r.structuredContent?.files))throw new Error('Destination inventory failed');
 remote[id]=r.structuredContent.files;
}
const queue=[],existing=[];
for(const name of ['ccore-glb-dataset','pixel-atlas-reference','ccore-scenes-dataset','3dcodeverse-research-only','ccore-original-checkpoint']){
 const p=data.packages.find(x=>x.package===name);
 for(let i=0;i<p.parts.length;i++){
  const part=p.parts[i];if(part.bytes>96*1024*1024)throw new Error('Part exceeds approved transfer size');
  const parent=name==='ccore-original-checkpoint'?modelFolders[Math.floor(i/50)]:folders[name];
  const same=remote[parent].filter(x=>x.title===part.file);
  if(same.length>1||same.length===1&&Number(same[0].size)!==part.bytes)throw new Error('Duplicate or mismatched part: '+part.file);
  const item={package:name,...part,parent};
  if(same.length)existing.push({...item,id:same[0].id,status:'preexisting-size-verified'});else queue.push(item);
 }
}
text({missing:queue.length,existing:existing.length,execute:cfg.execute===true});
if(cfg.execute!==true)exit();
const receipt={schema:2,status:'uploading',folders,modelFolders,files:existing,failures:[],started:new Date().toISOString()};let cursor=0,completed=0;
async function save(){const body=JSON.stringify(receipt,null,2);await tools.exec_command({cmd:'python3 -c '+quote("from pathlib import Path;Path('work/sprint-prep/drive-transfer-final.json').write_text("+JSON.stringify(body)+"+'\\n')"),workdir:cfg.cwd,max_output_tokens:100});}
async function worker(){while(cursor<queue.length){
 const item=queue[cursor++];let okay=false;
 for(let attempt=0;attempt<2&&!okay;attempt++){
  try{
   const r=await tools.mcp__codex_apps__google_drive_upload_file({file_uri:cfg.cwd+'/work/sprint-prep/packages/'+item.package+'/'+item.file,file_name:item.file,parent_folder_id:item.parent,mime_type:'application/octet-stream'});
   if(!r.isError&&r.structuredContent?.success){receipt.files.push({...item,id:r.structuredContent.id,status:'uploaded'});okay=true;}
   else{
    const check=await tools.mcp__codex_apps__google_drive_list_folder({url:'https://drive.google.com/drive/folders/'+item.parent,top_k:100});
    const found=check.structuredContent?.files?.filter(f=>f.title===item.file&&Number(f.size)===item.bytes)||[];
    if(found.length===1){receipt.files.push({...item,id:found[0].id,status:'verified-after-ambiguous-result'});okay=true;}
    else if(attempt===1)receipt.failures.push({file:item.file,error:'Upload and destination verification failed'});
   }
  }catch(e){if(attempt===1)receipt.failures.push({file:item.file,error:String(e)});}
 }
 const n=++completed;if(n%5===0){await save();notify({completed:n,total:queue.length,failures:receipt.failures.length});}
}}
await save();await Promise.allSettled(Array.from({length:Math.max(1,Math.min(4,cfg.concurrency||4))},worker));
receipt.status=receipt.failures.length?'needs-retry':'uploaded-pending-final-inventory';receipt.finished=new Date().toISOString();await save();text({status:receipt.status,files:receipt.files.length,failures:receipt.failures.length});
