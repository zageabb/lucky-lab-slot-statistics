document.querySelectorAll('canvas.chart').forEach(canvas=>{const values=JSON.parse(canvas.dataset.values||'[]');const dpr=devicePixelRatio||1,w=canvas.clientWidth||600,h=260;canvas.width=w*dpr;canvas.height=h*dpr;const c=canvas.getContext('2d');c.scale(dpr,dpr);c.clearRect(0,0,w,h);if(!values.length)return;const min=Math.min(...values),max=Math.max(...values),range=max-min||1;c.strokeStyle='#d6c27b';c.globalAlpha=.3;for(let i=0;i<5;i++){let y=20+i*(h-40)/4;c.beginPath();c.moveTo(36,y);c.lineTo(w-12,y);c.stroke()}c.globalAlpha=1;if(canvas.dataset.chart==='bars'){const bw=(w-50)/values.length;c.fillStyle='#168260';values.forEach((v,i)=>{let bh=(v-min)/range*(h-50)+4;c.fillRect(38+i*bw,h-25-bh,Math.max(2,bw-3),bh)})}else{c.strokeStyle='#20a778';c.lineWidth=3;c.beginPath();values.forEach((v,i)=>{let x=38+i*(w-55)/Math.max(1,values.length-1),y=h-25-(v-min)/range*(h-50);i?c.lineTo(x,y):c.moveTo(x,y)});c.stroke()}c.fillStyle='#57655f';c.font='12px system-ui';c.fillText(min.toFixed(1),2,h-22);c.fillText(max.toFixed(1),2,22)});

const reelForm=document.querySelector('[data-reel-form]');
if(reelForm){
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const newRequestToken=()=>{
    if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();
    if(globalThis.crypto?.getRandomValues){const bytes=new Uint8Array(16);globalThis.crypto.getRandomValues(bytes);bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;return [...bytes].map((value,index)=>([4,6,8,10].includes(index)?'-':'')+value.toString(16).padStart(2,'0')).join('')}
    return 'mobile-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)+'-'+Math.random().toString(36).slice(2);
  };
  const labels={clover:'clover',harp:'harp',horseshoe:'horseshoe',rainbow:'rainbow',emerald:'emerald',crown:'crown',gold_pot:'gold pot'};
  const credit=value=>(value/100).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
  const setCell=(cell,id)=>{const image=cell.querySelector('img');image.src=image.src.replace(/[^/]+\.svg$/,id+'.svg');image.alt=labels[id];cell.querySelector(':scope > span').textContent=labels[id]};
  reelForm.addEventListener('submit',async event=>{
    if(reelForm.dataset.submitting==='1')return;
    event.preventDefault();reelForm.dataset.submitting='1';
    const button=reelForm.querySelector('button');button.disabled=true;button.querySelector('span').textContent='ROLLING';
    const reels=document.querySelector('#reels');reels?.classList.add('rolling','true-strip');
    const symbols=['clover','harp','horseshoe','rainbow','emerald','crown','gold_pot'];
    const cells=[...(reels?.querySelectorAll('.symbol')||[])];
    const drums=[...(reels?.querySelectorAll('.reel-drum')||[])];
    drums.forEach(drum=>drum.classList.remove('reel-stopped'));
    cells.forEach(cell=>{cell.classList.remove('winning-cell','reel-stopped');cell.querySelector('.win-label')?.remove()});
    let result;
    try{
      const response=await fetch(reelForm.action,{method:'POST',body:new FormData(reelForm),headers:{'X-Requested-With':'LuckyLabDrums'}});
      result=await response.json();if(!response.ok||!result.ok)throw new Error(result.error||'Spin could not be completed');
      const finalCells=[];
      const animations=drums.map((drumNode,column)=>{
        const originals=[...drumNode.querySelectorAll(':scope > .symbol')];
        const box=originals[0].getBoundingClientRect(),gap=parseFloat(getComputedStyle(drumNode).rowGap)||3;
        drumNode.style.height=`${box.height*3+gap*2}px`;drumNode.style.overflow='hidden';
        const ids=originals.map(cell=>cell.querySelector('img').src.match(/([^/]+)\.svg$/)?.[1]||'clover');
        for(let index=0;index<18+column*3;index++)ids.push(symbols[Math.floor(Math.random()*symbols.length)]);
        result.board.forEach(row=>ids.push(row[column]));
        const track=document.createElement('div');track.className='spin-track';track.style.gap=`${gap}px`;
        ids.forEach((id,index)=>{const cell=originals[index%3].cloneNode(true);cell.classList.remove('winning-cell','reel-stopped');cell.querySelector('.win-label')?.remove();setCell(cell,id);track.append(cell)});
        finalCells[column]=[...track.children].slice(-3).map(cell=>cell.cloneNode(true));drumNode.replaceChildren(track);
        if(reduced||!track.animate)return Promise.resolve();
        const distance=(ids.length-3)*(box.height+gap);
        return track.animate([{transform:'translateY(0)'},{transform:`translateY(-${distance}px)`}],{duration:2850+column*310,easing:'cubic-bezier(.12,.72,.12,1)',fill:'forwards'}).finished;
      });
      await Promise.all(animations);
      drums.forEach((drumNode,column)=>{drumNode.replaceChildren(...finalCells[column]);drumNode.style.removeProperty('height');drumNode.style.removeProperty('overflow')});
      reels.classList.remove('rolling','true-strip');
      const winners=result.line_awards.filter(line=>line.payout_units>0);
      winners.forEach(line=>line.rows.slice(0,line.matches).forEach((row,column)=>{const cell=drums[column].children[row];cell.classList.add('winning-cell');const tag=document.createElement('b');tag.className='win-label';tag.textContent='WIN';cell.append(tag)}));
      const readouts=document.querySelectorAll('.game-readouts strong');readouts[0].textContent=credit(result.balance_units);readouts[1].textContent=credit(result.payout_units);
      const panel=document.querySelector('.game-result');panel.replaceChildren();
      const headline=document.createElement('strong');headline.textContent=credit(result.payout_units)+' credits returned';panel.append(headline);
      const net=document.createElement('span');net.textContent='Net change '+credit(result.payout_units-result.stake_units);panel.append(net);
      if(winners.length){const list=document.createElement('div');list.className='winning-lines';winners.forEach(line=>{const item=document.createElement('span');item.textContent=`Line ${line.line} · ${line.matches} ${labels[line.symbols[0]]} · ${line.multiplier}× · ${credit(line.payout_units)}`;list.append(item)});panel.append(list)}
      const audit=document.createElement('a');audit.href=result.audit_url;audit.textContent='Full calculation';panel.append(audit);
      reelForm.querySelector('[name=request_token]').value=newRequestToken();
    }catch(error){reels?.classList.remove('rolling','true-strip');const panel=document.querySelector('.game-result');panel.textContent=error.message}
    finally{button.disabled=false;button.querySelector('span').textContent='SPIN';reelForm.dataset.submitting='0'}
  });
}
