(async function installHeroPhoto(){
  const el=document.querySelector('.hero-photo');
  if(!el)return;
  try{
    const response=await fetch('hero-data-small.txt?v=5',{cache:'no-store'});
    if(!response.ok)throw new Error('hero image data unavailable');
    const b64=(await response.text()).trim();
    el.style.backgroundImage=`linear-gradient(90deg,rgba(3,4,8,.70) 0%,rgba(3,4,8,.22) 40%,rgba(3,4,8,.02) 72%),linear-gradient(180deg,rgba(4,6,10,.02),rgba(4,6,10,.04) 50%,rgba(4,5,7,.69) 100%),url("data:image/webp;base64,${b64}")`;
    el.style.backgroundSize='cover';
    el.style.backgroundPosition='center center';
    el.style.backgroundRepeat='no-repeat';
    el.style.filter='saturate(1.24) contrast(1.08) brightness(.96)';
    el.dataset.heroLoaded='true';
  }catch(error){
    console.warn('Hero photo fallback active:',error);
  }
})();
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
function chisinauNow(){const n=new Date();const t=new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Chisinau',hour:'2-digit',minute:'2-digit'}).format(n);const d=new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Chisinau',weekday:'long',day:'numeric',month:'long'}).format(n);$('#clock').textContent=t;$('#date').textContent=d.charAt(0).toUpperCase()+d.slice(1)}
chisinauNow();setInterval(chisinauNow,30000);
$$('[data-scroll]').forEach(b=>b.addEventListener('click',()=>$(b.dataset.scroll)?.scrollIntoView({behavior:'smooth'})));
const toast=$('#toast');let timer;function say(text){toast.textContent=text;toast.classList.add('show');clearTimeout(timer);timer=setTimeout(()=>toast.classList.remove('show'),2600)}
function filterCards(filter){$$('.venue').forEach(c=>c.style.display=c.dataset.kind.split(' ').includes(filter)?'block':'none')}
$$('.mood').forEach(b=>b.addEventListener('click',()=>{$$('.mood').forEach(x=>x.classList.remove('active'));b.classList.add('active');filterCards(b.dataset.filter);$('#picks').scrollIntoView({behavior:'smooth'})}));
$$('.hero-tab').forEach(b=>b.addEventListener('click',()=>{$$('.hero-tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');const f=b.dataset.heroFilter;const mood=$(`.mood[data-filter="${f}"]`);if(mood){mood.click()}else{say('Подборка будет добавлена после наполнения реальными местами.')}}));
$$('.fav').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();b.textContent=b.textContent==='♡'?'♥':'♡';say(b.textContent==='♥'?'Добавлено в избранное':'Удалено из избранного')}));
const scenarios={wild:{crew:['Шумный бар для сбора','Клуб или большая вечеринка','Ночная еда для всей банды'],couple:['Коктейльный разогрев','Танцпол без скуки','Поздний бургер'],solo:['Бар у стойки','Событие с живой публикой','Перекус после ночи']},balanced:{crew:['Бар, где можно собраться','Концерт / DJ / rooftop','Еда после полуночи'],couple:['Красивый бар','Кино, live или rooftop','Финальный бокал'],solo:['Камерное место','Квиз / live / кино','Ночная кухня']},calm:{crew:['Вино и закуски','Спокойный live','Десерт или прогулка'],couple:['Место с видом','Поздний сеанс или музыка','Тихий бар'],solo:['Кофе-бар или вино','Кино / выставка / джем','Прогулка через центр']}};
$('#build').addEventListener('click',()=>{const e=$('#energy').value,c=$('#company').value,b=$('#budget').value,s=scenarios[e][c];$('#s1').textContent=s[0];$('#s2').textContent=s[1];$('#s3').textContent=s[2];const names={wild:'«Сегодня без тормозов»',balanced:'«Сначала культурно»',calm:'«Красиво и без суеты»'},money={low:' · бюджетно',mid:' · нормальный бюджет',high:' · без компромиссов'};$('#resultTitle').textContent='Твой сценарий: '+names[e]+money[b];$('#result').classList.add('show');$('#result').scrollIntoView({behavior:'smooth',block:'nearest'})});
$$('[data-map]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();$('#mapModal').classList.add('show')}));
$('#mapClose').addEventListener('click',()=>$('#mapModal').classList.remove('show'));
$('#mapModal').addEventListener('click',e=>{if(e.target===$('#mapModal'))$('#mapModal').classList.remove('show')});
$('#newsletter').addEventListener('submit',e=>{e.preventDefault();e.target.reset();say('Это демонстрация. Настоящую подписку подключим после запуска.')});
