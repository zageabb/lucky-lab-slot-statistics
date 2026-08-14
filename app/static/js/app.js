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
    const reels=document.querySelector('#reels');reels?.classList.add('rolling');
    const symbols=['clover','harp','horseshoe','rainbow','emerald','crown','gold_pot'];
    const cells=[...(reels?.querySelectorAll('.symbol')||[])];
    const drums=[...(reels?.querySelectorAll('.reel-drum')||[])];
    drums.forEach(drum=>drum.classList.remove('reel-stopped'));
    cells.forEach(cell=>{cell.classList.remove('winning-cell','reel-stopped');cell.querySelector('.win-label')?.remove()});
    let tick=0;
    const drum=setInterval(()=>{tick++;cells.forEach(cell=>{
      const column=Number(cell.dataset.column),row=[...cell.parentElement.children].indexOf(cell);
      if(cell.classList.contains('reel-stopped'))return;
      const previous=cell.dataset.rollingSymbol;
      let id=symbols[Math.floor(Math.random()*symbols.length)];
      if(id===previous)id=symbols[(symbols.indexOf(id)+1+row+column)%symbols.length];
      cell.dataset.rollingSymbol=id;setCell(cell,id);
    })},reduced?50:145);
    let result;
    try{
      const response=await fetch(reelForm.action,{method:'POST',body:new FormData(reelForm),headers:{'X-Requested-With':'LuckyLabDrums'}});
      result=await response.json();if(!response.ok||!result.ok)throw new Error(result.error||'Spin could not be completed');
      await new Promise(resolve=>setTimeout(resolve,reduced?50:2350));
      for(let column=0;column<5;column++){
        const drumNode=drums.find(item=>Number(item.dataset.reel)===column);
        const columnCells=cells.filter(cell=>Number(cell.dataset.column)===column);
        columnCells.forEach((cell,row)=>{setCell(cell,result.board[row][column]);cell.classList.add('reel-stopped')});
        drumNode?.classList.add('reel-stopped');
        await new Promise(resolve=>setTimeout(resolve,reduced?10:285));
      }
      clearInterval(drum);reels.classList.remove('rolling');
      const winners=result.line_awards.filter(line=>line.payout_units>0);
      winners.forEach(line=>line.rows.slice(0,line.matches).forEach((row,column)=>{const cell=drums[column].children[row];cell.classList.add('winning-cell');const tag=document.createElement('b');tag.className='win-label';tag.textContent='WIN';cell.append(tag)}));
      const readouts=document.querySelectorAll('.game-readouts strong');readouts[0].textContent=credit(result.balance_units);readouts[1].textContent=credit(result.payout_units);
      const panel=document.querySelector('.game-result');panel.replaceChildren();
      const headline=document.createElement('strong');headline.textContent=credit(result.payout_units)+' credits returned';panel.append(headline);
      const net=document.createElement('span');net.textContent='Net change '+credit(result.payout_units-result.stake_units);panel.append(net);
      if(winners.length){const list=document.createElement('div');list.className='winning-lines';winners.forEach(line=>{const item=document.createElement('span');item.textContent=`Line ${line.line} · ${line.matches} ${labels[line.symbols[0]]} · ${line.multiplier}× · ${credit(line.payout_units)}`;list.append(item)});panel.append(list)}
      const audit=document.createElement('a');audit.href=result.audit_url;audit.textContent='Full calculation';panel.append(audit);
      reelForm.querySelector('[name=request_token]').value=newRequestToken();
    }catch(error){clearInterval(drum);reels?.classList.remove('rolling');const panel=document.querySelector('.game-result');panel.textContent=error.message}
    finally{button.disabled=false;button.querySelector('span').textContent='SPIN';reelForm.dataset.submitting='0'}
  });
}
