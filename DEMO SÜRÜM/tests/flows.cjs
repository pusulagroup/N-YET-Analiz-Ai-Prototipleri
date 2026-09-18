const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8').replace(/\r\n/g,'\n');
const a=html.indexOf('async function turnJSONV6'),b=html.indexOf('\nfunction responderIdForV1442',a),x=html.lastIndexOf('sendChat=async function(){'),y=html.indexOf('\n};',x)+4;
const code=html.slice(a,b)+html.slice(x,y);
const ok=d=>({ok:true,status:200,json:async()=>d});
async function scenario(kind,failScore=false,failReply=false,replyFirst=false){
 let input={value:'test'},p={comments:[],text:'post',id:1},events=[],waiting={},calls=[];
 let c={console,document:{getElementById:()=>input,querySelector:()=>input},findPost:()=>p,pendingCommentTurnsVFix:new Set(),pendingChatTurnsVFix:new Set(),isYouthMode:()=>false,threadHeat:()=>10,toast:()=>{},commentContextV14:()=>'',contextForReply:()=>'',responderIdForV1442:()=> 'sila',render:()=>{},runCommentShadowV14:()=>{},applyHeatEvent:(p,d)=>({before:10,after:10+d,delta:d}),heatDeltaFromAnalysis:()=>5,applyPublicBehavior:()=>events.push('me'),activeChat:'sila',blockedUsers:new Set(),P:()=>({}),chatContextV14:()=>'',chats:{sila:[]},chatEngaged:{},renderRoom:()=>{},renderChats:()=>{},renderV10Panels:()=>{},updateYouthChatGuardV14:()=>{},runChatShadowV14:()=>{},updateChatHealth:(id,a,who)=>events.push(who),fetch:(url,opts)=>{calls.push(url);return new Promise((resolve,reject)=>waiting[url]={resolve,reject,body:JSON.parse(opts.body)})}};
 vm.createContext(c);vm.runInContext(code,c);
 let done=kind==='chat'?c.sendChat():c.reply(1),replyURL=kind==='chat'?'/api/chat':'/api/bot_comment';
 assert.equal(calls.length,2,'analysis and reply both start before either resolves');assert(waiting[replyURL].body.reply_only);
 const resolveReply=()=>failReply?waiting[replyURL].reject(Error('reply failure')):waiting[replyURL].resolve(ok({reply:'reply',reply_analysis:{}}));
 if(replyFirst)resolveReply();
 if(failScore)waiting['/api/analyze_behavior'].reject(Error('score failure'));else waiting['/api/analyze_behavior'].resolve(ok({analysis:{}}));
 for(let i=0;i<15;i++)await Promise.resolve();
 assert.equal(events.filter(x=>x==='me').length,failScore?0:1);
 if(!replyFirst)resolveReply();await done;
 assert.equal(events.filter(x=>x==='me').length,failScore?0:1);assert.equal(c.pendingChatTurnsVFix.size+c.pendingCommentTurnsVFix.size,0);
 if(kind==='chat'){assert.equal(events.filter(x=>x==='bot').length,failReply?0:1,'bot analysis applies even when user analysis fails');assert.equal(c.chats.sila.filter(x=>x.text==='reply').length,failReply?0:1);}else assert.equal(p.comments.length,failReply?1:2);
}
(async()=>{for(const kind of ['chat','comment'])for(const options of [[false,false,false],[false,false,true],[true,false,false],[false,true,false]])await scenario(kind,...options);
 let calls=0,c={fetch:async()=>++calls===1?{ok:false,status:503,json:async()=>({retryable:true})}:ok({reply:'done'})};vm.createContext(c);vm.runInContext(code.slice(0,code.indexOf('reply=async')),c);assert.equal((await c.turnJSONV6('/api/chat',{})).reply,'done');assert.equal(calls,2);
 console.log('9 V6 scenarios passed: simultaneous starts, either completion order, independent failures, exactly-once score, cleanup and bounded transient retry.');
})().catch(e=>{console.error(e);process.exit(1)});
