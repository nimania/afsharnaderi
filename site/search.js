(()=>{
const input=document.getElementById('full-search');
const status=document.getElementById('full-search-count');
const results=document.getElementById('full-results');
if(!input||!status||!results)return;
const norm=s=>s.normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u064b-\u065f]/g,'').toLowerCase();
let records=[];
fetch('./search-index.json').then(r=>{if(!r.ok)throw new Error('index unavailable');return r.json()}).then(data=>{records=data;status.textContent='نمایهٔ متنی آماده است؛ عبارت مورد نظر را بنویسید.';if(input.value)show()}).catch(()=>{status.textContent='نمایهٔ متنی در دسترس نیست.'});
const show=()=>{
 const q=norm(input.value.trim());
 results.replaceChildren();
 if(q.length<2){status.textContent='حداقل دو نویسه برای جست‌وجو وارد کنید.';return}
 const found=records.map(x=>({...x,hay:norm(x.content)})).filter(x=>norm(x.title+' '+x.content).includes(q)).slice(0,30);
 status.textContent=found.length+' نتیجه از '+records.length+' پروندهٔ متنی';
 for(const x of found){
  const box=document.createElement('article');box.className='resource';
  const h=document.createElement('h2');h.textContent=x.title;
  const p=document.createElement('p');
  const pos=x.hay.indexOf(q);const at=Math.max(0,pos-85);
  p.textContent=(at?'…':'')+x.content.slice(at,Math.min(x.content.length,at+260))+'…';
  const a=document.createElement('a');a.href=x.path;a.textContent='مشاهدهٔ متن کامل ←';
  box.append(h,p,a);results.append(box);
 }
};
input.addEventListener('input',show);
})();