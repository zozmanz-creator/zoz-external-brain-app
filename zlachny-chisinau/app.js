const HERO_SOURCES=[
  'https://images.squarespace-cdn.com/content/v1/58d6b4fff7e0ab027a072845/1599487851648-2JOW59IZPAYPFH8PLD8F/zaxi-night1.jpg?format=2500w',
  'https://images.squarespace-cdn.com/content/v1/58d6b4fff7e0ab027a072845/1599487852061-X90P1WCGF0P7AKF2UYU1/zaxi-night2.jpg?format=2500w',
  'https://images.unsplash.com/photo-1619126382039-4807e9677ec2?auto=format&fit=crop&w=2400&q=92'
];
(function loadSharpHero(index=0){
  const target=document.querySelector('.hero-photo');if(!target||index>=HERO_SOURCES.length)return;
  const image=new Image();image.decoding='async';image.onload=()=>{target.style.backgroundImage=`url("${HERO_SOURCES[index]}")`;target.dataset.heroSource=String(index)};image.onerror=()=>loadSharpHero(index+1);image.src=HERO_SOURCES[index];
})();
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
function chisinauNow(){
  const n=new Date();
  const t=new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Chisinau',hour:'2-digit',minute:'2-digit'}).format(n);
  const d=new Intl.DateTimeFormat('ru-RU',{timeZone:'Europe/Chisinau',weekday:'long',day:'numeric',month:'long'}).format(n);
  $('#clock').textContent=t;
  $('#date').textContent=d.charAt(0).toUpperCase()+d.slice(1);
}
chisinauNow();setInterval(chisinauNow,30000);
$$('[data-scroll]').forEach(b=>b.addEventListener('click',()=>$(b.dataset.scroll)?.scrollIntoView({behavior:'smooth'})));
const toast=$('#toast');let tt;
function say(text){toast.textContent=text;toast.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>toast.classList.remove('show'),2600)}
function filterCards(filter){
  $$('.venue').forEach(card=>{card.style.display=card.dataset.kind.split(' ').includes(filter)?'block':'none'});
  $('#picks').scrollIntoView({behavior:'smooth',block:'start'});
}
$$('.mood').forEach(button=>button.addEventListener('click',()=>{
  $$('.mood').forEach(x=>x.classList.remove('active'));button.classList.add('active');filterCards(button.dataset.filter);
}));
$$('.hero-tab').forEach(button=>button.addEventListener('click',()=>{
  $$('.hero-tab').forEach(x=>x.classList.remove('active'));button.classList.add('active');
  const corresponding=$(`.mood[data-filter="${button.dataset.heroFilter}"]`);if(corresponding){$$('.mood').forEach(x=>x.classList.remove('active'));corresponding.classList.add('active')}
  filterCards(button.dataset.heroFilter);
}));
$$('.fav').forEach(button=>button.addEventListener('click',event=>{
  event.stopPropagation();button.classList.toggle('active');say(button.classList.contains('active')?'Добавлено в избранное':'Удалено из избранного');
}));
const scenarios={
  wild:{crew:['Шумный бар для сбора','Клуб или большая вечеринка','Ночная еда для всей банды'],couple:['Коктейльный разогрев','Танцпол без скуки','Поздний бургер'],solo:['Бар у стойки','Событие с живой публикой','Перекус после ночи']},
  balanced:{crew:['Бар, где можно собраться','Концерт / DJ / rooftop','Еда после полуночи'],couple:['Красивый бар','Кино, live или rooftop','Финальный бокал'],solo:['Камерное место','Квиз / live / кино','Ночная кухня']},
  calm:{crew:['Вино и закуски','Спокойный live','Десерт или прогулка'],couple:['Место с видом','Поздний сеанс или музыка','Тихий бар'],solo:['Кофе-бар или вино','Кино / выставка / джем','Прогулка через центр']}
};
$('#build').addEventListener('click',()=>{
  const e=$('#energy').value,c=$('#company').value,b=$('#budget').value,s=scenarios[e][c];
  $('#s1').textContent=s[0];$('#s2').textContent=s[1];$('#s3').textContent=s[2];
  const names={wild:'«Сегодня без тормозов»',balanced:'«Сначала культурно»',calm:'«Красиво и без суеты»'},money={low:' · бюджетно',mid:' · нормальный бюджет',high:' · без компромиссов'};
  $('#resultTitle').textContent='Твой сценарий: '+names[e]+money[b];$('#result').classList.add('show');$('#result').scrollIntoView({behavior:'smooth',block:'nearest'});
});
$$('[data-map]').forEach(button=>button.addEventListener('click',event=>{event.preventDefault();$('#mapModal').classList.add('show')}));
$('#mapClose').addEventListener('click',()=>$('#mapModal').classList.remove('show'));
$('#mapModal').addEventListener('click',event=>{if(event.target===$('#mapModal'))$('#mapModal').classList.remove('show')});
$('#newsletter').addEventListener('submit',event=>{event.preventDefault();event.currentTarget.reset();say('Готово. Настоящую подписку подключим после запуска базы мест.')});
