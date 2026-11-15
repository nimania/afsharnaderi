(() => {
  const input = document.getElementById('search');
  const select = document.getElementById('category');
  const items = [...document.querySelectorAll('.resource')];
  const none = document.getElementById('no-results');
  if (!input || !select || !none) return;
  const normalize = (text) => text.normalize('NFKC').replace(/ي/g, 'ی').replace(/ك/g, 'ک').toLocaleLowerCase('fa');
  const refresh = () => {
    const query = normalize(input.value.trim());
    let count = 0;
    for (const item of items) {
      const matches = normalize(item.textContent || '').includes(query) && (select.value === 'all' || item.dataset.category === select.value);
      item.hidden = !matches;
      if (matches) count++;
    }
    none.hidden = count > 0;
  };
  input.addEventListener('input', refresh);
  select.addEventListener('change', refresh);
})();
// Family chart browser v2

// Family chart browser v2
(() => {
 const image=document.getElementById('branch-image');
 const buttons=[...document.querySelectorAll('.branch-choice')];
 if(!image||!buttons.length)return;
 const names=JSON.parse(document.getElementById('branch-data').textContent);
 const heading=document.getElementById('branch-heading');
 const full=document.getElementById('branch-full');
 const page=document.getElementById('branch-page');
 const width=document.getElementById('diagram-scroll');
 let zoom=1;
 const select=(i,updateUrl=true)=>{
   if(!(i>=1&&i<=names.length))return;
   image.src='./tabaar/png_'+i+'.png';
   image.alt='شجره‌نامهٔ شاخهٔ '+names[i-1];
   heading.textContent=names[i-1];
   full.href=image.src;
   page.href='./tabaar/png_'+i+'.htm';
   buttons.forEach(b=>{const on=Number(b.dataset.branch)===i;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',String(on))});
   zoom=1;image.style.width='100%';width.scrollTop=0;width.scrollLeft=0;
   if(updateUrl&&window.history?.replaceState) {
     const next=new URL(window.location.href);next.searchParams.set('branch',String(i));
     window.history.replaceState(null,'',next.pathname+next.search);
   }
 };
 const resize=(factor)=>{zoom=Math.max(.4,Math.min(4,factor));image.style.width=(zoom*100)+'%'};
 buttons.forEach(b=>b.addEventListener('click',()=>select(Number(b.dataset.branch))));
 document.getElementById('zoom-in')?.addEventListener('click',()=>resize(zoom*1.25));
 document.getElementById('zoom-out')?.addEventListener('click',()=>resize(zoom/1.25));
 document.getElementById('zoom-reset')?.addEventListener('click',()=>resize(1));
 const branch=Number(new URL(window.location.href).searchParams.get('branch'))||1;
 select(branch,false);
})();
