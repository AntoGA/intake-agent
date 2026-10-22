import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const ids=['demo-form','next','stage','result-title','result-body','events','request','failure','source','reset'];
const nodes=Object.fromEntries(ids.map(id=>[id,{textContent:'',hidden:false,disabled:false,checked:false,value:'Пример',selectedOptions:[{text:'Форма сайта'}],handlers:{},children:[],addEventListener(e,f){this.handlers[e]=f},append(x){this.children.push(x)},replaceChildren(){this.children=[]},focus(){}}]));
nodes['demo-form'].elements=[nodes.source,nodes.request,nodes.failure];
const context={document:{querySelector:s=>nodes[s.slice(1)],createElement:()=>({textContent:''})}};
vm.runInNewContext(fs.readFileSync(new URL('../public/demo.js',import.meta.url),'utf8'),context);
for(const source of ['Форма сайта','Почта','Telegram']){
 nodes.reset.handlers.click();nodes.source.selectedOptions[0].text=source;
 nodes.failure.checked=true;nodes['demo-form'].handlers.submit({preventDefault(){}});
 assert.equal(nodes.stage.textContent,'Принято: '+source);
 nodes.next.handlers.click();assert.equal(nodes.stage.textContent,'Сбой обработки');
 nodes.next.handlers.click();assert.equal(nodes.stage.textContent,'Черновик готов');
 nodes.next.handlers.click();assert.equal(nodes.stage.textContent,'Согласовано');assert.equal(nodes.next.hidden,true);
 assert.equal(nodes.events.children.length,4);
}
console.log('Демо: три источника, сбой, повтор, согласование и сброс — OK');
