const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
let nodes={},now=0,vis;
const ctx={document:{hidden:false,getElementById:id=>nodes[id]??(nodes[id]={style:{}}),addEventListener:(n,f)=>vis=f},performance:{now:()=>now},Number,Math};vm.createContext(ctx);
const a=html.indexOf('let lessonWatchV12=null;'),b=html.indexOf('let lessonKey=',a);vm.runInContext(html.slice(a,b),ctx);
function video(){return {currentTime:0,duration:10,paused:false,seeking:false,playbackRate:1,pause(){this.paused=true;this.onpause?.()}}}
let v=video();nodes.lessonVideo=v;ctx.installLessonWatchV12(v);v.onplay();
// Jumping to end and firing ended must not unlock the quiz.
v.currentTime=10;v.onseeking();assert.equal(v.currentTime,0);v.onended();assert.notEqual(nodes.lessonQuiz?.style.display,'block');
v.playbackRate=4;v.onratechange();assert.equal(v.playbackRate,1);
for(let t=.25;t<=5;t+=.25){now=t*1000;v.currentTime=t;v.ontimeupdate()}
ctx.document.hidden=true;vis();assert(v.paused);ctx.document.hidden=false;
v.paused=false;now+=10000;v.onplay();
for(let t=5.25;t<=10;t+=.25){now+=250;v.currentTime=t;v.ontimeupdate()}
v.paused=true;v.onpause();v.onended();assert.equal(nodes.lessonQuiz.style.display,'block');
ctx.clearLessonWatchV12(v);assert.equal(v.onended,null);
// Active chat health includes hard bots but excludes untouched and blocked contacts.
const x=html.indexOf('function activeChatIdsV134'),y=html.indexOf('function ownChatConductAverageV134',x);
const health={chatHealth:{tolga:78,berk:80,normal:100,blocked:10},chatEngaged:{},blockedUsers:new Set(['blocked']),Math,Number};vm.createContext(health);vm.runInContext(html.slice(x,y),health);assert.equal(health.generalChatScoreV10(),79);
// Early completion does not inspect answers or award points.
let early={lessonWatchV12:{complete:false},toast:()=>early.warned=true};vm.createContext(early);
const q=html.indexOf('function completeLessonQuiz()'),end=html.indexOf('let pendingPostAnalysis',q);vm.runInContext(html.slice(q,end),early);early.completeLessonQuiz();assert(early.warned);
// Parse every executable inline script independently.
let scripts=0;for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){if(match[1].includes('application/ld+json'))continue;new vm.Script(match[2]);scripts++}
console.log('PASS: seek-to-end rejection, speed reset, hidden-tab pause, full playback unlock, cleanup, active-health mean, early-quiz denial; '+scripts+' inline scripts parsed.');
// Duplicate post ids appear on feed/profile: preserve drafts independently and restore focus last.
function input(screen,value){return {id:'reply-42',value,selectionStart:2,selectionEnd:4,closest:()=>({id:screen}),focus(){this.focused=true},setSelectionRange(a,b){this.selectionStart=a;this.selectionEnd=b}}}
let inputs=[input('feed','feed draft'),input('profile','profile draft')];
let draftCtx={document:{activeElement:inputs[1],querySelectorAll:()=>inputs,getElementById:id=>({querySelector:()=>inputs[id==='feed'?0:1]})},render(){inputs=[input('feed',''),input('profile','')]}};
vm.createContext(draftCtx);vm.runInContext(html.slice(html.indexOf('const renderBeforeV12='),html.indexOf('function seedTestCommentsV5()')),draftCtx);draftCtx.render();assert.equal(inputs[0].value,'feed draft');assert.equal(inputs[1].value,'profile draft');assert(inputs[1].focused);assert.equal(inputs[1].selectionStart,2);
// New own posts remain addressable even outside the current feed.
let findCtx={feed:[],myPosts:[{id:42}],publicPostRegistryV5:new Map()};vm.createContext(findCtx);vm.runInContext(html.match(/function findPost\(id\)\{[^\n]+/)[0],findCtx);assert.equal(findCtx.findPost(42).id,42);
// Two appropriate behaviors validate +3; expired temporary bonus disappears.
let learn={tempBonuses:{'Saygı':{amount:3,validationCount:0,expiresAt:Date.now()+1000}},verifiedBonuses:{},interventionStats:{},toast(){},saveBonuses(){},saveV9Learning(){}};
vm.createContext(learn);vm.runInContext(html.match(/function pruneBonuses\(\)\{[^\n]+/)[0],learn);vm.runInContext(html.slice(html.indexOf('function maybeValidateLearning'),html.indexOf('function intentEntropy')),learn);learn.maybeValidateLearning({is_respectful:true},{respect:95});assert.equal(learn.tempBonuses['Saygı'].validationCount,1);learn.maybeValidateLearning({is_respectful:true},{respect:95});assert.equal(learn.verifiedBonuses['Saygı'],3);assert(!learn.tempBonuses['Saygı']);
learn.tempBonuses['Yapıcılık']={amount:3,expiresAt:Date.now()-1};vm.runInContext(html.match(/function pruneBonuses\(\)\{[^\n]+/)[0],learn);learn.pruneBonuses();assert(!learn.tempBonuses['Yapıcılık']);
console.log('PASS: separate feed/profile drafts, caret retention, new own-post lookup, two-behavior bonus verification, expired-bonus removal.');
