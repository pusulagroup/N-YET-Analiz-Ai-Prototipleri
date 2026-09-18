const fs=require('fs'),vm=require('vm'),assert=require('assert');
const h=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
const cut=(a,b)=>h.slice(h.indexOf(a),h.indexOf(b,h.indexOf(a)));
let c={clamp:n=>Math.max(0,Math.min(100,n)),chats:{tolga:[],berk:[]},blockedUsers:new Set(),unreadCountsVSon:{},chatSelfConduct:{tolga:100,berk:100},chatOtherConduct:{tolga:100,berk:100},chatHealth:{tolga:100,berk:100},chatRiskEvents:{tolga:[],berk:[]},chatEngaged:{},chatUserDamage:{},chatBotDamage:{},safetyContinueAt:{},renderRoom:()=>{},renderChats:()=>{},renderV10Panels:()=>{},renderScores:()=>{},applyChatBehaviorToScoreV132:()=>{},maybeReportChat:()=>{}};
vm.createContext(c);vm.runInContext(cut('function chatTurnHealthTargetV10','function maybeReportChat')+cut('function seedHarshInboxV11','function seedInboxVSon'),c);
c.seedHarshInboxV11();
for(const id of ['tolga','berk']){assert.equal(c.chats[id].length,2);assert(c.chatHealth[id]<100);assert.equal(c.chats[id][0].healthEvent.old,100);assert.equal(c.chats[id][1].healthEvent.old,c.chats[id][0].healthEvent.next);assert.equal(c.unreadCountsVSon[id],2);}
let before=JSON.stringify(c.chats);c.seedHarshInboxV11();assert.equal(JSON.stringify(c.chats),before);
c.chats.berk=[];c.blockedUsers.add('berk');c.seedHarshInboxV11();assert.equal(c.chats.berk.length,0);
console.log('Harsh inbox: two messages each, real health chain, unread count, no duplicates, blocked contact respected.');
